from fastapi import FastAPI
from app.database.session import lifespan
from app.api.health import health_router
from app.api.admin import virtual_router
from app.api.chat import chat_router
from app.utils.logger import setup_logging

# Initialize logging before app startup
setup_logging()

app = FastAPI(
    title="LLM Gateway",
    description="Production-ready gateway for routing LLM API calls",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health_router)
app.include_router(virtual_router)
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)