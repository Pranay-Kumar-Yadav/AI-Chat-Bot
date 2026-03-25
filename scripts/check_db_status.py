"""Check database status without modifying any data."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.database import Database
from loguru import logger


async def main():
    """Check database status."""
    logger.info("Checking database status...")
    logger.info(f"MongoDB URI: {settings.mongo_uri}")

    db = Database(settings.mongo_uri, settings.mongo_db_name)

    try:
        await db.connect()
        
        # Health check
        is_healthy = await db.health_check()
        
        if is_healthy:
            logger.info("✓ Database is healthy and accessible")
            
            # Get some stats
            if db.db:
                conversations = await db.get_all_conversations(limit=5)
                logger.info(f"✓ Database contains {len(conversations)} conversation(s)")
            
            return 0
        else:
            logger.error("✗ Database health check failed")
            return 1

    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return 1

    finally:
        await db.disconnect()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
