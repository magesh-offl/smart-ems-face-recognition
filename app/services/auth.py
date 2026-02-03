"""Authentication Service"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.config import get_settings
from app.repositories.user import UserRepository
from app.utils.exceptions import AuthenticationException, BadRequestException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        """Initialize auth service"""
        self.user_repo = UserRepository()
        self.settings = get_settings()
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, username: str) -> str:
        """Create JWT access token"""
        to_encode = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.SECRET_KEY,
            algorithm=self.settings.ALGORITHM
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username"""
        try:
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM]
            )
            username = payload.get("sub")
            if username is None:
                return None
            return username
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def register_user(self, username: str, password: str) -> str:
        """Register new user"""
        if self.user_repo.user_exists(username):
            raise BadRequestException(f"User {username} already exists")
        
        hashed_password = self.hash_password(password)
        user_id = self.user_repo.create_user(username, hashed_password)
        logger.info(f"User registered: {username}")
        return user_id
    
    def login_user(self, username: str, password: str) -> str:
        """Authenticate user and return token"""
        user = self.user_repo.get_user_by_username(username)
        
        if not user or not self.verify_password(password, user["hashed_password"]):
            raise AuthenticationException("Invalid credentials")
        
        token = self.create_access_token(username)
        logger.info(f"User logged in: {username}")
        return token
