from pydantic import BaseModel
from datetime import datetime
from typing import List


class SpeedAverageResponse(BaseModel):
    device_id: str
    average_speed: float
    unit: str = "km/h"


class EventCountResponse(BaseModel):
    hours: int
    total_events: int


class ActiveDevicesResponse(BaseModel):
    active_devices: int


class OverspeedAlert(BaseModel):
    id: int
    device_id: str
    speed: float
    latitude: float
    longitude: float
    engine_temp: float
    timestamp: datetime
    created_at: datetime


class OverspeedAlertsResponse(BaseModel):
    total_alerts: int
    alerts: List[OverspeedAlert]
