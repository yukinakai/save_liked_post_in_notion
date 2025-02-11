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
    raw_body = '''{
    "text": "Test tweet",
    "userName": "test_user",
    "linkToTweet": "https://twitter.com/test_user/status/123456789",
    "createdAt": "invalid-date",
    "tweetEmbedCode": "<blockquote>Test</blockquote>"
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

def test_webhook_post_with_empty_text():
    """空のテキストフィールドのテスト"""
    raw_body = '''{
    "text": "",
    "userName": "test_user",
    "linkToTweet": "https://twitter.com/test_user/status/123456789",
    "createdAt": "2025-02-10T13:35:49Z",
    "tweetEmbedCode": "<blockquote>Test</blockquote>"
}'''
    response = client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422

def test_webhook_post_with_missing_field():
    """必須フィールドが欠けているテスト"""
    raw_body = '''{
    "text": "Test tweet",
    "linkToTweet": "https://twitter.com/test_user/status/123456789",
    "createdAt": "2025-02-10T13:35:49Z",
    "tweetEmbedCode": "<blockquote>Test</blockquote>"
}'''
    response = client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"Content-Type": "application/json"}
    )
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
    
    from datetime import datetime
    raw_body = f'''{{
    "text": "Test tweet with
line breaks and "quotes"",
    "userName": "test_user",
    "linkToTweet": "https://twitter.com/test_user/status/123456789",
    "createdAt": "{datetime.now().isoformat()}",
    "tweetEmbedCode": "<blockquote>Test</blockquote>"
}}'''

    response = client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": "test-page-id"}
