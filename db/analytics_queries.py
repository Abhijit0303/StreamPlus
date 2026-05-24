import logging
from datetime import datetime, timedelta
from db.connection import get_db_pool

logger = logging.getLogger(__name__)


async def get_device_event_count(device_id: str) -> int:
    """
    Get count of events for a specific device
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*) FROM telemetry_events
                WHERE device_id = $1
                """,
                device_id
            )
            return int(result) if result else 0
    except Exception as e:
        logger.error(f"Failed to get device event count: {e}")
        raise


async def get_average_speed(device_id: str) -> float:
    """
    Get average speed for a device
    Returns average speed or 0 if no data
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT AVG(speed) FROM telemetry_events
                WHERE device_id = $1
                """,
                device_id
            )
            return float(result) if result else 0.0
    except Exception as e:
        logger.error(f"Failed to get average speed: {e}")
        raise


async def get_event_count(hours: int = 1) -> int:
    """
    Get count of telemetry events in the last N hours
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*) FROM telemetry_events
                WHERE created_at >= NOW() - ($1 || ' hours')::INTERVAL
                """,
                str(hours)
            )
            return int(result) if result else 0
    except Exception as e:
        logger.error(f"Failed to get event count: {e}")
        raise


async def get_active_devices_count() -> int:
    """
    Get count of active devices (status = 'active')
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*) FROM devices
                WHERE status = 'active'
                """
            )
            return int(result) if result else 0
    except Exception as e:
        logger.error(f"Failed to get active devices count: {e}")
        raise


async def get_overspeed_alerts(limit: int = 100) -> list:
    """
    Get overspeed alerts (speed > 120)
    Returns list of alert records
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT
                    id, device_id, speed, latitude, longitude,
                    engine_temp, timestamp, created_at
                FROM telemetry_events
                WHERE flagged = TRUE
                ORDER BY created_at DESC
                LIMIT $1
                """,
                limit
            )
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Failed to get overspeed alerts: {e}")
        raise
