"""
Endpoints de administración para inicialización del sistema
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
import sys

# Importar scripts de inicialización
sys.path.insert(0, '/app')
from database import SessionLocal, engine, Base, get_db
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
        
        # Poblar regiones (jerárquicas: CCAA -> Provincias)
        logger.info("Obteniendo regiones desde BDNS...")
        regiones_data = await bdns.get_regiones()
        regiones_count = 0
        
        if regiones_data:
            def process_region(r_data, tipo="CCAA"):
                nonlocal regiones_count
                # La API devuelve "descripcion" con formato "ES11 - GALICIA"
                descripcion = r_data.get("descripcion", "")
                partes = descripcion.split(" - ", 1)
                codigo = partes[0].strip() if len(partes) > 0 else str(r_data.get("id"))
                nombre = partes[1].strip() if len(partes) > 1 else descripcion
                
                # Verificar si ya existe
                exists = db.query(Region).filter(Region.id == r_data.get("id")).first()
                
                if not exists:
                    region = Region(
                        id=r_data.get("id"),
                        codigo=codigo,
                        nombre=nombre,
                        tipo=tipo
                    )
                    db.add(region)
                    regiones_count += 1
                
                # Procesar children (provincias)
                for child in r_data.get("children", []):
                    process_region(child, tipo="Provincia")
            
            for r in regiones_data:
                process_region(r, tipo="CCAA")
            
            db.commit()
            logger.info(f"✓ {regiones_count} regiones cargadas")
        
        # Poblar finalidades
        logger.info("Obteniendo finalidades desde BDNS...")
        finalidades_data = await bdns.get_finalidades()
        finalidades_count = 0
        
        if finalidades_data:
            for fin_data in finalidades_data:
                # La API solo devuelve "descripcion" (sin código separado)
                descripcion = fin_data.get("descripcion", "")
                
                exists = db.query(Finalidad).filter(Finalidad.id == fin_data.get("id")).first()
                
                if not exists:
                    finalidad = Finalidad(
                        id=fin_data.get("id"),
                        codigo=None,  # No hay código en la API de BDNS
                        nombre=descripcion,
                        descripcion=descripcion
                    )
                    db.add(finalidad)
                    finalidades_count += 1
            
            db.commit()
            logger.info(f"✓ {finalidades_count} finalidades cargadas")
        
        # Para áreas temáticas, usamos las finalidades como proxy
        # (BDNS no tiene un endpoint específico de áreas temáticas)
        logger.info("Creando áreas temáticas predefinidas...")
        areas_predefinidas = [
            {"nombre": "Investigación Científica", "descripcion": "Proyectos de investigación básica y aplicada"},
            {"nombre": "Desarrollo Tecnológico", "descripcion": "Desarrollo de nuevas tecnologías y procesos"},
            {"nombre": "Innovación Empresarial", "descripcion": "Innovación en empresas y emprendimiento"},
            {"nombre": "Formación e Investigadores", "descripcion": "Formación de personal investigador"},
            {"nombre": "Infraestructuras Científicas", "descripcion": "Equipamiento e infraestructuras de I+D+i"},
        ]
        areas_count = 0
        
        for area_data in areas_predefinidas:
            exists = db.query(AreaTematica).filter(
                AreaTematica.nombre == area_data['nombre']
            ).first()
            
            if not exists:
                area = AreaTematica(
                    nombre=area_data['nombre'],
                    descripcion=area_data['descripcion']
                )
                db.add(area)
                areas_count += 1
        
        db.commit()
        logger.info(f"✓ {areas_count} áreas temáticas cargadas")
        
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


@router.get("/test-bdns")
async def test_bdns():
    """
    Prueba la API de BDNS para ver qué datos devuelve
    """
    try:
        bdns = BDNSService()
        
        # Probar regiones
        logger.info("Probando API de regiones...")
        regiones_data = await bdns.get_regiones()
        
        # Probar finalidades
        logger.info("Probando API de finalidades...")
        finalidades_data = await bdns.get_finalidades()
        
        return {
            "status": "success",
            "bdns_api_url": bdns.base_url,
            "regiones": {
                "count": len(regiones_data) if regiones_data else 0,
                "sample": regiones_data[:3] if regiones_data else [],
                "first_item": regiones_data[0] if regiones_data else None
            },
            "finalidades": {
                "count": len(finalidades_data) if finalidades_data else 0,
                "sample": finalidades_data[:3] if finalidades_data else [],
                "first_item": finalidades_data[0] if finalidades_data else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error al probar BDNS: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/sync-subvenciones")
async def sync_subvenciones_manual():
    """
    Forzar sincronización manual de subvenciones desde BDNS
    ⚠️ Esto ejecuta la tarea completa: obtener, guardar, crear eventos y notificar
    """
    from tasks.sync_subvenciones import fetch_subvenciones_bdns, guardar_subvenciones, crear_eventos_calendar, enviar_notificaciones
    
    db = SessionLocal()
    
    try:
        logger.info("=" * 80)
        logger.info("🔄 Iniciando sincronización manual de subvenciones...")
        logger.info("=" * 80)
        
        # 1. Obtener subvenciones de BDNS
        nuevas_subvenciones = await fetch_subvenciones_bdns(db)
        
        if not nuevas_subvenciones:
            logger.info("ℹ️  No se encontraron nuevas subvenciones")
            return {
                "status": "success",
                "message": "No se encontraron nuevas subvenciones"
            }
        
        logger.info(f"✓ {len(nuevas_subvenciones)} nuevas subvenciones obtenidas")
        
        # 2. Guardar en base de datos
        subvenciones_guardadas = guardar_subvenciones(db, nuevas_subvenciones)
        logger.info(f"✓ {len(subvenciones_guardadas)} subvenciones guardadas en BD")
        
        # 3. Crear eventos en Google Calendar
        crear_eventos_calendar(subvenciones_guardadas)
        
        # 4. Enviar notificaciones a usuarios
        enviar_notificaciones(db, subvenciones_guardadas)
        
        logger.info("=" * 80)
        logger.info("✅ Sincronización completada exitosamente")
        logger.info("=" * 80)
        
        return {
            "status": "success",
            "message": f"Sincronización completada: {len(subvenciones_guardadas)} subvenciones procesadas"
        }
        
    except Exception as e:
        logger.error(f"❌ Error en sincronización: {e}")
        db.rollback()
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }
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


@router.post("/ejecutar-migracion")
async def ejecutar_migracion(db: Session = Depends(get_db)):
    """
    Ejecutar migración completa para añadir todas las columnas necesarias
    ⚠️ Ejecutar una sola vez después del deploy
    """
    try:
        from sqlalchemy import text
        
        logger.info("🔧 Iniciando migración de base de datos...")
        
        migration_queries = [
            # Columnas para subvenciones
            "ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS organo_nivel1 VARCHAR(300);",
            "ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS organo_nivel2 VARCHAR(300);",
            "ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS organo_nivel3 VARCHAR(300);",
            "ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS tipo_convocatoria VARCHAR(200);",
            "ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS instrumentos JSON;",
            "ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS sectores JSON;",
            
            # Índices
            "CREATE INDEX IF NOT EXISTS idx_subvenciones_organo_nivel1 ON subvenciones (organo_nivel1);",
            "CREATE INDEX IF NOT EXISTS idx_subvenciones_organo_nivel2 ON subvenciones (organo_nivel2);",
            "CREATE INDEX IF NOT EXISTS idx_subvenciones_organo_nivel3 ON subvenciones (organo_nivel3);",
            "CREATE INDEX IF NOT EXISTS idx_subvenciones_tipo_convocatoria ON subvenciones (tipo_convocatoria);",
            "CREATE INDEX IF NOT EXISTS idx_subvenciones_finalidad_nombre ON subvenciones (finalidad_nombre);",
            
            # Columna para suscripciones
            "ALTER TABLE suscripciones ADD COLUMN IF NOT EXISTS filtros_json JSON;",
        ]
        
        results = []
        for query in migration_queries:
            try:
                db.execute(text(query))
                results.append({"query": query[:50] + "...", "status": "✓"})
                logger.info(f"✓ {query[:60]}")
            except Exception as e:
                results.append({"query": query[:50] + "...", "status": f"✗ {str(e)}"})
                logger.warning(f"⚠️ {query[:60]} - {e}")
        
        db.commit()
        
        logger.success("✅ Migración completada")
        
        return {
            "status": "success",
            "message": "Migración ejecutada exitosamente",
            "details": results
        }
        
    except Exception as e:
        logger.error(f"❌ Error al ejecutar migración: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al ejecutar migración: {str(e)}"
        )


@router.post("/actualizar-campos-subvenciones")
async def actualizar_campos_subvenciones():
    """
    Actualiza las subvenciones existentes para rellenar los nuevos campos
    ⚠️ Ejecutar después de la migración para poblar campos nuevos
    """
    db = SessionLocal()
    
    try:
        logger.info("🔄 Iniciando actualización de campos de subvenciones existentes...")
        
        bdns = BDNSService()
        
        # Obtener todas las subvenciones activas que no tienen organo_nivel1
        subvenciones = db.query(Subvencion).filter(
            Subvencion.activa == True,
            Subvencion.organo_nivel1 == None
        ).all()
        
        logger.info(f"📦 {len(subvenciones)} subvenciones a actualizar")
        
        actualizadas = 0
        errores = 0
        
        for subvencion in subvenciones:
            try:
                # Obtener detalle de BDNS
                detalle = await bdns.get_convocatoria_detalle(subvencion.id_bdns)
                parsed = bdns.parse_convocatoria_detalle(detalle)
                
                # Actualizar campos nuevos
                subvencion.organo_nivel1 = parsed.get("organo_nivel1")
                subvencion.organo_nivel2 = parsed.get("organo_nivel2")
                subvencion.organo_nivel3 = parsed.get("organo_nivel3")
                subvencion.tipo_convocatoria = parsed.get("tipo_convocatoria")
                subvencion.instrumentos = parsed.get("instrumentos")
                subvencion.sectores = parsed.get("sectores")
                
                db.add(subvencion)
                actualizadas += 1
                
                if actualizadas % 10 == 0:
                    db.commit()
                    logger.info(f"  ✓ {actualizadas}/{len(subvenciones)} actualizadas")
                
            except Exception as e:
                logger.error(f"  ✗ Error actualizando {subvencion.id_bdns}: {e}")
                errores += 1
                continue
        
        db.commit()
        
        logger.success(f"✅ Actualización completada: {actualizadas} actualizadas, {errores} errores")
        
        return {
            "status": "success",
            "message": f"Campos actualizados exitosamente",
            "actualizadas": actualizadas,
            "errores": errores,
            "total": len(subvenciones)
        }
        
    except Exception as e:
        logger.error(f"❌ Error al actualizar campos: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar campos: {str(e)}"
        )
    finally:
        db.close()