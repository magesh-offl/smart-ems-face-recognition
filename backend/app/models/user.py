"""User and APIKey Document Models"""
from datetime import datetime
from typing import Optional, Dict, Any
import secrets
from .base import BaseDocument


class UserDocument(BaseDocument):
    """MongoDB document model for users."""
    
    collection_name = "users"
    
    @staticmethod
    def create(
        username: str,
        hashed_password: str
    ) -> Dict[str, Any]:
        """Create a new user document.
        
        Args:
            username: Unique username
            hashed_password: Bcrypt hashed password
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "username": username,
            "hashed_password": hashed_password,
            **BaseDocument.get_base_fields()
        }
        return doc


class APIKeyDocument(BaseDocument):
    """MongoDB document model for API keys."""
    
    collection_name = "api_keys"
    
    @staticmethod
    def generate_key() -> str:
        """Generate a secure random API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create(
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new API key document.
        
        Args:
            name: Name/label for the API key
            description: Optional description
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "name": name,
            "key": APIKeyDocument.generate_key(),
            "description": description,
            "is_active": True,
            **BaseDocument.get_base_fields()
        }
        return doc
