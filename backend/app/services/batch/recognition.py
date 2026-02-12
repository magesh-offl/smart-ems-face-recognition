"""Batch Recognition Service with Face Detection and Recognition"""
import asyncio
import os
import sys
import time
from typing import List, Dict, Any, Optional, Tuple

from app.core.interfaces.services import IBatchRecognitionService
from app.repositories.batch_recognition import BatchRecognitionRepository
from app.models import BatchRecognitionLogDocument
from app.utils.logger import setup_logger

# Import centralized configuration
from ml.config import (
    DETECTION_MODEL,
    RECOGNITION_MODEL,
    CONFIDENCE_THRESHOLD,
    ENABLE_PREPROCESSING,
    MIN_IMAGE_WIDTH,
    ENABLE_UPSCALING,
    ENABLE_CLAHE,
    PROJECT_ROOT
)

logger = setup_logger(__name__)

# Lazy-loaded models (initialized on first use)
_detector = None
_recognizer = None
_images_names = None
_images_embs = None
_device = None

# CLAHE settings (used only if ENABLE_CLAHE is True)
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_SIZE = (8, 8)


def _preprocess_image(image):
    """
    Preprocess image for better face detection.
    
    1. Upscale if image is too small (helps detect small faces in group photos)
    2. Apply CLAHE contrast enhancement (improves visibility in dark/bright areas)
    
    Args:
        image: OpenCV image (BGR)
    
    Returns:
        Preprocessed image
    """
    # Master switch - skip all preprocessing if disabled
    if not ENABLE_PREPROCESSING:
        logger.info("Preprocessing disabled - using original image")
        return image
    
    import cv2
    
    original_shape = image.shape
    height, width = image.shape[:2]
    
    # 1. Upscale if image width is below minimum
    if ENABLE_UPSCALING and width < MIN_IMAGE_WIDTH:
        scale_factor = MIN_IMAGE_WIDTH / width
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        logger.info(f"Upscaled image from {width}x{height} to {new_width}x{new_height}")
    
    # 2. Apply CLAHE contrast enhancement
    if ENABLE_CLAHE:
        # Convert to LAB color space (L = lightness, A & B = color)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Apply CLAHE to L channel only
        clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_SIZE)
        l_enhanced = clahe.apply(l_channel)
        
        # Merge channels back
        lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
        image = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        logger.info("Applied CLAHE contrast enhancement")
    
    return image

def _get_device():
    """Get torch device from factory"""
    from ml.factory import get_device
    return get_device()


def _get_detector():
    """Get face detector from factory"""
    from ml.factory import get_detector
    return get_detector()


def _get_recognizer():
    """Get face recognizer from factory"""
    from ml.factory import get_recognizer
    return get_recognizer()


def _get_features():
    """Load pre-computed face features from factory"""
    from ml.factory import get_features
    return get_features()


def _get_face_embedding(face_image) -> Any:
    """Extract features from a face image using factory"""
    from ml.factory import get_face_embedding
    return get_face_embedding(face_image)


def _recognize_face(face_image) -> Tuple[float, str]:
    """
    Recognize a face image against stored features.
    Returns (confidence_score, person_name)
    """
    from ml.factory import compare_embeddings
    
    query_emb = _get_face_embedding(face_image)
    images_names, images_embs = _get_features()
    
    # Guard: No trained data available
    if images_names is None or images_embs is None or len(images_names) == 0:
        return 0.0, "unknown"
    
    score, best_idx = compare_embeddings(query_emb, images_embs)
    name = images_names[best_idx]
    
    return score, name


