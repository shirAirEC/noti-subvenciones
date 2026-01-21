# Guía de Instalación

Esta guía te ayudará a instalar y configurar el Sistema de Notificaciones de Subvenciones BDNS.

## Requisitos Previos

### Opción 1: Docker (Recomendado)
- Docker 20.10+
- Docker Compose 2.0+

### Opción 2: Instalación Local
- Python 3.11+
- PostgreSQL 14+
- pip
- Cuenta de Google Cloud
- Servidor SMTP o Gmail

## Instalación con Docker (Recomendado)

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd noti-subvenciones
```

### 2. Configurar variables de entorno

```bash
cp .env.docker.example .env
```

Edita el archivo `.env` con tus credenciales:

```env
POSTGRES_PASSWORD=tu_password_seguro

# Google Calendar (obtener después del paso 3)
CALENDAR_ID=tu-calendar-id@group.calendar.google.com

# Email
EMAIL_FROM=noreply@tu-dominio.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
```

### 3. Configurar Google Cloud

#### 3.1 Crear proyecto en Google Cloud Console

1. Ve a https://console.cloud.google.com
2. Crea un nuevo proyecto
3. Habilita Google Calendar API

#### 3.2 Crear cuenta de servicio

1. En el menú lateral: APIs & Services → Credentials
2. Create Credentials → Service Account
3. Completa los detalles y crea
4. En la cuenta de servicio creada, ve a Keys
5. Add Key → Create New Key → JSON
6. Descarga el archivo JSON

#### 3.3 Guardar credenciales

```bash
mkdir -p credentials
mv ~/Downloads/service-account-*.json credentials/service-account.json
chmod 600 credentials/service-account.json
```

### 4. Crear calendario compartido

```bash
# Opción A: Con Docker
docker-compose run --rm backend python backend/scripts/setup_calendar.py

# Opción B: Local
python backend/scripts/setup_calendar.py
```

Copia el `CALENDAR_ID` generado y añádelo al archivo `.env`.

### 5. Compartir calendario

1. Ve a Google Calendar
2. Encuentra el calendario creado
3. Compartir con la cuenta de servicio (email en el JSON)
4. Dale permisos de "Make changes to events"

### 6. Iniciar aplicación

```bash
make build
make start
```

O directamente:

```bash
docker-compose up -d
```

### 7. Verificar instalación

- Frontend: http://localhost
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 8. Poblar catálogos

```bash
docker-compose exec backend python backend/scripts/populate_catalogs.py
```

## Instalación Local (Sin Docker)

### 1. Instalar PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@15

# Iniciar servicio
sudo systemctl start postgresql  # Linux
brew services start postgresql@15  # macOS
```

### 2. Crear base de datos

```bash
sudo -u postgres psql

postgres=# CREATE DATABASE subvenciones;
postgres=# CREATE USER subvenciones_user WITH PASSWORD 'tu_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE subvenciones TO subvenciones_user;
postgres=# \q
```

### 3. Configurar entorno Python

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Configurar Google Calendar

Sigue los pasos 3.1-3.3 de la instalación Docker.

### 6. Inicializar base de datos

```bash
python backend/scripts/init_db.py
python backend/scripts/populate_catalogs.py
python backend/scripts/setup_calendar.py
```

### 7. Iniciar aplicación

```bash
# Terminal 1: Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
python -m http.server 8080
```

## Configuración de Email

### Gmail con App Password

1. Habilitar 2FA en tu cuenta Google
2. Ir a: https://myaccount.google.com/apppasswords
3. Generar app password para "Mail"
4. Usar el password generado en `SMTP_PASSWORD`

### Otro servidor SMTP

Configura las variables:
- `SMTP_HOST`: servidor SMTP
- `SMTP_PORT`: puerto (587 para STARTTLS, 465 para SSL)
- `SMTP_USER`: usuario
- `SMTP_PASSWORD`: contraseña

## Verificación

### Test de API

```bash
curl http://localhost:8000/health
```

### Test de base de datos

```bash
docker-compose exec postgres psql -U subvenciones_user -d subvenciones -c "SELECT COUNT(*) FROM usuarios;"
```

### Ejecutar sincronización manual

```bash
make sync-now
```

O con Docker:

```bash
docker-compose exec backend python -c "from backend.tasks.sync_subvenciones import sync_subvenciones_task; sync_subvenciones_task()"
```

## Troubleshooting

### Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# Ver logs
docker-compose logs postgres
```

### Error de Google Calendar

- Verificar que el archivo de credenciales existe
- Verificar que el calendar_id está en .env
- Verificar que la cuenta de servicio tiene permisos en el calendario

### Error SMTP

- Verificar credenciales
- Para Gmail, verificar que App Password está habilitado
- Verificar configuración de firewall/puertos

## Próximos Pasos

1. Acceder a http://localhost
2. Crear una suscripción de prueba
3. Verificar email de confirmación
4. Ejecutar sincronización manual para probar

## Soporte

Para problemas o preguntas, consulta la documentación o abre un issue en el repositorio.
