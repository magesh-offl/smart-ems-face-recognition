"""RBAC Dependencies - FastAPI dependency injection for role-based access control"""
from typing import List, Optional, Callable
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth.service import AuthService
from app.services.rbac import RBACService
from app.services.id_generator import IDGeneratorService, IDCounterRepository
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.repositories.password_reset import PasswordResetRepository


# HTTP Bearer security scheme
security = HTTPBearer()


def get_id_generator() -> IDGeneratorService:
    """Get IDGeneratorService instance."""
    counter_repo = IDCounterRepository()
    return IDGeneratorService(counter_repo)


def get_auth_service() -> AuthService:
    """Get AuthService instance with all dependencies."""
    return AuthService(
        user_repository=UserRepository(),
        role_repository=RoleRepository(),
        password_reset_repository=PasswordResetRepository(),
        id_generator=get_id_generator()
    )


def get_rbac_service() -> RBACService:
    """Get RBACService instance."""
    return RBACService(RoleRepository())


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current authenticated user from JWT token.
    
    Returns:
        User document with role information
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """Get current active user (not deactivated).
    
    Raises:
        HTTPException: 403 if user is deactivated
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return current_user


def require_permissions(*permissions: str):
    """Dependency factory for requiring specific permissions.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_permissions("manage_users"))])
        async def admin_endpoint():
            ...
    
    Args:
        *permissions: One or more permission strings required
        
    Returns:
        Dependency function that checks permissions
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_active_user),
        rbac_service: RBACService = Depends(get_rbac_service)
    ):
        role_id = current_user.get("role_id")
        if not role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No role assigned to user"
            )
        
        # Check if user has any of the required permissions
        has_permission = await rbac_service.has_any_permission(role_id, list(permissions))
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission(s): {', '.join(permissions)}"
            )
        
        return current_user
    
    return permission_checker


def require_roles(*role_names: str):
    """Dependency factory for requiring specific roles.
    
    Usage:
        @router.get("/super-admin", dependencies=[Depends(require_roles("super_admin"))])
        async def super_admin_endpoint():
            ...
    
    Args:
        *role_names: One or more role names required
        
    Returns:
        Dependency function that checks roles
    """
    async def role_checker(
        current_user: dict = Depends(get_current_active_user)
    ):
        user_role = current_user.get("role_name")
        if not user_role or user_role not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires role(s): {', '.join(role_names)}"
            )
        
        return current_user
    
    return role_checker


# Convenience dependencies for common role checks
require_super_admin = require_roles("super_admin")
require_admin = require_roles("super_admin", "admin")
require_teacher = require_roles("super_admin", "admin", "teacher")
require_manage_students = require_permissions("manage_students")
require_manage_teachers = require_permissions("manage_teachers")
require_view_reset_requests = require_permissions("view_reset_requests")
