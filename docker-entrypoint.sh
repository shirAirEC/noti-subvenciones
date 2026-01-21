#!/bin/bash
set -e

echo "🐳 Iniciando contenedor backend..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U subvenciones_user -d subvenciones -c '\q' 2>/dev/null; do
  echo "  PostgreSQL no disponible aún, reintentando..."
  sleep 2
done

echo "✓ PostgreSQL está listo"

# Inicializar base de datos si es necesario
echo "🔧 Inicializando base de datos..."
python3 -c "
import sys
sys.path.insert(0, '/app')
from backend.scripts.init_db import init_database
try:
    init_database()
    print('✓ Base de datos inicializada')
except Exception as e:
    print(f'ℹ️  Base de datos ya existe o error: {e}')
" || echo "ℹ️  Tablas ya existen"

# Ejecutar comando proporcionado
echo "🚀 Iniciando aplicación..."
exec "$@"
