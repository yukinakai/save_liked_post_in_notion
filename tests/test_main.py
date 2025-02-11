from fastapi.testclient import TestClient
from datetime import datetime
import pytest
from dotenv import load_dotenv
from app.main import app
from app.exceptions import ValidationException

# テスト用の環境変数を読み込む
load_dotenv(".env.test")

@pytest.fixture
def test_client():
    return TestClient(app)

def test_root(test_client):
    """ルートエンドポイントのテスト"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Save Liked Post in Notion API"}

def test_webhook_get(test_client):
    """GETリクエストのテスト"""
    headers = {"X-API-Key": "test-api-key"}
    response = test_client.get("/webhook", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_webhook_post_with_invalid_date(test_client):
    """不正な日付フォーマットのテスト"""
    # フィールドの順序: text, userName, linkToTweet, createdAt
    raw_body = '''Test tweet___POST_FIELD_SEPARATOR___test_user___POST_FIELD_SEPARATOR___https://twitter.com/test_user/status/123456789___POST_FIELD_SEPARATOR___invalid-date'''
    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    )
    assert response.status_code == 422
    assert response.json() == {
        "message": "Invalid date format. Expected ISO format.",
        "details": {}
    }

def test_webhook_post_with_empty_text(test_client):
    """空のテキストフィールドのテスト"""
    # フィールドの順序: text, userName, linkToTweet, createdAt
    raw_body = '''___POST_FIELD_SEPARATOR___test_user___POST_FIELD_SEPARATOR___https://twitter.com/test_user/status/123456789___POST_FIELD_SEPARATOR___2025-02-10T13:35:49Z'''
    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    )
    assert response.status_code == 422
    assert response.json() == {
        "message": "Text field cannot be empty",
        "details": {}
    }

def test_webhook_post_success(test_client, monkeypatch):
    """正常なPOSTリクエストのテスト"""
    # NotionServiceのcreate_pageメソッドをモック
    def mock_create_page(self, data):
        return {"id": "test-page-id"}

    # NotionServiceのadd_tweet_urlメソッドをモック
    def mock_add_tweet_url(self, page_id, link_to_tweet):
        return {"id": page_id}

    # モックを適用
    from app.services.notion_service import NotionService
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)
    monkeypatch.setattr(NotionService, "add_tweet_url", mock_add_tweet_url)

    from datetime import datetime
    # フィールドの順序: text, userName, linkToTweet, createdAt
    raw_body = f'''Test tweet with
line breaks and "quotes"___POST_FIELD_SEPARATOR___test_user___POST_FIELD_SEPARATOR___https://twitter.com/test_user/status/123456789___POST_FIELD_SEPARATOR___{datetime.now().isoformat()}'''

    response = test_client.post(
        "/webhook",
        content=raw_body.encode(),
        headers={"X-API-Key": "test-api-key", "Content-Type": "text/plain"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": "test-page-id"}
