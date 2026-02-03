"""Base Repository for MongoDB operations - Implements IRepository"""
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime
from bson.objectid import ObjectId

from app.config import get_settings
from app.core.interfaces.repository import IRepository


class BaseRepository(IRepository):
    """
    Base repository implementing IRepository interface.
    Provides common MongoDB operations for all repositories.
    """
    
    def __init__(self, collection_name: str):
        """Initialize repository with collection name"""
        settings = get_settings()
        self.client = MongoClient(settings.MONGO_DB_URL)
        self.db = self.client[settings.MONGO_DB_NAME]
        self.collection: Collection = self.db[collection_name]
    
    def create(self, data: Dict[str, Any]) -> str:
        """Create a new document"""
        result = self.collection.insert_one(data)
        return str(result.inserted_id)
    
    def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        try:
            return self.collection.find_one({"_id": ObjectId(doc_id)})
        except:
            return None
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find single document by query"""
        return self.collection.find_one(query)
    
    def find_many(self, query: Dict[str, Any], skip: int = 0, 
                 limit: int = 10) -> List[Dict[str, Any]]:
        """Find multiple documents with pagination"""
        return list(self.collection.find(query).skip(skip).limit(limit))
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all documents"""
        return list(self.collection.find())
    
    def update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """Update documents matching the query"""
        try:
            result = self.collection.update_one(query, {"$set": update_data})
            return result.modified_count > 0
        except:
            return False
    
    def update_by_id(self, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update document by ID"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def update_many(self, query: Dict[str, Any], data: Dict[str, Any]) -> int:
        """Update multiple documents"""
        result = self.collection.update_many(query, {"$set": data})
        return result.modified_count
    
    def delete(self, query: Dict[str, Any]) -> bool:
        """Delete documents matching the query"""
        try:
            result = self.collection.delete_one(query)
            return result.deleted_count > 0
        except:
            return False
    
    def delete_by_id(self, doc_id: str) -> bool:
        """Delete document by ID"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(doc_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete multiple documents"""
        result = self.collection.delete_many(query)
        return result.deleted_count
    
    def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents"""
        if query is None:
            return self.collection.count_documents({})
        return self.collection.count_documents(query)
    
    def increment(self, doc_id: str, field: str, value: int = 1) -> bool:
        """Increment a field value"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$inc": {field: value}}
            )
            return result.modified_count > 0
        except:
            return False
