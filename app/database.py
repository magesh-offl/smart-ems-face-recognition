"""Async MongoDB Database Module"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


async def get_database() -> AsyncIOMotorDatabase:
    """Get async MongoDB database instance."""
    global _client, _db
    if _db is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.MONGO_DB_URL)
        _db = _client[settings.MONGO_DB_NAME]
    return _db


async def close_database():
    """Close database connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
