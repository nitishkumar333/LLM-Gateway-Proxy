from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import Config
from contextlib import asynccontextmanager
from app.core.provider_manager import ProviderManager
from app.core.cache_manager import CacheManager
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    from app.schemas import request_log, virtual_key
    Base.metadata.create_all(engine)
    # Initialize components
    app.state.cache_manager = CacheManager()
    app.state.provider_manager = ProviderManager()
    print("🚀 LLM Gateway started successfully")
    yield
    print("👋 LLM Gateway shutting down")