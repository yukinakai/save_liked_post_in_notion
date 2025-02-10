from fastapi import FastAPI
from dotenv import load_dotenv
from routes import notion

# 環境変数を読み込む
load_dotenv()

app = FastAPI(
    title="Save Liked Post in Notion",
    description="いいねしたツイートをNotionのデータベースに保存するAPIサービス"
)

# ルーターを追加
app.include_router(notion.router, prefix="/api/v1/notion", tags=["notion"])
