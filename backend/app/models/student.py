"""Student Document Model"""
from datetime import datetime, date
from typing import Dict, Any, Optional
from .base import BaseDocument


class StudentDocument(BaseDocument):
    """MongoDB document model for students.
    
    Stores student-specific data including name and face recognition status.
    
    Relationships:
        - user_ref: Optional reference to UserDocument._id (can be None)
        - current_course_id: References CourseDocument.course_id
    """
    
    collection_name = "students"
    
    @staticmethod
    def create(
        student_id: str,
        user_ref: Optional[str],
        current_course_id: str,
        date_of_birth: date,
        guardian_name: str,
        guardian_phone: str,
        address: Optional[str] = None,
        is_trained: bool = False,
        first_name: str = "",
        last_name: str = ""
    ) -> Dict[str, Any]:
        """Create a new student document.
        
        Args:
            student_id: Unique student identifier (e.g., STU260030001)
            user_ref: Optional MongoDB _id of associated UserDocument
            current_course_id: Current course ID (e.g., CRS0001)
            date_of_birth: Student's date of birth
            guardian_name: Parent/guardian name
            guardian_phone: Guardian contact number
            address: Student's address (optional)
            is_trained: Whether face recognition is trained (default False)
            first_name: Student's first name
            last_name: Student's last name
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "student_id": student_id,
            "user_ref": user_ref,
            "current_course_id": current_course_id,
            "date_of_birth": date_of_birth.isoformat() if isinstance(date_of_birth, date) else date_of_birth,
            "guardian_name": guardian_name,
            "guardian_phone": guardian_phone,
            "address": address,
            "is_trained": is_trained,
            "first_name": first_name,
            "last_name": last_name,
            **BaseDocument.get_base_fields()
        }
        return doc

