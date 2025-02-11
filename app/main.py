from fastapi import FastAPI, HTTPException, Request, JSONResponse
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

# 環境変数を読み込む
load_dotenv()

app = FastAPI(
    title="Save Liked Post in Notion",
    description="いいねしたツイートをNotionのデータベースに保存するAPIサービス"
)

# ミドルウェアを追加
app.add_middleware(ServerErrorMiddleware, handler=general_exception_handler)

# エラーハンドラーを登録
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

notion_service = NotionService()

@app.get("/")
async def root():
    return {"message": "Welcome to Save Liked Post in Notion API"}

@app.get("/webhook")
async def hello_world():
    return {"message": "Hello World"}

@app.post("/webhook", response_model=NotionPageResponse)
async def webhook_post(request: Request):
    # リクエストボディを取得して改行を正規化
    body = await request.body()
    body_str = body.decode()
    normalized_body = body_str.replace('\r\n', '\\n').replace('\r', '\\n').replace('\n', '\\n')
    
    try:
        # JSONとしてパース
        data = json.loads(normalized_body)
        # Tweetモデルとしてバリデーション
        tweet = Tweet(**data)
        
        # Notionページの作成
        page = notion_service.create_page({
            "text": tweet.text,
            "user_name": tweet.userName,
            "link_to_tweet": tweet.linkToTweet,
            "created_at": tweet.createdAt.isoformat(),
        })

        # ツイートの埋め込みコードを追加
        notion_service.add_tweet_embed_code(page["id"], tweet.tweetEmbedCode)

        return NotionPageResponse(id=page["id"])
    except json.JSONDecodeError as e:
        raise ValidationException(f"Invalid JSON format: {str(e)}")
    except ValidationError as e:
        # バリデーションエラーの詳細を確認
        for error in e.errors():
            if error.get("type") == "datetime_from_date_parsing":
                return JSONResponse(
                    status_code=422,
                    content={
                        "message": "Invalid date format. Expected ISO format.",
                        "details": {}
                    }
                )
        raise ValidationException(f"Invalid Tweet data: {str(e)}")
    except Exception as e:
        raise AppException("Failed to create Notion page", 500, {"error": str(e)})

# Notionのルーターを追加
app.include_router(notion.router, prefix="/api/v1/notion", tags=["notion"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
