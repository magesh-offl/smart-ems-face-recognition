"""Batch Recognition API Routes"""
from fastapi import APIRouter, Depends, Query

from app.controllers.batch import BatchRecognitionController, AddPersonsController
from app.core.dependencies import get_batch_recognition_service
from app.services.batch import AddPersonsService
from app.schemas import BatchRecognitionRequest, BatchRecognitionResponse, AddPersonsRequest
from app.middleware import require_api_key

router = APIRouter(prefix="/api/v1/batch", tags=["Batch Recognition"])


# Dependency Providers
def get_batch_controller(service=Depends(get_batch_recognition_service)) -> BatchRecognitionController:
    return BatchRecognitionController(service)


def get_add_persons_controller(service=Depends(AddPersonsService)) -> AddPersonsController:
    return AddPersonsController(service)


# Batch Recognition Endpoints
@router.post("/process", response_model=BatchRecognitionResponse)
async def process_batch(
    data: BatchRecognitionRequest,
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_controller)
):
    """Process an image for face recognition."""
    return controller.process_image(data.image_path)


@router.get("/{batch_id}", response_model=dict)
async def get_batch_results(
    batch_id: str,
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_controller)
):
    """Get results for a specific batch."""
    return controller.get_batch_results(batch_id)


@router.get("/", response_model=dict)
async def get_all_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_controller)
):
    """Get all batch recognition summaries."""
    return controller.get_all_batches(skip, limit)


@router.delete("/", response_model=dict)
async def delete_all_batches(
    _: str = Depends(require_api_key),
    controller: BatchRecognitionController = Depends(get_batch_controller)
):
    """Delete ALL batch recognition logs."""
    return controller.delete_all_batches()


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
    """Get list of all known persons."""
    return controller.get_known_persons()
