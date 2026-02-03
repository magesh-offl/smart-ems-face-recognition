"""User Repository for database operations"""
from typing import Optional, Dict, Any
from app.repositories.base import BaseRepository
from app.schemas import UserSchema
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class UserRepository(BaseRepository):
    """Repository for user management"""
    
    def __init__(self):
        """Initialize user repository"""
        super().__init__(UserSchema.collection_name)
    
    def create_user(self, username: str, hashed_password: str) -> str:
        """Create a new user"""
        doc = UserSchema.get_document(username, hashed_password)
        user_id = self.create(doc)
        logger.info(f"Created user: {username}")
        return user_id
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        return self.find_one({"username": username})
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.find_by_id(user_id)
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return self.find_one({"username": username}) is not None
