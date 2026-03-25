#!/usr/bin/env python3
"""
Database initialization and testing script.

This script tests MongoDB connection and creates initial indexes.
Run this before starting the application for the first time.

Usage:
    python scripts/init_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.database import Database
from loguru import logger


async def main():
    """Initialize and test database."""
    logger.info("Starting database initialization...")
    logger.info(f"MongoDB URI: {settings.mongo_uri}")
    logger.info(f"Database: {settings.mongo_db_name}")

    # Create database instance
    db = Database(settings.mongo_uri, settings.mongo_db_name)

    try:
        # Connect to database
        logger.info("Connecting to MongoDB...")
        await db.connect()
        logger.info("✓ Successfully connected to MongoDB")

        # Test basic operations
        logger.info("\nTesting basic operations...")

        # Create a test conversation
        logger.info("Creating test conversation...")
        test_conv_id = await db.create_conversation("Test system prompt")
        logger.info(f"✓ Created conversation: {test_conv_id}")

        # Save a test message
        logger.info("Saving test message...")
        await db.save_message(test_conv_id, "user", "Hello, how are you?")
        logger.info("✓ Message saved")

        # Get conversation
        logger.info("Retrieving conversation...")
        conv = await db.get_conversation(test_conv_id)
        logger.info(f"✓ Retrieved conversation: {conv.get('title')}")

        # Get conversation history
        logger.info("Retrieving conversation history...")
        history = await db.get_conversation_history(test_conv_id)
        logger.info(f"✓ Retrieved {len(history)} message(s)")

        # Clean up test data
        logger.info("\nCleaning up test data...")
        await db.delete_conversation(test_conv_id)
        logger.info("✓ Deleted test conversation")

        # Health check
        logger.info("\nRunning health check...")
        is_healthy = await db.health_check()
        if is_healthy:
            logger.info("✓ Database health check passed")
        else:
            logger.error("✗ Database health check failed")
            return 1

        logger.info("\n✓ Database initialization completed successfully!")
        logger.info(f"✓ Collections: conversations, messages, documents")
        logger.info("✓ Indexes created")
        logger.info("\nYou can now start the application.")

        return 0

    except Exception as e:
        logger.error(f"✗ Error during initialization: {e}")
        logger.error("\nMake sure MongoDB is running and accessible.")
        logger.error(f"Connection string: {settings.mongo_uri}")
        return 1

    finally:
        # Disconnect
        await db.disconnect()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
