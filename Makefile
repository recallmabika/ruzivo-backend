.PHONY: help setup run-backend scrape-kwayedza scrape-herald scrape-all docker-up docker-down lint test clean

help:
	@echo ""
	@echo "  Ruzivo — Multimodal Conversational Shona AI"
	@echo ""
	@echo "  setup             Create venv and install all dependencies"
	@echo "  run-backend       Start FastAPI dev server"
	@echo "  scrape-kwayedza   Run Kwayedza spider (primary Shona corpus)"
	@echo "  scrape-herald     Run Herald Shona spider (secondary corpus)"
	@echo "  scrape-all        Run all corpus spiders sequentially"
	@echo "  docker-up         Start all services via Docker Compose"
	@echo "  docker-down       Stop all services"
	@echo "  lint              Run flake8 + black check"
	@echo "  test              Run pytest"
	@echo "  clean             Remove __pycache__ and .pyc files"
	@echo ""

setup:
	bash scripts/setup.sh

run-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

scrape-kwayedza:
	cd pipeline/scrapers && scrapy crawl kwayedza

scrape-herald:
	cd pipeline/scrapers && scrapy crawl herald_shona

scrape-all:
	cd pipeline/scrapers && scrapy crawl kwayedza && scrapy crawl herald_shona

docker-up:
	docker compose -f infra/docker/docker-compose.yml up -d

docker-down:
	docker compose -f infra/docker/docker-compose.yml down

lint:
	.venv/bin/flake8 backend/ pipeline/ rag/ --max-line-length=100
	.venv/bin/black --check backend/ pipeline/ rag/

test:
	.venv/bin/pytest backend/tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true
