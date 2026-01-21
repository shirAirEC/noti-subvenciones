"""
Scheduler de tareas programadas
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from config import get_settings
from tasks.sync_subvenciones import sync_subvenciones_task

settings = get_settings()

scheduler = BackgroundScheduler()


def start_scheduler():
    """Iniciar scheduler de tareas"""
    if not scheduler.running:
        # Tarea diaria de sincronización
        scheduler.add_job(
            sync_subvenciones_task,
            trigger=CronTrigger(
                hour=settings.scheduler_hour,
                minute=settings.scheduler_minute
            ),
            id="sync_subvenciones",
            name="Sincronizar subvenciones de BDNS",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info(f"✓ Scheduler iniciado - Tarea diaria a las {settings.scheduler_hour:02d}:{settings.scheduler_minute:02d}")


def stop_scheduler():
    """Detener scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✓ Scheduler detenido")


def run_task_now():
    """Ejecutar tarea inmediatamente (para testing)"""
    logger.info("Ejecutando tarea manualmente...")
    sync_subvenciones_task()
