"""Async User Repository"""
from typing import Optional, Dict, Any

from app.repositories.base import BaseRepository
from app.models import UserDocument


class UserRepository(BaseRepository):
    """Async repository for user management."""
    
    def __init__(self):
        super().__init__(UserDocument.collection_name)
    
    async def create_user(self, username: str, hashed_password: str) -> str:
        """Create a new user."""
        return await self.create(UserDocument.create(username, hashed_password))
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        return await self.find_one({"username": username})
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return await self.find_by_id(user_id)
    
    async def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        return await self.find_one({"username": username}) is not None
