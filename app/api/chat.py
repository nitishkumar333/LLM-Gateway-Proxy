from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request
from app.schemas.request_log import RequestLog
from app.schemas.virtual_key import VirtualKey
from app.config.settings import Config
from app.database.session import get_db
from app.models.chat import ChatCompletionRequest
from app.core.pii_masker import PIIMasker
from app.api.deps import verify_virtual_key, invalidate_virtual_key_cache
from app.core.budget_manager import BudgetManager
from app.core.cost_calculator import CostCalculator
import time
import json
from fastapi import APIRouter

chat_router = APIRouter()

@chat_router.post("/ai-chat/")
async def chat_completions(
    request_http: Request,
    request: ChatCompletionRequest,
    virtual_key = Depends(verify_virtual_key),
    db: Session = Depends(get_db)
):
    """OpenAI-compatible chat completions endpoint
    
    Supports provider selection:
    - provider="auto" (default): Uses fallback chain if a provider fails
    - provider="openai"|"anthropic"|"gemini": Direct routing, no fallback
    """
    start_time = time.time()
    
    # PII Masking
    if Config.ENABLE_PII_MASKING:
        for message in request.messages:
            message.content, pii_detected = PIIMasker.mask_text(message.content)
            if pii_detected:
                print(f"PII detected and masked: {pii_detected}")
    
    # Check cache first
    cache_manager = request_http.app.state.cache_manager
    
    # Try exact cache
    cached_response = cache_manager.get_exact_cache(request)
    if cached_response:
        # Log cached request
        log = RequestLog(
            virtual_key_id=virtual_key.id,
            provider="cache",
            model=request.model,
            cached=True,
            latency_ms=(time.time() - start_time) * 1000,
            request_body=json.dumps(request.dict()),
            response_body=json.dumps(cached_response)
        )
        db.add(log)
        db.commit()
        return cached_response
    
    # Try semantic cache
    cached_response = cache_manager.get_semantic_cache(request)
    if cached_response:
        log = RequestLog(
            virtual_key_id=virtual_key.id,
            provider="semantic_cache",
            model=request.model,
            cached=True,
            latency_ms=(time.time() - start_time) * 1000,
            request_body=json.dumps(request.dict()),
            response_body=json.dumps(cached_response)
        )
        db.add(log)
        db.commit()
        return cached_response
    
    # Estimate cost and check budget
    estimated_cost = 0.01  # Rough estimate
    budget_manager = BudgetManager(db)
    if not budget_manager.check_budget(virtual_key.id, estimated_cost):
        raise HTTPException(status_code=429, detail="Budget limit exceeded")
    
    # Execute request with fallback (conditional based on provider)
    try:
        provider_manager = request_http.app.state.provider_manager
        response, provider_used = await provider_manager.execute_with_fallback(request)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Calculate actual cost
        usage = response.get("usage", {})
        actual_cost = CostCalculator.calculate(
            request.model,
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0)
        )
        
        # Update budget and invalidate cache
        budget_manager.update_spend(virtual_key.id, actual_cost)
        invalidate_virtual_key_cache(virtual_key.id)
        
        # Log request with full request/response for fine-tuning
        log = RequestLog(
            virtual_key_id=virtual_key.id,
            provider=provider_used,
            model=request.model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_cost=actual_cost,
            latency_ms=latency_ms,
            status="success",
            request_body=json.dumps(request.dict()),
            response_body=json.dumps(response)
        )
        db.add(log)
        db.commit()
        
        # Cache the response
        cache_manager.set_exact_cache(request, response)
        cache_manager.set_semantic_cache(request, response)
        
        return response
        
    except Exception as e:
        # Log error
        log = RequestLog(
            virtual_key_id=virtual_key.id,
            provider=request.provider or "unknown",
            model=request.model,
            status="error",
            error_message=str(e),
            latency_ms=(time.time() - start_time) * 1000,
            request_body=json.dumps(request.dict())
        )
        db.add(log)
        db.commit()
        raise