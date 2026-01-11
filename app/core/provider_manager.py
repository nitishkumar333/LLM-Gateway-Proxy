from app.models.chat import ChatCompletionRequest
from typing import Dict
from app.providers.anthropic_adapter import AnthropicAdapter
from app.providers.gemini_adapter import GeminiAdapter
from app.providers.openai_adapter import OpenAIAdapter
from app.providers.ollama_adapter import OllamaAdapter
from app.utils.logger import get_logger
from fastapi import HTTPException

logger = get_logger(__name__)

class ProviderManager:
    def __init__(self):
        self.providers = {
            "openai": OpenAIAdapter(),
            "anthropic": AnthropicAdapter(),
            "gemini": GeminiAdapter(),
            "ollama": OllamaAdapter(),
        }
        self.fallback_order = ["openai", "anthropic", "gemini"]
        logger.debug(f"ProviderManager initialized with fallback order: {self.fallback_order}")
    
    async def execute_with_fallback(self, request: ChatCompletionRequest) -> tuple[Dict, str]:
        """Execute request with conditional fallback
        
        - If provider is specified (not "auto"), route directly to that provider.
          If it fails, return error WITHOUT fallback.
        - If provider is "auto", iterate through fallback chain until one succeeds.
        """
        provider_name = request.provider or "auto"
        
        # Direct routing to specific provider (NO FALLBACK)
        if provider_name != "auto":
            if provider_name not in self.providers:
                logger.error(f"Unknown provider requested: {provider_name}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unknown provider: {provider_name}. Available: {list(self.providers.keys())}"
                )
            
            logger.debug(f"Direct routing to provider: {provider_name}")
            provider = self.providers[provider_name]
            try:
                result = await provider.chat_completion(request)
                logger.debug(f"Provider {provider_name} returned successfully")
                return result, provider_name
            except Exception as e:
                # NO FALLBACK for specific provider requests
                logger.error(f"Provider {provider_name} failed (no fallback): {str(e)}")
                raise HTTPException(
                    status_code=503, 
                    detail=f"Provider '{provider_name}' failed: {str(e)}"
                )
        
        # Auto mode: iterate through fallback chain
        logger.debug(f"Auto mode - trying fallback chain: {self.fallback_order}")
        last_error = None
        for fallback_provider_name in self.fallback_order:
            provider = self.providers[fallback_provider_name]
            try:
                result = await provider.chat_completion(request)
                logger.debug(f"Provider {fallback_provider_name} succeeded")
                return result, fallback_provider_name
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {fallback_provider_name} failed, trying next: {str(e)}")
                continue
        
        logger.error(f"All providers in fallback chain failed. Last error: {last_error}")
        raise HTTPException(
            status_code=503, 
            detail=f"All providers failed. Last error: {last_error}"
        )