"""Async Auth Service"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

from app.config import get_settings
from app.repositories.user import UserRepository
from app.utils.exceptions import AuthenticationException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Async service for authentication."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
        self.settings = get_settings()
    
    def _hash_password(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain: str, hashed: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain, hashed)
    
    def _create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create access token."""
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        return jwt.encode({**data, "exp": expire}, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)
    
    async def register(self, username: str, password: str) -> Dict[str, Any]:
        """Register new user."""
        if await self.user_repo.user_exists(username):
            raise AuthenticationException("Username already exists")
        user_id = await self.user_repo.create_user(username, self._hash_password(password))
        return {"id": user_id, "username": username, "message": "User registered successfully"}
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user."""
        user = await self.user_repo.get_user_by_username(username)
        if not user or not self._verify_password(password, user["hashed_password"]):
            raise AuthenticationException("Invalid credentials")
        token = self._create_token(
            {"sub": username},
            timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
