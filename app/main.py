from fastapi import FastAPI, HTTPException, Request, Security, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv
from app.routes import notion
from app.services.notion_service import NotionService
from app.exceptions import (
    AppException,
    ValidationException,
    NotionAPIException,
    ConfigurationException
)
from app.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    request_validation_exception_handler
)
from app.models import Tweet, NotionPageResponse
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
import json
import logging
from fastapi.security.api_key import APIKeyHeader

# ロガーの設定
logger = logging.getLogger(__name__)

# 環境変数を読み込む
load_dotenv()

# NotionServiceのインスタンスを作成
notion_service = NotionService(
    api_key=os.getenv("NOTION_API_KEY"),
    database_id=os.getenv("NOTION_DATABASE_ID")
)

app = FastAPI(
    title="Save Liked Post in Notion",
    description="いいねしたツイートをNotionのデータベースに保存するAPIサービス"
)

# API Key認証の設定
API_KEY_NAME = "X-API-Key"

def get_api_key(api_key: str = Header(None, alias="X-API-Key")) -> str:
    """API Keyを取得する関数"""
    if api_key is None:
        raise HTTPException(
            status_code=401,
            detail={"message": "Invalid API Key"}
        )
    
    if api_key != os.getenv("WEBHOOK_API_KEY"):
        raise HTTPException(
            status_code=401,
            detail={"message": "Invalid API Key"}
        )
    
    return api_key

# ミドルウェアを追加
app.add_middleware(ServerErrorMiddleware, handler=general_exception_handler)

# エラーハンドラーを登録
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

@app.get("/")
async def root():
    return {"message": "Welcome to Save Liked Post in Notion API"}

@app.get("/webhook")
async def hello_world(api_key: str = Depends(get_api_key)):
    return {"message": "Hello World"}

@app.post("/webhook", response_model=NotionPageResponse)
async def webhook_post(request: Request, api_key: str = Depends(get_api_key)):
    """Webhookエンドポイント
    
    リクエストボディは以下の順序でフィールドを___POST_FIELD_SEPARATOR___で区切って送信:
    1. text: ツイートのテキスト
    2. userName: ユーザー名
    3. linkToTweet: ツイートへのリンク
    4. createdAt: 作成日時（ISO形式または "Month DD, YYYY at HH:MMAM/PM" 形式）
    """
    # リクエストボディをテキストとして読み取る
    body = await request.body()
    raw_text = body.decode()
    
    # フィールドを分割
    fields = raw_text.split("___POST_FIELD_SEPARATOR___")
    if len(fields) != 4:
        raise ValidationException(
            "Invalid request format. Expected 4 fields separated by ___POST_FIELD_SEPARATOR___",
            details={"received_fields": len(fields)}
        )
    
    # フィールドを取り出す
    text, user_name, link_to_tweet, created_at = fields

    # 必須フィールドのバリデーション
    if not text:
        raise ValidationException(
            "Text field cannot be empty",
            details={}
        )

    # 日付フォーマットを検証して変換
    try:
        # まずISO形式として解析を試みる
        parsed_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    except ValueError:
        try:
            # 次にMonth DD, YYYY at HH:MMAM/PM形式として解析を試みる
            parsed_date = datetime.strptime(created_at, "%B %d, %Y at %I:%M%p")
        except ValueError:
            raise ValidationException(
                "Invalid date format. Expected ISO format.",
                details={}
            )
    
    # Tweetモデルを作成
    tweet = Tweet(
        text=text,
        userName=user_name,
        linkToTweet=link_to_tweet,
        createdAt=parsed_date.isoformat()
    )
    
    # NotionServiceを初期化してページを作成
    logger.info("Creating new Notion page")
    page = notion_service.create_page(tweet.model_dump())  # Pydanticモデルを辞書に変換

    # 埋め込みコードを追加
    if link_to_tweet:
        logger.info("Adding tweet url")
        notion_service.add_tweet_url(page["id"], link_to_tweet)

    # レスポンスを返す
    return NotionPageResponse(id=page["id"])

# Notionのルーターを追加
app.include_router(notion.router, prefix="/api/v1/notion", tags=["notion"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
