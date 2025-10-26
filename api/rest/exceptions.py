"""Exception handlers for FastAPI."""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup custom exception handlers."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handle HTTP exceptions.

        If exc.detail is a dict with an 'error' key, use it as-is.
        Otherwise, wrap it in a standard error format.
        """
        logger.error(f"HTTP error {exc.status_code}: {exc.detail}")

        # If detail is already a dict with error info, use it directly
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            content = exc.detail
        else:
            # Otherwise, wrap in standard format
            content = {
                "error": "HTTP Error",
                "message": exc.detail,
                "status_code": exc.status_code,
            }

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle request validation errors."""
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "Invalid request data",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            },
        )
