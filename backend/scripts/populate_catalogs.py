"""
Script para poblar catálogos desde BDNS
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database import SessionLocal
from models.catalogo import Region, Finalidad, AreaTematica
from services.bdns_service import BDNSService
from loguru import logger


async def populate_catalogs():
    """Poblar catálogos de regiones y finalidades desde BDNS"""
    db = SessionLocal()
    bdns = BDNSService()
    
    try:
        # 1. Obtener y guardar finalidades
        logger.info("Obteniendo finalidades de BDNS...")
        finalidades = await bdns.get_finalidades()
        
        for fin in finalidades:
            finalidad = Finalidad(
                id=fin.get("id"),
                codigo=fin.get("codigo"),
                nombre=fin.get("nombre"),
                descripcion=fin.get("descripcion")
            )
            db.merge(finalidad)
        
        db.commit()
        logger.success(f"✓ {len(finalidades)} finalidades guardadas")
        
        # 2. Obtener y guardar regiones
        logger.info("Obteniendo regiones de BDNS...")
        regiones = await bdns.get_regiones()
        
        for reg in regiones:
            region = Region(
                id=reg.get("id"),
                codigo=reg.get("codigo"),
                nombre=reg.get("nombre"),
                tipo=reg.get("tipo")
            )
            db.merge(region)
        
        db.commit()
        logger.success(f"✓ {len(regiones)} regiones guardadas")
        
        # 3. Crear áreas temáticas personalizadas
        logger.info("Creando áreas temáticas personalizadas...")
        areas = [
            {
                "nombre": "Investigación Científica",
                "descripcion": "Subvenciones para investigación científica y desarrollo",
                "finalidades_bdns": "11,12,13"  # Ajustar según finalidades reales
            },
            {
                "nombre": "Desarrollo Tecnológico",
                "descripcion": "Proyectos de I+D+i y desarrollo tecnológico",
                "finalidades_bdns": "14,15"
            },
            {
                "nombre": "Innovación Empresarial",
                "descripcion": "Innovación aplicada y transferencia tecnológica",
                "finalidades_bdns": "16,17"
            },
            {
                "nombre": "Formación e Investigadores",
                "descripcion": "Becas y ayudas para formación de investigadores",
                "finalidades_bdns": "18,19"
            },
            {
                "nombre": "Infraestructuras Científicas",
                "descripcion": "Equipamiento e infraestructuras de investigación",
                "finalidades_bdns": "20,21"
            }
        ]
        
        for area_data in areas:
            area = db.query(AreaTematica).filter_by(nombre=area_data["nombre"]).first()
            if not area:
                area = AreaTematica(**area_data)
                db.add(area)
        
        db.commit()
        logger.success(f"✓ {len(areas)} áreas temáticas creadas")
        
        logger.success("✓ Catálogos poblados exitosamente")
        
    except Exception as e:
        logger.error(f"Error al poblar catálogos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(populate_catalogs())
