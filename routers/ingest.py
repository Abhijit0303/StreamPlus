from fastapi import APIRouter, HTTPException
from models.telemetry import TelemetryIngest, TelemetryResponse
from services import redis_stream

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=TelemetryResponse)
async def ingest_telemetry(data: TelemetryIngest) -> TelemetryResponse:
    """
    Receive telemetry data from IoT devices
    Validates with Pydantic and pushes to Redis Stream
    """
    if not await redis_stream.is_redis_available():
        raise HTTPException(status_code=500, detail="Redis not available")

    try:
        # Write to Redis Stream
        await redis_stream.write_to_stream(
            "telemetry_stream",
            {
                "device_id": data.device_id,
                "speed": data.speed,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "engine_temp": data.engine_temp,
                "timestamp": data.timestamp.isoformat(),
            }
        )

        return TelemetryResponse(
            status="received",
            device_id=data.device_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest telemetry: {str(e)}")
