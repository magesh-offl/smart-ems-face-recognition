"""Recognition API Routes - Async"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional
from datetime import datetime

from app.controllers.recognition import RecognitionController
from app.controllers.batch import BatchRecognitionController, AddPersonsController
from app.core.dependencies import get_recognition_service, get_batch_recognition_service
from app.services.batch import AddPersonsService
from app.schemas import (
    RecognitionLogCreate, RecognitionLogResponse, RecognitionLogUpdate,
    BatchRecognitionRequest, BatchRecognitionResponse, AddPersonsRequest
)
from app.middleware import require_api_key

router = APIRouter(prefix="/api/v1/recognition", tags=["Recognition"])


# Dependency Providers
def get_recognition_controller(service=Depends(get_recognition_service)) -> RecognitionController:
    return RecognitionController(service)


def get_batch_controller(service=Depends(get_batch_recognition_service)) -> BatchRecognitionController:
    return BatchRecognitionController(service)


def get_add_persons_controller(service: AddPersonsService = Depends(AddPersonsService)) -> AddPersonsController:
    return AddPersonsController(service)


# Recognition Endpoints
@router.post("/save", response_model=dict)
async def save_recognition(
    data: RecognitionLogCreate,
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """Save face recognition data."""
    return await controller.save_recognition(data.person_name, data.camera_id, data.confidence_score)


@router.get("/logs/{log_id}", response_model=RecognitionLogResponse)
async def get_log(
    log_id: str,
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """Get a specific recognition log by ID."""
    log = await controller.get_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@router.get("/logs", response_model=dict)
async def get_all_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """Get all recognition logs with pagination."""
    return await controller.get_logs(skip=skip, limit=limit)


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
    """Filter recognition logs by person, camera, and date range."""
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    return await controller.get_logs(person_name, camera_id, start_dt, end_dt, skip, limit)


@router.put("/logs/{log_id}", response_model=dict)
async def update_log(
    log_id: str,
    data: RecognitionLogUpdate,
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """Update a recognition log."""
    return await controller.update_log(log_id, data.person_name, data.camera_id, data.confidence_score)


@router.delete("/logs/{log_id}", response_model=dict)
async def delete_log(
    log_id: str,
    _: str = Depends(require_api_key),
    controller: RecognitionController = Depends(get_recognition_controller)
):
    """Delete a recognition log."""
    return await controller.delete_log(log_id)


# Batch Recognition Endpoints
@router.post("/batch/process", response_model=BatchRecognitionResponse)
async def process_batch(
    data: BatchRecognitionRequest,
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_controller)
):
    """Process an image for face recognition."""
    return await controller.process_image(data.image_path)


@router.get("/batch/{batch_id}", response_model=dict)
async def get_batch_results(
    batch_id: str,
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_controller)
):
    """Get results for a specific batch."""
    result = await controller.get_batch_results(batch_id)
    if not result:
        raise HTTPException(status_code=404, detail="Batch not found")
    return result


@router.get("/batches", response_model=dict)
async def get_all_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_controller)
):
    """Get all batch recognition summaries."""
    batches = await controller.get_all_batches(skip, limit)
    return {"success": True, "batches": batches, "count": len(batches)}


@router.delete("/batches", response_model=dict)
async def delete_all_batches(
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_controller)
):
    """Delete ALL batch recognition logs."""
    return await controller.delete_all()


# Add Persons Endpoints
@router.post("/persons/add", response_model=dict)
async def add_persons(
    data: AddPersonsRequest = None,
    _: str = Depends(require_api_key),
    controller: AddPersonsController = Depends(get_add_persons_controller)
):
    """Add new persons to the face recognition database."""
    source_path = data.source_path if data else None
    move_to_backup = data.move_to_backup if data else True
    return controller.add_persons(source_path, move_to_backup)


@router.get("/persons", response_model=dict)
async def get_known_persons(
    _: str = Depends(require_api_key),
    controller: AddPersonsController = Depends(get_add_persons_controller)
):
    """Get list of all known persons in the database."""
    return controller.get_known_persons()
