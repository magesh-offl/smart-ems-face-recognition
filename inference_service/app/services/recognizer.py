"""Recognizer Service — wraps ML face recognition models.

Provides face embedding extraction and comparison via AdaFace (primary)
or ArcFace (fallback). Models are loaded lazily and cached for process lifetime.
"""
import os
import logging
import numpy as np
import torch
from typing import Tuple, Optional
from torchvision import transforms

from app.config import get_settings, PROJECT_ROOT

logger = logging.getLogger(__name__)

# Lazy-loaded instances
_recognizer = None
_recognizer_type: str = ""
_device = None


def get_device() -> torch.device:
    """Get torch device (GPU if available)."""
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {_device}")
    return _device


def get_recognizer_type() -> str:
    """Return the name of the currently loaded recognizer."""
    return _recognizer_type


def get_recognizer():
    """Get or create the face recognizer singleton."""
    global _recognizer, _recognizer_type
    if _recognizer is not None:
        return _recognizer

    settings = get_settings()
    model_name = settings.RECOGNITION_MODEL

    if model_name == "adaface":
        try:
            from ml.recognition.adaface.model import AdaFaceRecognizer
            _recognizer = AdaFaceRecognizer(device=get_device())
            _recognizer_type = "adaface"
            logger.info("Loaded AdaFace recognizer")
        except (ImportError, FileNotFoundError) as e:
            logger.warning(f"AdaFace unavailable ({e}), falling back to ArcFace")
            model_name = "arcface"

    if model_name != "adaface" or _recognizer is None:
        from ml.recognition.arcface.model import iresnet_inference
        model_path = os.path.join(
            PROJECT_ROOT, "ml", "recognition", "arcface", "weights", "arcface_r100.pth"
        )
        _recognizer = iresnet_inference(
            model_name="r100", path=model_path, device=get_device()
        )
        _recognizer_type = "arcface"
        logger.info("Loaded ArcFace recognizer")

    return _recognizer


def get_face_embedding(face_image: np.ndarray) -> np.ndarray:
    """Extract face embedding from an aligned face image.

    Args:
        face_image: Aligned face image (BGR, ideally 112x112).

    Returns:
        Normalized embedding vector (512-d).
    """
    recognizer = get_recognizer()
    device = get_device()

    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((112, 112)),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])

    face_tensor = preprocess(face_image).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = recognizer(face_tensor)
        if isinstance(embedding, tuple):
            embedding = embedding[0]
        embedding = embedding.cpu().numpy()

    return (embedding / np.linalg.norm(embedding, axis=1, keepdims=True))[0]


def compare_embeddings(
    query_emb: np.ndarray, gallery_embs: np.ndarray
) -> Tuple[float, int]:
    """Compare query embedding against a gallery of embeddings.

    Args:
        query_emb: 1-D embedding vector.
        gallery_embs: NxD gallery matrix.

    Returns:
        (best_score, best_index)
    """
    sims = np.dot(gallery_embs, query_emb.T)
    best_idx = int(np.argmax(sims))
    return float(sims[best_idx]), best_idx


def align_face(image: np.ndarray, landmark: np.ndarray) -> np.ndarray:
    """Align a face using 5-point landmarks (norm_crop).

    Args:
        image: Full BGR image.
        landmark: 5×2 array of landmark points.

    Returns:
        Aligned 112×112 face image.
    """
    from ml.alignment.alignment import norm_crop
    return norm_crop(img=image, landmark=landmark)
