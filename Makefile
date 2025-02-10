.PHONY: run-local test clean deploy

# Variables
SERVICE_NAME := webhook-service
REGION := asia-northeast1

# Local development
run-local:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

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
deploy:
	gcloud run deploy $(SERVICE_NAME) \
		--source . \
		--region $(REGION) \
		--platform managed \
		--allow-unauthenticated \
		--service-account webhook-service@save-liked-post-notion.iam.gserviceaccount.com
