from sqlalchemy import Column, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from app.config.settings import Config
from datetime import datetime
from app.database.session import Base

class VirtualKey(Base):
    __tablename__ = "virtual_keys"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    budget_limit = Column(Float, default=Config.DEFAULT_BUDGET_LIMIT)
    current_spend = Column(Float, default=0.0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)