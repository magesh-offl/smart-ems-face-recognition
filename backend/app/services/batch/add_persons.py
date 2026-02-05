"""Add Persons Service - Add new persons to face recognition database"""
import os
import shutil
from typing import Dict, Any, List, Optional

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Project root (CompVisn/) - go up from app/services/batch/add_persons.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Default paths
DEFAULT_NEW_PERSONS_DIR = os.path.join(PROJECT_ROOT, "datasets/new_persons")
DEFAULT_FACES_DIR = os.path.join(PROJECT_ROOT, "datasets/data")
DEFAULT_FEATURES_PATH = os.path.join(PROJECT_ROOT, "datasets/face_features/feature")
DEFAULT_BACKUP_DIR = os.path.join(PROJECT_ROOT, "datasets/backup")


# Use centralized factory for ML components
def _get_detector():
    """Get face detector from factory"""
    from ml.factory import get_detector
    return get_detector()


def _get_feature(face_image):
    """Extract facial features using centralized factory"""
    from ml.factory import get_face_embedding
    return get_face_embedding(face_image)


class AddPersonsService:
    """Service for adding new persons to the face recognition database"""
    
    def __init__(self):
        self.new_persons_dir = DEFAULT_NEW_PERSONS_DIR
        self.faces_dir = DEFAULT_FACES_DIR
        self.features_path = DEFAULT_FEATURES_PATH
        self.backup_dir = DEFAULT_BACKUP_DIR
    
    def add_persons_from_folder(
        self, 
        source_path: Optional[str] = None,
        move_to_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Add persons from a folder to the face recognition database.
        
        Args:
            source_path: Path to folder containing person subfolders.
                        Each subfolder name = person name, contains their photos.
                        Defaults to datasets/new_persons/
            move_to_backup: Whether to move processed folders to backup
        
        Returns:
            Dict with success status, persons added, and face count
        """
        import cv2
        import numpy as np
        from ml.recognition.arcface.utils import read_features
        
        # Use default path if not provided
        source_dir = source_path or self.new_persons_dir
        
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        
        # Check if directory has any person folders
        person_folders = [
            d for d in os.listdir(source_dir) 
            if os.path.isdir(os.path.join(source_dir, d))
        ]
        
        if not person_folders:
            return {
                "success": False,
                "message": "No person folders found in source directory",
                "persons_added": [],
                "faces_processed": 0
            }
        
        # Initialize lists for new features
        images_name = []
        images_emb = []
        persons_added = set()
        
        detector = _get_detector()
        
        # Process each person folder
        for person_name in person_folders:
            person_path = os.path.join(source_dir, person_name)
            person_faces_dir = os.path.join(self.faces_dir, person_name)
            os.makedirs(person_faces_dir, exist_ok=True)
            
            # Get all images in person folder
            image_files = [
                f for f in os.listdir(person_path)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ]
            
            for image_file in image_files:
                image_path = os.path.join(person_path, image_file)
                image = cv2.imread(image_path)
                
                if image is None:
                    logger.warning(f"Could not read image: {image_path}")
                    continue
                
                # Detect faces
                bboxes, landmarks = detector.detect(image=image)
                
                for i, bbox in enumerate(bboxes):
                    x1, y1, x2, y2, score = bbox
                    face_image = image[int(y1):int(y2), int(x1):int(x2)]
                    
                    if face_image.size == 0:
                        continue
                    
                    # Save face
                    face_count = len(os.listdir(person_faces_dir))
                    face_path = os.path.join(person_faces_dir, f"{face_count}.jpg")
                    cv2.imwrite(face_path, face_image)
                    
                    # Extract features
                    emb = _get_feature(face_image)
                    images_emb.append(emb)
                    images_name.append(person_name)
                    persons_added.add(person_name)
                    
                    logger.info(f"Processed face for {person_name}: {face_path}")
        
        if not images_emb:
            return {
                "success": False,
                "message": "No faces detected in any images",
                "persons_added": [],
                "faces_processed": 0
            }
        
        # Convert to arrays
        images_emb = np.array(images_emb)
        images_name = np.array(images_name)
        
        # Read existing features and merge
        existing = read_features(self.features_path)
        if existing is not None:
            old_names, old_embs = existing
            images_name = np.hstack((old_names, images_name))
            images_emb = np.vstack((old_embs, images_emb))
            logger.info("Merged with existing features")
        
        # Save updated features
        os.makedirs(os.path.dirname(self.features_path), exist_ok=True)
        np.savez_compressed(
            self.features_path,
            images_name=images_name,
            images_emb=images_emb
        )
        
        # Move processed folders to backup
        if move_to_backup:
            os.makedirs(self.backup_dir, exist_ok=True)
            for person_name in persons_added:
                src = os.path.join(source_dir, person_name)
                dst = os.path.join(self.backup_dir, person_name)
                if os.path.exists(src):
                    if os.path.exists(dst):
                        # Merge: Move files into existing backup folder
                        for file in os.listdir(src):
                            src_file = os.path.join(src, file)
                            dst_file = os.path.join(dst, file)
                            # Add timestamp to avoid overwriting existing files
                            if os.path.exists(dst_file):
                                import time
                                name, ext = os.path.splitext(file)
                                timestamp = int(time.time())
                                dst_file = os.path.join(dst, f"{name}_{timestamp}{ext}")
                            shutil.move(src_file, dst_file)
                        # Remove empty source folder
                        os.rmdir(src)
                        logger.info(f"Merged {person_name} into existing backup")
                    else:
                        shutil.move(src, dst)
                        logger.info(f"Moved {person_name} to backup")
        
        return {
            "success": True,
            "message": f"Successfully added {len(persons_added)} person(s)",
            "persons_added": list(persons_added),
            "faces_processed": len(images_emb) if existing is None else len(images_emb) - len(existing[0])
        }
    
    def list_known_persons(self) -> List[str]:
        """Get list of all known persons in the database"""
        from ml.recognition.arcface.utils import read_features
        
        features = read_features(self.features_path)
        if features is None:
            return []
        
        names, _ = features
        return list(set(names.tolist()))
