"""Add Persons Service — delegates face training to the inference microservice.

Reads person images from the filesystem, sends them to the inference service
for detection and embedding extraction, and manages backup of processed images.

File I/O (reading images, listing folders, backup) remains in the backend.
ML work (detection, embedding) is delegated entirely to the inference service.
"""
import os
from typing import Dict, Any, List, Optional

from app.core.inference_client import InferenceClient
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Project root (CompVisn/backend/) - go up from app/services/batch/add_persons.py
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Default paths
DEFAULT_NEW_PERSONS_DIR = os.path.join(PROJECT_ROOT, "datasets/new_persons")
DEFAULT_FACES_DIR = os.path.join(PROJECT_ROOT, "datasets/data")
DEFAULT_FEATURES_PATH = os.path.join(PROJECT_ROOT, "datasets/face_features")
DEFAULT_BACKUP_DIR = os.path.join(PROJECT_ROOT, "datasets/backup")

# Supported image extensions
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')


class AddPersonsService:
    """Service for adding new persons to the face recognition database.

    Reads images from the filesystem, sends them to the inference service
    for training, and handles backup of processed folders.
    """

    def __init__(self, inference_client: InferenceClient):
        self.inference = inference_client
        self.new_persons_dir = DEFAULT_NEW_PERSONS_DIR
        self.faces_dir = DEFAULT_FACES_DIR
        self.features_path = DEFAULT_FEATURES_PATH
        self.backup_dir = DEFAULT_BACKUP_DIR

    async def add_persons_from_folder(
        self,
        source_path: Optional[str] = None,
        move_to_backup: bool = True,
    ) -> Dict[str, Any]:
        """
        Add persons from a folder to the face recognition database.

        Reads images from person subfolders, sends them to the inference
        service for detection + embedding, and persists the results.

        Args:
            source_path: Path to folder containing person subfolders.
                        Each subfolder name = person_id, contains their photos.
                        Defaults to datasets/new_persons/
            move_to_backup: Whether to move processed folders to backup

        Returns:
            Dict with success status, persons added, and face count
        """
        source_dir = source_path or self.new_persons_dir

        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        # Discover person folders
        person_folders = [
            d for d in os.listdir(source_dir)
            if os.path.isdir(os.path.join(source_dir, d))
        ]

        if not person_folders:
            return {
                "success": False,
                "message": "No person folders found in source directory",
                "persons_added": [],
                "faces_processed": 0,
            }

        # Read all images per person into memory as bytes
        persons_images: Dict[str, List[bytes]] = {}
        for person_name in person_folders:
            person_path = os.path.join(source_dir, person_name)
            image_files = [
                f for f in os.listdir(person_path)
                if f.lower().endswith(IMAGE_EXTENSIONS)
            ]

            images_bytes = []
            for image_file in image_files:
                image_path = os.path.join(person_path, image_file)
                try:
                    with open(image_path, "rb") as f:
                        images_bytes.append(f.read())
                except Exception as e:
                    logger.warning(f"Could not read image {image_path}: {e}")

            if images_bytes:
                persons_images[person_name] = images_bytes
                logger.info(
                    f"Read {len(images_bytes)} images for {person_name}"
                )

        if not persons_images:
            return {
                "success": False,
                "message": "No valid images found in person folders",
                "persons_added": [],
                "faces_processed": 0,
            }

        # Delegate training to inference service
        result = await self.inference.train(
            persons_images=persons_images,
            move_to_backup=move_to_backup,
        )

        logger.info(
            f"Training complete: {result.get('message', '')} "
            f"({result.get('faces_processed', 0)} faces)"
        )

        return result

    async def list_known_persons(self) -> List[str]:
        """Get list of all known persons in the feature store."""
        return await self.inference.list_known_persons()
