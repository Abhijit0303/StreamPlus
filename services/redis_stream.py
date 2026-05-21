import redis.asyncio as redis
import logging
from config import REDIS_URL
from typing import Optional

logger = logging.getLogger(__name__)

redis_client = None


async def connect_redis(url: Optional[str] = None) -> bool:
    """
    Connect to Redis and verify connection
    Returns True if successful, False otherwise
    """
    global redis_client
    try:
        if url is None:
            url = REDIS_URL
        redis_client = await redis.from_url(url, decode_responses=True)
        result = redis_client.ping()
        if isinstance(result, bool):
            ping_result = result
        else:
            ping_result = await result
        logger.info("✓ Redis connected successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {e}")
        return False


async def disconnect_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("✓ Redis disconnected")


async def is_redis_available() -> bool:
    """Check if Redis is available"""
    global redis_client
    if redis_client is None:
        return False
    try:
        result = redis_client.ping()
        if isinstance(result, bool):
            return result
        else:
            return await result
    except Exception:
        return False


async def write_to_stream(stream_name: str, data: dict) -> str:
    """
    Write data to Redis Stream
    Returns message ID if successful
    Raises exception if failed
    """
    global redis_client
    if redis_client is None:
        raise Exception("Redis not connected")

    try:
        message_id = await redis_client.xadd(stream_name, data)
        logger.info(f"Message written to stream {stream_name}: {message_id}")
        return message_id
    except Exception as e:
        logger.error(f"Failed to write to stream {stream_name}: {e}")
        raise


def get_redis_client():
    """Get current Redis client"""
    global redis_client
    return redis_client
