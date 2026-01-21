"""
Endpoints de catálogos
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from api import schemas
from models.catalogo import Region, AreaTematica

router = APIRouter(prefix="/api", tags=["catalogos"])


@router.get("/regiones", response_model=List[schemas.RegionSchema])
async def listar_regiones(db: Session = Depends(get_db)):
    """Obtener catálogo de regiones"""
    regiones = db.query(Region).order_by(Region.nombre).all()
    return regiones


@router.get("/areas", response_model=List[schemas.AreaTematicaSchema])
async def listar_areas_tematicas(db: Session = Depends(get_db)):
    """Obtener catálogo de áreas temáticas"""
    areas = db.query(AreaTematica).order_by(AreaTematica.nombre).all()
    return areas
