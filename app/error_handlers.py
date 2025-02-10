from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from .exceptions import AppException, ValidationException

logger = logging.getLogger(__name__)

async def app_exception_handler(request: Request, exc: AppException):
    """アプリケーション例外のハンドラー"""
    logger.error(f"Application error occurred: {str(exc)}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": str(exc),
            "details": exc.details
        }
    )

async def validation_exception_handler(request: Request, exc: ValidationException):
    """バリデーション例外のハンドラー"""
    logger.error(f"Validation error occurred: {str(exc)}")
    return JSONResponse(status_code=422, content={
        "message": str(exc),
        "details": exc.details
    })

async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """リクエストバリデーションエラーのハンドラー"""
    logger.error(f"Request validation error occurred: {exc.errors()}")
    
    # 日付フォーマットのエラーの場合は、専用のメッセージを返す
    for error in exc.errors():
        if error.get("type") == "datetime_from_date_parsing":
            return JSONResponse(
                status_code=422,
                content={
                    "message": "Invalid date format. Expected ISO format.",
                    "details": {}
                }
            )
    
    # その他のバリデーションエラー
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "details": {
                f"{' -> '.join(str(loc) for loc in error['loc'])}": error["msg"]
                for error in exc.errors()
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """一般的な例外のハンドラー"""
    logger.error(f"Unexpected error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
