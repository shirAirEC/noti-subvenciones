"""
Script para crear el calendario compartido de Google
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.calendar_service import CalendarService
from loguru import logger


def setup_calendar():
    """Crear calendario compartido para subvenciones"""
    try:
        calendar_service = CalendarService()
        
        # Crear calendario
        calendar_name = "Subvenciones de Investigación ULL"
        calendar_description = (
            "Calendario automático de subvenciones de investigación "
            "obtenidas de la Base de Datos Nacional de Subvenciones (BDNS). "
            "Actualizado diariamente."
        )
        
        calendar_id = calendar_service.create_calendar(
            name=calendar_name,
            description=calendar_description
        )
        
        logger.success(f"✓ Calendario creado exitosamente")
        logger.info(f"  ID del calendario: {calendar_id}")
        logger.info(f"  URL pública: {calendar_service.get_calendar_url()}")
        logger.info(f"  URL iCal: {calendar_service.get_ical_url()}")
        logger.info("")
        logger.info("Añade este ID al archivo .env:")
        logger.info(f"  CALENDAR_ID={calendar_id}")
        
    except Exception as e:
        logger.error(f"Error al crear calendario: {e}")
        raise


if __name__ == "__main__":
    setup_calendar()
