from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from routes import notion
from app.exceptions import AppException
from app.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.logging_config import logger

# 環境変数を読み込む
load_dotenv()

app = FastAPI(
    title="Save Liked Post in Notion",
    description="いいねしたツイートをNotionのデータベースに保存するAPIサービス"
)

# エラーハンドラーを登録
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ルーターを追加
app.include_router(notion.router, prefix="/api/v1/notion", tags=["notion"])

logger.info("Application startup complete")
