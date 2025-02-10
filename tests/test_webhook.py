from fastapi.testclient import TestClient
from app.main import app
from app.exceptions import NotionAPIException

client = TestClient(app)

def test_hello_world_get():
    response = client.get("/webhook")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_hello_world_post(monkeypatch):
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
    
    tweet_data = {
        "text": "This is a test tweet",
        "userName": "testuser",
        "linkToTweet": "https://twitter.com/testuser/status/123456789",
        "createdAt": "2025-02-10T13:35:49Z",
        "tweetEmbedCode": "<blockquote>Test Tweet</blockquote>"
    }
    response = client.post("/webhook", json=tweet_data)
    assert response.status_code == 200
    assert "id" in response.json()

def test_webhook_post_success(monkeypatch):
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
    
    tweet_data = {
        "text": "This is a test tweet",
        "userName": "testuser",
        "linkToTweet": "https://twitter.com/testuser/status/123456789",
        "createdAt": "2025-02-10T13:35:49Z",
        "tweetEmbedCode": "<blockquote>Test Tweet</blockquote>"
    }
    response = client.post("/webhook", json=tweet_data)
    assert response.status_code == 200
    assert "id" in response.json()

def test_webhook_post_missing_required_fields():
    tweet_data = {
        "text": "This is a test tweet",
        # userName is missing
        "linkToTweet": "https://twitter.com/testuser/status/123456789",
        "createdAt": "2025-02-10T13:35:49Z",
        "tweetEmbedCode": "<blockquote>Test Tweet</blockquote>"
    }
    response = client.post("/webhook", json=tweet_data)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_webhook_post_invalid_date_format():
    tweet_data = {
        "text": "This is a test tweet",
        "userName": "testuser",
        "linkToTweet": "https://twitter.com/testuser/status/123456789",
        "createdAt": "invalid-date",  # Invalid date format
        "tweetEmbedCode": "<blockquote>Test Tweet</blockquote>"
    }
    response = client.post("/webhook", json=tweet_data)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_webhook_post_notion_api_error(monkeypatch):
    # NotionServiceのcreate_pageメソッドをモック（エラーを発生させる）
    def mock_create_page(self, data):
        raise NotionAPIException("Notion API error", 500, {"api": "error"})
    
    # モックを適用
    from app.services.notion_service import NotionService
    monkeypatch.setattr(NotionService, "create_page", mock_create_page)
    
    tweet_data = {
        "text": "This is a test tweet",
        "userName": "testuser",
        "linkToTweet": "https://twitter.com/testuser/status/123456789",
        "createdAt": "2025-02-10T13:35:49Z",
        "tweetEmbedCode": "<blockquote>Test Tweet</blockquote>"
    }
    response = client.post("/webhook", json=tweet_data)
    assert response.status_code == 500
    assert response.json() == {
        "message": "Notion API error",
        "details": {"api": "error"}
    }
