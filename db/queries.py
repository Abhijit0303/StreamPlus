import logging
from datetime import datetime
from db.connection import get_db_pool

logger = logging.getLogger(__name__)


async def insert_telemetry_event(
    device_id: str,
    speed: float,
    latitude: float,
    longitude: float,
    engine_temp: float,
    timestamp: datetime,
    flagged: bool = False
) -> int:
    """
    Insert telemetry event into database
    Returns the ID of the inserted event
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            event_id = await conn.fetchval(
                """
                INSERT INTO telemetry_events
                (device_id, speed, latitude, longitude, engine_temp, timestamp, flagged)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                device_id, speed, latitude, longitude, engine_temp, timestamp, flagged
            )
            logger.info(f"Telemetry event inserted: ID={event_id}, device_id={device_id}")
            return event_id
    except Exception as e:
        logger.error(f"Failed to insert telemetry event: {e}")
        raise


async def upsert_device(device_id: str) -> int:
    """
    Upsert device in devices table
    Updates last_seen and total_events if exists, creates new if not
    Returns the device ID
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            device_row = await conn.fetchrow(
                """
                INSERT INTO devices (device_id, last_seen, total_events)
                VALUES ($1, NOW(), 1)
                ON CONFLICT (device_id)
                DO UPDATE SET
                    last_seen = NOW(),
                    total_events = devices.total_events + 1
                RETURNING id
                """,
                device_id
            )
            logger.info(f"Device upserted: device_id={device_id}")
            return device_row['id']
    except Exception as e:
        logger.error(f"Failed to upsert device: {e}")
        raise
