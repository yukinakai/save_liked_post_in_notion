.PHONY: build deploy run-local test clean

# 環境変数
PROJECT_ID := $(shell gcloud config get-value project)
REGION := asia-northeast1
SERVICE_NAME := webhook-service

# ローカル開発
run-local:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# テスト実行
test:
	pytest

# Dockerイメージのビルド
build:
	docker build -t gcr.io/$(PROJECT_ID)/$(SERVICE_NAME) .

# Cloud Runへのデプロイ
deploy: build
	docker push gcr.io/$(PROJECT_ID)/$(SERVICE_NAME)
	gcloud run deploy $(SERVICE_NAME) \
		--image gcr.io/$(PROJECT_ID)/$(SERVICE_NAME) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated

# Cloud Buildを使用したデプロイ
deploy-cloudbuild:
	gcloud builds submit --config cloudbuild.yaml

# ローカルのDockerコンテナを実行（テスト用）
run-docker: build
	docker run -p 8080:8080 gcr.io/$(PROJECT_ID)/$(SERVICE_NAME)

# クリーンアップ
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
