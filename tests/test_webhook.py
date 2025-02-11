from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.services.notion_service import NotionService
from app.exceptions import NotionAPIException

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """テスト用の環境変数を設定"""
    monkeypatch.setenv("WEBHOOK_API_KEY", "test-api-key")

def test_webhook_get(test_client):
    """GETリクエストのテスト"""
    headers = {"X-API-Key": "test-api-key"}
    response = test_client.get("/webhook", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_webhook_post_success(test_client, monkeypatch):
    """正常なPOSTリクエストのテスト"""
    # NotionServiceのcreate_pageメソッドをモック
    def mock_create_page(self, data):
        return {"id": "test-page-id"}
    
    # NotionServiceのadd_tweet_embed_codeメソッドをモック
    def mock_add_tweet_embed_code(self, page_id, tweet_embed_code):
        return True
    
    # モックを適用
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)
    monkeypatch.setattr(NotionService, "add_tweet_embed_code", mock_add_tweet_embed_code)
    
    # 実際のリクエストボディを模擬（改行とダブルクォートを生の状態で含む）
    # フィールドの順序: text, userName, linkToTweet, createdAt, tweetEmbedCode
    raw_body = '''This is a test
tweet with
line breaks and "quotes"___POST_FIELD_SEPARATOR___testuser___POST_FIELD_SEPARATOR___https://twitter.com/testuser/status/123456789___POST_FIELD_SEPARATOR___2025-02-10T13:35:49Z___POST_FIELD_SEPARATOR___<blockquote>Test
Tweet</blockquote>'''
    
    headers = {"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {"id": "test-page-id"}

def test_webhook_post_missing_field(test_client):
    """必須フィールドが欠けているPOSTリクエストのテスト（フィールド数が足りない）"""
    # フィールドの順序: text, userName, linkToTweet, createdAt（tweetEmbedCodeが欠けている）
    raw_body = '''This is a test tweet___POST_FIELD_SEPARATOR___testuser___POST_FIELD_SEPARATOR___https://twitter.com/testuser/status/123456789___POST_FIELD_SEPARATOR___2025-02-10T13:35:49Z'''
    
    headers = {"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers=headers
    )
    assert response.status_code == 422

def test_webhook_post_invalid_date_format(test_client):
    """不正な日付フォーマットのテスト"""
    # フィールドの順序: text, userName, linkToTweet, createdAt, tweetEmbedCode
    raw_body = '''This is a test
tweet with "quotes"___POST_FIELD_SEPARATOR___testuser___POST_FIELD_SEPARATOR___https://twitter.com/testuser/status/123456789___POST_FIELD_SEPARATOR___invalid-date___POST_FIELD_SEPARATOR___<blockquote>Test Tweet</blockquote>'''
    
    headers = {"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "message": "Invalid date format. Expected ISO format.",
        "details": {}
    }

def test_webhook_post_with_formatted_date(test_client, monkeypatch):
    """Month DD, YYYY at HH:MMAM/PM形式の日付を含むPOSTリクエストのテスト"""
    # NotionServiceのcreate_pageメソッドをモック
    def mock_create_page(self, data):
        return {"id": "test-page-id"}
    
    # NotionServiceのadd_tweet_embed_codeメソッドをモック
    def mock_add_tweet_embed_code(self, page_id, tweet_embed_code):
        return True
    
    # モックを適用
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)
    monkeypatch.setattr(NotionService, "add_tweet_embed_code", mock_add_tweet_embed_code)
    
    # フィールドの順序: text, userName, linkToTweet, createdAt, tweetEmbedCode
    raw_body = '''Test tweet___POST_FIELD_SEPARATOR___test_user___POST_FIELD_SEPARATOR___https://twitter.com/test_user/status/123456789___POST_FIELD_SEPARATOR___February 11, 2025 at 01:25AM___POST_FIELD_SEPARATOR___<blockquote>Test</blockquote>'''
    headers = {"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {"id": "test-page-id"}

def test_webhook_post_notion_api_error(test_client, monkeypatch):
    """NotionAPIエラーのテスト"""
    # NotionServiceのcreate_pageメソッドをモック（エラーを発生させる）
    def mock_create_page(self, data):
        raise NotionAPIException("Failed to create Notion page", details={"error": "Failed to create Notion page"})

    # モックを適用
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)

    # フィールドの順序: text, userName, linkToTweet, createdAt, tweetEmbedCode
    raw_body = '''This is a test
tweet with "quotes"___POST_FIELD_SEPARATOR___testuser___POST_FIELD_SEPARATOR___https://twitter.com/testuser/status/123456789___POST_FIELD_SEPARATOR___2025-02-10T13:35:49Z___POST_FIELD_SEPARATOR___<blockquote>Test
Tweet</blockquote>'''
    
    headers = {"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers=headers
    )
    assert response.status_code == 500
    assert response.json() == {
        "message": "Failed to create Notion page",
        "details": {"error": "Failed to create Notion page"}
    }

def test_webhook_post_empty_text(test_client):
    """空のテキストフィールドのテスト"""
    # フィールドの順序: text, userName, linkToTweet, createdAt, tweetEmbedCode
    raw_body = '''___POST_FIELD_SEPARATOR___testuser___POST_FIELD_SEPARATOR___https://twitter.com/testuser/status/123456789___POST_FIELD_SEPARATOR___2025-02-10T13:35:49Z___POST_FIELD_SEPARATOR___<blockquote>Test Tweet</blockquote>'''

    headers = {"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "message": "Text field cannot be empty",
        "details": {}
    }

def test_webhook_without_api_key(test_client):
    """API Keyなしのリクエストのテスト"""
    response = test_client.get("/webhook")
    assert response.status_code == 401
    assert response.json() == {
        "detail": {
            "message": "Invalid API Key"
        }
    }

def test_webhook_with_invalid_api_key(test_client):
    """不正なAPI Keyのテスト"""
    headers = {"X-API-Key": "invalid-key"}
    response = test_client.get("/webhook", headers=headers)
    assert response.status_code == 401
    assert response.json() == {
        "detail": {
            "message": "Invalid API Key"
        }
    }
