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

async def validation_exception_handler(request: Request, exc: ValidationException):  # pylint: disable=unused-argument
    """バリデーションエラーのハンドラー"""# リクエストボディを取得
    body = await request.body()
    body_str = body.decode() if body else ""

    logger.error(f"Validation error occurred: {str(exc)}, Request body: {body_str}")
    return JSONResponse(status_code=422, content={
        "message": str(exc),
        "details": exc.details
    })

async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """リクエストバリデーションエラーのハンドラー"""
    # リクエストボディを取得
    body = await request.body()
    body_str = body.decode() if body else ""

    # JSONとしてパースを試みる
    try:
        if body_str:
            import json
            parsed_body = json.loads(body_str)
            body_analysis = f"Parsed JSON body: {parsed_body}"
        else:
            body_analysis = "Empty body"
    except json.JSONDecodeError as e:
        body_analysis = f"Invalid JSON format: {str(e)}, position: {e.pos}, line: {e.lineno}, column: {e.colno}, raw_body: {body_str}"
    
    logger.error(
        f"Request validation error occurred: {exc.errors()}, "
        f"Request details - method: {request.method}, url: {request.url}, "
        f"headers: {dict(request.headers)}, query_params: {dict(request.query_params)}, "
        f"body_analysis: {body_analysis}, "
        f"raw_body: {body_str}"
    )
    
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

async def general_exception_handler(request: Request, exc: Exception):  # pylint: disable=unused-argument
    """一般的な例外のハンドラー"""
    logger.error(f"Unexpected error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
