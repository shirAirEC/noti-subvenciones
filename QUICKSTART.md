# Inicio Rápido - 5 Minutos

Guía ultra-rápida para tener el sistema funcionando.

## Con Docker (Más Fácil)

```bash
# 1. Clonar y entrar
git clone <repositorio>
cd noti-subvenciones

# 2. Configurar entorno
cp .env.docker.example .env
nano .env  # Editar con tus datos

# 3. Añadir credenciales de Google
mkdir credentials
# Copiar tu service-account.json aquí

# 4. Iniciar
make build
make start

# 5. Poblar catálogos
docker-compose exec backend python backend/scripts/populate_catalogs.py

# ✓ Listo!
```

Acceder a:
- **Frontend**: http://localhost
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Sin Docker

```bash
# 1. Instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configurar PostgreSQL
sudo -u postgres psql
CREATE DATABASE subvenciones;
CREATE USER subvenciones_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE subvenciones TO subvenciones_user;
\q

# 3. Configurar .env
cp .env.example .env
nano .env

# 4. Inicializar
python backend/scripts/init_db.py
python backend/scripts/populate_catalogs.py

# 5. Ejecutar
# Terminal 1:
uvicorn backend.main:app --reload

# Terminal 2:
cd frontend && python -m http.server 8080
```

## Configuración Mínima en .env

```env
# Base de datos
DATABASE_URL=postgresql://subvenciones_user:password@localhost:5432/subvenciones

# Google (obtener de Google Cloud Console)
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
CALENDAR_ID=tu-calendar-id@group.calendar.google.com

# Email (usar Gmail con App Password)
EMAIL_FROM=tu@email.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@gmail.com
SMTP_PASSWORD=tu-app-password
```

## Obtener Credenciales Google

1. Ve a https://console.cloud.google.com
2. Crear proyecto → Habilitar Calendar API
3. Credentials → Create Service Account
4. Descargar JSON → Guardar en `credentials/service-account.json`
5. Ejecutar: `python backend/scripts/setup_calendar.py`
6. Copiar el CALENDAR_ID al `.env`

## Gmail App Password

1. Habilitar 2FA: https://myaccount.google.com/security
2. App Passwords: https://myaccount.google.com/apppasswords
3. Crear password para "Mail"
4. Copiar al `.env` como `SMTP_PASSWORD`

## Verificar Instalación

```bash
# Health check
curl http://localhost:8000/health

# Crear suscripción de prueba
curl -X POST http://localhost:8000/api/suscripcion/crear \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "nombre": "Usuario Test",
    "regiones": null,
    "areas_tematicas": [1,2]
  }'

# Ejecutar sincronización manual
make sync-now
```

## Comandos Útiles

```bash
make start      # Iniciar con Docker
make stop       # Detener
make logs       # Ver logs
make restart    # Reiniciar
make clean      # Limpiar todo
make sync-now   # Sincronizar ahora
```

## Troubleshooting Express

### No conecta a PostgreSQL
```bash
docker-compose ps postgres  # Verificar que está corriendo
docker-compose logs postgres  # Ver logs
```

### Error de Google Calendar
- Verificar que `service-account.json` existe
- Verificar que `CALENDAR_ID` está en `.env`
- Compartir el calendario con el email de la cuenta de servicio

### Error de Email
- Para Gmail: verificar que App Password está habilitado
- Verificar credenciales en `.env`

## Siguiente Paso

Lee [INSTALL.md](INSTALL.md) para configuración completa y [DEPLOYMENT.md](DEPLOYMENT.md) para producción.

## ¿Necesitas Ayuda?

- 📖 Documentación completa: `README.md`
- 🐛 Reportar bug: Abrir Issue
- 💬 Preguntas: Abrir Discussion

¡Disfruta del sistema! 🎉
