"""POST /api/remove-bg — strip background from an uploaded image using rembg."""
from __future__ import annotations

import io
from functools import lru_cache

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from rembg import new_session, remove

from ..config import settings
from ..logging_config import logger

router = APIRouter(prefix="/api", tags=["remove-bg"])


@lru_cache(maxsize=1)
def _session():
    """Lazy-init rembg session; cached so the model loads exactly once."""
    logger.info("Loading rembg model: %s", settings.rembg_model)
    return new_session(settings.rembg_model)


# Warm the model on module import so the first request is fast.
_session()


_ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


@router.post(
    "/remove-bg",
    summary="Remove image background",
    response_class=StreamingResponse,
    responses={
        200: {"content": {"image/png": {}}, "description": "Transparent PNG"},
        400: {"description": "Invalid upload"},
        413: {"description": "File too large"},
    },
)
async def remove_bg(file: UploadFile = File(...)) -> StreamingResponse:
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {file.content_type}. "
                   f"Allowed: {sorted(_ALLOWED_TYPES)}",
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty file")
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File exceeds {settings.max_upload_bytes // (1024 * 1024)} MB limit",
        )

    try:
        cutout = remove(raw, session=_session())
    except Exception as exc:  # noqa: BLE001 — rembg raises plain Exception
        logger.exception("rembg failed")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Background removal failed: {exc}",
        ) from exc

    safe_name = (file.filename or "image").rsplit(".", 1)[0]
    headers = {
        "Content-Disposition": f'inline; filename="{safe_name}-no-bg.png"',
        "Cache-Control": "no-store",
    }
    return StreamingResponse(io.BytesIO(cutout), media_type="image/png", headers=headers)
