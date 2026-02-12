"""Admission Document Model"""
from datetime import datetime
from typing import Dict, Any
from .base import BaseDocument


class AdmissionDocument(BaseDocument):
    """MongoDB document model for admissions.
    
    Tracks student admissions per academic year.
    Students can have multiple admission records (one per year/promotion).
    
    Relationships:
        - student_id: References StudentDocument.student_id
        - course_id: References CourseDocument.course_id
    """
    
    collection_name = "admissions"
    
    # Status constants
    STATUS_ACTIVE = "active"
    STATUS_PROMOTED = "promoted"
    STATUS_WITHDRAWN = "withdrawn"
    STATUS_GRADUATED = "graduated"
    
    @staticmethod
    def create(
        admission_id: str,
        student_id: str,
        course_id: str,
        academic_year: str,
        admission_date: datetime,
        status: str = "active"
    ) -> Dict[str, Any]:
        """Create a new admission document.
        
        Args:
            admission_id: Unique admission identifier (e.g., ADMN26030001)
            student_id: Student's ID (e.g., STU260030001)
            course_id: Course ID for this admission (e.g., CRS0001)
            academic_year: Academic year (e.g., "2026-2027")
            admission_date: Date of admission
            status: Admission status (active, promoted, withdrawn, graduated)
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "admission_id": admission_id,
            "student_id": student_id,
            "course_id": course_id,
            "academic_year": academic_year,
            "admission_date": admission_date.isoformat() if isinstance(admission_date, datetime) else admission_date,
            "status": status,
            **BaseDocument.get_base_fields()
        }
        return doc
