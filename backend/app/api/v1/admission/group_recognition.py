"""Group Face Recognition API - Recognize students from group photos"""
import os
import tempfile
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.api.deps import require_teacher, get_current_active_user
from app.services.batch.recognition import BatchRecognitionService
from app.repositories.batch_recognition import BatchRecognitionRepository
from app.repositories.student import StudentRepository
from app.repositories.course import CourseRepository
from app.repositories.user import UserRepository
from app.repositories.admission import AdmissionRepository
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/admission", tags=["Group Recognition"])

# Max file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def get_batch_service() -> BatchRecognitionService:
    """Get BatchRecognitionService instance."""
    return BatchRecognitionService(BatchRecognitionRepository())


def get_student_repo() -> StudentRepository:
    """Get StudentRepository instance."""
    return StudentRepository()


def get_course_repo() -> CourseRepository:
    """Get CourseRepository instance."""
    return CourseRepository()


def get_user_repo() -> UserRepository:
    """Get UserRepository instance."""
    return UserRepository()


@router.post(
    "/recognize-group",
    dependencies=[Depends(require_teacher)],
    summary="Recognize students from group photo",
    description="Upload a group photo to identify registered students. Requires teacher, admin, or super_admin role."
)
async def recognize_group(
    image: UploadFile = File(..., description="Group photo (JPEG, PNG, WebP, max 10MB)"),
    batch_service: BatchRecognitionService = Depends(get_batch_service),
    student_repo: StudentRepository = Depends(get_student_repo),
    course_repo: CourseRepository = Depends(get_course_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Recognize students from a group photo.
    
    - Detects all faces in the image using YOLOv12
    - Matches faces against registered students using AdaFace
    - Returns student details for recognized faces
    - Returns face locations for unknown faces
    
    **Authorization:** Super Admin, Admin, or Teacher only
    """
    # Validate file extension
    if not image.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    ext = os.path.splitext(image.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await image.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Save to temp file for processing
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Process image using existing batch recognition service
        result = await batch_service.process_image(temp_path)
        
        # Check if any faces were detected
        if result["total_faces_detected"] == 0:
            raise HTTPException(
                status_code=404,
                detail="No faces detected in the image"
            )
        
        # Enrich recognized faces with student details via admission lookup
        recognized_students = []
        batch_repo = BatchRecognitionRepository()
        admission_repo = AdmissionRepository()
        
        for face in result.get("results", []):
            admission_id = face.get("person_name")  # npz key is now admission_id
            record_id = face.get("_id")
            
            if admission_id:
                # Look up admission → student
                admission = await admission_repo.get_by_admission_id(admission_id)
                student = None
                if admission:
                    student = await student_repo.get_by_student_id(admission["student_id"])
                
                if student:
                    # Get course details
                    course = await course_repo.get_by_course_id(student.get("current_course_id", ""))
                    
                    # Names from student document
                    first_name = student.get("first_name", "")
                    last_name = student.get("last_name", "")
                    
                    # Fallback: user lookup
                    if not first_name and student.get("user_ref"):
                        user = await user_repo.get_user_by_mongo_id(student["user_ref"])
                        if user:
                            first_name = user.get("first_name", "")
                            last_name = user.get("last_name", "")
                    
                    student_id = student["student_id"]
                    course_id = student.get("current_course_id", "")
                    course_name = course.get("name", "Unknown") if course else "Unknown"
                    section = course.get("section", "") if course else ""
                    
                    # Update DB record with enriched data
                    if record_id:
                        await batch_repo.update_log(str(record_id), {
                            "admission_id": admission_id,
                            "student_id": student_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "course_id": course_id,
                            "course_name": course_name,
                            "section": section
                        })
                    
                    recognized_students.append({
                        "student_id": student_id,
                        "admission_id": admission_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "course_name": course_name,
                        "section": section,
                        "confidence": round(face.get("confidence_score", 0), 3),
                        "face_location": face.get("face_location", {})
                    })
                else:
                    # Admission ID found in features but no student in DB
                    recognized_students.append({
                        "student_id": admission_id,
                        "admission_id": admission_id,
                        "first_name": "Unknown",
                        "last_name": "",
                        "course_name": "Unknown",
                        "section": "",
                        "confidence": round(face.get("confidence_score", 0), 3),
                        "face_location": face.get("face_location", {})
                    })
        
        # Calculate unknown faces count
        unknown_count = result["total_faces_detected"] - result["recognized_faces"]
        
        # Build response
        response = {
            "success": True,
            "batch_id": result["batch_id"],
            "stats": {
                "total_faces_detected": result["total_faces_detected"],
                "recognized_count": len(recognized_students),
                "unknown_count": unknown_count,
                "processing_time_ms": round(result["processing_time_ms"], 2)
            },
            "recognized": recognized_students,
            "unknown_faces": [
                {"face_location": {"note": "Unknown face locations not tracked"}}
            ] if unknown_count > 0 else []
        }
        
        logger.info(
            f"Group recognition by {current_user.get('username', 'unknown')}: "
            f"{len(recognized_students)} recognized, {unknown_count} unknown"
        )
        
        return response
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Group recognition error: {e}")
        raise HTTPException(status_code=500, detail=f"Recognition failed: {str(e)}")
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get(
    "/recognition-history",
    dependencies=[Depends(require_teacher)],
    summary="Get recognition history with filters",
    description="Retrieve past recognition logs with optional filters. Requires teacher, admin, or super_admin role."
)
async def get_recognition_history(
    student_id: str = None,
    course_id: str = None,
    start_date: str = None,
    end_date: str = None,
    skip: int = 0,
    limit: int = 50,
    _: dict = Depends(get_current_active_user)
):
    """
    Get recognition history with optional filters.
    
    - **student_id**: Filter by student ID (partial match)
    - **course_id**: Filter by course ID (exact match)
    - **start_date**: Filter from date (YYYY-MM-DD format)
    - **end_date**: Filter to date (YYYY-MM-DD format)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (default 50)
    """
    from datetime import datetime
    
    batch_repo = BatchRecognitionRepository()
    
    # Parse dates if provided
    parsed_start = None
    parsed_end = None
    
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    # Get logs with filters
    logs = await batch_repo.get_logs_with_filters(
        student_id=student_id,
        course_id=course_id,
        start_date=parsed_start,
        end_date=parsed_end,
        skip=skip,
        limit=limit
    )
    
    # Get total count
    total = await batch_repo.count_logs_with_filters(
        student_id=student_id,
        course_id=course_id,
        start_date=parsed_start,
        end_date=parsed_end
    )
    
    # Format response - enrich with student details via admission_id
    from app.repositories.student import StudentRepository
    from app.repositories.course import CourseRepository
    student_repo = StudentRepository()
    course_repo = CourseRepository()
    admission_repo = AdmissionRepository()
    
    # Cache lookups to avoid repeated DB calls
    admission_cache: dict = {}
    student_cache: dict = {}
    course_cache: dict = {}
    
    formatted_logs = []
    for log in logs:
        admission_id_val = log.get("admission_id", "")
        student_id_val = log.get("student_id", log.get("person_name", "Unknown"))
        first_name = log.get("first_name", "")
        last_name = log.get("last_name", "")
        course_name = log.get("course_name", "")
        section = log.get("section", "")
        
        # Enrich via admission_id if available, else try student_id
        if not first_name:
            student = None
            
            # Try admission_id lookup first
            if admission_id_val and admission_id_val != "Unknown":
                if admission_id_val not in admission_cache:
                    admission_cache[admission_id_val] = await admission_repo.get_by_admission_id(admission_id_val)
                admission = admission_cache[admission_id_val]
                if admission:
                    sid = admission["student_id"]
                    student_id_val = sid
                    if sid not in student_cache:
                        student_cache[sid] = await student_repo.get_by_student_id(sid)
                    student = student_cache[sid]
            # Fallback: try student_id directly
            elif student_id_val and student_id_val != "Unknown":
                if student_id_val not in student_cache:
                    student_cache[student_id_val] = await student_repo.get_by_student_id(student_id_val)
                student = student_cache[student_id_val]
            
            if student:
                first_name = student.get("first_name", "")
                last_name = student.get("last_name", "")
                if not course_name:
                    cid = student.get("current_course_id", "")
                    if cid and cid not in course_cache:
                        course_cache[cid] = await course_repo.get_by_course_id(cid)
                    course = course_cache.get(cid)
                    if course:
                        course_name = course.get("name", "")
                        section = course.get("section", "")
        
        formatted_logs.append({
            "id": str(log.get("_id", "")),
            "student_id": student_id_val,
            "admission_id": admission_id_val,
            "first_name": first_name,
            "last_name": last_name,
            "course_name": course_name,
            "section": section,
            "confidence": round(log.get("confidence_score", 0), 3),
            "detection_datetime": log.get("detection_datetime").isoformat() if log.get("detection_datetime") else None,
            "batch_id": log.get("batch_id", "")
        })
    
    return {
        "success": True,
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": formatted_logs
    }


@router.get(
    "/known-persons",
    dependencies=[Depends(require_teacher)],
    summary="Get known persons in face database",
    description="Get list of all persons registered in the face recognition database. Requires teacher, admin, or super_admin role."
)
async def get_known_persons(
    _: dict = Depends(get_current_active_user)
):
    """
    Get all known persons from face recognition database.
    Returns list of person IDs (student IDs) that have face embeddings registered.
    """
    import asyncio
    from app.services.batch import AddPersonsService
    
    service = AddPersonsService()
    # Offload file I/O to thread pool so event loop isn't blocked
    persons = await asyncio.to_thread(service.list_known_persons)
    
    return {
        "success": True,
        "persons": persons,
        "count": len(persons)
    }
