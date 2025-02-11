import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(autouse=True)
def setup_env():
    """テスト環境のセットアップ"""
    # テスト用のAPI Keyを環境変数に設定
    os.environ["WEBHOOK_API_KEY"] = "test-api-key"
    yield
    # テスト後にAPI Keyを削除
    os.environ.pop("WEBHOOK_API_KEY", None)

@pytest.fixture
def test_client():
    """テストクライアントを提供するフィクスチャ"""
    return TestClient(app)
