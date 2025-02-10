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

    def add_tweet_embed_code(self, page_id: str, tweet_embed_code: str) -> Dict[str, Any]:
        """
        Notionページの本文にツイート埋め込みコードを追加します
        
        Args:
            page_id: NotionページのID
            tweet_embed_code: ツイートの埋め込みコード
        
        Returns:
            更新されたページの情報
        
        Raises:
            ValueError: page_idまたはtweet_embed_codeが空の場合
        """
        if not page_id:
            raise ValueError("Page ID is required")
        if not tweet_embed_code:
            raise ValueError("Tweet embed code is required")
            
        return self.notion.blocks.children.append(
            block_id=page_id,
            children=[
                {
                    "object": "block",
                    "type": "embed",
                    "embed": {
                        "url": tweet_embed_code
                    }
                }
            ]
        )
