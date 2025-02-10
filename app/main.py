from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv
from app.routes import notion
from app.services.notion_service import NotionService

# 環境変数を読み込む
load_dotenv()

app = FastAPI(
    title="Save Liked Post in Notion",
    description="いいねしたツイートをNotionのデータベースに保存するAPIサービス"
)

# NotionServiceのインスタンスを作成
notion_service = NotionService()

class TweetRequest(BaseModel):
    text: str = Field(..., description="The text content of the tweet")
    userName: str = Field(..., description="The username of the tweet author")
    linkToTweet: str = Field(..., description="URL to the original tweet")
    createdAt: str = Field(..., description="Creation timestamp of the tweet in ISO format")
    tweetEmbedCode: str = Field(..., description="HTML embed code for the tweet")

    def validate_date_format(self):
        try:
            datetime.fromisoformat(self.createdAt.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False

class TweetResponse(BaseModel):
    id: str

@app.get("/")
async def root():
    return {"message": "Welcome to Save Liked Post in Notion API"}

@app.get("/webhook")
async def webhook_get():
    return {"message": "Hello World"}

@app.post("/webhook", response_model=TweetResponse)
async def webhook_post(tweet: TweetRequest):
    if not tweet.validate_date_format():
        raise HTTPException(status_code=422, detail="Invalid date format. Expected ISO format.")
    
    try:
        # Notionにページを作成
        notion_page = notion_service.create_page({
            "userName": tweet.userName,
            "text": tweet.text,
            "linkToTweet": tweet.linkToTweet,
            "createdAt": tweet.createdAt
        })
        
        # NotionページのIDを返す
        return TweetResponse(id=notion_page["id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Notionのルーターを追加
app.include_router(notion.router, prefix="/api/v1/notion", tags=["notion"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
