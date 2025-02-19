from typing import Any, Dict, Optional

class AppException(Exception):
    """アプリケーションの基本例外クラス"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

class NotionAPIException(AppException):
    """NotionAPIの例外クラス"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, 500, details)

class ValidationException(AppException):
    """バリデーション関連の例外"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=422,
            details=details
        )

class ConfigurationException(AppException):
    """設定関連の例外"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            details=details
        )
