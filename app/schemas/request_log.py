from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, Text
from datetime import datetime
from app.database.session import Base

class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    virtual_key_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    ttft_ms = Column(Float, nullable=True)  # Time to first token
    status = Column(String, default="success")
    error_message = Column(Text, nullable=True)
    cached = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    request_body = Column(Text, nullable=True)   # Full request JSON for fine-tuning
    response_body = Column(Text, nullable=True)  # Full response JSON for fine-tuning