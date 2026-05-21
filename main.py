from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import ingest
from services import redis_stream
from config import APP_HOST, APP_PORT, LOG_LEVEL
import logging

# Setup logging
logging.basicConfig(level=LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_stream.connect_redis()
    yield
    # Shutdown
    await redis_stream.disconnect_redis()


app = FastAPI(
    title="StreamPulse API",
    description="API for StreamPulse service",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingest.router)


@app.get("/health")
async def health():
    redis_available = await redis_stream.is_redis_available()
    return {
        "status": "ok",
        "service": "StreamPulse",
        "redis": "connected" if redis_available else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)