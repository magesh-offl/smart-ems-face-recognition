"""Student Log Document Model - Unified audit trail for all student changes"""
from datetime import datetime
from typing import Dict, Any
from .base import BaseDocument


class StudentLogDocument(BaseDocument):
    """MongoDB document model for student change logs.
    
    Uses `change_type` to distinguish between:
    - "course_transfer": course change that triggers student_id regeneration
    - "field_update": regular field edits (name, DOB, guardian, etc.)
    """
    
    collection_name = "student_logs"
    
    @staticmethod
    def create_course_transfer(
        student_id: str,
        admission_id: str,
        old_student_id: str,
        new_student_id: str,
        old_course_id: str,
        new_course_id: str,
        updated_by: str
    ) -> Dict[str, Any]:
        """Create a course transfer log entry.
        
        Args:
            student_id: Current (new) student ID
            admission_id: Stable admission identifier
            old_student_id: Previous student ID before transfer
            new_student_id: New student ID after transfer
            old_course_id: Previous course ID
            new_course_id: New course ID
            updated_by: Admin user_id who made the change
        """
        return {
            "student_id": student_id,
            "admission_id": admission_id,
            "change_type": "course_transfer",
            "old_student_id": old_student_id,
            "new_student_id": new_student_id,
            "old_course_id": old_course_id,
            "new_course_id": new_course_id,
            "updated_by": updated_by,
            "created_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_field_update(
        student_id: str,
        admission_id: str,
        field_name: str,
        old_value: str,
        new_value: str,
        updated_by: str
    ) -> Dict[str, Any]:
        """Create a field update log entry.
        
        Args:
            student_id: The student's current ID
            admission_id: Stable admission identifier
            field_name: Name of the field that changed
            old_value: Previous value (stringified)
            new_value: New value (stringified)
            updated_by: Admin user_id who made the change
        """
        return {
            "student_id": student_id,
            "admission_id": admission_id,
            "change_type": "field_update",
            "field_name": field_name,
            "old_value": str(old_value) if old_value is not None else "",
            "new_value": str(new_value) if new_value is not None else "",
            "updated_by": updated_by,
            "created_at": datetime.utcnow()
        }
