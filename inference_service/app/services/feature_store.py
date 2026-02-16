"""Feature Store Service — Manages face embeddings gallery.

Loads and saves feature vectors (.npz) for face recognition.
Handles adding new persons and reloading the gallery.

Thread-safety: All gallery mutations are serialized via _gallery_lock
so that concurrent training requests cannot corrupt the .npz file.
The heavy ML work (detection, alignment, embedding) runs outside the lock.
"""
import os
import logging
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple

from app.config import get_settings

logger = logging.getLogger(__name__)

# Lazy-loaded gallery (protected by _gallery_lock)
_gallery_names: Optional[np.ndarray] = None
_gallery_embs: Optional[np.ndarray] = None
_gallery_lock = threading.Lock()


def get_features() -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Get the currently loaded gallery features.

    Returns:
        (names, embeddings)
    """
    with _gallery_lock:
        global _gallery_names, _gallery_embs

        if _gallery_names is None:
            _reload_features_unlocked()

        return _gallery_names, _gallery_embs


def reload_features() -> Tuple[int, int]:
    """Reload features from disk (.npz file).

    Returns:
        (num_persons, num_embeddings)
    """
    with _gallery_lock:
        return _reload_features_unlocked()


def _reload_features_unlocked() -> Tuple[int, int]:
    """Internal reload — caller must hold _gallery_lock."""
    global _gallery_names, _gallery_embs

    settings = get_settings()
    feature_dir = settings.FEATURE_PATH
    npz_path = os.path.join(feature_dir, "features.npz")

    if not os.path.isfile(npz_path):
        logger.warning(f"Feature file not found: {npz_path}")
        _gallery_names = None
        _gallery_embs = None
        return 0, 0

    try:
        data = np.load(npz_path, allow_pickle=True)
        _gallery_names = data["names"]
        _gallery_embs = data["encodings"]
        num_persons = len(set(_gallery_names.tolist()))
        num_embeddings = len(_gallery_names)
        logger.info(f"Reloaded features: {num_persons} persons, {num_embeddings} embeddings")
        return num_persons, num_embeddings
    except Exception as e:
        logger.error(f"Failed to reload features: {e}")
        _gallery_names = None
        _gallery_embs = None
        return 0, 0


def list_known_persons() -> List[str]:
    """List all unique person IDs in the gallery."""
    with _gallery_lock:
        global _gallery_names

        if _gallery_names is None:
            _reload_features_unlocked()

        if _gallery_names is None:
            return []

        return sorted(set(_gallery_names.tolist()))


def add_persons(
    persons_images: Dict[str, List[np.ndarray]],
    move_to_backup: bool = True,
) -> dict:
    """Add new persons to the gallery.

    Thread-safe: ML processing runs without the lock (parallel),
    only the final gallery merge + save acquires the lock (serialized).

    Args:
        persons_images: Dict mapping person_id -> list of BGR images
        move_to_backup: Whether to backup original images (backend handles this)

    Returns:
        Dict with success, persons_added, faces_processed
    """
    from app.services.detector import detect_faces, preprocess_image
    from app.services.recognizer import get_face_embedding, align_face

    settings = get_settings()
    feature_dir = settings.FEATURE_PATH
    os.makedirs(feature_dir, exist_ok=True)

    # ── ML processing (runs in parallel, no lock needed) ─────────────
    new_names = []
    new_embeddings = []
    failed_count = 0

    for person_id, images in persons_images.items():
        for img in images:
            try:
                preprocessed = preprocess_image(img)
                bboxes, landmarks = detect_faces(preprocessed)

                if len(bboxes) == 0:
                    logger.warning(f"No face detected for {person_id}")
                    failed_count += 1
                    continue

                # Use the first (largest/most confident) face
                # Scale landmarks back to original coordinates
                orig_h, orig_w = img.shape[:2]
                prep_h, prep_w = preprocessed.shape[:2]
                scale_x = prep_w / orig_w
                scale_y = prep_h / orig_h

                lmk = landmarks[0].copy()
                lmk[:, 0] = landmarks[0][:, 0] / scale_x
                lmk[:, 1] = landmarks[0][:, 1] / scale_y

                face_aligned = align_face(img, lmk)
                embedding = get_face_embedding(face_aligned)

                new_names.append(person_id)
                new_embeddings.append(embedding)

            except Exception as e:
                logger.error(f"Error processing image for {person_id}: {e}")
                failed_count += 1

    # ── Gallery merge + save (serialized via lock) ───────────────────
    if new_names:
        new_names_arr = np.array(new_names)
        new_embs_arr = np.array(new_embeddings)

        with _gallery_lock:
            global _gallery_names, _gallery_embs

            # Re-read current gallery state under the lock
            if _gallery_names is not None and len(_gallery_names) > 0:
                all_names = np.concatenate([_gallery_names, new_names_arr])
                all_embs = np.concatenate([_gallery_embs, new_embs_arr])
            else:
                all_names = new_names_arr
                all_embs = new_embs_arr

            # Save to disk
            npz_path = os.path.join(feature_dir, "features.npz")
            np.savez(npz_path, names=all_names, encodings=all_embs)

            # Update in-memory gallery
            _gallery_names = all_names
            _gallery_embs = all_embs

            logger.info(f"Added {len(new_names)} new embeddings. Total: {len(all_names)}")

    # Unique person IDs that were successfully added
    persons_added = sorted(set(new_names))

    return {
        "success": len(new_names) > 0,
        "message": f"Added {len(new_names)} embeddings for {len(persons_added)} persons. "
                   f"Failed: {failed_count}. Total gallery: "
                   f"{len(_gallery_names) if _gallery_names is not None else 0}",
        "persons_added": persons_added,
        "faces_processed": len(new_names),
    }
