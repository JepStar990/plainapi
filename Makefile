.PHONY: help install dev test clean scrape vectorstore run docker-up docker-down

help:
	@echo "PlainAPI - AI-powered API Simplification System"
	@echo ""
	@echo "Commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Install development dependencies"
	@echo "  test        Run tests"
	@echo "  clean       Clean up generated files"
	@echo "  scrape      Scrape NASA documentation"
	@echo "  vectorstore Create vector store from scraped data"
	@echo "  run         Run the FastAPI server"
	@echo "  docker-up   Start all services with Docker"
	@echo "  docker-down Stop all Docker services"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

test:
	python -m pytest tests/ -v

clean:
	rm -rf data/ logs/ __pycache__/ *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

scrape:
	python scripts/scrape_nasa_docs.py

vectorstore:
	python scripts/create_vector_store.py

run:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

format:
	black src/ scripts/ tests/
	flake8 src/ scripts/ tests/

type-check:
	mypy src/

lint: format type-check
