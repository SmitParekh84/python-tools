"""FastAPI entry point — exposed by uvicorn as `app.main:app`."""
from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .logging_config import logger
from .routers import remove_bg

app = FastAPI(
    title="Smit Parekh — Python Tools",
    description="ML-backed tools (background removal, etc.) for the portfolio site.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "%s %s -> %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    return JSONResponse({"service": "python-tools", "status": "ok", "docs": "/docs"})


@app.get("/api/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "model": settings.rembg_model}


app.include_router(remove_bg.router)
