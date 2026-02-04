"""Base Document Model - Common fields for all MongoDB documents"""
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId


class BaseDocument:
    """Base class for all MongoDB document models.
    
    Provides common fields and utility methods that all documents share.
    """
    
    collection_name: str = ""  # Override in subclass
    
    @staticmethod
    def generate_id() -> str:
        """Generate a new MongoDB ObjectId as string"""
        return str(ObjectId())
    
    @staticmethod
    def get_base_fields() -> Dict[str, Any]:
        """Get common fields for all documents"""
        now = datetime.utcnow()
        return {
            "created_at": now,
            "updated_at": now
        }
    
    @staticmethod
    def update_timestamp() -> Dict[str, datetime]:
        """Get update timestamp for document modifications"""
        return {"updated_at": datetime.utcnow()}
