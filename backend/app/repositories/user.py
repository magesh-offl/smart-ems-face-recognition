"""Async User Repository"""
from typing import Optional, Dict, Any, List

from app.repositories.base import BaseRepository
from app.models import UserDocument


class UserRepository(BaseRepository):
    """Async repository for user management with RBAC support."""
    
    def __init__(self):
        super().__init__(UserDocument.collection_name)
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user from user document data."""
        return await self.create(user_data)
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        return await self.find_one({"username": username})
    
    async def get_user_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by semantic user_id (e.g., USR26020001)."""
        return await self.find_one({"user_id": user_id})
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        return await self.find_one({"email": email})
    
    async def get_user_by_mongo_id(self, mongo_id: str) -> Optional[Dict[str, Any]]:
        """Get user by MongoDB _id."""
        return await self.find_by_id(mongo_id)
    
    async def get_users_by_role(
        self, 
        role_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all users with a specific role."""
        return await self.find_many({"role_id": role_id}, skip=skip, limit=limit)
    
    async def get_super_admin(self) -> Optional[Dict[str, Any]]:
        """Get the super admin user (ROL0001)."""
        return await self.find_one({"role_id": "ROL0001"})
    
    async def user_exists(self, username: str) -> bool:
        """Check if user exists by username."""
        return await self.find_one({"username": username}) is not None
    
    async def email_exists(self, email: str) -> bool:
        """Check if email is already in use."""
        return await self.find_one({"email": email}) is not None
    
    async def update_password(self, user_id: str, hashed_password: str) -> bool:
        """Update user password by semantic user_id."""
        user = await self.get_user_by_user_id(user_id)
        if user:
            return await self.update(str(user["_id"]), {"hashed_password": hashed_password})
        return False
    
    async def update_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Update user data by semantic user_id."""
        user = await self.get_user_by_user_id(user_id)
        if user:
            return await self.update(str(user["_id"]), data)
        return False
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        return await self.update_user(user_id, {"is_active": False})
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        return await self.update_user(user_id, {"is_active": True})
    
    async def count_by_role(self, role_id: str) -> int:
        """Count users with a specific role."""
        return await self.count({"role_id": role_id})
