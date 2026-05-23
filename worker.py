import asyncio
import logging
from datetime import datetime
from typing import Optional
from services import redis_stream
from db import connection as db
from db import queries

logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

STREAM_NAME = "telemetry_stream"
CONSUMER_GROUP = "telemetry_workers"
CONSUMER_NAME = "worker-1"
SPEED_THRESHOLD = 120


async def initialize_consumer_group():
    """Create consumer group if it doesn't exist"""
    try:
        redis_client = redis_stream.get_redis_client()
        if redis_client is None:
            raise Exception("Redis not connected")

        try:
            await redis_client.xgroup_create(STREAM_NAME, CONSUMER_GROUP, id="0", mkstream=True)
            logger.info(f"✓ Created consumer group: {CONSUMER_GROUP}")
        except Exception as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"✓ Consumer group {CONSUMER_GROUP} already exists")
            else:
                raise
    except Exception as e:
        logger.error(f"✗ Failed to initialize consumer group: {e}")
        raise


async def process_event(event_data: dict) -> bool:
    """
    Process a telemetry event
    Returns True if successful, False otherwise
    """
    try:
        # Extract and parse event data
        device_id: Optional[str] = event_data.get("device_id")
        if not device_id:
            logger.warning(f"✗ Missing device_id in event: {event_data}")
            return False

        speed = float(event_data.get("speed", 0))
        latitude = float(event_data.get("latitude", 0))
        longitude = float(event_data.get("longitude", 0))
        engine_temp = float(event_data.get("engine_temp", 0))
        timestamp_str = event_data.get("timestamp")

        # Parse timestamp and make it naive (remove timezone info)
        if timestamp_str:
            try:
                ts = datetime.fromisoformat(timestamp_str)
                timestamp = ts.replace(tzinfo=None) if ts.tzinfo else ts
            except Exception:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        # Check if speed exceeds threshold
        flagged = speed > SPEED_THRESHOLD

        # Save to telemetry_events table
        await queries.insert_telemetry_event(
            device_id=device_id,
            speed=speed,
            latitude=latitude,
            longitude=longitude,
            engine_temp=engine_temp,
            timestamp=timestamp,
            flagged=flagged
        )

        # Update devices table
        await queries.upsert_device(device_id)

        # Log if flagged
        if flagged:
            logger.warning(f"⚠️ OVERSPEED: device_id={device_id}, speed={speed}km/h")
        else:
            logger.debug(f"✓ Event processed: device_id={device_id}, speed={speed}km/h")

        return True
    except Exception as e:
        logger.error(f"✗ Failed to process event: {e}")
        return False


async def worker_loop():
    """
    Main worker loop
    Reads from Redis Stream and saves to PostgreSQL
    """
    logger.info("🚀 Worker started")

    try:
        # Initialize consumer group
        await initialize_consumer_group()

        redis_client = redis_stream.get_redis_client()
        if redis_client is None:
            raise Exception("Redis client not initialized")

        while True:
            try:
                # Read from stream using consumer group
                messages = await redis_client.xreadgroup(
                    CONSUMER_GROUP,
                    CONSUMER_NAME,
                    {STREAM_NAME: ">"},
                    count=10,
                    block=1000
                )

                if messages:
                    for stream_name, message_list in messages:
                        for message_id, event_data in message_list:
                            # Process the event
                            success = await process_event(event_data)

                            # Acknowledge message in Redis only if processed successfully
                            if success:
                                await redis_client.xack(STREAM_NAME, CONSUMER_GROUP, message_id)
                                logger.debug(f"Acknowledged message: {message_id}")

                # Sleep before next read
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"✗ Error in worker loop: {e}")
                await asyncio.sleep(1)  # Wait before retrying

    except Exception as e:
        logger.error(f"✗ Worker initialization failed: {e}")


async def main():
    """Main entry point"""
    try:
        # Connect to services
        redis_connected = await redis_stream.connect_redis()
        db_connected = await db.connect_db()

        if not redis_connected or not db_connected:
            logger.error("✗ Failed to connect to services")
            return

        logger.info("✓ Connected to Redis and PostgreSQL")

        # Run worker loop
        await worker_loop()

    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}")
    finally:
        # Cleanup
        await redis_stream.disconnect_redis()
        await db.disconnect_db()
        logger.info("✓ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
