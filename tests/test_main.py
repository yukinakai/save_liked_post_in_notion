from fastapi.testclient import TestClient
from datetime import datetime
import pytest
from dotenv import load_dotenv
from app.main import app
from app.exceptions import ValidationException

# テスト用の環境変数を読み込む
load_dotenv(".env.test")

client = TestClient(app)

def test_root():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Save Liked Post in Notion API"}

def test_webhook_get():
    """GETリクエストのテスト"""
    response = client.get("/webhook")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_webhook_post_with_invalid_date():
    """不正な日付フォーマットのテスト"""
    invalid_data = {
        "text": "Test tweet",
        "userName": "test_user",
        "linkToTweet": "https://twitter.com/test_user/status/123456789",
        "createdAt": "invalid-date",  # 不正な日付フォーマット
        "tweetEmbedCode": "<blockquote>Test</blockquote>"
    }
    response = client.post("/webhook", json=invalid_data)
    assert response.status_code == 422
    assert response.json() == {
        "message": "Invalid date format. Expected ISO format.",
        "details": {}
    }

def test_webhook_post_with_empty_text():
    """空のテキストフィールドのテスト"""
    invalid_data = {
        "text": "",  # 空のテキスト
        "userName": "test_user",
        "linkToTweet": "https://twitter.com/test_user/status/123456789",
        "createdAt": "2025-02-10T13:35:49Z",
        "tweetEmbedCode": "<blockquote>Test</blockquote>"
    }
    response = client.post("/webhook", json=invalid_data)
    assert response.status_code == 422

def test_webhook_post_with_missing_field():
    """必須フィールドが欠けているテスト"""
    invalid_data = {
        "text": "Test tweet",
        # userNameが欠けている
        "linkToTweet": "https://twitter.com/test_user/status/123456789",
        "createdAt": "2025-02-10T13:35:49Z",
        "tweetEmbedCode": "<blockquote>Test</blockquote>"
    }
    response = client.post("/webhook", json=invalid_data)
    assert response.status_code == 422

def test_webhook_post_success(monkeypatch):
    """正常なPOSTリクエストのテスト"""
    # NotionServiceのcreate_pageメソッドをモック
    def mock_create_page(self, data):
        return {"id": "test-page-id"}
    
    # NotionServiceのadd_tweet_embed_codeメソッドをモック
    def mock_add_tweet_embed_code(self, page_id, tweet_embed_code):
        return {"id": page_id}
    
    # モックを適用
    from app.services.notion_service import NotionService
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)
    monkeypatch.setattr(NotionService, "add_tweet_embed_code", mock_add_tweet_embed_code)
    
    valid_data = {
        "text": "Test tweet",
        "userName": "test_user",
        "linkToTweet": "https://twitter.com/test_user/status/123456789",
        "createdAt": datetime.now().isoformat(),
        "tweetEmbedCode": "<blockquote>Test</blockquote>"
    }
    
    response = client.post("/webhook", json=valid_data)
    assert response.status_code == 200
    assert response.json() == {"id": "test-page-id"}
