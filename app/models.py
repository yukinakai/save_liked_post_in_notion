from pydantic import BaseModel, Field
from datetime import datetime

class Tweet(BaseModel):
    """ツイートデータのモデル"""
    text: str = Field(..., min_length=1)
    userName: str
    linkToTweet: str
    createdAt: datetime
    tweetEmbedCode: str

class NotionPageResponse(BaseModel):
    """Notionページのレスポンスモデル"""
    id: str
