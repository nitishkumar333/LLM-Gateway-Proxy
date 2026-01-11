from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header
from app.schemas.virtual_key import VirtualKey
from app.database.session import get_db
from app.config.settings import Config
from pydantic import BaseModel
from app.utils.logger import get_logger
import redis
import json

logger = get_logger(__name__)

# Redis client for virtual key caching
redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
VIRTUAL_KEY_CACHE_TTL = 60  # seconds

class VirtualKeyCache(BaseModel):
    """Cached representation of a virtual key"""
    id: str
    name: str
    budget_limit: float
    current_spend: float
    enabled: bool

async def verify_virtual_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    """Verify virtual API key with Redis caching (60s TTL)"""
    cache_key = f"vk:{x_api_key}"
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        key_data = json.loads(cached)
        if not key_data["enabled"]:
            logger.warning(f"Disabled API key used: {x_api_key[:12]}...")
            raise HTTPException(status_code=401, detail="API key is disabled")
        logger.debug(f"API key verified from cache: {x_api_key[:12]}...")
        return VirtualKeyCache(**key_data)
    
    # Query database
    key = db.query(VirtualKey).filter(VirtualKey.id == x_api_key).first()
    if not key or not key.enabled:
        logger.warning(f"Invalid/disabled API key attempt: {x_api_key[:12]}...")
        raise HTTPException(status_code=401, detail="Invalid or disabled API key")
    
    logger.debug(f"API key verified from database: {x_api_key[:12]}...")
    
    # Cache the result
    key_data = {
        "id": key.id, 
        "name": key.name, 
        "budget_limit": key.budget_limit, 
        "current_spend": key.current_spend, 
        "enabled": key.enabled
    }
    redis_client.setex(cache_key, VIRTUAL_KEY_CACHE_TTL, json.dumps(key_data))
    
    return key


def invalidate_virtual_key_cache(key_id: str):
    """Invalidate cached virtual key (call after budget updates)"""
    redis_client.delete(f"vk:{key_id}")
    logger.debug(f"Invalidated cache for key: {key_id[:12]}...")