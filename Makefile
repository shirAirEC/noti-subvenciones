# Makefile para comandos comunes del proyecto

.PHONY: help install dev start stop restart logs clean build test

help:
	@echo "Comandos disponibles:"
	@echo "  make install      - Instalar dependencias"
	@echo "  make dev          - Ejecutar en modo desarrollo"
	@echo "  make start        - Iniciar con Docker Compose"
	@echo "  make stop         - Detener contenedores"
	@echo "  make restart      - Reiniciar contenedores"
	@echo "  make logs         - Ver logs"
	@echo "  make clean        - Limpiar contenedores y volúmenes"
	@echo "  make build        - Construir imágenes Docker"
	@echo "  make test         - Ejecutar tests"
	@echo "  make init-db      - Inicializar base de datos"
	@echo "  make populate     - Poblar catálogos"

# Desarrollo local
install:
	pip install -r requirements.txt

dev:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Docker
build:
	docker-compose build

start:
	docker-compose up -d
	@echo "✓ Aplicación iniciada"
	@echo "  Frontend: http://localhost"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

stop:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	@echo "✓ Contenedores y volúmenes eliminados"

# Base de datos
init-db:
	python backend/scripts/init_db.py

populate:
	python backend/scripts/populate_catalogs.py

setup-calendar:
	python backend/scripts/setup_calendar.py

# Testing
test:
	pytest tests/ -v

# Mantenimiento
sync-now:
	@echo "Ejecutando sincronización manual..."
	@python -c "from backend.tasks.sync_subvenciones import sync_subvenciones_task; sync_subvenciones_task()"
