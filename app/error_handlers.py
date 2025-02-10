from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import AppException
from .logging_config import logger

async def app_exception_handler(request: Request, exc: AppException):
    """アプリケーション例外のハンドラー"""
    logger.error(
        f"Application error occurred: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "details": exc.details
        }
    )

async def validation_exception_handler(request: Request, exc: Exception):
    """バリデーション例外のハンドラー"""
    logger.error(
        f"Validation error occurred: {str(exc)}",
        extra={"path": request.url.path}
    )
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "details": {"error": str(exc)}
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """一般的な例外のハンドラー"""
    logger.error(
        f"Unexpected error occurred: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "details": {"error": str(exc)}
        }
    )
