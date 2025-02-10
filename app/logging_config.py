import logging
import os
import sys
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from google.cloud.logging_v2.handlers import setup_logging

def setup_logger():
    """ロギングの設定を行います"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # フォーマッターの作成
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 環境に応じてハンドラーを設定
    if os.getenv('ENVIRONMENT') == 'production':
        # Cloud Loggingクライアントの設定
        client = google.cloud.logging.Client()
        handler = CloudLoggingHandler(client)
        setup_logging(handler)
    else:
        # 開発環境用のコンソールハンドラー
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# グローバルロガーの設定
logger = setup_logger()
