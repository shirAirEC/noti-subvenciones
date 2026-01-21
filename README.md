# Sistema de Notificaciones de Subvenciones BDNS

Sistema automatizado que consulta la Base de Datos Nacional de Subvenciones (BDNS) de España para detectar nuevas subvenciones de investigación, las publica en Google Calendar y notifica a usuarios suscritos por email.

## Características

- ✅ Consulta diaria automática de la API BDNS
- ✅ Filtros avanzados (región, área temática, presupuesto)
- ✅ Integración con Google Calendar compartido
- ✅ Notificaciones por email personalizadas
- ✅ Interfaz web simple para suscripciones
- ✅ Sin conocimientos técnicos requeridos para usuarios

## Requisitos

- Python 3.11+
- PostgreSQL 14+
- Cuenta de Google Cloud con Calendar API habilitada
- Servidor SMTP o Gmail con app password

## Instalación

### 1. Clonar repositorio y configurar entorno

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar base de datos

```bash
# Crear base de datos PostgreSQL
createdb subvenciones

# Ejecutar migraciones
python backend/scripts/init_db.py
```

### 3. Configurar Google Calendar API

1. Ir a [Google Cloud Console](https://console.cloud.google.com)
2. Crear proyecto nuevo
3. Habilitar Google Calendar API
4. Crear cuenta de servicio
5. Descargar credenciales JSON
6. Guardar en `credentials/service-account.json`
7. Compartir calendario con email de la cuenta de servicio

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Inicializar datos

```bash
# Poblar catálogos de BDNS
python backend/scripts/populate_catalogs.py

# Crear calendario compartido
python backend/scripts/setup_calendar.py
```

### 6. Ejecutar aplicación

```bash
# Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (servidor simple)
cd frontend
python -m http.server 8080
```

## Uso con Docker

```bash
docker-compose up -d
```

## Estructura del Proyecto

```
.
├── backend/
│   ├── api/              # Endpoints REST
│   ├── models/           # Modelos de base de datos
│   ├── services/         # Lógica de negocio
│   ├── tasks/            # Tareas programadas
│   ├── scripts/          # Scripts de utilidad
│   └── config.py         # Configuración
├── frontend/
│   ├── index.html        # Página principal
│   ├── styles.css        # Estilos
│   └── app.js            # JavaScript
├── credentials/          # Credenciales Google (no versionado)
├── docker-compose.yml    # Configuración Docker
└── requirements.txt      # Dependencias Python
```

## API Endpoints

- `POST /api/suscripcion/crear` - Crear suscripción
- `GET /api/suscripcion/{email}` - Obtener suscripción
- `PUT /api/suscripcion/{id}` - Actualizar filtros
- `DELETE /api/suscripcion/{id}` - Cancelar suscripción
- `GET /api/subvenciones` - Listar subvenciones activas
- `GET /api/regiones` - Catálogo de regiones
- `GET /api/areas` - Áreas temáticas

## Contribuir

Este proyecto es de código abierto. Las contribuciones son bienvenidas.

## Licencia

MIT License
