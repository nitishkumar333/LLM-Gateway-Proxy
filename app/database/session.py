from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import Config
from contextlib import asynccontextmanager
from app.core.provider_manager import ProviderManager
from app.core.cache_manager import CacheManager
from sqlalchemy.ext.declarative import declarative_base
from app.utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()

logger.debug(f"Connecting to database: {Config.DATABASE_URL.split('@')[-1]}")  # Log without credentials
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
logger.debug("Database engine and session factory created")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Initializing LLM Gateway...")
    
    from app.schemas import request_log, virtual_key
    Base.metadata.create_all(engine)
    logger.debug("Database tables created/verified")
    
    # Initialize components
    app.state.cache_manager = CacheManager()
    logger.debug("Cache manager initialized")
    
    app.state.provider_manager = ProviderManager()
    logger.debug("Provider manager initialized")
    
    logger.info("🚀 LLM Gateway started successfully")
    yield
    logger.info("👋 LLM Gateway shutting down")