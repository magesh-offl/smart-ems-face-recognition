"""Course Document Model"""
from datetime import datetime
from typing import Dict, Any
from .base import BaseDocument


class CourseDocument(BaseDocument):
    """MongoDB document model for courses/classes.
    
    Represents academic classes/courses that students enroll in.
    
    Examples:
        - CRS0001: Class 10, Section A
        - CRS0002: Class 10, Section B
        - CRS0003: Class 11, Section A
    """
    
    collection_name = "courses"
    
    @staticmethod
    def create(
        course_id: str,
        name: str,
        section: str,
        description: str = "",
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a new course document.
        
        Args:
            course_id: Unique course identifier (e.g., CRS0001)
            name: Course/class name (e.g., "Class 10", "Grade 12")
            section: Section identifier (e.g., "A", "B", "C")
            description: Optional course description
            is_active: Whether course is currently active
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "course_id": course_id,
            "name": name,
            "section": section,
            "description": description,
            "is_active": is_active,
            **BaseDocument.get_base_fields()
        }
        return doc
