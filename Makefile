.PHONY: help install run dev clean

help:
	@echo "StreamPulse Makefile commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make run      - Run FastAPI server (production mode)"
	@echo "  make dev      - Run FastAPI server (development mode with auto-reload)"
	@echo "  make clean    - Remove Python cache files"

install:
	uv sync

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
