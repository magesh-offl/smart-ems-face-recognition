"""Admin API Routes - Student/Teacher/Course Management"""
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from app.services.admission import AdmissionService
from app.services.id_generator import IDGeneratorService, IDCounterRepository
from app.services.auth.service import AuthService
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.repositories.course import CourseRepository
from app.repositories.student import StudentRepository
from app.repositories.admission import AdmissionRepository
from app.repositories.password_reset import PasswordResetRepository
from app.api.deps import require_admin, require_manage_students, get_current_active_user
from app.models import CourseDocument
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1/admission", tags=["Admission"])


def get_id_generator() -> IDGeneratorService:
    """Get IDGeneratorService instance."""
    return IDGeneratorService(IDCounterRepository())


def get_auth_service() -> AuthService:
    """Get AuthService with all dependencies."""
    return AuthService(
        user_repository=UserRepository(),
        role_repository=RoleRepository(),
        password_reset_repository=PasswordResetRepository(),
        id_generator=get_id_generator()
    )


def get_admission_service() -> AdmissionService:
    """Get AdmissionService with all dependencies."""
    return AdmissionService(
        user_repo=UserRepository(),
        student_repo=StudentRepository(),
        admission_repo=AdmissionRepository(),
        course_repo=CourseRepository(),
        id_generator=get_id_generator(),
        auth_service=get_auth_service()
    )


# ==================== Course Management ====================

@router.post("/courses", dependencies=[Depends(require_admin)])
async def create_course(
    name: str = Form(...),
    section: str = Form(...),
    description: str = Form(default=""),
    id_generator: IDGeneratorService = Depends(get_id_generator),
    course_repo: CourseRepository = Depends(lambda: CourseRepository())
):
    """Create a new course/class. Requires admin role."""
    # Check if course+section already exists
    existing = await course_repo.get_by_name_section(name, section)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course {name} Section {section} already exists"
        )
    
    course_id = await id_generator.generate_course_id()
    course_doc = CourseDocument.create(
        course_id=course_id,
        name=name,
        section=section,
        description=description
    )
    await course_repo.create_course(course_doc)
    
    return {
        "course_id": course_id,
        "name": name,
        "section": section,
        "message": "Course created successfully"
    }


@router.get("/courses")
async def list_courses(
    active_only: bool = True,
    current_user: dict = Depends(get_current_active_user),
    course_repo: CourseRepository = Depends(lambda: CourseRepository())
):
    """List all courses. Any authenticated user can view."""
    courses = await course_repo.get_all_courses(active_only=active_only)
    return {
        "courses": [
            {
                "course_id": c["course_id"],
                "name": c["name"],
                "section": c["section"],
                "description": c.get("description", ""),
                "is_active": c.get("is_active", True)
            }
            for c in courses
        ]
    }


# ==================== Student Admission ====================

@router.get("/students/check-phone", dependencies=[Depends(require_manage_students)])
async def check_phone(
    phone: str,
    exclude_student_id: Optional[str] = None,
    student_repo: StudentRepository = Depends(lambda: StudentRepository())
):
    """Check if guardian phone number already exists."""
    existing = await student_repo.get_by_guardian_phone(phone)
    if existing:
        if exclude_student_id and existing["student_id"] == exclude_student_id:
            return {"exists": False}
        return {"exists": True, "message": "Phone number already exists"}
    return {"exists": False}

