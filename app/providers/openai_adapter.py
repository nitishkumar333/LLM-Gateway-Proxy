from typing import Dict
from app.models.chat import ChatCompletionRequest
from app.providers.base import ProviderAdapter
from app.config.settings import Config
from app.utils.logger import get_logger
import httpx

logger = get_logger(__name__)

class OpenAIAdapter(ProviderAdapter):
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
    
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        
        logger.debug(f"OpenAI request - model: {request.model}, messages: {len(request.messages)}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=request.dict(exclude_none=True),
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            logger.debug(
                f"OpenAI response - tokens: {data.get('usage', {}).get('total_tokens', 'N/A')}"
            )
            
            return data