from app.config.settings import Config
from app.models.chat import ChatCompletionRequest
from typing import Optional, Dict
import hashlib, json, redis, chromadb
from datetime import datetime

class CacheManager:
    def __init__(self):
        self.redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
        self.chroma_client = chromadb.Client()
        self.semantic_collection = self.chroma_client.get_or_create_collection("semantic_cache")
    
    def _generate_cache_key(self, request: ChatCompletionRequest) -> str:
        """Generate a hash key for exact caching"""
        cache_str = f"{request.model}:{json.dumps([m.dict() for m in request.messages], sort_keys=True)}"
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get_exact_cache(self, request: ChatCompletionRequest) -> Optional[Dict]:
        """Retrieve from exact cache"""
        if not Config.ENABLE_EXACT_CACHE:
            return None
        
        key = self._generate_cache_key(request)
        cached = self.redis_client.get(f"exact:{key}")
        if cached:
            return json.loads(cached)
        return None
    
    def set_exact_cache(self, request: ChatCompletionRequest, response: Dict):
        """Store in exact cache"""
        if not Config.ENABLE_EXACT_CACHE:
            return
        
        key = self._generate_cache_key(request)
        self.redis_client.setex(
            f"exact:{key}",
            Config.CACHE_TTL_SECONDS,
            json.dumps(response)
        )
    
    def get_semantic_cache(self, request: ChatCompletionRequest) -> Optional[Dict]:
        """Retrieve from semantic cache using similarity search"""
        if not Config.ENABLE_SEMANTIC_CACHE:
            return None
        
        try:
            query_text = " ".join([m.content for m in request.messages])
            results = self.semantic_collection.query(
                query_texts=[query_text],
                n_results=1
            )
            
            if results['distances'][0] and results['distances'][0][0] < (1 - Config.SEMANTIC_SIMILARITY_THRESHOLD):
                metadata = results['metadatas'][0][0]
                return json.loads(metadata['response'])
        except Exception as e:
            print(f"Semantic cache error: {e}")
        
        return None
    
    def set_semantic_cache(self, request: ChatCompletionRequest, response: Dict):
        """Store in semantic cache"""
        if not Config.ENABLE_SEMANTIC_CACHE:
            return
        
        try:
            query_text = " ".join([m.content for m in request.messages])
            cache_id = self._generate_cache_key(request)
            
            self.semantic_collection.add(
                documents=[query_text],
                metadatas=[{"response": json.dumps(response), "timestamp": datetime.utcnow().isoformat()}],
                ids=[cache_id]
            )
        except Exception as e:
            print(f"Semantic cache store error: {e}")