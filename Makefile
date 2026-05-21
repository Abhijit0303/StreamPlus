.PHONY: help install run dev clean docker-up docker-down docker-logs init-db

help:
	@echo "StreamPulse Makefile commands:"
	@echo ""
	@echo "Install & Setup:"
	@echo "  make install   - Install dependencies"
	@echo "  make init-db   - Initialize PostgreSQL database"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up   - Start Redis and PostgreSQL containers"
	@echo "  make docker-down - Stop and remove containers"
	@echo "  make docker-logs - View Docker logs"
	@echo ""
	@echo "Running:"
	@echo "  make run       - Run FastAPI server (production mode)"
	@echo "  make dev       - Run FastAPI server (development mode with auto-reload)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean     - Remove Python cache files"

install:
	uv sync

docker-up:
	docker-compose up -d
	@echo "✓ Redis and PostgreSQL started"

docker-down:
	docker-compose down -v
	@echo "✓ Containers stopped and removed"

docker-logs:
	docker-compose logs -f

init-db:
	.venv/Scripts/python.exe init_db.py

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
