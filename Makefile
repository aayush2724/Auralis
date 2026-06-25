.PHONY: test lint format docker-up docker-down

test:
	pytest tests/ -v --tb=short --cov=src --cov-report=term-missing --cov-report=html:htmlcov

lint:
	ruff check src/ tests/
	black --check src/ tests/

format:
	ruff check --fix src/ tests/
	black src/ tests/

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v
