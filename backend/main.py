"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from config import get_settings
from api import suscripciones, subvenciones, catalogos
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(suscripciones.router)
app.include_router(subvenciones.router)
app.include_router(catalogos.router)


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
