"""Authentication Service"""
from datetime import datetime, timedelta
from typing import Optional
from functools import lru_cache

import jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.repositories.user import UserRepository
from app.utils.exceptions import AuthenticationException, BadRequestException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.settings = get_settings()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain, hashed)
    
    def create_access_token(self, username: str) -> str:
        """Create JWT access token."""
        payload = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username."""
        try:
            payload = jwt.decode(token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM])
            return payload.get("sub")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
    
    def register_user(self, username: str, password: str) -> str:
        """Register new user."""
        if self.user_repo.user_exists(username):
            raise BadRequestException(f"User {username} already exists")
        return self.user_repo.create_user(username, self.hash_password(password))
    
    def login_user(self, username: str, password: str) -> str:
        """Authenticate user and return token."""
        user = self.user_repo.get_user_by_username(username)
        if not user or not self.verify_password(password, user["hashed_password"]):
            raise AuthenticationException("Invalid credentials")
        return self.create_access_token(username)
