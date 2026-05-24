from fastapi import APIRouter, Query, HTTPException
from models.analytics import (
    SpeedAverageResponse,
    EventCountResponse,
    ActiveDevicesResponse,
    OverspeedAlert,
    OverspeedAlertsResponse
)
from db import analytics_queries

router = APIRouter(prefix="/analytics", tags=["analytics"])


# Endpoints
@router.get("/speed/average", response_model=SpeedAverageResponse)
async def get_speed_average(device_id: str = Query(..., description="Device ID")) -> SpeedAverageResponse:
    """
    Get average speed for a specific device
    Returns 404 if device has no telemetry data
    """
    try:
        # Check if device has any events
        event_count = await analytics_queries.get_device_event_count(device_id)
        if event_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No telemetry data found for device_id: {device_id}"
            )

        avg_speed = await analytics_queries.get_average_speed(device_id)
        return SpeedAverageResponse(
            device_id=device_id,
            average_speed=round(avg_speed, 2)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get average speed: {str(e)}")


@router.get("/events/count", response_model=EventCountResponse)
async def get_events_count(hours: int = Query(1, ge=1, description="Number of hours to look back")) -> EventCountResponse:
    """
    Get count of telemetry events in the last N hours
    """
    try:
        count = await analytics_queries.get_event_count(hours)
        return EventCountResponse(
            hours=hours,
            total_events=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event count: {str(e)}")


@router.get("/devices/active", response_model=ActiveDevicesResponse)
async def get_active_devices() -> ActiveDevicesResponse:
    """
    Get count of active devices
    """
    try:
        count = await analytics_queries.get_active_devices_count()
        return ActiveDevicesResponse(active_devices=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active devices: {str(e)}")


@router.get("/alerts/overspeed", response_model=OverspeedAlertsResponse)
async def get_overspeed_alerts(limit: int = Query(100, ge=1, le=1000, description="Max alerts to return")) -> OverspeedAlertsResponse:
    """
    Get overspeed alerts (speed > 120 km/h)
    Returns most recent alerts first
    """
    try:
        alerts = await analytics_queries.get_overspeed_alerts(limit)

        alert_list = [
            OverspeedAlert(
                id=alert['id'],
                device_id=alert['device_id'],
                speed=alert['speed'],
                latitude=alert['latitude'],
                longitude=alert['longitude'],
                engine_temp=alert['engine_temp'],
                timestamp=alert['timestamp'],
                created_at=alert['created_at']
            )
            for alert in alerts
        ]

        return OverspeedAlertsResponse(
            total_alerts=len(alert_list),
            alerts=alert_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get overspeed alerts: {str(e)}")
