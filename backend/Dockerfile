# Dockerfile para Backend en Railway
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/credentials /app/logs

# Exponer puerto (Railway asigna dinámicamente)
EXPOSE $PORT

# Comando de inicio usando variable de entorno PORT de Railway
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