@router.post("/students/admit", dependencies=[Depends(require_manage_students)])
async def admit_student(
    first_name: str = Form(...),
    last_name: str = Form(...),
    course_id: str = Form(...),
    date_of_birth: str = Form(...),
    guardian_name: str = Form(...),
    guardian_phone: str = Form(...),
    address: Optional[str] = Form(default=None),
    academic_year: Optional[str] = Form(default=None),
    admission_service: AdmissionService = Depends(get_admission_service),
    course_repo: CourseRepository = Depends(lambda: CourseRepository())
):
    """Admit a new student. Creates student record and admission.
    
    Requires: manage_students permission.
    """
    # Validate course_id exists
    course = await course_repo.get_by_course_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid course_id: {course_id}. Course does not exist."
        )
    
    try:
        result = await admission_service.admit_student(
            first_name=first_name,
            last_name=last_name,
            course_id=course_id,
            date_of_birth=date_of_birth,
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            address=address,
            academic_year=academic_year
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Admission failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/students/{admission_id}/images", dependencies=[Depends(require_manage_students)])
async def upload_student_images(
    admission_id: str,
    images: List[UploadFile] = File(...),
    admission_service: AdmissionService = Depends(get_admission_service)
):
    """Upload face images for a student. Accepts multiple image files.
    
    Uses admission_id as the stable identifier for face recognition storage.
    After uploading, call /students/{admission_id}/train to process the images.
    """
    if not images:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No images provided")
    
    # Validate all files are images
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
    for img in images:
        if img.filename:
            ext = os.path.splitext(img.filename)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type: '{img.filename}'. Only image files allowed ({', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))})"
                )
        # Also check content type
        if img.content_type and not img.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type: '{img.content_type}' for file '{img.filename}'. Only image files allowed."
            )
    
    # Read image bytes
    image_bytes = []
    filenames = []
    for img in images:
        content = await img.read()
        image_bytes.append(content)
        filenames.append(img.filename or f"image_{len(filenames)}.jpg")
    
    try:
        result = await admission_service.save_student_images(admission_id, image_bytes, filenames)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/students/{admission_id}/train", dependencies=[Depends(require_manage_students)])
async def train_student_face(
    admission_id: str,
    admission_service: AdmissionService = Depends(get_admission_service)
):
    """Process uploaded images and train face recognition for a student.
    
    Uses the ML pipeline to detect faces, extract embeddings, and save to feature.npz.
    The npz key is admission_id (stable, unlike student_id which changes on course transfer).
    """
    try:
        result = await admission_service.process_student_faces(admission_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Face training failed for {admission_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/students", dependencies=[Depends(require_manage_students)])
async def list_students(
    course_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    admission_service: AdmissionService = Depends(get_admission_service)
):
    """List students with optional course filter."""
    students = await admission_service.list_students(course_id=course_id, skip=skip, limit=limit)
    return {"students": students, "count": len(students)}


@router.get("/students/{student_id}", dependencies=[Depends(require_manage_students)])
async def get_student(
    student_id: str,
    admission_service: AdmissionService = Depends(get_admission_service)
):
    """Get complete student details."""
    result = await admission_service.get_student_details(student_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return result


@router.put("/students/{student_id}", dependencies=[Depends(require_manage_students)])
async def update_student(
    student_id: str,
    first_name: Optional[str] = Form(default=None),
    last_name: Optional[str] = Form(default=None),
    date_of_birth: Optional[str] = Form(default=None),
    guardian_name: Optional[str] = Form(default=None),
    guardian_phone: Optional[str] = Form(default=None),
    address: Optional[str] = Form(default=None),
    course_id: Optional[str] = Form(default=None),
    current_user: dict = Depends(get_current_active_user),
    admission_service: AdmissionService = Depends(get_admission_service)
):
    """Update student details. If course_id changes, student_id will be regenerated.
    
    Requires: manage_students permission.
    """
    try:
        result = await admission_service.update_student(
            student_id=student_id,
            updated_by=current_user.get("user_id", "unknown"),
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            address=address,
            course_id=course_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Student update failed for {student_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== Password Reset Management ====================

@router.get("/password-resets", dependencies=[Depends(require_admin)])
async def list_password_reset_requests(
    skip: int = 0,
    limit: int = 50,
    password_reset_repo: PasswordResetRepository = Depends(lambda: PasswordResetRepository())
):
    """List pending password reset requests for admin review."""
    requests = await password_reset_repo.get_pending_requests(skip=skip, limit=limit)
    count = await password_reset_repo.count_pending()
    
    return {
        "requests": [
            {
                "id": str(r["_id"]),
                "user_id": r["user_id"],
                "username": r["username"],
                "role_name": r["role_name"],
                "new_password": r["new_password"],
                "course_id": r.get("course_id"),
                "created_at": r.get("created_at"),
                "status": r["status"]
            }
            for r in requests
        ],
        "pending_count": count
    }


@router.post("/password-resets/{request_id}/complete", dependencies=[Depends(require_admin)])
async def complete_password_reset(
    request_id: str,
    password_reset_repo: PasswordResetRepository = Depends(lambda: PasswordResetRepository()),
    user_repo: UserRepository = Depends(lambda: UserRepository()),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Mark a password reset as completed and update the user's password.
    
    The admin should communicate the new password to the user before calling this.
    Idempotent: re-calling with an already-completed request returns success.
    """
    # Fetch the request by ID directly (not just pending ones)
    reset_request = await password_reset_repo.find_by_id(request_id)
    
    if not reset_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reset request not found")
    
    # Idempotency: If already completed, return success without re-processing
    if reset_request.get("status") == "completed":
        return {"message": "Password reset already completed", "user_id": reset_request["user_id"]}
    
    # Update user's password
    success = await user_repo.update_password(
        reset_request["user_id"],
        auth_service._hash_password(reset_request["new_password"])
    )
    
    if success:
        await password_reset_repo.mark_completed(request_id)
        return {"message": "Password reset completed", "user_id": reset_request["user_id"]}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update password")
