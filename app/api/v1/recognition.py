"""Recognition API Routes with Dependency Injection - Optimized"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional
from datetime import datetime

from app.controllers.recognition import RecognitionController
from app.controllers.batch_recognition import BatchRecognitionController
from app.core.dependencies import (
    get_recognition_service,
    get_batch_recognition_service
)
from app.services.recognition import RecognitionService
from app.services.batch_recognition import BatchRecognitionService
from app.models import (
    RecognitionLogCreate, RecognitionLogResponse, 
    RecognitionLogUpdate, RecognitionLogFilter,
    BatchRecognitionRequest, BatchRecognitionResponse
)
from app.middleware.auth import require_api_key
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/recognition", tags=["Recognition"])


# ============= Dependency Injection Providers =============

def get_recognition_controller(
    service: RecognitionService = Depends(get_recognition_service)
) -> RecognitionController:
    """Provides RecognitionController with injected service"""
    return RecognitionController(service)


def get_batch_recognition_controller(
    service: BatchRecognitionService = Depends(get_batch_recognition_service)
) -> BatchRecognitionController:
    """Provides BatchRecognitionController with injected service"""
    return BatchRecognitionController(service)


# ============= Recognition Endpoints =============

@router.post("/save", response_model=dict)
async def save_recognition(
    data: RecognitionLogCreate,
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """
    Save face recognition data.
    
    Requires API key in 'X-API-Key' header.
    If same person detected at same camera within 1 hour, counter increments instead of creating new record.
    
    - **person_name**: Name of recognized person
    - **camera_id**: ID of the camera that detected the face
    - **confidence_score**: Optional confidence score (0.0-1.0)
    """
    result = controller.save_recognition(
        data.person_name, data.camera_id, data.confidence_score
    )
    logger.info(f"Recognition saved: {data.person_name} from {data.camera_id}")
    return result


@router.get("/logs/{log_id}", response_model=RecognitionLogResponse)
async def get_log(
    log_id: str,
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """
    Get a specific recognition log by ID.
    
    Requires API key in 'X-API-Key' header.
    """
    return controller.get_recognition_log(log_id)


@router.get("/logs", response_model=dict)
async def get_all_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """
    Get all recognition logs with pagination.
    
    Requires API key in 'X-API-Key' header.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 10, max: 100)
    """
    return controller.get_all_logs(skip, limit)


@router.get("/filter", response_model=dict)
async def filter_logs(
    person_name: Optional[str] = Query(None),
    camera_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """
    Filter recognition logs.
    
    Requires API key in 'X-API-Key' header.
    
    - **person_name**: Filter by person name (case-insensitive partial match)
    - **camera_id**: Filter by camera ID (case-insensitive partial match)
    - **start_date**: Filter by start date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
    - **end_date**: Filter by end date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    """
    # Parse dates if provided
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            )
    
    return controller.filter_logs(
        person_name, camera_id, start_dt, end_dt, skip, limit
    )


@router.put("/logs/{log_id}", response_model=dict)
async def update_log(
    log_id: str,
    data: RecognitionLogUpdate,
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """
    Update a recognition log.
    
    Requires API key in 'X-API-Key' header.
    
    - **log_id**: ID of the log to update
    - **person_name**: New person name (optional)
    - **camera_id**: New camera ID (optional)
    - **confidence_score**: New confidence score (optional)
    """
    return controller.update_log(log_id, data)


@router.delete("/logs/{log_id}", response_model=dict)
async def delete_log(
    log_id: str,
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """
    Delete a recognition log.
    
    Requires API key in 'X-API-Key' header.
    
    - **log_id**: ID of the log to delete
    """
    return controller.delete_log(log_id)


# ============= Batch Recognition Endpoints =============

@router.post("/batch/process", response_model=BatchRecognitionResponse)
async def process_batch_recognition(
    data: BatchRecognitionRequest,
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_recognition_controller)
):
    """
    Process an image for face recognition.
    
    Detects all faces in the image, recognizes them against trained features,
    and saves results to the batch_recognition_logs collection.
    
    Requires API key in 'X-API-Key' header.
    
    - **image_path**: Server-side path to the image file
    """
    return controller.process_image(data.image_path)


@router.get("/batch/{batch_id}", response_model=dict)
async def get_batch_results(
    batch_id: str,
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_recognition_controller)
):
    """
    Get results for a specific batch recognition.
    
    Requires API key in 'X-API-Key' header.
    
    - **batch_id**: ID of the batch to retrieve
    """
    return controller.get_batch_results(batch_id)


@router.get("/batches", response_model=dict)
async def get_all_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_recognition_controller)
):
    """
    Get all batch recognition summaries with pagination.
    
    Requires API key in 'X-API-Key' header.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 10, max: 100)
    """
    return controller.get_all_batches(skip, limit)


@router.delete("/batches", response_model=dict)
async def delete_all_batches(
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_recognition_controller)
):
    """
    Delete ALL batch recognition logs.
    
    ⚠️ WARNING: This action cannot be undone!
    
    Requires API key in 'X-API-Key' header.
    """
    return controller.delete_all_batches()


# ============= Add Persons Endpoints =============

from pydantic import BaseModel
from app.controllers.add_persons import AddPersonsController
from app.services.add_persons import AddPersonsService


class AddPersonsRequest(BaseModel):
    """Request model for adding persons"""
    source_path: Optional[str] = None
    move_to_backup: bool = True


def get_add_persons_service() -> AddPersonsService:
    """Provides AddPersonsService instance"""
    return AddPersonsService()


def get_add_persons_controller(
    service: AddPersonsService = Depends(get_add_persons_service)
) -> AddPersonsController:
    """Provides AddPersonsController with injected service"""
    return AddPersonsController(service)


@router.post("/persons/add", response_model=dict)
async def add_persons(
    data: AddPersonsRequest = None,
    _: str = Depends(require_api_key),
    controller: AddPersonsController = Depends(get_add_persons_controller)
):
    """
    Add new persons to the face recognition database.
    
    Scans a folder for person subfolders, detects faces, extracts features,
    and adds them to the recognition database.
    
    Requires API key in 'X-API-Key' header.
    
    - **source_path**: Optional path to folder containing person subfolders.
                      Defaults to datasets/new_persons/
    - **move_to_backup**: Whether to move processed folders to backup (default: true)
    
    Folder structure expected:
    ```
    source_path/
    ├── person_name_1/
    │   ├── photo1.jpg
    │   └── photo2.jpg
    └── person_name_2/
        └── photo.jpg
    ```
    """
    source_path = data.source_path if data else None
    move_to_backup = data.move_to_backup if data else True
    return controller.add_persons(source_path, move_to_backup)


@router.get("/persons", response_model=dict)
async def get_known_persons(
    _: str = Depends(require_api_key),
    controller: AddPersonsController = Depends(get_add_persons_controller)
):
    """
    Get list of all known persons in the database.
    
    Requires API key in 'X-API-Key' header.
    
    Returns list of person names that have been added to the recognition database.
    """
    return controller.get_known_persons()

