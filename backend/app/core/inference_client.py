"""Inference Client — HTTP client for communicating with the inference microservice.

All ML operations (detection, recognition, embedding, training) are
delegated to the inference service via REST HTTP calls.

The backend no longer imports any ML libraries directly.
"""
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class InferenceClient:
    """Async HTTP client for the inference microservice.

    Usage:
        client = InferenceClient()
        result = await client.recognize(image_bytes)
    """

    def __init__(self, base_url: Optional[str] = None):
        settings = get_settings()
        self._base_url = base_url or settings.INFERENCE_SERVICE_URL
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialize the httpx async client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=httpx.Timeout(
                    connect=5.0,   # 5s to establish connection
                    read=120.0,    # 120s for inference response (large images)
                    write=30.0,    # 30s to send request body
                    pool=10.0,     # 10s waiting for connection pool
                ),
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    async def health(self) -> Dict[str, Any]:
        """Check inference service health."""
        try:
            resp = await self.client.get("/health")
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            return {"status": "unreachable", "models_loaded": False}
        except Exception as e:
            logger.error(f"Inference health check failed: {e}")
            return {"status": "error", "error": str(e)}

    # -------------------------------------------------------------------------
    # Detection
    # -------------------------------------------------------------------------

    async def detect(self, image_bytes: bytes) -> Dict[str, Any]:
        """Detect faces in an image.

        Args:
            image_bytes: Raw image bytes (JPEG/PNG).

        Returns:
            Dict with 'faces' list and 'total_faces' count.

        Raises:
            httpx.HTTPStatusError on inference service errors.
        """
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        resp = await self._post_with_retry("/detect", {"image": b64})
        return resp

    # -------------------------------------------------------------------------
    # Recognition (full pipeline)
    # -------------------------------------------------------------------------

    async def recognize(
        self,
        image_bytes: bytes,
        confidence_threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Full recognition pipeline: detect → align → embed → match.

        Args:
            image_bytes: Raw image bytes.
            confidence_threshold: Override default threshold.

        Returns:
            Dict with 'results', 'total_faces_detected', 'processing_time_ms'.
        """
        payload: Dict[str, Any] = {
            "image": base64.b64encode(image_bytes).decode("utf-8"),
        }
        if confidence_threshold is not None:
            payload["confidence_threshold"] = confidence_threshold

        return await self._post_with_retry("/recognize", payload)

    # -------------------------------------------------------------------------
    # Embedding
    # -------------------------------------------------------------------------

    async def embed(self, face_image_bytes: bytes) -> List[float]:
        """Extract embedding from an aligned face image.

        Args:
            face_image_bytes: Raw aligned face image bytes.

        Returns:
            List of floats (512-d embedding vector).
        """
        b64 = base64.b64encode(face_image_bytes).decode("utf-8")
        resp = await self._post_with_retry("/embed", {"face_image": b64})
        return resp.get("embedding", [])

    # -------------------------------------------------------------------------
    # Training (add persons)
    # -------------------------------------------------------------------------

    async def train(
        self,
        persons_images: Dict[str, List[bytes]],
        move_to_backup: bool = True,
    ) -> Dict[str, Any]:
        """Add new persons to the feature store.

        Args:
            persons_images: Dict mapping person_id → list of raw image bytes.
            move_to_backup: Move source images to backup after processing.

        Returns:
            Dict with 'success', 'persons_added', 'faces_processed'.
        """
        # Encode all images to base64
        encoded: Dict[str, List[str]] = {}
        for person_id, images in persons_images.items():
            encoded[person_id] = [
                base64.b64encode(img).decode("utf-8") for img in images
            ]

        return await self._post_with_retry("/train", {
            "images": encoded,
            "move_to_backup": move_to_backup,
        })

    # -------------------------------------------------------------------------
    # Feature Store
    # -------------------------------------------------------------------------

    async def reload_features(self) -> Dict[str, Any]:
        """Reload the feature store from disk."""
        return await self._post_with_retry("/features/reload", {})

    async def list_known_persons(self) -> List[str]:
        """List all known person IDs in the feature store."""
        try:
            resp = await self.client.get("/features/list")
            resp.raise_for_status()
            data = resp.json()
            return data.get("persons", [])
        except httpx.ConnectError:
            logger.warning("Inference service not available yet — returning empty persons list")
            return []
        except Exception as e:
            logger.error(f"Failed to list known persons: {e}")
            raise

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    async def _post_with_retry(
        self, path: str, payload: Dict[str, Any], max_retries: int = 1
    ) -> Dict[str, Any]:
        """POST with a single retry on 5xx errors.

        Args:
            path: Endpoint path (e.g. '/recognize').
            payload: JSON payload dict.
            max_retries: Number of retries on 5xx (default 1).

        Returns:
            JSON response dict.

        Raises:
            httpx.ConnectError: If inference service is unreachable.
            httpx.HTTPStatusError: On non-retryable HTTP errors.
        """
        last_error = None
        for attempt in range(1 + max_retries):
            try:
                resp = await self.client.post(path, json=payload)
                resp.raise_for_status()
                return resp.json()
            except httpx.ConnectError:
                logger.error("Inference service unreachable")
                raise
            except httpx.TimeoutException as e:
                logger.error(f"Inference timeout on {path}: {e}")
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < max_retries:
                    logger.warning(
                        f"Inference 5xx on {path} (attempt {attempt + 1}), retrying…"
                    )
                    last_error = e
                    continue
                raise
            except Exception as e:
                logger.error(f"Inference request failed: {e}")
                raise

        # Should not reach here, but just in case
        raise last_error  # type: ignore
