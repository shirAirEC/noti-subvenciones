"""
Script para inicializar la base de datos
"""
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database import engine, Base
from models import (
    Subvencion, Usuario, Suscripcion, 
    NotificacionEnviada, Region, AreaTematica, Finalidad
)
from loguru import logger


def init_database():
    """Crear todas las tablas en la base de datos"""
    logger.info("Iniciando creación de tablas...")
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        logger.success("✓ Tablas creadas exitosamente")
        
        # Listar tablas creadas
        logger.info("Tablas creadas:")
        for table in Base.metadata.sorted_tables:
            logger.info(f"  - {table.name}")
            
    except Exception as e:
        logger.error(f"Error al crear tablas: {e}")
        raise


if __name__ == "__main__":
    init_database()
