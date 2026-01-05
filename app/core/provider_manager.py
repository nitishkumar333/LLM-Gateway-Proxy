from app.models.chat import ChatCompletionRequest
from typing import Dict
from app.providers.anthropic_adapter import AnthropicAdapter
from app.providers.gemini_adapter import GeminiAdapter
from app.providers.openai_adapter import OpenAIAdapter
from fastapi import HTTPException

class ProviderManager:
    def __init__(self):
        self.providers = {
            "openai": OpenAIAdapter(),
            "anthropic": AnthropicAdapter(),
            "gemini": GeminiAdapter(),
        }
        self.fallback_order = ["openai", "anthropic", "gemini"]
    
    async def execute_with_fallback(self, request: ChatCompletionRequest) -> tuple[Dict, str]:
        """Execute request with automatic fallback"""
        last_error = None
        
        for provider_name in self.fallback_order:
            provider = self.providers[provider_name]
            try:
                result = await provider.chat_completion(request)
                return result, provider_name
            except Exception as e:
                last_error = e
                print(f"Provider {provider_name} failed: {e}")
                continue
        
        raise HTTPException(status_code=503, detail=f"All providers failed. Last error: {last_error}")