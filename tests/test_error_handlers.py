import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.exceptions import (
    AppException,
    NotionAPIException,
    ValidationException,
    ConfigurationException
)
from app.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

@pytest.fixture
def test_app():
    app = FastAPI()
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    @app.get("/test-app-exception")
    async def test_app_exception():
        raise AppException("Test error", 400, {"test": "details"})
    
    @app.get("/test-notion-exception")
    async def test_notion_exception():
        raise NotionAPIException("Notion API error", 500, {"api": "error"})
    
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
    response = client.get("/test-general-exception")
    assert response.status_code == 500
    assert response.json() == {
        "message": "Internal server error",
        "details": {"error": "General error"}
    }
