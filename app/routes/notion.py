from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
from app.services.notion_service import NotionService

router = APIRouter()
notion_service = NotionService()

class NotionPageCreate(BaseModel):
    userName: str
    text: str
    linkToTweet: str
    createdAt: datetime

@router.post("/pages")
async def create_page(page: NotionPageCreate) -> Dict[str, Any]:
    """
    Notionデータベースに新しいページを作成します
    """
    try:
        return notion_service.create_page(page.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
