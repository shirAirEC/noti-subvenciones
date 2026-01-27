"""
Tarea de sincronización de subvenciones
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from loguru import logger
from sqlalchemy.orm import Session

from database import SessionLocal
from models.subvencion import Subvencion
from models.usuario import Usuario
from models.suscripcion import Suscripcion
from models.notificacion_enviada import NotificacionEnviada
from services.bdns_service import BDNSService
from services.calendar_service import CalendarService
from services.email_service import EmailService

# Filtros configurados
ALLOWED_REGIONES = {
    "ESPAÑA", "ES - ESPAÑA", "CANARIAS", "ISLAS CANARIAS",
    "COMUNIDAD AUTONOMA DE CANARIAS", "COMUNIDAD AUTÓNOMA DE CANARIAS",
}

def sync_subvenciones_task():
    """
    Tarea principal de sincronización:
    1. Consultar API de BDNS
    2. Guardar nuevas subvenciones
    3. Crear eventos en Calendar
    4. Enviar notificaciones
    """
    logger.info("=" * 80)
    logger.info("🔄 Iniciando sincronización de subvenciones...")
    logger.info("=" * 80)
    
    db = SessionLocal()
    
    try:
        # 1. Obtener subvenciones de BDNS
        nuevas_subvenciones = asyncio.run(fetch_subvenciones_bdns(db))
        
        if not nuevas_subvenciones:
            logger.info("ℹ️  No se encontraron nuevas subvenciones")
            return
        
        logger.success(f"✓ {len(nuevas_subvenciones)} nuevas subvenciones obtenidas")
        
        # 2. Guardar en base de datos
        subvenciones_guardadas = guardar_subvenciones(db, nuevas_subvenciones)
        logger.success(f"✓ {len(subvenciones_guardadas)} subvenciones guardadas en BD")
        
        # 3. Crear eventos en Google Calendar
        crear_eventos_calendar(subvenciones_guardadas)
        
        # 4. Enviar notificaciones a usuarios
        enviar_notificaciones(db, subvenciones_guardadas)
        
        logger.success("=" * 80)
        logger.success("✅ Sincronización completada exitosamente")
        logger.success("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Error en sincronización: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def fetch_subvenciones_bdns(db: Session) -> List[Dict[str, Any]]:
    """Obtener subvenciones de BDNS API (listado + detalle)"""
    bdns = BDNSService()
    
    fecha_desde = datetime(2025, 1, 1)
    fecha_hasta = datetime(2026, 12, 31)
    
    logger.info(
        f"📅 Buscando subvenciones desde {fecha_desde.strftime('%d/%m/%Y')} hasta {fecha_hasta.strftime('%d/%m/%Y')}"
    )
    logger.info("🔎 Finalidad: INVESTIGACIÓN, DESARROLLO E INNOVACIÓN (17)")
    
    nuevas_subvenciones = []
    page = 0
    page_size = 100
    
    while True:
        resultado = await bdns.get_convocatorias(
            finalidad=17,
            fecha_desde=fecha_desde.date(),
            fecha_hasta=fecha_hasta.date(),
            page=page,
            page_size=page_size
        )
        
        convocatorias = resultado.get("convocatorias", [])
        total_elementos = resultado.get("totalElementos", 0)
        
        logger.info(f"📦 Página {page}: {len(convocatorias)} convocatorias (total disponibles: {total_elementos})")
        
        if not convocatorias:
            break
        
        for conv in convocatorias:
            id_bdns = str(conv.get("numeroConvocatoria"))
            if not id_bdns:
                continue
            
            existe = db.query(Subvencion).filter(Subvencion.id_bdns == id_bdns).first()
            if existe:
                continue
            
            try:
                detalle = await bdns.get_convocatoria_detalle(id_bdns)
                parsed_base = bdns.parse_convocatoria(conv)
                parsed_detalle = bdns.parse_convocatoria_detalle(detalle)
                
                subvencion_data = {**parsed_base, **parsed_detalle}
                
                # FILTRO 1: Debe tener fechas de solicitud
                if not subvencion_data.get("fecha_fin_solicitud"):
                    logger.debug(f"  ⏭️ {id_bdns}: Sin fecha fin de solicitud")
                    continue
                
                # FILTRO 2: Órgano del ámbito de Ciencia e Innovación (flexible)
                organo = subvencion_data.get("organo_convocante", "").upper()
                palabras_clave = ["CIENCIA", "INNOVACI", "INVESTIGACI", "I+D"]
                tiene_palabras_clave = any(palabra in organo for palabra in palabras_clave)
                
                if not tiene_palabras_clave:
                    logger.debug(f"  ⏭️ {id_bdns}: Órgano sin palabras clave I+D+i ({organo[:50]})")
                    continue
                
                # FILTRO 3: Regiones España/Canarias (si está especificada)
                regiones_detalle = [r.get('descripcion', '').upper() for r in detalle.get('regiones', [])]
                if regiones_detalle:  # Si hay regiones especificadas
                    if not any(r in ALLOWED_REGIONES or "ESPAÑA" in r or "CANARIAS" in r for r in regiones_detalle):
                        logger.debug(f"  ⏭️ {id_bdns}: Región no permitida ({regiones_detalle})")
                        continue
                
                logger.info(f"  ✅ {id_bdns}: {subvencion_data.get('titulo', '')[:60]}")
                nuevas_subvenciones.append(subvencion_data)
            except Exception as e:
                logger.error(f"Error al obtener detalle de convocatoria {id_bdns}: {e}")
                continue
        
        if len(convocatorias) < page_size:
            break
        page += 1
    
    return nuevas_subvenciones


def guardar_subvenciones(db: Session, subvenciones: List[Dict[str, Any]]) -> List[Subvencion]:
    """Guardar subvenciones en base de datos"""
    subvenciones_guardadas = []
    
    for sub_data in subvenciones:
        try:
            subvencion = Subvencion(**sub_data)
            db.add(subvencion)
            db.flush()
            subvenciones_guardadas.append(subvencion)
            
            logger.debug(f"  ✓ Guardada: {subvencion.titulo[:50]}...")
            
        except Exception as e:
            logger.error(f"Error al guardar subvención {sub_data.get('id_bdns')}: {e}")
            continue
    
    db.commit()
    return subvenciones_guardadas


def crear_eventos_calendar(subvenciones: List[Subvencion]):
    """Crear eventos en Google Calendar"""
    try:
        calendar_service = CalendarService()
        
        for subvencion in subvenciones:
            try:
                # Solo crear evento si tiene fecha de fin
                if not subvencion.fecha_fin_solicitud:
                    continue
                
                event_id = calendar_service.create_event(
                    titulo=subvencion.titulo,
                    descripcion=subvencion.descripcion or "",
                    fecha_inicio=subvencion.fecha_inicio_solicitud or subvencion.fecha_fin_solicitud,
                    fecha_fin=subvencion.fecha_fin_solicitud,
                    url_bdns=subvencion.url_bdns,
                    presupuesto=float(subvencion.presupuesto_total) if subvencion.presupuesto_total else None,
                    region=subvencion.region_nombre,
                    organo=subvencion.organo_convocante
                )
                
                # Guardar ID del evento
                subvencion.calendar_event_id = event_id
                
                logger.debug(f"  ✓ Evento creado para: {subvencion.titulo[:50]}...")
                
            except Exception as e:
                logger.error(f"Error al crear evento para {subvencion.id_bdns}: {e}")
                continue
        
        logger.success(f"✓ {len([s for s in subvenciones if s.calendar_event_id])} eventos creados en Calendar")
        
    except Exception as e:
        logger.error(f"Error al crear eventos en Calendar: {e}")


def enviar_notificaciones(db: Session, subvenciones: List[Subvencion]):
    """Enviar notificaciones a usuarios suscritos"""
    email_service = EmailService()
    calendar_service = CalendarService()
    calendar_url = calendar_service.get_calendar_url()
    
    # Obtener usuarios con suscripciones activas
    suscripciones = db.query(Suscripcion).filter(
        Suscripcion.activa == True,
        Suscripcion.notificar_email == True
    ).all()
    
    logger.info(f"📧 Enviando notificaciones a {len(suscripciones)} usuarios...")
    
    notificaciones_enviadas = 0
    
    for suscripcion in suscripciones:
        usuario = suscripcion.usuario
        
        if not usuario.confirmado:
            continue
        
        for subvencion in subvenciones:
            # Verificar si la subvención coincide con los filtros
            if not coincide_con_filtros(subvencion, suscripcion):
                continue
            
            # Verificar si ya se envió notificación
            ya_enviada = db.query(NotificacionEnviada).filter(
                NotificacionEnviada.usuario_id == usuario.id,
                NotificacionEnviada.subvencion_id == subvencion.id,
                NotificacionEnviada.enviada == True
            ).first()
            
            if ya_enviada:
                continue
            
            # Enviar email
            try:
                unsubscribe_url = f"{calendar_url}?unsubscribe={suscripcion.id}"
                
                subvencion_dict = {
                    "titulo": subvencion.titulo,
                    "descripcion": subvencion.descripcion,
                    "organo_convocante": subvencion.organo_convocante,
                    "region_nombre": subvencion.region_nombre,
                    "presupuesto_total": subvencion.presupuesto_total,
                    "fecha_fin_solicitud": subvencion.fecha_fin_solicitud,
                    "url_bdns": subvencion.url_bdns
                }
                
                enviado = email_service.send_nueva_subvencion(
                    to_email=usuario.email,
                    nombre_usuario=usuario.nombre,
                    subvencion=subvencion_dict,
                    calendar_url=calendar_url,
                    unsubscribe_url=unsubscribe_url
                )
                
                # Registrar notificación
                notif = NotificacionEnviada(
                    usuario_id=usuario.id,
                    subvencion_id=subvencion.id,
                    tipo="email",
                    enviada=enviado,
                    fecha_envio=datetime.utcnow() if enviado else None
                )
                db.add(notif)
                
                if enviado:
                    notificaciones_enviadas += 1
                
            except Exception as e:
                logger.error(f"Error al enviar notificación a {usuario.email}: {e}")
                continue
    
    db.commit()
    logger.success(f"✓ {notificaciones_enviadas} notificaciones enviadas")


def coincide_con_filtros(subvencion: Subvencion, suscripcion: Suscripcion) -> bool:
    """Verificar si una subvención coincide con los filtros de una suscripción"""
    
    # Filtro por región
    if suscripcion.regiones:
        if subvencion.region_id not in suscripcion.regiones:
            return False
    
    # Filtro por presupuesto
    if suscripcion.presupuesto_min:
        if not subvencion.presupuesto_total or subvencion.presupuesto_total < suscripcion.presupuesto_min:
            return False
    
    if suscripcion.presupuesto_max:
        if not subvencion.presupuesto_total or subvencion.presupuesto_total > suscripcion.presupuesto_max:
            return False
    
    # Filtro por área temática (mapear finalidad)
    if suscripcion.areas_tematicas:
        # TODO: Implementar mapeo de finalidades a áreas temáticas
        pass
    
    return True
