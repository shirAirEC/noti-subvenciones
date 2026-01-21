"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from config import get_settings
from api import suscripciones, subvenciones, catalogos, admin
from tasks.scheduler import start_scheduler, stop_scheduler

settings = get_settings()

# Configurar logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre de la aplicación"""
    logger.info("🚀 Iniciando aplicación...")
    
    # Configurar credenciales desde variable de entorno (Railway/Cloud)
    try:
        from scripts.setup_credentials import setup_credentials
        setup_credentials()
    except Exception as e:
        logger.warning(f"No se pudieron configurar credenciales automáticas: {e}")
    
    # Iniciar scheduler si está habilitado
    if settings.scheduler_enabled:
        start_scheduler()
        logger.info("✓ Scheduler iniciado")
    
    yield
    
    # Detener scheduler
    if settings.scheduler_enabled:
        stop_scheduler()
        logger.info("✓ Scheduler detenido")
    
    logger.info("👋 Aplicación detenida")


# Crear aplicación
app = FastAPI(
    title="Sistema de Notificaciones de Subvenciones BDNS",
    description="API para gestión de suscripciones y notificaciones de subvenciones de investigación",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
# Permitir Vercel (todos los subdominios), localhost y frontend_url configurado
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

# Añadir frontend_url si está configurado
if settings.frontend_url:
    allowed_origins.append(settings.frontend_url)

# Permitir todos los subdominios de Vercel para el proyecto
allowed_origins.extend([
    "https://noti-subvenciones.vercel.app",
    "https://noti-subvenciones-9ysq0eotg-shirairs-projects.vercel.app",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://noti-subvenciones.*\.vercel\.app",  # Wildcard para previews de Vercel
)

# Registrar routers
app.include_router(suscripciones.router)
app.include_router(subvenciones.router)
app.include_router(catalogos.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Sistema de Notificaciones de Subvenciones BDNS",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "scheduler": settings.scheduler_enabled
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
