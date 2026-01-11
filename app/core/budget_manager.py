from sqlalchemy.orm import Session
from app.schemas.virtual_key import VirtualKey
from app.config.settings import Config
import httpx

class BudgetManager:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def check_budget(self, virtual_key_id: str, estimated_cost: float) -> bool:
        """Check if request is within budget"""
        key = self.db.query(VirtualKey).filter(VirtualKey.id == virtual_key_id).first()
        if not key or not key.enabled:
            return False
        
        if key.current_spend + estimated_cost > key.budget_limit:
            return False
        
        return True
    
    def update_spend(self, virtual_key_id: str, cost: float):
        """Update spending for virtual key"""
        key = self.db.query(VirtualKey).filter(VirtualKey.id == virtual_key_id).first()
        if key:
            key.current_spend += cost
            self.db.commit()
            
            # Check for budget alerts
            if key.current_spend / key.budget_limit >= Config.BUDGET_ALERT_THRESHOLD:
                pass
