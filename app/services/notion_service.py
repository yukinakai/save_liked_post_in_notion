import os
from typing import Dict, Any, Optional
from notion_client import Client
from notion_client.errors import APIResponseError
from ..exceptions import NotionAPIException, ValidationException, ConfigurationException
from ..logging_config import logger

class NotionService:
    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")
        
        if not self.api_key:
            raise ConfigurationException("NOTION_API_KEY is not set")
        if not self.database_id:
            raise ConfigurationException("NOTION_DATABASE_ID is not set")
        
        try:
            self.notion = Client(auth=self.api_key)
            logger.info("NotionService initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize NotionService", exc_info=True)
            raise ConfigurationException("Failed to initialize Notion client", {"error": str(e)})
    
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
        
        Raises:
            ValidationException: 必要なデータが不足している場合
            NotionAPIException: Notion APIとの通信に失敗した場合
        """
        logger.info("Creating new Notion page", extra={"data": data})
        
        required_fields = ["userName", "text", "linkToTweet", "createdAt"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            error_msg = f"Required fields are missing or empty: {', '.join(missing_fields)}"
            logger.error(error_msg, extra={"data": data})
            raise ValidationException(error_msg, {"missing_fields": missing_fields})
            
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
                    "start": data["createdAt"].isoformat() if hasattr(data["createdAt"], "isoformat") else data["createdAt"]
                }
            }
        }
        
        try:
            response = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            logger.info("Successfully created Notion page", extra={"page_id": response["id"]})
            return response
        except APIResponseError as e:
            error_msg = "Failed to create Notion page"
            logger.error(error_msg, extra={"error": str(e)}, exc_info=True)
            raise NotionAPIException(error_msg, details={"api": "error"})
        except Exception as e:
            error_msg = "Failed to create Notion page"
            logger.error(error_msg, exc_info=True)
            raise NotionAPIException(error_msg, details={"api": "error"})

    def add_tweet_url(self, page_id: str, linkToTweet: str) -> Dict[str, Any]:
        """
        Notionページの本文にツイートURLを埋め込みコードを追加します
        
        Args:
            page_id: NotionページのID
            linkToTweet: ツイートのURL
        
        Returns:
            更新されたページの情報
        
        Raises:
            ValidationException: page_idまたはlinkToTweetが空の場合
            NotionAPIException: Notion APIとの通信に失敗した場合
        """
        logger.info("Adding tweet url", extra={"page_id": page_id})
        
        if not page_id:
            raise ValidationException("Page ID is required")
        if not linkToTweet:
            raise ValidationException("Tweet URL is required")
            
        try:
            response = self.notion.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "embed",
                        "embed": {
                            "url": linkToTweet
                        }
                    }
                ]
            )
            logger.info("Successfully added embed tweet", extra={"page_id": page_id})
            return response
        except APIResponseError as e:
            error_msg = "Failed to add embed tweet"
            logger.error(error_msg, extra={"error": str(e)}, exc_info=True)
            raise NotionAPIException(error_msg, details={"api": "error"})
        except Exception as e:
            error_msg = "Failed to add embed tweet"
            logger.error(error_msg, exc_info=True)
            raise NotionAPIException(error_msg, details={"api": "error"})
