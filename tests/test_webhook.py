from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_hello_world_get():
    response = client.get("/webhook")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_hello_world_post():
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

def test_webhook_post_success():
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
