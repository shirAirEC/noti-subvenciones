"""
Servicio de integración con Google Calendar
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from loguru import logger
from config import get_settings
import os
import json
from pathlib import Path

settings = get_settings()

SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarService:
    """Cliente para Google Calendar API"""
    
    def __init__(self):
        self.calendar_id = settings.calendar_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autenticar con cuenta de servicio"""
        try:
            # Intentar primero desde variable de entorno (Railway/Cloud)
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            
            if credentials_json:
                logger.info("Usando credenciales desde variable de entorno GOOGLE_CREDENTIALS_JSON")
                credentials_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=SCOPES
                )
            else:
                # Fallback: usar archivo local
                logger.info(f"Usando credenciales desde archivo: {settings.google_service_account_file}")
                credentials = service_account.Credentials.from_service_account_file(
                    settings.google_service_account_file,
                    scopes=SCOPES
                )
            
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("✓ Autenticación con Google Calendar exitosa")
        except Exception as e:
            logger.error(f"Error al autenticar con Google Calendar: {e}")
            raise
    
    def create_calendar(self, name: str, description: str) -> str:
        """
        Crear un calendario nuevo
        
        Args:
            name: Nombre del calendario
            description: Descripción del calendario
            
        Returns:
            ID del calendario creado
        """
        calendar = {
            'summary': name,
            'description': description,
            'timeZone': 'Europe/Madrid'
        }
        
        try:
            created_calendar = self.service.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar['id']
            
            # Hacer el calendario público
            rule = {
                'scope': {
                    'type': 'default'
                },
                'role': 'reader'
            }
            self.service.acl().insert(calendarId=calendar_id, body=rule).execute()
            
            logger.success(f"✓ Calendario creado: {calendar_id}")
            return calendar_id
            
        except HttpError as error:
            logger.error(f"Error al crear calendario: {error}")
            raise
    
    def create_event(
        self,
        titulo: str,
        descripcion: str,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        url_bdns: str,
        presupuesto: Optional[float] = None,
        region: Optional[str] = None,
        organo: Optional[str] = None,
        url_bases_reguladoras: Optional[str] = None,
        url_sede_electronica: Optional[str] = None
    ) -> str:
        """
        Crear evento de subvención en el calendario
        
        Args:
            titulo: Título de la subvención
            descripcion: Descripción detallada
            fecha_inicio: Fecha de inicio de la convocatoria
            fecha_fin: Fecha de cierre de la convocatoria
            url_bdns: URL en BDNS
            presupuesto: Presupuesto total (opcional)
            region: Región de impacto (opcional)
            organo: Órgano convocante (opcional)
            
        Returns:
            ID del evento creado
        """
        # Construir descripción enriquecida
        description_parts = [descripcion or ""]
        
        if organo:
            description_parts.append(f"\n\n📋 Órgano convocante: {organo}")
        
        if region:
            description_parts.append(f"\n🌍 Región: {region}")
        
        if presupuesto:
            description_parts.append(f"\n💰 Presupuesto: {presupuesto:,.2f} €")
        
        description_parts.append(f"\n\n🔗 ENLACES:")
        description_parts.append(f"\n• Ficha BDNS: {url_bdns}")
        
        if url_bases_reguladoras:
            description_parts.append(f"\n• Bases reguladoras: {url_bases_reguladoras}")
        
        if url_sede_electronica:
            description_parts.append(f"\n• Sede electrónica: {url_sede_electronica}")
        
        description_parts.append(f"\n\n⚠️ IMPORTANTE: Fecha límite de solicitud")
        
        full_description = "".join(description_parts)
        
        # Crear evento
        event = {
            'summary': f"🔔 {titulo}",
            'description': full_description,
            'start': {
                'date': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else fecha_fin.strftime('%Y-%m-%d'),
                'timeZone': 'Europe/Madrid',
            },
            'end': {
                'date': fecha_fin.strftime('%Y-%m-%d'),
                'timeZone': 'Europe/Madrid',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 7 * 24 * 60},   # 7 días antes
                    {'method': 'email', 'minutes': 3 * 24 * 60},   # 3 días antes
                    {'method': 'popup', 'minutes': 1 * 24 * 60},   # 1 día antes
                    {'method': 'email', 'minutes': 1 * 24 * 60},   # 1 día antes
                    {'method': 'popup', 'minutes': 2 * 60},        # 2 horas antes
                ],
            },
            'colorId': '9',  # Azul para subvenciones
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            event_id = created_event['id']
            logger.info(f"✓ Evento creado en Calendar: {event_id} - {titulo[:50]}")
            return event_id
            
        except HttpError as error:
            logger.error(f"Error al crear evento: {error}")
            raise
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """
        Actualizar evento existente
        
        Args:
            event_id: ID del evento
            updates: Diccionario con campos a actualizar
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            event.update(updates)
            
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"✓ Evento actualizado: {event_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Error al actualizar evento: {error}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Eliminar evento del calendario
        
        Args:
            event_id: ID del evento
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"✓ Evento eliminado: {event_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Error al eliminar evento: {error}")
            return False
    
    def get_calendar_url(self) -> str:
        """
        Obtener URL pública del calendario
        
        Returns:
            URL para suscribirse al calendario
        """
        return f"https://calendar.google.com/calendar/embed?src={self.calendar_id}"
    
    def get_ical_url(self) -> str:
        """
        Obtener URL iCal para suscripción
        
        Returns:
            URL iCal
        """
        return f"https://calendar.google.com/calendar/ical/{self.calendar_id}/public/basic.ics"
