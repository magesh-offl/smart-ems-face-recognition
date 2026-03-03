"""Feature Store Service — Manages face embeddings gallery.

Loads and saves feature vectors (.npz) for face recognition.
Handles adding new persons and reloading the gallery.

Multi-worker support (via Redis):
    • Gallery cache:  serialised numpy arrays stored in Redis so every
                      worker reads the same data.
    • Version counter: workers skip deserialisation when nothing changed.
    • Pub/Sub:         after training or reload, a message is published so
                       peer workers refresh their local cache.
    • Distributed lock: training acquires a Redis lock to prevent
                        concurrent .npz corruption across workers.

If Redis is unavailable the service degrades gracefully to
single-worker mode (process-local cache + threading.Lock).
"""
import io
import os
import logging
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── Process-local cache ─────────────────────────────────────────────────
_gallery_names: Optional[np.ndarray] = None
_gallery_embs: Optional[np.ndarray] = None
_gallery_lock = threading.Lock()       # guards local cache mutations
_local_version: int = 0               # last-seen Redis version


# =====================================================================
# Redis helpers (serialisation / version counter)
# =====================================================================

def _serialize_gallery(names: np.ndarray, embs: np.ndarray) -> bytes:
    """Serialise numpy arrays to bytes for Redis storage."""
    buf = io.BytesIO()
    np.savez_compressed(buf, names=names, encodings=embs)
    return buf.getvalue()


def _deserialize_gallery(data: bytes) -> Tuple[np.ndarray, np.ndarray]:
    """Deserialise bytes from Redis back to numpy arrays."""
    buf = io.BytesIO(data)
    npz = np.load(buf, allow_pickle=True)
    return npz["names"], npz["encodings"]


