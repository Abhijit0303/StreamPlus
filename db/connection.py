import asyncpg
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

db_pool = None


async def connect_db():
    """
    Create PostgreSQL connection pool
    """
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=10,
            max_size=20,
            command_timeout=60,
        )
        logger.info("✓ PostgreSQL connected successfully")
        return True
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {e}")
        return False


async def disconnect_db():
    """
    Close PostgreSQL connection pool
    """
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("✓ PostgreSQL disconnected")


async def is_db_available() -> bool:
    """Check if database is available"""
    global db_pool
    if db_pool is None:
        return False
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception:
        return False


def get_db_pool():
    """Get current database pool"""
    global db_pool
    return db_pool
