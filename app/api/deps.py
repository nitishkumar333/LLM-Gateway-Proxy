from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header
from app.schemas.virtual_key import VirtualKey
from app.database.session import get_db

async def verify_virtual_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    """Verify virtual API key"""
    key = db.query(VirtualKey).filter(VirtualKey.id == x_api_key).first()
    if not key or not key.enabled:
        raise HTTPException(status_code=401, detail="Invalid or disabled API key")
    return key