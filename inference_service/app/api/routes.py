"""Inference API Routes

All inference endpoints exposed by the microservice.
Images are received as base64-encoded strings in JSON payloads.
"""
import asyncio
import base64
import logging
import time
import numpy as np
import cv2
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    DetectionRequest, DetectionResponse,
    RecognitionRequest, RecognitionResponse, RecognizedFace,
    EmbeddingRequest, EmbeddingResponse,
    TrainRequest, TrainResponse,
    ReloadResponse,
    KnownPersonsResponse,
    HealthResponse,
)
from app.schemas.inference import DetectedFace, BoundingBox, Landmark
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Helpers
# =============================================================================

def _decode_image(b64_string: str) -> np.ndarray:
    """Decode a base64 string to an OpenCV BGR image."""
    try:
        img_bytes = base64.b64decode(b64_string)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("cv2.imdecode returned None")
        return image
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image data: {e}",
        )


# =============================================================================
# Health
# =============================================================================

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check — reports loaded model types."""
    from app.services.detector import get_detector_type
    from app.services.recognizer import get_recognizer_type

    det_type = get_detector_type()
    rec_type = get_recognizer_type()

    return HealthResponse(
        status="healthy",
        models_loaded=bool(det_type and rec_type),
        detector_type=det_type,
        recognizer_type=rec_type,
    )


# =============================================================================
# Detection
# =============================================================================

@router.post("/detect", response_model=DetectionResponse, tags=["Detection"])
async def detect_faces(request: DetectionRequest):
    """Detect faces in an image. Returns bounding boxes and landmarks."""
    from app.services.detector import detect_faces as _detect, preprocess_image

    image = _decode_image(request.image)

    def _run():
        preprocessed = preprocess_image(image)
        bboxes, landmarks = _detect(preprocessed)
        return bboxes, landmarks

    bboxes, landmarks = await asyncio.to_thread(_run)

    faces = []
    for i, bbox in enumerate(bboxes):
        x1, y1, x2, y2, score = bbox[:5]
        lmk = landmarks[i].tolist() if i < len(landmarks) else []
        faces.append(DetectedFace(
            bbox=BoundingBox(
                x_min=int(x1), y_min=int(y1),
                x_max=int(x2), y_max=int(y2),
                score=float(score),
            ),
            landmark=Landmark(points=lmk),
        ))

    return DetectionResponse(faces=faces, total_faces=len(faces))


# =============================================================================
# Recognition (full pipeline)
# =============================================================================

@router.post("/recognize", response_model=RecognitionResponse, tags=["Recognition"])
async def recognize_faces(request: RecognitionRequest):
    """Full recognition pipeline: detect → align → embed → match.

    Returns recognized faces with names and confidence scores.
    """
    from app.services.detector import detect_faces as _detect, preprocess_image
    from app.services.recognizer import (
        get_face_embedding, compare_embeddings, align_face,
    )
    from app.services.feature_store import get_features

    settings = get_settings()
    threshold = request.confidence_threshold or settings.CONFIDENCE_THRESHOLD
    image = _decode_image(request.image)

    def _run():
        start = time.time()

        # Keep original for recognition (preprocessing may alter appearance)
        original_image = image.copy()

        # Preprocess for detection
        preprocessed = preprocess_image(image)

        # Scale factors for mapping landmarks back to original
        orig_h, orig_w = original_image.shape[:2]
        prep_h, prep_w = preprocessed.shape[:2]
        scale_x = prep_w / orig_w
        scale_y = prep_h / orig_h

        # Detect
        bboxes, landmarks = _detect(preprocessed)
        total_faces = len(bboxes)

        # Load gallery
        gallery_names, gallery_embs = get_features()

        results = []
        for bbox, landmark in zip(bboxes, landmarks):
            bbox = np.squeeze(bbox)
            if len(bbox) < 4:
                continue

            x_min, y_min, x_max, y_max = bbox[:4].astype(int)

            # Scale landmark back to original coordinates
            lmk_original = landmark.copy()
            lmk_original[:, 0] = landmark[:, 0] / scale_x
            lmk_original[:, 1] = landmark[:, 1] / scale_y

            # Align face from original image
            face_aligned = align_face(original_image, lmk_original)

            # Skip if no gallery
            if gallery_names is None or gallery_embs is None or len(gallery_names) == 0:
                continue

            # Embed + match
            emb = get_face_embedding(face_aligned)
            score, best_idx = compare_embeddings(emb, gallery_embs)
            name = gallery_names[best_idx]

            if score >= threshold:
                logger.info(f"✓ RECOGNIZED: {name} (score: {score:.3f})")
                results.append(RecognizedFace(
                    person_name=str(name),
                    confidence_score=round(float(score), 4),
                    face_location={
                        "x_min": int(x_min), "y_min": int(y_min),
                        "x_max": int(x_max), "y_max": int(y_max),
                    },
                ))
            else:
                logger.warning(
                    f"✗ BELOW THRESHOLD: {name} (score: {score:.3f}, "
                    f"threshold: {threshold})"
                )

        elapsed_ms = (time.time() - start) * 1000
        return results, total_faces, elapsed_ms

    results, total_faces, elapsed_ms = await asyncio.to_thread(_run)

    return RecognitionResponse(
        results=results,
        total_faces_detected=total_faces,
        processing_time_ms=round(elapsed_ms, 2),
    )


# =============================================================================
# Embedding
# =============================================================================

@router.post("/embed", response_model=EmbeddingResponse, tags=["Embedding"])
async def extract_embedding(request: EmbeddingRequest):
    """Extract face embedding from an aligned face image."""
    from app.services.recognizer import get_face_embedding

    face_image = _decode_image(request.face_image)

    def _run():
        return get_face_embedding(face_image)

    embedding = await asyncio.to_thread(_run)

    return EmbeddingResponse(embedding=embedding.tolist())


# =============================================================================
# Training
# =============================================================================

@router.post("/train", response_model=TrainResponse, tags=["Training"])
async def train_persons(request: TrainRequest):
    """Add new persons to the feature store.

    Accepts a dict of person_id → list of base64 images.
    Detects faces, extracts embeddings, and appends to .npz gallery.
    """
    from app.services.feature_store import add_persons

    # Decode all images
    persons_images = {}
    for person_id, b64_images in request.images.items():
        decoded = []
        for b64 in b64_images:
            decoded.append(_decode_image(b64))
        persons_images[person_id] = decoded

    def _run():
        return add_persons(
            persons_images=persons_images,
            move_to_backup=request.move_to_backup,
        )

    result = await asyncio.to_thread(_run)

    return TrainResponse(**result)


# =============================================================================
# Feature Store Management
# =============================================================================

@router.post("/features/reload", response_model=ReloadResponse, tags=["Features"])
async def reload_features():
    """Reload the feature store from disk (e.g. after external training)."""
    from app.services.feature_store import reload_features as _reload

    persons_count, embeddings_count = await asyncio.to_thread(_reload)

    return ReloadResponse(
        status="ok",
        persons_count=persons_count,
        embeddings_count=embeddings_count,
    )


@router.get("/features/list", response_model=KnownPersonsResponse, tags=["Features"])
async def list_known_persons():
    """List all known person IDs in the feature store."""
    from app.services.feature_store import list_known_persons as _list

    persons = _list()
    return KnownPersonsResponse(persons=persons, count=len(persons))
