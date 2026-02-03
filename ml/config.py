"""ML Configuration - Single Source of Truth for Model Selection

Change detection/recognition models HERE. All services will use these settings.
"""
import os

# =============================================================================
# DETECTION MODEL
# =============================================================================
# Options: "scrfd", "yolov12"
# - scrfd: Faster, lighter, good for real-time
# - yolov12: More accurate, detects more faces in group photos
DETECTION_MODEL = "yolov12"


# =============================================================================
# RECOGNITION MODEL
# =============================================================================
# Options: "arcface", "adaface"
# - arcface: Fast, reliable, good all-around performance
# - adaface: Quality-adaptive, better for varying image quality
# IMPORTANT: When changing this, you must regenerate training features!
# Use: POST /api/v1/recognition/persons/add to re-add all persons
RECOGNITION_MODEL = "adaface"


# =============================================================================
# PREPROCESSING SETTINGS
# =============================================================================
ENABLE_PREPROCESSING = True  # Master switch for image preprocessing
MIN_IMAGE_WIDTH = 1920  # Upscale if width is smaller
ENABLE_UPSCALING = True  # Enable upscaling for small images
ENABLE_CLAHE = False  # DISABLED - causes false positives


# =============================================================================
# RECOGNITION SETTINGS
# =============================================================================
CONFIDENCE_THRESHOLD = 0.4  # Minimum similarity score to consider a match


# =============================================================================
# PATHS
# =============================================================================
# ml/config.py is at CompVisn/ml/config.py, so one dirname gets us to CompVisn
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURE_PATH = os.path.join(PROJECT_ROOT, "datasets", "face_features", "feature")
