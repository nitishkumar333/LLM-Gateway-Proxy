from fastapi import FastAPI
from app.database.session import lifespan
from app.api.health import health_router
from app.api.admin import virtual_router
from app.api.chat import chat_router

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
    # uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)