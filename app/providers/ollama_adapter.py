from typing import Dict
from app.models.chat import ChatCompletionRequest
from app.providers.base import ProviderAdapter
from app.config.settings import Config
from app.utils.logger import get_logger
import httpx
import time

logger = get_logger(__name__)

class OllamaAdapter(ProviderAdapter):
    """Adapter for local Ollama LLM server"""
    
    def __init__(self):
        self.base_url = Config.OLLAMA_URL
    
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict:
        """Execute chat completion against Ollama API"""
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        logger.debug(f"Ollama request - model: {request.model}, messages: {len(messages)}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": request.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens or 2048
                    }
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            total_tokens = data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
            logger.debug(f"Ollama response - tokens: {total_tokens}")
            
            # Convert Ollama response to OpenAI format
            return {
                "id": f"ollama-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant", 
                        "content": data["message"]["content"]
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": total_tokens
                }
            }
