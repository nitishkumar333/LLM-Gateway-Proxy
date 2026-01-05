from typing import Dict
from app.models.chat import ChatCompletionRequest
from app.providers.base import ProviderAdapter
from app.config.settings import Config
import httpx, time

class GeminiAdapter(ProviderAdapter):
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict:
        # Convert messages
        contents = []
        for msg in request.messages:
            role = "user" if msg.role in ["user", "system"] else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})
        
        model = "gemini-pro"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/{model}:generateContent",
                params={"key": self.api_key},
                json={
                    "contents": contents,
                    "generationConfig": {
                        "temperature": request.temperature,
                        "maxOutputTokens": request.max_tokens or 8192,
                    }
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Convert to OpenAI format
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "id": f"gemini-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": data.get("usageMetadata", {}).get("promptTokenCount", 0),
                    "completion_tokens": data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                    "total_tokens": data.get("usageMetadata", {}).get("totalTokenCount", 0)
                }
            }