from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class DeviceRegister(BaseModel):
    """Request model for registering a device"""
    device_id: str = Field(..., min_length=1, max_length=50, description="Unique device identifier")
    status: Optional[str] = Field("active", description="Device status (active/inactive)")


class DeviceUpdate(BaseModel):
    """Request model for updating a device"""
    status: Optional[str] = Field(None, description="Device status (active/inactive)")


class DeviceResponse(BaseModel):
    """Response model for device"""
    id: int
    device_id: str
    last_seen: Optional[datetime]
    total_events: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DevicesListResponse(BaseModel):
    """Response model for device list"""
    total_devices: int
    devices: List[DeviceResponse]


class DeviceDeleteResponse(BaseModel):
    """Response model for device deletion"""
    message: str
    device_id: str
