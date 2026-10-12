.PHONY: help install install-dev test lint format clean docker-build docker-run k8s-deploy helm-install

help:
	@echo "OrionAI - Production Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test             Run test suite"
	@echo "  make lint             Run linters"
	@echo "  make format           Format code"
	@echo "  make clean            Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-run       Run with docker-compose"
	@echo "  make docker-stop      Stop docker-compose"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-deploy       Deploy to Kubernetes"
	@echo "  make k8s-delete       Delete from Kubernetes"
	@echo "  make helm-install     Install with Helm"
	@echo "  make helm-uninstall   Uninstall Helm release"
	@echo ""
	@echo "Application:"
	@echo "  make run              Run application locally"
	@echo "  make ingest           Ingest sample documents"

install:
	pip install -r requirements-cpu.txt

install-dev:
	pip install -r requirements-cpu.txt
	pip install pytest pytest-cov pytest-asyncio flake8 black isort

test:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-api:
	pytest tests/api/ -v

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check .
	isort --check-only .

format:
	black .
	isort .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf build dist

docker-build:
	docker build -t orionai:cpu -f Dockerfile .
	docker build -t orionai:gpu -f Dockerfile.gpu .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

k8s-deploy:
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/

k8s-delete:
	kubectl delete -f k8s/

k8s-status:
	kubectl get pods -n orionai
	kubectl get svc -n orionai
	kubectl get hpa -n orionai

helm-install:
	helm install orionai ./helm/orionai --namespace orionai --create-namespace

helm-upgrade:
	helm upgrade orionai ./helm/orionai --namespace orionai

helm-uninstall:
	helm uninstall orionai --namespace orionai

helm-lint:
	helm lint helm/orionai

run:
	python main.py

ingest:
	python scripts/ingest_documents.py sample_docs/

validate:
	python scripts/validate_environment.py

benchmark:
	python scripts/run_benchmark.py
