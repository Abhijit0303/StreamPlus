from fastapi import FastAPI

app = FastAPI(title="StreamPulse API", description="API for StreamPulse service", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "StreamPulse"}