async def _save_to_redis(names: np.ndarray, embs: np.ndarray) -> bool:
    """Push gallery to Redis and bump the version counter.

    Returns True on success, False if Redis is unavailable.
    """
    from app.services.redis_client import get_redis, is_redis_available

    if not is_redis_available():
        return False

    redis = get_redis()
    settings = get_settings()
    try:
        data = _serialize_gallery(names, embs)
        pipe = redis.pipeline()
        pipe.set(settings.REDIS_FEATURE_KEY, data)
        pipe.incr(settings.REDIS_FEATURE_VERSION_KEY)
        await pipe.execute()
        logger.info(
            f"Gallery pushed to Redis ({len(names)} embeddings, "
            f"{len(data) / 1024:.1f} KB)"
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to push gallery to Redis: {e}")
        return False


async def _load_from_redis() -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """Pull gallery from Redis.

    Returns (names, embeddings) or None if unavailable / empty.
    """
    from app.services.redis_client import get_redis, is_redis_available

    if not is_redis_available():
        return None

    redis = get_redis()
    settings = get_settings()
    try:
        data = await redis.get(settings.REDIS_FEATURE_KEY)
        if data is None:
            return None
        return _deserialize_gallery(data)
    except Exception as e:
        logger.warning(f"Failed to load gallery from Redis: {e}")
        return None


async def _get_redis_version() -> int:
    """Read the current version counter from Redis (0 if unavailable)."""
    from app.services.redis_client import get_redis, is_redis_available

    if not is_redis_available():
        return 0

    redis = get_redis()
    settings = get_settings()
    try:
        val = await redis.get(settings.REDIS_FEATURE_VERSION_KEY)
        return int(val) if val else 0
    except Exception:
        return 0


async def _publish_reload_event() -> None:
    """Publish a feature-reload event so peer workers refresh."""
    from app.services.redis_client import get_redis, is_redis_available

    if not is_redis_available():
        return

    redis = get_redis()
    settings = get_settings()
    try:
        await redis.publish(settings.REDIS_CHANNEL, b"reload")
        logger.debug("Published feature_reload event")
    except Exception as e:
        logger.warning(f"Failed to publish reload event: {e}")


# =====================================================================
# Public API (called from routes.py, unchanged signatures)
# =====================================================================

def get_features() -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Get the currently loaded gallery features.

    Returns:
        (names, embeddings)
    """
    with _gallery_lock:
        global _gallery_names, _gallery_embs

        if _gallery_names is None:
            _reload_features_from_disk()

        return _gallery_names, _gallery_embs


async def get_features_async() -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Async version — checks Redis version and refreshes if stale.

    Prefer this in async route handlers for automatic cross-worker sync.
    Falls back to synchronous get_features() if Redis is down.
    """
    from app.services.redis_client import is_redis_available

    if not is_redis_available():
        return get_features()

    global _local_version
    remote_version = await _get_redis_version()

    if remote_version > _local_version:
        result = await _load_from_redis()
        if result is not None:
            with _gallery_lock:
                global _gallery_names, _gallery_embs
                _gallery_names, _gallery_embs = result
                _local_version = remote_version
                logger.info(
                    f"Local cache refreshed from Redis (v{remote_version}, "
                    f"{len(_gallery_names)} embeddings)"
                )

    with _gallery_lock:
        if _gallery_names is None:
            _reload_features_from_disk()
        return _gallery_names, _gallery_embs


def reload_features() -> Tuple[int, int]:
    """Reload features from disk (.npz file).  Synchronous version.

    Returns:
        (num_persons, num_embeddings)
    """
    with _gallery_lock:
        return _reload_features_from_disk()


async def reload_features_async() -> Tuple[int, int]:
    """Reload from disk → push to Redis → notify all workers.

    Prefer this in async route handlers.
    """
    num_persons, num_embs = reload_features()

    # Push to Redis and notify peers
    if _gallery_names is not None and _gallery_embs is not None:
        pushed = await _save_to_redis(_gallery_names, _gallery_embs)
        if pushed:
            global _local_version
            _local_version = await _get_redis_version()
            await _publish_reload_event()

    return num_persons, num_embs


def _reload_features_from_disk() -> Tuple[int, int]:
    """Internal reload from .npz — caller must hold _gallery_lock."""
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
        logger.info(f"Reloaded features from disk: {num_persons} persons, {num_embeddings} embeddings")
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
            _reload_features_from_disk()

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


async def add_persons_async(
    persons_images: Dict[str, List[np.ndarray]],
    move_to_backup: bool = True,
) -> dict:
    """Async wrapper — trains, saves, pushes to Redis, notifies peers.

    Acquires a distributed Redis lock so only one worker trains at a time.
    Falls back to local-only if Redis is unavailable.
    """
    import asyncio
    from app.services.redis_client import get_redis, is_redis_available

    if is_redis_available():
        redis = get_redis()
        settings = get_settings()
        lock = redis.lock(
            settings.REDIS_LOCK_KEY,
            timeout=settings.REDIS_LOCK_TIMEOUT,
            blocking_timeout=120,  # wait up to 2 min for a peer to finish training
        )
        try:
            acquired = await lock.acquire()
            if not acquired:
                return {
                    "success": False,
                    "message": "Another worker is currently training. Try again later.",
                    "persons_added": [],
                    "faces_processed": 0,
                }

            # Run the CPU-heavy training in a thread
            result = await asyncio.to_thread(
                add_persons, persons_images, move_to_backup
            )

            # Push updated gallery to Redis + notify peers
            if result["success"] and _gallery_names is not None:
                await _save_to_redis(_gallery_names, _gallery_embs)
                global _local_version
                _local_version = await _get_redis_version()
                await _publish_reload_event()

            return result
        finally:
            try:
                await lock.release()
            except Exception:
                pass  # lock may have expired
    else:
        # No Redis — run locally (single-worker safe)
        import asyncio
        return await asyncio.to_thread(
            add_persons, persons_images, move_to_backup
        )


async def refresh_from_redis() -> None:
    """Called by the pub/sub listener when a peer publishes a reload event.

    Pulls the latest gallery from Redis into the local cache.
    """
    result = await _load_from_redis()
    if result is not None:
        with _gallery_lock:
            global _gallery_names, _gallery_embs, _local_version
            _gallery_names, _gallery_embs = result
            _local_version = await _get_redis_version()
            logger.info(
                f"Gallery refreshed via pub/sub (v{_local_version}, "
                f"{len(_gallery_names)} embeddings)"
            )
