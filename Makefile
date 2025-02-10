.PHONY: run-local test clean deploy

# Variables
SERVICE_NAME := webhook-service
REGION := asia-northeast1

# Local development
run-local: test
	@echo "Running unit tests before starting local server..."
	@if [ $$? -eq 0 ]; then \
		echo "Tests passed. Starting local server..."; \
		uvicorn app.main:app --reload --host 0.0.0.0 --port 8080; \
	else \
		echo "Tests failed. Local server start aborted."; \
		exit 1; \
	fi

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -r {} +

# Deploy to Cloud Run
deploy: test
	@echo "Running unit tests before deployment..."
	@if [ $$? -eq 0 ]; then \
		echo "Tests passed. Proceeding with deployment..."; \
		echo "Loading environment variables from .env file..."; \
		$(eval include .env) \
		gcloud run deploy $(SERVICE_NAME) \
			--source . \
			--region $(REGION) \
			--platform managed \
			--allow-unauthenticated \
			--service-account webhook-service@save-liked-post-notion.iam.gserviceaccount.com \
			--set-env-vars NOTION_API_KEY=$(NOTION_API_KEY),NOTION_DATABASE_ID=$(NOTION_DATABASE_ID); \
	else \
		echo "Tests failed. Deployment aborted."; \
		exit 1; \
	fi
