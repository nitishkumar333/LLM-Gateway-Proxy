import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/llm_gateway")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Provider API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    # Caching
    ENABLE_EXACT_CACHE = True
    ENABLE_SEMANTIC_CACHE = True
    SEMANTIC_SIMILARITY_THRESHOLD = 0.95
    CACHE_TTL_SECONDS = 3600
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Governance
    ENABLE_PII_MASKING = True
    DEFAULT_BUDGET_LIMIT = 100.0  # USD
    BUDGET_ALERT_THRESHOLD = 0.8  # 80%
    
    # Webhooks
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
