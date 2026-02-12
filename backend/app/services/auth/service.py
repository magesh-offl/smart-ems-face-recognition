"""Async Auth Service with RBAC Support"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import secrets

from app.config import get_settings
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.repositories.password_reset import PasswordResetRepository
from app.models import UserDocument, PasswordResetDocument
from app.services.id_generator import IDGeneratorService, IDCounterRepository
from app.utils.exceptions import AuthenticationException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Async service for authentication with RBAC support."""
    
    def __init__(
        self, 
        user_repository: UserRepository,
        role_repository: RoleRepository = None,
        password_reset_repository: PasswordResetRepository = None,
        id_generator: IDGeneratorService = None
    ):
        self.user_repo = user_repository
        self.role_repo = role_repository
        self.password_reset_repo = password_reset_repository
        self.id_generator = id_generator
        self.settings = get_settings()
    
    def _hash_password(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain: str, hashed: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain, hashed)
    
    def _generate_password(self, length: int = 12) -> str:
        """Generate a secure random password."""
        return secrets.token_urlsafe(length)[:length]
    
    def _create_token(
        self, 
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token with role information."""
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        return jwt.encode(
            {**data, "exp": expire}, 
            self.settings.SECRET_KEY, 
            algorithm=self.settings.ALGORITHM
        )
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token.
        
        Returns:
            Decoded token payload
            
        Raises:
            AuthenticationException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, 
                self.settings.SECRET_KEY, 
                algorithms=[self.settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationException("Invalid token")
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from JWT token.
        
        Returns:
            User document with role information
        """
        payload = self.decode_token(token)
        username = payload.get("sub")
        if not username:
            raise AuthenticationException("Invalid token payload")
        
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            raise AuthenticationException("User not found")
        
        if not user.get("is_active", True):
            raise AuthenticationException("User account is deactivated")
        
        # Add role name if role_repo available
        if self.role_repo and user.get("role_id"):
            role = await self.role_repo.get_by_role_id(user["role_id"])
            user["role_name"] = role.get("name") if role else None
            user["permissions"] = role.get("permissions", []) if role else []
        
        return user
    
    async def register(
        self, 
        username: str, 
        password: str,
        email: str,
        role_id: str = "ROL0004",  # Default to student
        first_name: str = "",
        last_name: str = ""
    ) -> Dict[str, Any]:
        """Register new user with role."""
        if await self.user_repo.user_exists(username):
            raise AuthenticationException("Username already exists")
        
        if await self.user_repo.email_exists(email):
            raise AuthenticationException("Email already exists")
        
        # Generate semantic user_id
        user_id = await self.id_generator.generate_user_id()
        
        # Create user document
        user_doc = UserDocument.create(
            user_id=user_id,
            username=username,
            hashed_password=self._hash_password(password),
            email=email,
            role_id=role_id,
            first_name=first_name,
            last_name=last_name
        )
        
        mongo_id = await self.user_repo.create_user(user_doc)
        
        logger.info(f"User registered: {user_id} ({username})")
        
        return {
            "id": mongo_id,
            "user_id": user_id,
            "username": username,
            "message": "User registered successfully"
        }
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and return JWT with role claims."""
        user = await self.user_repo.get_user_by_username(username)
        
        if not user or not self._verify_password(password, user["hashed_password"]):
            raise AuthenticationException("Invalid credentials")
        
        if not user.get("is_active", True):
            raise AuthenticationException("Account is deactivated")
        
        # Get role name for token
        role_name = None
        if self.role_repo and user.get("role_id"):
            role = await self.role_repo.get_by_role_id(user["role_id"])
            role_name = role.get("name") if role else None
        
        # Create token with role information
        token = self._create_token(
            {
                "sub": username,
                "user_id": user.get("user_id"),
                "role_id": user.get("role_id"),
                "role": role_name
            },
            timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"User logged in: {user.get('user_id')} ({username})")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "user_id": user.get("user_id"),
                "username": username,
                "email": user.get("email"),
                "role_id": user.get("role_id"),
                "role": role_name,
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name")
            }
        }
    
    async def forgot_password(self, username: str) -> Dict[str, Any]:
        """Create password reset request for admin review.
        
        Does NOT email the user. Creates a request visible on admin dashboard.
        """
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            # Don't reveal if user exists
            return {"message": "If the account exists, a reset request has been created"}
        
        # Check for existing pending request
        if self.password_reset_repo:
            existing = await self.password_reset_repo.get_pending_by_user_id(user["user_id"])
            if existing:
                return {"message": "A reset request is already pending"}
        
        # Generate new password
        new_password = self._generate_password()
        
        # Get role name
        role_name = "unknown"
        if self.role_repo and user.get("role_id"):
            role = await self.role_repo.get_by_role_id(user["role_id"])
            role_name = role.get("name") if role else "unknown"
        
        # Create reset request document
        reset_doc = PasswordResetDocument.create(
            user_id=user["user_id"],
            username=username,
            role_name=role_name,
            new_password=new_password,
            course_id=user.get("current_course_id")
        )
        
        if self.password_reset_repo:
            await self.password_reset_repo.create_reset_request(reset_doc)
            logger.info(f"Password reset request created for: {user['user_id']}")
        
        return {"message": "Password reset request has been submitted to admin"}
    
    async def create_super_admin_if_not_exists(self) -> Optional[Dict[str, Any]]:
        """Create super admin user on startup if none exists.
        
        Uses environment variables for credentials:
        - SUPER_ADMIN_PASSWORD (set in .env)
        - SUPER_ADMIN_EMAIL (set in .env)
        """
        # Check if super admin already exists
        existing = await self.user_repo.get_super_admin()
        if existing:
            logger.info(f"Super admin already exists: {existing.get('user_id')}")
            return None
        
        # Ensure default roles exist
        if self.role_repo:
            created_roles = await self.role_repo.seed_default_roles()
            if created_roles:
                logger.info(f"Seeded default roles: {created_roles}")
        
        # Get credentials from settings
        username = "superadmin"
        password = self.settings.SUPER_ADMIN_PASSWORD or self._generate_password(16)
        email = self.settings.SUPER_ADMIN_EMAIL
        
        # Generate user_id
        user_id = await self.id_generator.generate_user_id()
        
        # Create super admin user
        user_doc = UserDocument.create(
            user_id=user_id,
            username=username,
            hashed_password=self._hash_password(password),
            email=email,
            role_id="ROL0001",  # Super Admin role
            first_name="Super",
            last_name="Admin"
        )
        
        mongo_id = await self.user_repo.create_user(user_doc)
        
        logger.info(f"Created super admin: {user_id} ({username})")
        
        # Log password to console on first run (for initial setup)
        if not self.settings.SUPER_ADMIN_PASSWORD:
            logger.warning(f"Generated super admin password: {password}")
            logger.warning("Set SUPER_ADMIN_PASSWORD env var to use a specific password")
        else:
            logger.info("Super admin created with password from environment variable")
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "role_id": "ROL0001"
        }

