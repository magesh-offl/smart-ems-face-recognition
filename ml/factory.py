"""ML Model Factory - Provides detector and recognizer instances

Use these functions to get model instances. They respect the settings in config.py.
"""
import os
import numpy as np
import torch
from typing import Optional, Tuple, Any
from torchvision import transforms

from .config import (
    DETECTION_MODEL, 
    RECOGNITION_MODEL, 
    PROJECT_ROOT,
    FEATURE_PATH
)

# Logger
from app.utils.logger import setup_logger
logger = setup_logger(__name__)

# Lazy-loaded model instances
_detector = None
_recognizer = None
_device = None
_images_names = None
_images_embs = None


def get_device() -> torch.device:
    """Get torch device (GPU if available, else CPU)"""
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {_device}")
    return _device


def get_detector():
    """
    Get face detector based on DETECTION_MODEL config.
    
    Returns:
        Detector with .detect() method that returns (bboxes, landmarks)
    """
    global _detector
    if _detector is None:
        if DETECTION_MODEL == "yolov12":
            try:
                from ml.detection.yolov12.detector import YOLOv12FaceDetector
                _detector = YOLOv12FaceDetector()
                logger.info("YOLOv12 face detector loaded")
            except (ImportError, FileNotFoundError) as e:
                logger.warning(f"YOLOv12 unavailable ({e}), falling back to SCRFD")
                from ml.detection.scrfd.detector import SCRFD
                model_path = os.path.join(PROJECT_ROOT, "ml/detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")
                _detector = SCRFD(model_file=model_path)
                logger.info("SCRFD face detector loaded (fallback)")
        else:
            # Default: SCRFD
            from ml.detection.scrfd.detector import SCRFD
            model_path = os.path.join(PROJECT_ROOT, "ml/detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")
            _detector = SCRFD(model_file=model_path)
            logger.info("SCRFD face detector loaded")
    return _detector


def get_recognizer():
    """
    Get face recognizer based on RECOGNITION_MODEL config.
    
    Returns:
        Recognizer callable that takes face tensor and returns embeddings
    """
    global _recognizer
    if _recognizer is None:
        if RECOGNITION_MODEL == "adaface":
            try:
                from ml.recognition.adaface.model import AdaFaceRecognizer
                _recognizer = AdaFaceRecognizer(device=get_device())
                logger.info("AdaFace recognizer loaded")
            except (ImportError, FileNotFoundError) as e:
                logger.warning(f"AdaFace unavailable ({e}), falling back to ArcFace")
                from ml.recognition.arcface.model import iresnet_inference
                model_path = os.path.join(PROJECT_ROOT, "ml/recognition/arcface/weights/arcface_r100.pth")
                _recognizer = iresnet_inference(model_name="r100", path=model_path, device=get_device())
                logger.info("ArcFace recognizer loaded (fallback)")
        else:
            # Default: ArcFace
            from ml.recognition.arcface.model import iresnet_inference
            model_path = os.path.join(PROJECT_ROOT, "ml/recognition/arcface/weights/arcface_r100.pth")
            _recognizer = iresnet_inference(model_name="r100", path=model_path, device=get_device())
            logger.info("ArcFace recognizer loaded")
    return _recognizer


def get_face_embedding(face_image: np.ndarray) -> np.ndarray:
    """
    Extract face embedding from aligned face image.
    
    Args:
        face_image: Aligned face image (BGR, typically 112x112)
        
    Returns:
        512-dimensional normalized embedding
    """
    recognizer = get_recognizer()
    device = get_device()
    
    # Preprocessing
    face_preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((112, 112)),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])
    
    face_tensor = face_preprocess(face_image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        embedding = recognizer(face_tensor)
        
        # Handle tuple return (AdaFace returns (output, norm))
        if isinstance(embedding, tuple):
            embedding = embedding[0]
        
        embedding = embedding.cpu().numpy()
    
    # Normalize
    embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)
    
    return embedding[0]


def get_features() -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Load pre-computed face features for recognition.
    
    Returns:
        (images_names, images_embeddings) or (None, None) if not found
    """
    global _images_names, _images_embs
    if _images_names is None or _images_embs is None:
        try:
            data = np.load(FEATURE_PATH + ".npz", allow_pickle=True)
            _images_names = data["images_name"]
            _images_embs = data["images_emb"]
            logger.info(f"Loaded {len(_images_names)} face features")
        except Exception as e:
            logger.error(f"Failed to load features: {e}")
            return None, None
    return _images_names, _images_embs


def reload_features():
    """Force reload of face features (after adding new persons)"""
    global _images_names, _images_embs
    _images_names = None
    _images_embs = None
    return get_features()


def compare_embeddings(query_emb: np.ndarray, gallery_embs: np.ndarray) -> Tuple[float, int]:
    """
    Compare query embedding against gallery.
    
    Args:
        query_emb: Query face embedding (512,)
        gallery_embs: Gallery embeddings (N, 512)
        
    Returns:
        (best_score, best_index)
    """
    sims = np.dot(gallery_embs, query_emb.T)
    best_idx = np.argmax(sims)
    best_score = sims[best_idx]
    return float(best_score), int(best_idx)
