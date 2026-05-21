from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TelemetryIngest(BaseModel):
    """Telemetry data model for ingest endpoint"""
    device_id: str = Field(..., min_length=1, max_length=50)
    speed: float = Field(..., ge=0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    engine_temp: float = Field(..., ge=-50, le=150)
    timestamp: datetime


class TelemetryEvent(BaseModel):
    """Telemetry event model for database"""
    id: int
    device_id: str
    speed: float
    latitude: float
    longitude: float
    engine_temp: float
    timestamp: datetime
    flagged: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TelemetryResponse(BaseModel):
    """Response model for ingest endpoint"""
    status: str
    device_id: str

