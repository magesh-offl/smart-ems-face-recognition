"""ID Generator Service - Atomic Sequential ID Generation

Provides centralized ID generation with configurable prefixes and formats.
Uses atomic MongoDB operations for thread-safe sequential numbering.
"""
from datetime import datetime
from typing import Optional
from app.repositories.base import BaseRepository
from app.models import IDCounterDocument


class IDCounterRepository(BaseRepository):
    """Repository for ID counter operations with atomic increment."""
    
    def __init__(self):
        super().__init__(IDCounterDocument.collection_name)
    
    async def get_next_id(self, counter_type: str, prefix: str) -> str:
        """Get next sequential ID atomically.
        
        Args:
            counter_type: Unique identifier for counter scope
            prefix: Prefix for the generated ID
            
        Returns:
            Complete ID string (e.g., "USR26020001")
        """
        coll = await self._get_collection()
        
        # Atomic find-and-modify: increment counter and return new value
        result = await coll.find_one_and_update(
            {"counter_type": counter_type},
            {
                "$inc": {"current_value": 1},
                "$setOnInsert": {
                    "prefix": prefix,
                    "created_at": datetime.utcnow()
                },
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True,
            return_document=True  # Return updated document
        )
        
        # Format with 4-digit sequence
        sequence = result["current_value"]
        return f"{prefix}{sequence:04d}"


class IDGeneratorService:
    """Service for generating semantic IDs across all entities.
    
    ID Formats:
        - User:      USR{YYMM}{NNNN}      -> USR26020001
        - Student:   STU{YY}{CCC}{NNNN}   -> STU260030001
        - Admission: ADMN{YY}{CCC}{NNNN}  -> ADMN26030001
        - Course:    CRS{NNNN}            -> CRS0001
        - Role:      ROL{NNNN}            -> ROL0001
        - Teacher:   TCH{YY}{NNNN}        -> TCH260001
    """
    
    def __init__(self, counter_repo: IDCounterRepository):
        self.counter_repo = counter_repo
    
    def _get_year_month(self) -> tuple[str, str]:
        """Get current year (YY) and month (MM)."""
        now = datetime.utcnow()
        return f"{now.year % 100:02d}", f"{now.month:02d}"
    
    def _get_year(self) -> str:
        """Get current year (YY)."""
        return f"{datetime.utcnow().year % 100:02d}"
    
    async def generate_user_id(self) -> str:
        """Generate User ID: USR{YYMM}{NNNN}
        
        Example: USR26020001 (Feb 2026, 1st user that month)
        """
        yy, mm = self._get_year_month()
        counter_type = f"user_{yy}{mm}"
        prefix = f"USR{yy}{mm}"
        return await self.counter_repo.get_next_id(counter_type, prefix)
    
    async def generate_student_id(self, course_code: str) -> str:
        """Generate Student ID: STU{YY}{CCC}{NNNN}
        
        Args:
            course_code: 3-digit course code (from course_id, e.g., "003" from CRS0003)
            
        Example: STU260030001 (2026, course 003, 1st student)
        """
        yy = self._get_year()
        counter_type = f"student_{yy}_{course_code}"
        prefix = f"STU{yy}{course_code}"
        return await self.counter_repo.get_next_id(counter_type, prefix)
    
    async def generate_admission_id(self, course_code: str) -> str:
        """Generate Admission ID: ADMN{YY}{CCC}{NNNN}
        
        Args:
            course_code: 3-digit course code
            
        Example: ADMN26030001 (2026, course 003, 1st admission)
        """
        yy = self._get_year()
        counter_type = f"admission_{yy}_{course_code}"
        prefix = f"ADMN{yy}{course_code}"
        return await self.counter_repo.get_next_id(counter_type, prefix)
    
    async def generate_course_id(self) -> str:
        """Generate Course ID: CRS{NNNN}
        
        Example: CRS0001 (1st course)
        """
        return await self.counter_repo.get_next_id("course", "CRS")
    
    async def generate_role_id(self) -> str:
        """Generate Role ID: ROL{NNNN}
        
        Example: ROL0001 (1st role)
        """
        return await self.counter_repo.get_next_id("role", "ROL")
    
    async def generate_teacher_id(self) -> str:
        """Generate Teacher ID: TCH{YY}{NNNN}
        
        Example: TCH260001 (2026, 1st teacher)
        """
        yy = self._get_year()
        counter_type = f"teacher_{yy}"
        prefix = f"TCH{yy}"
        return await self.counter_repo.get_next_id(counter_type, prefix)
    
    def extract_course_code(self, course_id: str) -> str:
        """Extract 3-digit course code from course_id.
        
        Args:
            course_id: Full course ID (e.g., "CRS0003")
            
        Returns:
            3-digit code (e.g., "003")
        """
        # CRS0003 -> 0003 -> take last 3 digits as code
        if course_id.startswith("CRS"):
            return course_id[3:7].lstrip("0").zfill(3)
        return "001"  # Default
