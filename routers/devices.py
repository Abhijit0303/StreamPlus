from fastapi import APIRouter, HTTPException, Path, Query, Body
from typing import Optional
from models.devices import (
    DeviceRegister,
    DeviceUpdate,
    DeviceResponse,
    DevicesListResponse,
    DeviceDeleteResponse
)
from db import devices_queries

router = APIRouter(prefix="/devices", tags=["devices"])


def dict_to_device_response(device_dict: Optional[dict]) -> DeviceResponse:
    """Convert database dict to DeviceResponse"""
    if not device_dict:
        raise ValueError("Device dict cannot be empty")

    return DeviceResponse(
        id=device_dict['id'],  # Required
        device_id=device_dict['device_id'],  # Required
        last_seen=device_dict.get('last_seen'),  # Optional
        total_events=device_dict.get('total_events', 0),  # Has default
        status=device_dict.get('status', 'active'),  # Has default
        created_at=device_dict['created_at']  # Required
    )


@router.post("", response_model=DeviceResponse, status_code=201)
async def register_device(payload: DeviceRegister) -> DeviceResponse:
    """
    Register a new IoT device
    """
    try:
        status = payload.status or "active"
        device_id = await devices_queries.register_device(payload.device_id, status)
        device = await devices_queries.get_device_by_id(payload.device_id)
        if not device:
            raise HTTPException(status_code=500, detail="Device registration failed")

        return dict_to_device_response(device)
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=f"Device {payload.device_id} already exists")
        raise HTTPException(status_code=500, detail=f"Failed to register device: {error_msg}")


@router.get("", response_model=DevicesListResponse)
async def get_devices() -> DevicesListResponse:
    """
    Get all registered devices
    """
    try:
        devices = await devices_queries.get_all_devices()
        return DevicesListResponse(
            total_devices=len(devices),
            devices=[dict_to_device_response(device) for device in devices]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {str(e)}")


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str = Path(..., description="Device ID")) -> DeviceResponse:
    """
    Get specific device by device_id
    """
    try:
        device = await devices_queries.get_device_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        return dict_to_device_response(device)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get device: {str(e)}")


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: str = Path(..., description="Device ID"), payload: DeviceUpdate = Body(...)) -> DeviceResponse:
    """
    Update device status (active/inactive)
    """
    try:
        # First verify device exists
        existing_device = await devices_queries.get_device_by_id(device_id)
        if not existing_device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        # Update status if provided
        if payload and payload.status:
            await devices_queries.update_device(device_id, payload.status)

        # Return updated device
        device = await devices_queries.get_device_by_id(device_id)
        return dict_to_device_response(device)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update device: {str(e)}")


@router.delete("/{device_id}", response_model=DeviceDeleteResponse)
async def delete_device(device_id: str = Path(..., description="Device ID")) -> DeviceDeleteResponse:
    """
    Delete a device
    """
    try:
        await devices_queries.delete_device(device_id)
        return DeviceDeleteResponse(
            message=f"Device {device_id} deleted successfully",
            device_id=device_id
        )
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        raise HTTPException(status_code=500, detail=f"Failed to delete device: {error_msg}")
