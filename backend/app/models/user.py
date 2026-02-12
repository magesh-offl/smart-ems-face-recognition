"""User and APIKey Document Models"""
from datetime import datetime
from typing import Optional, Dict, Any
import secrets
from .base import BaseDocument


class UserDocument(BaseDocument):
    """MongoDB document model for users.
    
    Supports RBAC with role_id reference and semantic user_id.
    
    Relationships:
        - role_id: References RoleDocument.role_id
    """
    
    collection_name = "users"
    
    @staticmethod
    def create(
        user_id: str,
        username: str,
        hashed_password: str,
        email: str,
        role_id: str,
        first_name: str = "",
        last_name: str = "",
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a new user document.
        
        Args:
            user_id: Unique semantic ID (e.g., USR26020001)
            username: Unique username for login
            hashed_password: Bcrypt hashed password
            email: User's email address
            role_id: Role ID reference (e.g., ROL0001)
            first_name: User's first name
            last_name: User's last name
            is_active: Whether user account is active
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "user_id": user_id,
            "username": username,
            "hashed_password": hashed_password,
            "email": email,
            "role_id": role_id,
            "first_name": first_name,
            "last_name": last_name,
            "is_active": is_active,
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
