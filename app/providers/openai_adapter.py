from typing import Dict
from app.models.chat import ChatCompletionRequest
from app.providers.base import ProviderAdapter
from app.config.settings import Config
import httpx

class OpenAIAdapter(ProviderAdapter):
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
    
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=request.dict(exclude_none=True),
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()