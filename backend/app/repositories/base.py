"""Async Base Repository for MongoDB operations"""
from typing import List, Optional, Dict, Any
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database import get_database
from app.core.interfaces.repository import IRepository


class BaseRepository(IRepository):
    """Async base repository with common MongoDB operations."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._collection: AsyncIOMotorCollection = None
    
    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Get collection (lazy initialization)."""
        if self._collection is None:
            db = await get_database()
            self._collection = db[self.collection_name]
        return self._collection
    
    @property
    async def collection(self) -> AsyncIOMotorCollection:
        return await self._get_collection()
    
    async def create(self, data: Dict[str, Any]) -> str:
        """Create a new document."""
        coll = await self._get_collection()
        result = await coll.insert_one(data)
        return str(result.inserted_id)
    
    async def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID."""
        try:
            coll = await self._get_collection()
            return await coll.find_one({"_id": ObjectId(doc_id)})
        except:
            return None
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find single document by query."""
        coll = await self._get_collection()
        return await coll.find_one(query)
    
    async def find_many(self, query: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Find multiple documents with pagination."""
        coll = await self._get_collection()
        cursor = coll.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_all(self) -> List[Dict[str, Any]]:
        """Find all documents."""
        coll = await self._get_collection()
        return await coll.find().to_list(length=None)
    
    async def update(self, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update document by ID."""
        try:
            coll = await self._get_collection()
            result = await coll.update_one({"_id": ObjectId(doc_id)}, {"$set": data})
            return result.modified_count > 0
        except:
            return False
    
    async def delete(self, doc_id: str) -> bool:
        """Delete document by ID."""
        try:
            coll = await self._get_collection()
            result = await coll.delete_one({"_id": ObjectId(doc_id)})
            return result.deleted_count > 0
        except:
            return False
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents."""
        coll = await self._get_collection()
        return await coll.count_documents(query or {})
    
    async def increment(self, doc_id: str, field: str, value: int = 1) -> bool:
        """Increment a field value."""
        try:
            coll = await self._get_collection()
            result = await coll.update_one({"_id": ObjectId(doc_id)}, {"$inc": {field: value}})
            return result.modified_count > 0
        except:
            return False
