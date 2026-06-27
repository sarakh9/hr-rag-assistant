import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {request.state.request_id}: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Exception: {request.state.request_id}: {exc}")
    return JSONResponse(
        status_code=422,
        content={"error": exc.errors()},
    )


def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Generic Exception: {request.state.request_id}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )