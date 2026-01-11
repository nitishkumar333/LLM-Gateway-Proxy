from sqlalchemy.orm import Session
from app.schemas.virtual_key import VirtualKey
from app.config.settings import Config
from app.utils.logger import get_logger
import httpx

logger = get_logger(__name__)

class BudgetManager:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def check_budget(self, virtual_key_id: str, estimated_cost: float) -> bool:
        """Check if request is within budget"""
        key = self.db.query(VirtualKey).filter(VirtualKey.id == virtual_key_id).first()
        if not key or not key.enabled:
            logger.debug(f"Budget check failed - key not found or disabled: {virtual_key_id[:12]}...")
            return False
        
        if key.current_spend + estimated_cost > key.budget_limit:
            logger.warning(
                f"Budget limit would be exceeded - key: {virtual_key_id[:12]}..., "
                f"current: ${key.current_spend:.2f}, limit: ${key.budget_limit:.2f}"
            )
            return False
        
        return True
    
    def update_spend(self, virtual_key_id: str, cost: float):
        """Update spending for virtual key"""
        key = self.db.query(VirtualKey).filter(VirtualKey.id == virtual_key_id).first()
        if key:
            key.current_spend += cost
            self.db.commit()
            
            usage_percent = key.current_spend / key.budget_limit
            logger.debug(
                f"Budget updated - key: {virtual_key_id[:12]}..., "
                f"spent: ${key.current_spend:.2f}/{key.budget_limit:.2f} ({usage_percent:.1%})"
            )
            
            # Check for budget alerts
            if usage_percent >= Config.BUDGET_ALERT_THRESHOLD:
                logger.warning(
                    f"Budget alert threshold reached - key: {virtual_key_id[:12]}..., "
                    f"usage: {usage_percent:.1%}"
                )
