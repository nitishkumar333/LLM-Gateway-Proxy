from typing import List, Dict
from app.models.chat import Message, ChatCompletionRequest
from app.providers.base import ProviderAdapter
from app.config.settings import Config
import httpx, time

class AnthropicAdapter(ProviderAdapter):
    def __init__(self):
        self.api_key = Config.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1"
    
    def _convert_messages(self, messages: List[Message]) -> tuple[str, List[Dict]]:
        """Convert OpenAI format to Anthropic format"""
        system = ""
        converted = []
        
        for msg in messages:
            if msg.role == "system":
                system = msg.content
            else:
                converted.append({"role": msg.role, "content": msg.content})
        
        return system, converted
    
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict:
        system, messages = self._convert_messages(request.messages)
        
        # Map model names
        model_map = {
            "gpt-4": "claude-sonnet-4-20250514",
            "gpt-3.5-turbo": "claude-haiku-4-5-20251001",
        }
        model = model_map.get(request.model, "claude-sonnet-4-20250514")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": model,
                    "max_tokens": request.max_tokens or 4096,
                    "messages": messages,
                    "system": system,
                    "temperature": request.temperature,
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Convert back to OpenAI format
            return {
                "id": data["id"],
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": data["content"][0]["text"]
                    },
                    "finish_reason": data["stop_reason"]
                }],
                "usage": {
                    "prompt_tokens": data["usage"]["input_tokens"],
                    "completion_tokens": data["usage"]["output_tokens"],
                    "total_tokens": data["usage"]["input_tokens"] + data["usage"]["output_tokens"]
                }
            }