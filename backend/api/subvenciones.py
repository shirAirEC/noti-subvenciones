"""
Endpoints de subvenciones
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.api import schemas
from backend.models.subvencion import Subvencion

router = APIRouter(prefix="/api/subvenciones", tags=["subvenciones"])


@router.get("", response_model=List[schemas.Subvencion])
async def listar_subvenciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    activa: Optional[bool] = True,
    region_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Listar subvenciones activas"""
    query = db.query(Subvencion)
    
    if activa is not None:
        query = query.filter(Subvencion.activa == activa)
    
    if region_id:
        query = query.filter(Subvencion.region_id == region_id)
    
    query = query.order_by(Subvencion.fecha_fin_solicitud.desc())
    
    subvenciones = query.offset(skip).limit(limit).all()
    return subvenciones


@router.get("/{subvencion_id}", response_model=schemas.Subvencion)
async def obtener_subvencion(subvencion_id: int, db: Session = Depends(get_db)):
    """Obtener detalle de una subvención"""
    subvencion = db.query(Subvencion).filter(Subvencion.id == subvencion_id).first()
    
    if not subvencion:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subvención no encontrada"
        )
    
    return subvencion
