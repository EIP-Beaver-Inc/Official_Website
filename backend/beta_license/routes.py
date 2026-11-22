"""HTTP routes of the BETA license feature + CORS scoping."""
from __future__ import annotations

import json
import logging
from typing import Iterable, Optional, Type

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ValidationError
from starlette.middleware.cors import CORSMiddleware

from .service import (BetaLicenseService, Denied, DownloadRequest, KeyRequest, RateLimited,
                      ValidateRequest)

logger = logging.getLogger("beaver.beta_license")

MAX_BODY_BYTES = 4096

router = APIRouter(prefix="/api/beta", tags=["beta-license"])

# Called by the native software only: never any CORS header.
NATIVE_ONLY_PREFIXES = ("/api/beta/validate", "/api/beta/files/")
# Called by the website's /beta page: CORS only for explicitly configured origins.
WEB_PATHS = ("/api/beta/download", "/api/beta/key-info")


def client_ip(request: Request) -> Optional[str]:
    # Caddy -> nginx -> backend: Caddy overwrites X-Forwarded-For with the real client IP.
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else None


def public_base_url(request: Request, service: BetaLicenseService) -> str:
    if service.config.public_base_url:
        return service.config.public_base_url
    proto = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip()
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    return f"{proto}://{host.split(',')[0].strip()}"


def _service(request: Request) -> Optional[BetaLicenseService]:
    return getattr(request.app.state, "beta_service", None)


def _unavailable() -> JSONResponse:
    return JSONResponse({"detail": "beta_unavailable"}, status_code=503)


def _bad_request() -> JSONResponse:
    return JSONResponse({"detail": "bad_request"}, status_code=400)


def _error(exc: Exception) -> JSONResponse:
    if isinstance(exc, RateLimited):
        return JSONResponse({"detail": exc.detail}, status_code=429, headers={"Retry-After": str(exc.retry_after)})
    assert isinstance(exc, Denied)
    return JSONResponse(exc.body, status_code=exc.http_status)


async def _parse(request: Request, model: Type[BaseModel]) -> Optional[BaseModel]:
    """Spec 5.1-1: strict schema, any error -> 400 (not FastAPI's default 422)."""
    try:
        if int(request.headers.get("content-length") or 0) > MAX_BODY_BYTES:
            return None
        body = await request.body()
        if len(body) > MAX_BODY_BYTES:
            return None
        data = json.loads(body)
        if not isinstance(data, dict):
            return None
        return model.model_validate(data)
    except (ValueError, ValidationError):
        return None


@router.post("/validate")
async def beta_validate(request: Request):
    service = _service(request)
    if service is None:
        return _unavailable()
    req = await _parse(request, ValidateRequest)
    if req is None:
        return _bad_request()
    try:
        return JSONResponse(await service.validate(req, service_ip(request)))
    except (RateLimited, Denied) as exc:
        return _error(exc)


@router.post("/download")
async def beta_download(request: Request):
    service = _service(request)
    if service is None:
        return _unavailable()
    req = await _parse(request, DownloadRequest)
    if req is None:
        return _bad_request()
    try:
        return JSONResponse(await service.issue_download(req, service_ip(request), public_base_url(request, service)))
    except (RateLimited, Denied) as exc:
        return _error(exc)


@router.post("/key-info")
async def beta_key_info(request: Request):
    service = _service(request)
    if service is None:
        return _unavailable()
    req = await _parse(request, KeyRequest)
    if req is None:
        return _bad_request()
    try:
        return JSONResponse(await service.key_info(req, service_ip(request)))
    except (RateLimited, Denied) as exc:
        return _error(exc)


@router.get("/files/{token}")
async def beta_file(token: str, request: Request):
    service = _service(request)
    if service is None:
        return _unavailable()
    try:
        f = await service.resolve_download(token, service_ip(request))
    except (RateLimited, Denied) as exc:
        return _error(exc)
    return FileResponse(f.path, filename=f.filename, media_type="application/octet-stream",
                        headers={"Cache-Control": "no-store"})


def service_ip(request: Request) -> Optional[str]:
    from .storage import truncate_ip

    return truncate_ip(client_ip(request))


class ScopedCORSMiddleware:
    """Site-wide CORS, except for the BETA license routes (spec 5.4: no permissive CORS).

    - NATIVE_ONLY_PREFIXES: no CORS at all (native client).
    - WEB_PATHS: CORS only for explicit origins (a "*" entry is ignored).
    - everything else: the site's usual CORS configuration.
    """

    def __init__(self, app, origins: Iterable[str]):
        origins = [o.strip() for o in origins if o.strip()]
        self.app = app
        self.site = CORSMiddleware(app, allow_origins=origins, allow_credentials=True,
                                   allow_methods=["*"], allow_headers=["*"])
        strict = [o for o in origins if o != "*"]
        self.web = (CORSMiddleware(app, allow_origins=strict, allow_methods=["POST"], allow_headers=["Content-Type"])
                    if strict else app)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.site(scope, receive, send)
        path = scope.get("path", "")
        if path.startswith(NATIVE_ONLY_PREFIXES):
            return await self.app(scope, receive, send)
        if path in WEB_PATHS:
            return await self.web(scope, receive, send)
        return await self.site(scope, receive, send)


async def setup(app, db) -> None:
    """Called from the app lifespan: load config, create indexes, attach the service."""
    from .config import ConfigError, load_config
    from .storage import ensure_indexes

    try:
        config = load_config()
    except ConfigError as exc:
        app.state.beta_service = None
        logger.error("BETA license feature DISABLED: %s", exc)
        return
    await ensure_indexes(db)
    app.state.beta_service = BetaLicenseService(db, config)
    logger.info("BETA license feature enabled (kid=%s, model keys: %s)",
                config.signing_kid, ", ".join(sorted(config.model_keys)))
