import asyncio
import asyncpg
import logging
from config import DATABASE_URL

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

# SQL to create tables
CREATE_TABLES_SQL = """
-- Create telemetry_events table
CREATE TABLE IF NOT EXISTS telemetry_events (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    speed FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    engine_temp FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    flagged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) UNIQUE NOT NULL,
    last_seen TIMESTAMP DEFAULT NOW(),
    total_events INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_telemetry_device_id ON telemetry_events(device_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_devices_device_id ON devices(device_id);
"""


async def init_db():
    """Initialize database tables"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("✓ Connected to PostgreSQL")

        await conn.execute(CREATE_TABLES_SQL)
        logger.info("✓ Tables created successfully")

        await conn.close()
        logger.info("✓ Database initialization complete")
        return True
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(init_db())
    exit(0 if success else 1)
