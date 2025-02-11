import os
import pytest
from datetime import datetime
from dotenv import load_dotenv
from app.services.notion_service import NotionService
from app.exceptions import NotionAPIException, ValidationException, ConfigurationException
from notion_client.errors import APIResponseError

# テスト用の環境変数を読み込む
load_dotenv(".env.test")

def test_notion_service_initialization_without_api_key(monkeypatch):
    """API Keyが設定されていない場合のテスト"""
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    with pytest.raises(ConfigurationException) as exc_info:
        NotionService()
    assert str(exc_info.value) == "NOTION_API_KEY is not set"

def test_notion_service_initialization_without_database_id(monkeypatch):
    """Database IDが設定されていない場合のテスト"""
    monkeypatch.delenv("NOTION_DATABASE_ID", raising=False)
    with pytest.raises(ConfigurationException) as exc_info:
        NotionService()
    assert str(exc_info.value) == "NOTION_DATABASE_ID is not set"

def test_create_page_with_invalid_data():
    """入力データのバリデーションテスト"""
    notion_service = NotionService()
    
    # 空のデータでテスト
    with pytest.raises(ValidationException) as exc_info:
        notion_service.create_page({})
    assert "Required fields are missing" in str(exc_info.value)
    
    # 必須フィールドが欠けているデータでテスト
    invalid_data = {
        "userName": "test_user",
        # textが欠けている
        "linkToTweet": "https://twitter.com/test_user/status/123456789",
        "createdAt": datetime.now().isoformat()
    }
    with pytest.raises(ValidationException) as exc_info:
        notion_service.create_page(invalid_data)
    assert "Required fields are missing" in str(exc_info.value)

def test_create_page_with_api_error(monkeypatch):
    """Notion API エラーのテスト"""
    def mock_create_page(*args, **kwargs):
        raise Exception("API Error")
    
    notion_service = NotionService()
    monkeypatch.setattr(notion_service.notion.pages, "create", mock_create_page)
    
    valid_data = {
        "userName": "test_user",
        "text": "test text",
        "linkToTweet": "https://twitter.com/test_user/status/123456789",
        "createdAt": datetime.now().isoformat()
    }
    
    with pytest.raises(NotionAPIException) as exc_info:
        notion_service.create_page(valid_data)
    assert "Failed to create Notion page" in str(exc_info.value)

def test_add_tweet_url():
    """ツイートURLの追加テスト"""
    notion_service = NotionService()
    
    # テスト用のページIDとツイートURL
    page_id = "test_page_id"
    link_to_tweet = "https://twitter.com/test_user/status/123456789"
    
    # 無効なページIDでテスト
    with pytest.raises(ValidationException) as exc_info:
        notion_service.add_tweet_url("", link_to_tweet)
    assert "Page ID is required" in str(exc_info.value)
    
    # 無効なURLでテスト
    with pytest.raises(ValidationException) as exc_info:
        notion_service.add_tweet_url(page_id, "")
    assert "Tweet URL is required" in str(exc_info.value)

def test_add_tweet_url_with_api_error(monkeypatch):
    """ツイートURL追加時のAPI エラーテスト"""
    def mock_append(*args, **kwargs):
        raise Exception("API Error")
    
    notion_service = NotionService()
    monkeypatch.setattr(notion_service.notion.blocks.children, "append", mock_append)
    
    page_id = "test_page_id"
    link_to_tweet = "https://twitter.com/test_user/status/123456789"
    
    with pytest.raises(NotionAPIException) as exc_info:
        notion_service.add_tweet_url(page_id, link_to_tweet)
    assert "Failed to add tweet URL" in str(exc_info.value)
