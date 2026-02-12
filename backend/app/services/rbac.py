"""RBAC Service - Role-Based Access Control"""
from typing import List, Optional, Dict, Any
from app.repositories.role import RoleRepository


class RBACService:
    """Service for role-based access control.
    
    Provides permission checking against role definitions stored in MongoDB.
    """
    
    # Cached role permissions for performance
    _role_cache: Dict[str, List[str]] = {}
    
    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo
    
    async def get_permissions(self, role_id: str) -> List[str]:
        """Get permissions for a role.
        
        Args:
            role_id: Role ID (e.g., ROL0001)
            
        Returns:
            List of permission strings
        """
        # Check cache first
        if role_id in self._role_cache:
            return self._role_cache[role_id]
        
        role = await self.role_repo.get_by_role_id(role_id)
        if role:
            permissions = role.get("permissions", [])
            self._role_cache[role_id] = permissions
            return permissions
        return []
    
    async def has_permission(self, role_id: str, permission: str) -> bool:
        """Check if a role has a specific permission.
        
        Args:
            role_id: Role ID (e.g., ROL0001)
            permission: Permission to check (e.g., "manage_students")
            
        Returns:
            True if role has permission, False otherwise
        """
        permissions = await self.get_permissions(role_id)
        
        # Wildcard permission grants all
        if "*" in permissions:
            return True
        
        return permission in permissions
    
    async def has_any_permission(self, role_id: str, permissions: List[str]) -> bool:
        """Check if role has any of the specified permissions.
        
        Args:
            role_id: Role ID
            permissions: List of permissions to check
            
        Returns:
            True if role has at least one permission
        """
        role_permissions = await self.get_permissions(role_id)
        
        if "*" in role_permissions:
            return True
        
        return any(p in role_permissions for p in permissions)
    
    async def has_all_permissions(self, role_id: str, permissions: List[str]) -> bool:
        """Check if role has all specified permissions.
        
        Args:
            role_id: Role ID
            permissions: List of permissions required
            
        Returns:
            True if role has all permissions
        """
        role_permissions = await self.get_permissions(role_id)
        
        if "*" in role_permissions:
            return True
        
        return all(p in role_permissions for p in permissions)
    
    async def get_role_name(self, role_id: str) -> Optional[str]:
        """Get role name by ID."""
        role = await self.role_repo.get_by_role_id(role_id)
        return role.get("name") if role else None
    
    async def get_role_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get role by name."""
        return await self.role_repo.get_by_name(name)
    
    def clear_cache(self):
        """Clear the role permissions cache."""
        self._role_cache.clear()
    
    async def refresh_cache(self):
        """Refresh cache by reloading all roles."""
        self._role_cache.clear()
        roles = await self.role_repo.get_all_roles()
        for role in roles:
            self._role_cache[role["role_id"]] = role.get("permissions", [])
