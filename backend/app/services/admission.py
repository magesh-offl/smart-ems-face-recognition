"""Admission Service - Student Registration and Face Processing

Handles the complete student admission workflow:
1. Create student record
2. Create admission record
3. Process face images for recognition training

Uses admission_id as the stable identifier for face recognition pipeline 
(datasets folders, npz keys). student_id may change on course transfers.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil
import os

from app.models import UserDocument, StudentDocument, AdmissionDocument
from app.models.student_log import StudentLogDocument
from app.repositories.user import UserRepository
from app.repositories.student import StudentRepository
from app.repositories.admission import AdmissionRepository
from app.repositories.course import CourseRepository
from app.repositories.student_log import StudentLogRepository
from app.services.id_generator import IDGeneratorService
from app.services.auth.service import AuthService
from app.utils.logger import setup_logger
from app.config import get_settings

logger = setup_logger(__name__)
settings = get_settings()


class AdmissionService:
    """Service for student admission and face registration workflow."""
    
    # Base path for student images
    DATASETS_PATH = Path(settings.DATASETS_PATH if hasattr(settings, 'DATASETS_PATH') 
                         else "datasets/new_persons")
    
    def __init__(
        self,
        user_repo: UserRepository,
        student_repo: StudentRepository,
        admission_repo: AdmissionRepository,
        course_repo: CourseRepository,
        id_generator: IDGeneratorService,
        auth_service: AuthService
    ):
        self.user_repo = user_repo
        self.student_repo = student_repo
        self.admission_repo = admission_repo
        self.course_repo = course_repo
        self.id_generator = id_generator
        self.auth_service = auth_service
        self.student_log_repo = StudentLogRepository()
    
    def _validate_name(self, value: str, field_name: str):
        """Validate that the field contains only letters and spaces."""
        if not value: return
        
        # Check against regex for letters and spaces only
        import re
        if not re.match(r"^[a-zA-Z\s]+$", value):
            raise ValueError(f"{field_name} can only contain letters and spaces.")

    async def _validate_phone_unique(self, phone: str, exclude_student_id: Optional[str] = None):
        """Ensure phone number is unique among ACTIVE students only."""
        existing = await self.student_repo.get_by_guardian_phone(phone)
        if existing:
            # If same student, it's allowed (for updates)
            if exclude_student_id and existing["student_id"] == exclude_student_id:
                return 

            # Check if existing student is ACTIVE
            existing_student_id = existing["student_id"]
            admission = await self.admission_repo.get_current_admission(existing_student_id)
            
            # Only block if the existing student has an ACTIVE (current) admission
            if admission and admission.get("status") == "active":
                raise ValueError(f"Guardian Phone Number already exists for an active student.")

    def _validate_phone(self, value: str):
        """Validate phone number is exactly 10 digits."""
        if not value or not value.isdigit() or len(value) != 10:
            raise ValueError("Guardian Phone must be exactly 10 digits.")

    async def admit_student(
        self,
        first_name: str,
        last_name: str,
        # Student fields
        course_id: str,
        date_of_birth: str,
        guardian_name: str,
        guardian_phone: str,
        address: Optional[str] = None,
        # Admission fields
        academic_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete student admission process.
        
        Creates:
        1. Student record
        2. Admission record for the academic year
        
        Args:
            first_name, last_name: Student name
            course_id: Course to enroll in (e.g., CRS0001)
            date_of_birth: DOB in YYYY-MM-DD format
            guardian_name: Parent/guardian name
            guardian_phone: Guardian contact
            address: Student address (Optional)
            academic_year: e.g., "2026-2027" (defaults to current year)
            
        Returns:
            Dict with student_id, admission_id and confirmation
        """
        # Validate course exists
        course = await self.course_repo.get_by_course_id(course_id)
        if not course:
            raise ValueError(f"Course not found: {course_id}")
            
        # Validate names
        self._validate_name(first_name, "First Name")
        self._validate_name(last_name, "Last Name")
        self._validate_name(guardian_name, "Guardian Name")
        self._validate_phone(guardian_phone)
        await self._validate_phone_unique(guardian_phone)
        
        # Idempotency: Check for duplicate admission within the last 60 seconds
        # This prevents double-click from creating duplicate student records
        recent_cutoff = datetime.utcnow() - timedelta(seconds=60)
        existing_student = await self.student_repo.find_one({
            "guardian_phone": guardian_phone,
            "first_name": first_name,
            "last_name": last_name,
            "current_course_id": course_id,
            "created_at": {"$gte": recent_cutoff}
        })
        if existing_student:
            # Return the existing result instead of creating a duplicate
            existing_admission = await self.admission_repo.find_one({
                "student_id": existing_student["student_id"]
            })
            admission_id = existing_admission["admission_id"] if existing_admission else "unknown"
            logger.info(f"Idempotency: Returning existing student {existing_student['student_id']} (duplicate submission within 60s)")
            return {
                "student_id": existing_student["student_id"],
                "admission_id": admission_id,
                "course_id": course_id,
                "academic_year": existing_admission.get("academic_year", "") if existing_admission else "",
                "images_path": str(self.DATASETS_PATH / admission_id),
                "message": "Student admitted successfully. Upload face images for training."
            }
        
        # Default academic year
        if not academic_year:
            year = datetime.utcnow().year
            academic_year = f"{year}-{year + 1}"
        
        # 1. Generate student_id and create student record
        course_code = self.id_generator.extract_course_code(course_id)
        student_id = await self.id_generator.generate_student_id(course_code)
        
        student_doc = StudentDocument.create(
            student_id=student_id,
            user_ref=None,  # No user account linked
            current_course_id=course_id,
            date_of_birth=date_of_birth,
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            address=address if address else "",
            is_trained=False,
            first_name=first_name,
            last_name=last_name
        )
        await self.student_repo.create_student(student_doc)
        
        # 2. Generate admission_id and create admission record
        admission_id = await self.id_generator.generate_admission_id(course_code)
        
        admission_doc = AdmissionDocument.create(
            admission_id=admission_id,
            student_id=student_id,
            course_id=course_id,
            academic_year=academic_year,
            admission_date=datetime.utcnow()
        )
        await self.admission_repo.create_admission(admission_doc)
        
        # Create directory for face images using admission_id (stable key)
        student_images_path = self.DATASETS_PATH / admission_id
        student_images_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Student admitted: {student_id} (admission: {admission_id}, {first_name} {last_name})")
        
        return {
            "student_id": student_id,
            "admission_id": admission_id,
            "course_id": course_id,
            "academic_year": academic_year,
            "images_path": str(student_images_path),
            "message": "Student admitted successfully. Upload face images for training."
        }
    
    async def save_student_images(
        self, 
        admission_id: str, 
        images: List[bytes],
        filenames: List[str]
    ) -> Dict[str, Any]:
        """Save uploaded face images for a student.
        
        Args:
            admission_id: Admission ID (stable key for face recognition)
            images: List of image bytes
            filenames: Corresponding filenames
            
        Returns:
            Dict with saved file paths and count
        """
        # Verify admission exists
        admission = await self.admission_repo.get_by_admission_id(admission_id)
        if not admission:
            raise ValueError(f"Admission not found: {admission_id}")
        
        # Get/create images directory using admission_id
        images_path = self.DATASETS_PATH / admission_id
        images_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for img_bytes, filename in zip(images, filenames):
            # Sanitize filename and ensure unique
            safe_name = Path(filename).name
            file_path = images_path / safe_name
            
            # Handle duplicates
            counter = 1
            while file_path.exists():
                stem = Path(safe_name).stem
                suffix = Path(safe_name).suffix
                file_path = images_path / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Save image
            file_path.write_bytes(img_bytes)
            saved_files.append(str(file_path))
        
        logger.info(f"Saved {len(saved_files)} images for admission {admission_id}")
        
        return {
            "admission_id": admission_id,
            "student_id": admission.get("student_id", ""),
            "saved_count": len(saved_files),
            "saved_files": saved_files
        }
    
    async def process_student_faces(self, admission_id: str) -> Dict[str, Any]:
        """Process face images using ML pipeline.
        
        Uses the existing AddPersonsService to:
        1. Detect faces in images
        2. Extract embeddings
        3. Save to feature.npz (keyed by admission_id)
        
        Args:
            admission_id: Admission ID (folder name in datasets)
            
        Returns:
            Processing result with trained status
        """
        from app.services.batch.add_persons import AddPersonsService
        import shutil
        import os
        
        # Verify admission exists and get student_id
        admission = await self.admission_repo.get_by_admission_id(admission_id)
        if not admission:
            raise ValueError(f"Admission not found: {admission_id}")
        
        student_id = admission["student_id"]
        student = await self.student_repo.get_by_student_id(student_id)
        if not student:
            raise ValueError(f"Student not found: {student_id}")
        
        images_path = self.DATASETS_PATH / admission_id
        if not images_path.exists() or not list(images_path.glob("*")):
            raise ValueError(f"No images found for admission: {admission_id}")
        
        # AddPersonsService expects a folder containing person subfolders
        # where each subfolder name = person_id and contains their images.
        # The subfolder is named admission_id (stable face recognition key).
        add_persons_service = AddPersonsService()
        
        result = add_persons_service.add_persons_from_folder(
            source_path=str(self.DATASETS_PATH),
            move_to_backup=True
        )
        
        # Check if this admission was processed
        persons_added = result.get("persons_added", [])
        trained = admission_id in persons_added
        
        # Update is_trained status on the student document
        if trained:
            await self.student_repo.update_trained_status(student_id, True)
            logger.info(f"Face training completed for admission: {admission_id} (student: {student_id})")
        
        return {
            "admission_id": admission_id,
            "student_id": student_id,
            "is_trained": trained,
            "faces_detected": result.get("faces_processed", 0) if trained else 0,
            "message": f"Training {'completed' if trained else 'failed'} for {admission_id}"
        }
    
    async def update_student(
        self,
        student_id: str,
        updated_by: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        guardian_name: Optional[str] = None,
        guardian_phone: Optional[str] = None,
        address: Optional[str] = None,
        course_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update student details.
        
        If course_id changes:
        1. Generate new student_id for the new course
        2. Update student doc (student_id, current_course_id)
        3. Update admission doc (student_id, course_id)
        4. Log course change to admission_logs
        
        For other field changes:
        5. Update student doc
        6. Log each change to student_logs
        
        Args:
            student_id: Current student ID
            updated_by: Admin user_id performing the update
            
        Returns:
            Dict with updated student details
        """
        # Fetch current student
        student = await self.student_repo.get_by_student_id(student_id)
        if not student:
            raise ValueError(f"Student not found: {student_id}")
        
        # Fetch current admission
        admission = await self.admission_repo.get_current_admission(student_id)
        if not admission:
            raise ValueError(f"No active admission found for student: {student_id}")
        
        admission_id = admission["admission_id"]
        old_student_id = student_id
        old_course_id = student.get("current_course_id", "")
        new_student_id = student_id  # Will change if course changes
        
        # Track non-course field changes for student_logs
        field_changes = {}
        editable_fields = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "guardian_name": guardian_name,
            "guardian_phone": guardian_phone,
            "address": address,
        }
        
        # Validate names if updated
        if first_name: self._validate_name(first_name, "First Name")
        if last_name: self._validate_name(last_name, "Last Name")
        if guardian_name: self._validate_name(guardian_name, "Guardian Name")
        if guardian_phone: 
            self._validate_phone(guardian_phone)
            await self._validate_phone_unique(guardian_phone, exclude_student_id=student_id)
        
        for field, new_val in editable_fields.items():
            if new_val is not None:
                old_val = student.get(field, "")
                if str(old_val) != str(new_val):
                    field_changes[field] = {"old": str(old_val), "new": str(new_val)}
        
        # Build update data for student doc
        student_update = {}
        for field, new_val in editable_fields.items():
            if new_val is not None:
                student_update[field] = new_val
        
        # Handle course change — regenerate student_id
        course_changed = course_id and course_id != old_course_id
        if course_changed:
            # Validate new course
            course = await self.course_repo.get_by_course_id(course_id)
            if not course:
                raise ValueError(f"Course not found: {course_id}")
            
            # Generate new student_id
            course_code = self.id_generator.extract_course_code(course_id)
            new_student_id = await self.id_generator.generate_student_id(course_code)
            
            # Update student doc with new student_id and course
            student_update["student_id"] = new_student_id
            student_update["current_course_id"] = course_id
            
            # Update admission doc
            await self.admission_repo.update_admission(admission_id, {
                "student_id": new_student_id,
                "course_id": course_id
            })
            
            # Write admission change log to student_logs
            admission_log = StudentLogDocument.create_course_transfer(
                student_id=new_student_id,
                admission_id=admission_id,
                old_student_id=old_student_id,
                new_student_id=new_student_id,
                old_course_id=old_course_id,
                new_course_id=course_id,
                updated_by=updated_by
            )
            await self.student_log_repo.create_log(admission_log)
            
            logger.info(
                f"Course transfer: {old_student_id} → {new_student_id} "
                f"(course: {old_course_id} → {course_id})"
            )
        
        # Apply student doc updates
        if student_update:
            await self.student_repo.update_student(old_student_id, student_update)
        
        # Write student field change logs (non-course changes only)
        for field, vals in field_changes.items():
            log_entry = StudentLogDocument.create_field_update(
                student_id=new_student_id,
                admission_id=admission_id,
                field_name=field,
                old_value=vals["old"],
                new_value=vals["new"],
                updated_by=updated_by
            )
            await self.student_log_repo.create_log(log_entry)
        
        return {
            "student_id": new_student_id,
            "admission_id": admission_id,
            "course_changed": course_changed,
            "old_student_id": old_student_id if course_changed else None,
            "message": "Student updated successfully"
        }
    
    async def get_student_details(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get complete student details including user and admission info."""
        student = await self.student_repo.get_by_student_id(student_id)
        if not student:
            return None
        
        # Get user details (may be None if no user account linked)
        user = None
        if student.get("user_ref"):
            user = await self.user_repo.get_user_by_mongo_id(student["user_ref"])
        
        # Names from student document (primary) or user (fallback)
        first_name = student.get("first_name", "") or (user.get("first_name", "") if user else "")
        last_name = student.get("last_name", "") or (user.get("last_name", "") if user else "")
        
        # Get current admission
        admission = await self.admission_repo.get_current_admission(student_id)
        
        # Get course details
        course = await self.course_repo.get_by_course_id(student["current_course_id"])
        
        return {
            "student_id": student_id,
            "admission_id": admission.get("admission_id") if admission else None,
            "user": {
                "user_id": user.get("user_id") if user else None,
                "username": user.get("username") if user else None,
                "email": user.get("email") if user else None,
                "first_name": first_name,
                "last_name": last_name
            },
            "student": {
                "date_of_birth": student.get("date_of_birth"),
                "guardian_name": student.get("guardian_name"),
                "guardian_phone": student.get("guardian_phone"),
                "address": student.get("address"),
                "is_trained": student.get("is_trained", False)
            },
            "course": {
                "course_id": course.get("course_id") if course else None,
                "name": course.get("name") if course else None,
                "section": course.get("section") if course else None
            },
            "admission": {
                "admission_id": admission.get("admission_id") if admission else None,
                "academic_year": admission.get("academic_year") if admission else None,
                "status": admission.get("status") if admission else None
            }
        }
    
    async def list_students(
        self, 
        course_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List students with optional course filter."""
        if course_id:
            students = await self.student_repo.get_students_by_course(
                course_id, skip=skip, limit=limit
            )
        else:
            # Get all students (paginated)
            students = await self.student_repo.find_many({}, skip=skip, limit=limit)
        
        # Build result with admission_id included
        result = []
        for student in students:
            # Names from student document
            first_name = student.get("first_name", "")
            last_name = student.get("last_name", "")
            
            # Fallback: try user lookup if names are missing
            if not first_name and student.get("user_ref"):
                user = await self.user_repo.get_user_by_mongo_id(student["user_ref"])
                if user:
                    first_name = user.get("first_name", "")
                    last_name = user.get("last_name", "")
            
            # Get admission_id for this student
            admission = await self.admission_repo.get_current_admission(student["student_id"])
            
            result.append({
                "student_id": student["student_id"],
                "admission_id": admission.get("admission_id") if admission else None,
                "first_name": first_name,
                "last_name": last_name,
                "course_id": student["current_course_id"],
                "is_trained": student.get("is_trained", False)
            })
        
        return result
