from typing import Dict
from app.models.chat import ChatCompletionRequest

class ProviderAdapter:
    """Base class for provider adapters"""
    
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict:
        raise NotImplementedError