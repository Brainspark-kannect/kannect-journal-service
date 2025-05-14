# app/core/exceptions.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict
import logging
import traceback

logger = logging.getLogger(__name__)

class AppException(Exception):
    """Base application exception class"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors"""
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors"""
    error_msg = str(exc)
    stack_trace = traceback.format_exc()
    logger.error(f"Database error: {error_msg}")
    logger.debug(f"Stack trace: {stack_trace}")
    
    # Log additional request information
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request URL: {request.url}")
    logger.debug(f"Request headers: {request.headers}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "message": error_msg if not "password" in error_msg.lower() else "Database error occurred"
        }
    )

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application-specific exceptions"""
    logger.error(f"Application error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions"""
    error_msg = str(exc)
    stack_trace = traceback.format_exc()
    logger.error(f"Unhandled error: {error_msg}")
    logger.debug(f"Stack trace: {stack_trace}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )

def add_exception_handlers(app: FastAPI) -> None:
    """Add all exception handlers to the app"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
