"""Role Document Model"""
from datetime import datetime
from typing import Dict, Any, List
from .base import BaseDocument


class RoleDocument(BaseDocument):
    """MongoDB document model for roles.
    
    Defines user roles with associated permissions for RBAC.
    
    Default Roles:
        - ROL0001: super_admin (all permissions)
        - ROL0002: admin (manage teachers, students, roles)
        - ROL0003: teacher (manage students)
        - ROL0004: student (view own profile)
    """
    
    collection_name = "roles"
    
    # Permission constants
    PERMISSION_ALL = "*"
    PERMISSION_MANAGE_TEACHERS = "manage_teachers"
    PERMISSION_MANAGE_STUDENTS = "manage_students"
    PERMISSION_MANAGE_ROLES = "manage_roles"
    PERMISSION_VIEW_DASHBOARD = "view_dashboard"
    PERMISSION_VIEW_OWN_PROFILE = "view_own_profile"
    PERMISSION_MANAGE_COURSES = "manage_courses"
    PERMISSION_VIEW_RESET_REQUESTS = "view_reset_requests"
    
    @staticmethod
    def create(
        role_id: str,
        name: str,
        permissions: List[str],
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a new role document.
        
        Args:
            role_id: Unique role identifier (e.g., ROL0001)
            name: Role name (e.g., "super_admin", "admin", "teacher", "student")
            permissions: List of permission strings
            description: Optional role description
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "role_id": role_id,
            "name": name,
            "permissions": permissions,
            "description": description,
            **BaseDocument.get_base_fields()
        }
        return doc
    
    @staticmethod
    def get_default_roles() -> List[Dict[str, Any]]:
        """Get default system roles for seeding."""
        return [
            {
                "role_id": "ROL0001",
                "name": "super_admin",
                "permissions": ["*"],
                "description": "Full system access"
            },
            {
                "role_id": "ROL0002",
                "name": "admin",
                "permissions": [
                    "manage_teachers", "manage_students", "manage_roles",
                    "manage_courses", "view_dashboard", "view_reset_requests"
                ],
                "description": "Administrative access"
            },
            {
                "role_id": "ROL0003",
                "name": "teacher",
                "permissions": [
                    "manage_students", "view_dashboard"
                ],
                "description": "Teacher access"
            },
            {
                "role_id": "ROL0004",
                "name": "student",
                "permissions": [
                    "view_own_profile"
                ],
                "description": "Student access"
            }
        ]
