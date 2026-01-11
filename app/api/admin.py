from sqlalchemy.orm import Session
from fastapi import Depends
from app.schemas.request_log import RequestLog
from app.schemas.virtual_key import VirtualKey
from app.config.settings import Config
from app.database.session import get_db
from app.utils.logger import get_logger
from fastapi import APIRouter

logger = get_logger(__name__)

virtual_router = APIRouter()

@virtual_router.post("/admin/virtual-keys")
async def create_virtual_key(name: str, budget_limit: float = Config.DEFAULT_BUDGET_LIMIT, db: Session = Depends(get_db)):
    """Create a new virtual API key"""
    import secrets
    key_id = f"vk_{secrets.token_urlsafe(32)}"
    
    virtual_key = VirtualKey(
        id=key_id,
        name=name,
        budget_limit=budget_limit
    )
    db.add(virtual_key)
    db.commit()
    
    logger.info(f"Virtual key created - name: {name}, budget: ${budget_limit}, id: {key_id[:12]}...")
    
    return {"key_id": key_id, "name": name, "budget_limit": budget_limit}

@virtual_router.get("/admin/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Get analytics dashboard data"""
    from sqlalchemy import func
    
    logger.debug("Fetching analytics data...")
    
    # Calculate metrics
    total_requests = db.query(func.count(RequestLog.id)).scalar()
    total_cost = db.query(func.sum(RequestLog.total_cost)).scalar() or 0
    avg_latency = db.query(func.avg(RequestLog.latency_ms)).scalar() or 0
    cache_hit_rate = db.query(func.count(RequestLog.id)).filter(RequestLog.cached == True).scalar() / max(total_requests, 1) * 100
    
    # Get requests by provider
    provider_stats = db.query(
        RequestLog.provider,
        func.count(RequestLog.id).label("count"),
        func.avg(RequestLog.latency_ms).label("avg_latency")
    ).group_by(RequestLog.provider).all()
    
    # Get top spenders
    top_spenders = db.query(
        VirtualKey.name,
        VirtualKey.current_spend,
        VirtualKey.budget_limit
    ).order_by(VirtualKey.current_spend.desc()).limit(10).all()
    
    logger.info(f"Analytics retrieved - requests: {total_requests}, total_cost: ${total_cost:.2f}")
    
    return {
        "overview": {
            "total_requests": total_requests,
            "total_cost_usd": round(total_cost, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "cache_hit_rate_percent": round(cache_hit_rate, 2)
        },
        "provider_stats": [
            {
                "provider": stat.provider,
                "requests": stat.count,
                "avg_latency_ms": round(stat.avg_latency, 2)
            }
            for stat in provider_stats
        ],
        "top_spenders": [
            {
                "name": spender.name,
                "spend": round(spender.current_spend, 2),
                "limit": spender.budget_limit,
                "usage_percent": round(spender.current_spend / spender.budget_limit * 100, 1)
            }
            for spender in top_spenders
        ]
    }