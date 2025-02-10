import os
from typing import Dict, Any
from notion_client import Client

class NotionService:
    def __init__(self):
        self.notion = Client(auth=os.getenv("NOTION_API_KEY"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID is not set")
    
    def create_page(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notionデータベースに新しいページを作成します
        
        Args:
            data: ページ作成に必要なデータ
                - userName: ユーザー名
                - text: ツイートのテキスト
                - linkToTweet: ツイートへのリンク
                - createdAt: ツイートの作成日時
        
        Returns:
            作成されたページの情報
        """
        if not all(key in data for key in ["userName", "text", "linkToTweet", "createdAt"]):
            raise ValueError("Required data is missing")
            
        properties = {
            "ID": {
                "title": [
                    {
                        "text": {
                            "content": data["userName"]
                        }
                    }
                ]
            },
            "Text": {
                "rich_text": [
                    {
                        "text": {
                            "content": data["text"]
                        }
                    }
                ]
            },
            "URL": {
                "url": data["linkToTweet"]
            },
            "Tweeted_at": {
                "date": {
                    "start": data["createdAt"]
                }
            }
        }
        
        return self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )
