"""Batch Recognition Service — delegates ML inference to the inference microservice.

All face detection, alignment, embedding, and recognition are performed
by the inference service via HTTP. This service handles orchestration,
file I/O, and database persistence only.
"""
import os
import time
from typing import List, Dict, Any, Optional

from app.core.interfaces.services import IBatchRecognitionService
from app.repositories.batch_recognition import BatchRecognitionRepository
from app.models import BatchRecognitionLogDocument
from app.core.inference_client import InferenceClient
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class BatchRecognitionService(IBatchRecognitionService):
    """
    Service for batch face recognition from images.
    Implements IBatchRecognitionService interface.
    Delegates ML work to the inference microservice.
    """

    def __init__(
        self,
        repository: BatchRecognitionRepository,
        inference_client: InferenceClient,
    ):
        """
        Initialize batch recognition service.

        Args:
            repository: BatchRecognitionRepository instance (injected)
            inference_client: InferenceClient instance (injected)
        """
        self.repo = repository
        self.inference = inference_client

    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image for face recognition via the inference service.

        Reads the image file, sends it to the inference service for full
        recognition (detect → align → embed → match), then persists results.

        Args:
            image_path: Path to the image file

        Returns:
            Dict with batch_id, results, and metadata
        """
        start_time = time.time()

        # Validate image path
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Read image bytes
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        if not image_bytes:
            raise ValueError(f"Failed to read image: {image_path}")

        # Delegate to inference service (full pipeline)
        recognition_result = await self.inference.recognize(image_bytes)

        total_faces = recognition_result.get("total_faces_detected", 0)
        results = recognition_result.get("results", [])
        inference_time_ms = recognition_result.get("processing_time_ms", 0.0)

        # Generate batch ID
        batch_id = BatchRecognitionLogDocument.generate_batch_id()

        # Create database documents
        documents = []
        for result in results:
            admission_id = result["person_name"]
            doc = BatchRecognitionLogDocument.create(
                student_id=admission_id,
                admission_id=admission_id,
                confidence_score=result["confidence_score"],
                source_path=image_path,
                face_location=result["face_location"],
                batch_id=batch_id,
                total_faces_detected=total_faces,
                processing_time_ms=inference_time_ms,
            )
            documents.append(doc)

        # Save to database (async)
        if documents:
            inserted_ids = await self.repo.save_batch_logs(documents)
            for i, result in enumerate(results):
                result["_id"] = inserted_ids[i]

        total_time_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Processed image {image_path}: {total_faces} faces detected, "
            f"{len(results)} recognized in {total_time_ms:.2f}ms "
            f"(inference: {inference_time_ms:.2f}ms)"
        )

        return {
            "batch_id": batch_id,
            "source_path": image_path,
            "total_faces_detected": total_faces,
            "recognized_faces": len(results),
            "processing_time_ms": total_time_ms,
            "results": results,
        }

    async def get_batch_results(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific batch"""
        return await self.repo.get_batch_summary(batch_id)

    async def get_all_batches(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all batch summaries"""
        return await self.repo.get_all_batches(skip, limit)

    async def delete_all_batches(self) -> Dict[str, Any]:
        """Delete all batch recognition logs"""
        deleted_count = await self.repo.delete_all()
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} batch recognition logs",
        }
