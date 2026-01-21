"""
Endpoints de administración para inicialización del sistema
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
import sys

# Importar scripts de inicialización
sys.path.insert(0, '/app')
from database import SessionLocal, engine, Base
from models import Subvencion, Usuario, Suscripcion, NotificacionEnviada
from models.catalogo import Region, AreaTematica, Finalidad
from services.bdns_service import BDNSService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/init-database")
async def init_database():
    """
    Inicializa el esquema de la base de datos
    ⚠️ Solo ejecutar una vez
    """
    try:
        logger.info("Iniciando creación de tablas...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        logger.info("✓ Tablas creadas exitosamente")
        
        return {
            "status": "success",
            "message": "Base de datos inicializada correctamente",
            "tables": [
                "usuarios",
                "suscripciones",
                "subvenciones",
                "notificaciones_enviadas",
                "regiones",
                "areas_tematicas",
                "finalidades"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al inicializar base de datos: {str(e)}"
        )


@router.post("/populate-catalogs")
async def populate_catalogs():
    """
    Pobla los catálogos desde la API de BDNS
    ⚠️ Ejecutar después de init-database
    """
    db = SessionLocal()
    
    try:
        logger.info("Iniciando población de catálogos...")
        bdns = BDNSService()
        
        # Poblar regiones
        logger.info("Obteniendo regiones desde BDNS...")
        regiones_data = bdns.obtener_regiones()
        
        if regiones_data:
            for region_data in regiones_data:
                # Verificar si ya existe
                exists = db.query(Region).filter(
                    Region.codigo == region_data.get('code')
                ).first()
                
                if not exists:
                    region = Region(
                        codigo=region_data.get('code'),
                        nombre=region_data.get('description')
                    )
                    db.add(region)
            
            db.commit()
            logger.info(f"✓ {len(regiones_data)} regiones cargadas")
        
        # Poblar áreas temáticas
        logger.info("Obteniendo áreas temáticas desde BDNS...")
        areas_data = bdns.obtener_areas_tematicas()
        
        if areas_data:
            for area_data in areas_data:
                exists = db.query(AreaTematica).filter(
                    AreaTematica.codigo == area_data.get('code')
                ).first()
                
                if not exists:
                    area = AreaTematica(
                        codigo=area_data.get('code'),
                        nombre=area_data.get('description')
                    )
                    db.add(area)
            
            db.commit()
            logger.info(f"✓ {len(areas_data)} áreas temáticas cargadas")
        
        # Poblar finalidades
        logger.info("Obteniendo finalidades desde BDNS...")
        finalidades_data = bdns.obtener_finalidades()
        
        if finalidades_data:
            for fin_data in finalidades_data:
                exists = db.query(Finalidad).filter(
                    Finalidad.codigo == fin_data.get('code')
                ).first()
                
                if not exists:
                    finalidad = Finalidad(
                        codigo=fin_data.get('code'),
                        nombre=fin_data.get('description')
                    )
                    db.add(finalidad)
            
            db.commit()
            logger.info(f"✓ {len(finalidades_data)} finalidades cargadas")
        
        # Contar registros
        total_regiones = db.query(Region).count()
        total_areas = db.query(AreaTematica).count()
        total_finalidades = db.query(Finalidad).count()
        
        return {
            "status": "success",
            "message": "Catálogos poblados correctamente",
            "counts": {
                "regiones": total_regiones,
                "areas_tematicas": total_areas,
                "finalidades": total_finalidades
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error al poblar catálogos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al poblar catálogos: {str(e)}"
        )
    finally:
        db.close()


@router.get("/status")
async def admin_status():
    """
    Verifica el estado de la base de datos
    """
    db = SessionLocal()
    
    try:
        # Contar registros en cada tabla
        counts = {
            "usuarios": db.query(Usuario).count(),
            "suscripciones": db.query(Suscripcion).count(),
            "subvenciones": db.query(Subvencion).count(),
            "notificaciones_enviadas": db.query(NotificacionEnviada).count(),
            "regiones": db.query(Region).count(),
            "areas_tematicas": db.query(AreaTematica).count(),
            "finalidades": db.query(Finalidad).count()
        }
        
        # Determinar si está inicializada
        initialized = counts["regiones"] > 0 and counts["areas_tematicas"] > 0
        
        return {
            "status": "success",
            "database_initialized": initialized,
            "counts": counts,
            "next_steps": [] if initialized else [
                "1. POST /admin/init-database - Crear tablas",
                "2. POST /admin/populate-catalogs - Poblar catálogos"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error al verificar estado: {e}")
        return {
            "status": "error",
            "database_initialized": False,
            "error": str(e),
            "next_steps": [
                "1. POST /admin/init-database - Crear tablas",
                "2. POST /admin/populate-catalogs - Poblar catálogos"
            ]
        }
    finally:
        db.close()
