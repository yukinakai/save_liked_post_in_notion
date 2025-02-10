from fastapi.testclient import TestClient
from datetime import datetime
import pytest
from app.main import app

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
    assert "Invalid date format" in response.json()["detail"]

def test_webhook_post_success(monkeypatch):
    """正常なPOSTリクエストのテスト"""
    # NotionServiceのcreate_pageメソッドをモック
    def mock_create_page(self, data):
        return {"id": "test-page-id"}
    
    # モックを適用
    from app.services.notion_service import NotionService
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)
    
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
