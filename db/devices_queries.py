import logging
from typing import Optional
from db.connection import get_db_pool

logger = logging.getLogger(__name__)


async def register_device(device_id: str, status: str = "active") -> int:
    """
    Register a new device
    Returns device ID if successful
    Raises exception if device already exists
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            # Check if device already exists
            existing = await conn.fetchval(
                "SELECT id FROM devices WHERE device_id = $1",
                device_id
            )
            if existing:
                raise Exception(f"Device {device_id} already exists")

            device_row = await conn.fetchrow(
                """
                INSERT INTO devices (device_id, status, total_events, last_seen)
                VALUES ($1, $2, 0, NOW())
                RETURNING id
                """,
                device_id, status
            )
            logger.info(f"Device registered: device_id={device_id}")
            return device_row['id']
    except Exception as e:
        logger.error(f"Failed to register device: {e}")
        raise


async def get_all_devices() -> list[dict]:
    """
    Get all devices
    Returns list of device records
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT id, device_id, last_seen, total_events, status, created_at
                FROM devices
                ORDER BY created_at DESC
                """
            )
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        raise


async def get_device_by_id(device_id: str) -> Optional[dict]:
    """
    Get specific device by device_id
    Returns device record or None
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT id, device_id, last_seen, total_events, status, created_at
                FROM devices
                WHERE device_id = $1
                """,
                device_id
            )
            return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to get device: {e}")
        raise


async def update_device(device_id: str, status: str) -> bool:
    """
    Update device status
    Returns True if successful
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE devices
                SET status = $1
                WHERE device_id = $2
                """,
                status, device_id
            )
            if result == "UPDATE 0":
                raise Exception(f"Device {device_id} not found")

            logger.info(f"Device updated: device_id={device_id}, status={status}")
            return True
    except Exception as e:
        logger.error(f"Failed to update device: {e}")
        raise


async def delete_device(device_id: str) -> bool:
    """
    Delete a device
    Returns True if successful
    """
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool not initialized")

    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM devices WHERE device_id = $1",
                device_id
            )
            if result == "DELETE 0":
                raise Exception(f"Device {device_id} not found")

            logger.info(f"Device deleted: device_id={device_id}")
            return True
    except Exception as e:
        logger.error(f"Failed to delete device: {e}")
        raise
