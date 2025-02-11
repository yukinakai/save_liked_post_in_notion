from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.exceptions import NotionAPIException

client = TestClient(app)

def test_webhook_get():
    """GETリクエストのテスト"""
    response = client.get("/webhook")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_webhook_post_success(monkeypatch):
    """正常なPOSTリクエストのテスト"""
    # NotionServiceのcreate_pageメソッドをモック
    def mock_create_page(self, data):
        return {"id": "test-page-id"}
    
    # NotionServiceのadd_tweet_embed_codeメソッドをモック
    def mock_add_tweet_embed_code(self, page_id, tweet_embed_code):
        return True
    
    # モックを適用
    from app.services.notion_service import NotionService
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)
    monkeypatch.setattr(NotionService, "add_tweet_embed_code", mock_add_tweet_embed_code)
    
    # 実際のリクエストボディを模擬（改行とダブルクォートを生の状態で含む）
    raw_body = '''{
    "text": "This is a test
tweet with
line breaks and "quotes"",
    "userName": "testuser",
    "linkToTweet": "https://twitter.com/testuser/status/123456789",
    "createdAt": "2025-02-10T13:35:49Z",
    "tweetEmbedCode": "<blockquote>Test
Tweet</blockquote>"
}'''
    
    response = client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": "test-page-id"}

def test_webhook_post_missing_field():
    """必須フィールドが欠けているPOSTリクエストのテスト"""
    raw_body = '''{
    "text": "This is a test tweet",
    "userName": "testuser",
    "createdAt": "2025-02-10T13:35:49Z",
    "tweetEmbedCode": "<blockquote>Test Tweet</blockquote>"
}'''
    
    response = client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422

def test_webhook_post_invalid_date_format():
    """不正な日付フォーマットのテスト"""
    raw_body = '''{
    "text": "This is a test
tweet with "quotes"",
    "userName": "testuser",
    "linkToTweet": "https://twitter.com/testuser/status/123456789",
    "createdAt": "invalid-date",
    "tweetEmbedCode": "<blockquote>Test Tweet</blockquote>"
}'''
    
    response = client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert response.json() == {
        "message": "Invalid date format. Expected ISO format.",
        "details": {}
    }

def test_webhook_post_notion_api_error(monkeypatch):
    """NotionAPIエラーのテスト"""
    # NotionServiceのcreate_pageメソッドをモック（エラーを発生させる）
    def mock_create_page(self, data):
        raise NotionAPIException("Failed to create Notion page", details={"error": "Failed to create Notion page"})

    # モックを適用
    from app.services.notion_service import NotionService
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)

    raw_body = '''{
    "text": "This is a test
tweet with "quotes"",
    "userName": "testuser",
    "linkToTweet": "https://twitter.com/testuser/status/123456789",
    "createdAt": "2025-02-10T13:35:49Z",
    "tweetEmbedCode": "<blockquote>Test
Tweet</blockquote>"
}'''
    
    response = client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 500
    assert response.json() == {
        "message": "Failed to create Notion page",
        "details": {"error": "Failed to create Notion page"}
    }

def test_webhook_post_empty_text():
    """空のテキストフィールドのテスト"""
    raw_body = '''{
    "text": "",
    "userName": "testuser",
    "linkToTweet": "https://twitter.com/testuser/status/123456789",
    "createdAt": "2025-02-10T13:35:49Z",
    "tweetEmbedCode": "<blockquote>Test Tweet</blockquote>"
}'''
    
    response = client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
