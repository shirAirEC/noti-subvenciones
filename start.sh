#!/bin/bash

# Script de inicio para Railway
echo "🚀 Iniciando aplicación..."

# Configurar credenciales si existen en variable de entorno
if [ -n "$GOOGLE_CREDENTIALS_JSON" ]; then
    echo "📝 Configurando credenciales de Google..."
    python backend/scripts/setup_credentials.py
fi

# Inicializar base de datos
echo "🔧 Inicializando base de datos..."
python backend/scripts/init_db.py || echo "⚠️ Base de datos ya existe"

# Iniciar servidor
echo "✅ Iniciando servidor FastAPI..."
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