class BatchRecognitionService(IBatchRecognitionService):
    """
    Service for batch face recognition from images.
    Implements IBatchRecognitionService interface.
    Accepts repository via constructor for dependency injection.
    """
    
    def __init__(self, repository: BatchRecognitionRepository):
        """
        Initialize batch recognition service with injected repository.
        
        Args:
            repository: BatchRecognitionRepository instance (injected)
        """
        self.repo = repository
    
    def _process_image_sync(self, image_path: str) -> Dict[str, Any]:
        """
        Synchronous CPU-bound face detection and recognition.
        This runs in a thread pool to avoid blocking the async event loop.
        """
        import cv2
        import numpy as np
        
        start_time = time.time()
        
        # Validate image path
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Keep original for recognition (CLAHE changes appearance = wrong embeddings)
        original_image = image.copy()
        
        # Preprocess image for better detection (upscale + contrast enhancement)
        preprocessed_image = _preprocess_image(image)
        
        # Calculate scale factor if image was upscaled (need to map landmarks back)
        orig_height, orig_width = original_image.shape[:2]
        prep_height, prep_width = preprocessed_image.shape[:2]
        scale_x = prep_width / orig_width
        scale_y = prep_height / orig_height
        
        # Generate batch ID
        batch_id = BatchRecognitionLogDocument.generate_batch_id()
        
        # Detect faces on preprocessed image
        detector = _get_detector()
        detection_results = detector.detect(image=preprocessed_image)
        
        results = []
        total_faces = 0
        
        if detection_results is not None:
            bboxes, landmarks = detection_results
            total_faces = len(bboxes)
            
            # Import alignment function
            from ml.alignment.alignment import norm_crop
            
            for bbox, landmark in zip(bboxes, landmarks):
                bbox = np.squeeze(bbox)
                if len(bbox) >= 4:
                    x_min, y_min, x_max, y_max = bbox[:4].astype(int)
                    
                    # Scale landmark back to original image coordinates
                    landmark_original = landmark.copy()
                    landmark_original[:, 0] = landmark[:, 0] / scale_x
                    landmark_original[:, 1] = landmark[:, 1] / scale_y
                    
                    # Align face from ORIGINAL image (not preprocessed!)
                    face_aligned = norm_crop(img=original_image, landmark=landmark_original)
                    
                    # Recognize
                    score, name = _recognize_face(face_aligned)
                    
                    # Log ALL faces for debugging (even below threshold)
                    face_info = f"Face {len(results)+1}: {name} (score: {score:.3f})"
                    if score >= CONFIDENCE_THRESHOLD:
                        logger.info(f"✓ RECOGNIZED - {face_info}")
                    else:
                        logger.warning(f"✗ BELOW THRESHOLD - {face_info} (threshold: {CONFIDENCE_THRESHOLD})")
                    
                    # Only save if confidence >= threshold
                    if score >= CONFIDENCE_THRESHOLD:
                        face_location = {
                            "x_min": int(x_min),
                            "y_min": int(y_min),
                            "x_max": int(x_max),
                            "y_max": int(y_max)
                        }
                        
                        results.append({
                            "person_name": name,
                            "confidence_score": score,
                            "face_location": face_location
                        })
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Processed image {image_path}: {total_faces} faces detected, "
            f"{len(results)} recognized in {processing_time_ms:.2f}ms"
        )
        
        return {
            "batch_id": batch_id,
            "total_faces": total_faces,
            "results": results,
            "processing_time_ms": processing_time_ms,
            "image_path": image_path
        }
    
    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image for face recognition.
        Offloads CPU-bound ML work to a thread pool so other requests aren't blocked.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with batch_id, results, and metadata
        """
        # Run CPU-bound ML work in a thread pool to not block the event loop
        sync_result = await asyncio.to_thread(self._process_image_sync, image_path)
        
        batch_id = sync_result["batch_id"]
        total_faces = sync_result["total_faces"]
        results = sync_result["results"]
        processing_time_ms = sync_result["processing_time_ms"]
        
        # Create database documents (async DB operations stay on event loop)
        documents = []
        for result in results:
            # person_name from npz is now admission_id
            admission_id = result["person_name"]
            doc = BatchRecognitionLogDocument.create(
                student_id=admission_id,  # Will be enriched later with actual student_id
                admission_id=admission_id,
                confidence_score=result["confidence_score"],
                source_path=image_path,
                face_location=result["face_location"],
                batch_id=batch_id,
                total_faces_detected=total_faces,
                processing_time_ms=processing_time_ms
            )
            documents.append(doc)
        
        # Save to database (async)
        if documents:
            inserted_ids = await self.repo.save_batch_logs(documents)
            for i, result in enumerate(results):
                result["_id"] = inserted_ids[i]
        
        return {
            "batch_id": batch_id,
            "source_path": image_path,
            "total_faces_detected": total_faces,
            "recognized_faces": len(results),
            "processing_time_ms": processing_time_ms,
            "results": results
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
            "message": f"Deleted {deleted_count} batch recognition logs"
        }

