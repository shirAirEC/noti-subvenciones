"""
Endpoints de calendario
"""
from fastapi import APIRouter
from services.calendar_service import CalendarService
from loguru import logger

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("/url")
async def get_calendar_url():
    """
    Obtener URL pública del calendario de Google
    """
    try:
        calendar_service = CalendarService()
        calendar_url = calendar_service.get_calendar_url()
        ical_url = calendar_service.get_ical_url()
        
        return {
            "url": calendar_url,
            "ical_url": ical_url,
            "calendar_id": calendar_service.calendar_id
        }
    except Exception as e:
        logger.error(f"Error al obtener URL del calendario: {e}")
        return {
            "url": "#",
            "ical_url": "#",
            "error": "No se pudo obtener la URL del calendario"
        }
