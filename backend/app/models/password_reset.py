"""Password Reset Document Model"""
from datetime import datetime
from typing import Dict, Any
from .base import BaseDocument


class PasswordResetDocument(BaseDocument):
    """MongoDB document model for password reset requests.
    
    Stores password reset requests for admin review.
    New passwords are generated and shown to admin (NOT emailed to user).
    
    Relationships:
        - user_id: References UserDocument.user_id
    """
    
    collection_name = "password_resets"
    
    # Status constants
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_EXPIRED = "expired"
    
    @staticmethod
    def create(
        user_id: str,
        username: str,
        role_name: str,
        new_password: str,
        course_id: str = None,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Create a new password reset request document.
        
        Args:
            user_id: User's semantic ID (e.g., USR26020001)
            username: Username for easy identification
            role_name: User's role name (e.g., "teacher", "student")
            new_password: Generated new password (plaintext for admin to communicate)
            course_id: Optional course ID for students
            status: Request status (pending, completed, expired)
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "user_id": user_id,
            "username": username,
            "role_name": role_name,
            "new_password": new_password,
            "course_id": course_id,
            "status": status,
            **BaseDocument.get_base_fields()
        }
        return doc
