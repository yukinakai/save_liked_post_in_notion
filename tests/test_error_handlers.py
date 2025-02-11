import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from starlette.middleware.errors import ServerErrorMiddleware
from app.exceptions import (
    AppException,
    NotionAPIException,
    ValidationException,
    ConfigurationException
)
from app.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    request_validation_exception_handler,
    general_exception_handler
)

@pytest.fixture
def test_app():
    app = FastAPI()
    
    # ミドルウェアを追加
    app.add_middleware(ServerErrorMiddleware, handler=general_exception_handler)
    
    # 例外ハンドラーの登録順序を修正
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    
    @app.get("/test-app-exception")
    async def test_app_exception():
        raise AppException("Test error", 400, {"test": "details"})
    
    @app.get("/test-notion-exception")
    async def test_notion_exception():
        raise NotionAPIException("Notion API error", details={"api": "error"})
    
    @app.get("/test-validation-exception")
    async def test_validation_exception():
        raise ValidationException("Validation error", {"field": "error"})
    
    @app.get("/test-config-exception")
    async def test_config_exception():
        raise ConfigurationException("Config error", {"config": "error"})
    
    @app.get("/test-general-exception")
    async def test_general_exception():
        raise Exception("General error")
    
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_app_exception_handler(client):
    response = client.get("/test-app-exception")
    assert response.status_code == 400
    assert response.json() == {
        "message": "Test error",
        "details": {"test": "details"}
    }

def test_notion_exception_handler(client):
    response = client.get("/test-notion-exception")
    assert response.status_code == 500
    assert response.json() == {
        "message": "Notion API error",
        "details": {"api": "error"}
    }

def test_validation_exception_handler(client):
    response = client.get("/test-validation-exception")
    assert response.status_code == 422
    assert response.json() == {
        "message": "Validation error",
        "details": {"field": "error"}
    }

def test_config_exception_handler(client):
    response = client.get("/test-config-exception")
    assert response.status_code == 500
    assert response.json() == {
        "message": "Config error",
        "details": {"config": "error"}
    }

def test_general_exception_handler(client):
    """一般的な例外のハンドラーのテスト"""
    with pytest.raises(Exception) as exc_info:
        client.get("/test-general-exception")
    assert str(exc_info.value) == "General error"
