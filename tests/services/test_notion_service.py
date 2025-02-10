import os
import pytest
from datetime import datetime
from dotenv import load_dotenv
from app.services.notion_service import NotionService

# テスト用の環境変数を読み込む
load_dotenv(".env.test")

def test_create_page_with_invalid_data():
    """入力データのバリデーションテスト"""
    notion_service = NotionService()
    
    # 空のデータでテスト
    with pytest.raises(ValueError):
        notion_service.create_page({})
    
    # 必須フィールドが欠けているデータでテスト
    invalid_data = {
        "userName": "test_user",
        # textが欠けている
        "linkToTweet": "https://twitter.com/test_user/status/123456789",
        "createdAt": datetime.now().isoformat()
    }
    with pytest.raises(ValueError):
        notion_service.create_page(invalid_data)
