#!/usr/bin/env python
"""
Script para crear eventos de Google Calendar para subvenciones existentes
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import SessionLocal
from models import Subvencion
from services.calendar_service import CalendarService
from loguru import logger


def crear_eventos_faltantes():
    """Crear eventos de Calendar para subvenciones sin evento"""
    
    db = SessionLocal()
    
    try:
        # Obtener subvenciones sin evento de Calendar
        subvenciones = db.query(Subvencion).filter(
            Subvencion.calendar_event_id == None,
            Subvencion.fecha_fin_solicitud != None
        ).all()
        
        if not subvenciones:
            logger.info("✅ Todas las subvenciones ya tienen eventos de Calendar")
            return
        
        logger.info(f"📅 Creando eventos para {len(subvenciones)} subvenciones...")
        
        calendar_service = CalendarService()
        eventos_creados = 0
        
        for subvencion in subvenciones:
            try:
                event_id = calendar_service.create_event(
                    titulo=subvencion.titulo,
                    descripcion=subvencion.descripcion or "",
                    fecha_inicio=subvencion.fecha_inicio_solicitud or subvencion.fecha_fin_solicitud,
                    fecha_fin=subvencion.fecha_fin_solicitud,
                    url_bdns=subvencion.url_bdns,
                    presupuesto=float(subvencion.presupuesto_total) if subvencion.presupuesto_total else None,
                    region=subvencion.region_nombre,
                    organo=subvencion.organo_convocante,
                    url_bases_reguladoras=subvencion.url_bases_reguladoras,
                    url_sede_electronica=subvencion.url_sede_electronica
                )
                
                # Guardar ID del evento
                subvencion.calendar_event_id = event_id
                eventos_creados += 1
                
                logger.info(f"  ✅ {subvencion.id_bdns}: {subvencion.titulo[:60]}")
                
            except Exception as e:
                logger.error(f"  ❌ Error {subvencion.id_bdns}: {e}")
                continue
        
        db.commit()
        
        logger.success(f"\n✅ {eventos_creados} eventos creados exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🗓️  CREANDO EVENTOS DE GOOGLE CALENDAR")
    logger.info("=" * 80)
    
    crear_eventos_faltantes()
    
    logger.info("=" * 80)
    logger.info("✅ PROCESO COMPLETADO")
    logger.info("=" * 80)
