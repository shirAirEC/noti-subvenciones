"""
Endpoints de subvenciones
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, distinct
from typing import List, Optional
from datetime import datetime
from database import get_db
from api import schemas
from models.subvencion import Subvencion

router = APIRouter(prefix="/api/subvenciones", tags=["subvenciones"])


@router.get("", response_model=List[schemas.Subvencion])
async def listar_subvenciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    activa: Optional[bool] = True,
    organo: Optional[str] = None,
    tipo_convocatoria: Optional[str] = None,
    instrumento: Optional[str] = None,
    sector: Optional[str] = None,
    finalidad: Optional[str] = None,
    presupuesto_min: Optional[float] = None,
    keywords: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Listar subvenciones con filtros avanzados
    """
    query = db.query(Subvencion)
    
    if activa:
        query = query.filter(
            Subvencion.activa == True,
            Subvencion.fecha_fin_solicitud != None,
            Subvencion.fecha_fin_solicitud >= datetime.now()
        )
    
    if organo:
        query = query.filter(
            or_(
                Subvencion.organo_nivel1.ilike(f"%{organo}%"),
                Subvencion.organo_nivel2.ilike(f"%{organo}%"),
                Subvencion.organo_nivel3.ilike(f"%{organo}%"),
                Subvencion.organo_convocante.ilike(f"%{organo}%")
            )
        )
    
    if tipo_convocatoria:
        query = query.filter(Subvencion.tipo_convocatoria.ilike(f"%{tipo_convocatoria}%"))
    
    if instrumento:
        query = query.filter(Subvencion.instrumentos.astext.ilike(f"%{instrumento}%"))
    
    if sector:
        query = query.filter(Subvencion.sectores.astext.ilike(f"%{sector}%"))
    
    if finalidad:
        query = query.filter(Subvencion.finalidad_nombre.ilike(f"%{finalidad}%"))
    
    if presupuesto_min:
        query = query.filter(Subvencion.presupuesto_total >= presupuesto_min)
    
    if keywords:
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        if keyword_list:
            filters = []
            for keyword in keyword_list:
                filters.append(Subvencion.titulo.ilike(f"%{keyword}%"))
                filters.append(Subvencion.descripcion.ilike(f"%{keyword}%"))
            query = query.filter(or_(*filters))
    
    query = query.order_by(Subvencion.fecha_fin_solicitud.asc())
    
    subvenciones = query.offset(skip).limit(limit).all()
    return subvenciones


@router.get("/valores/organos", response_model=List[str])
async def listar_valores_organos(db: Session = Depends(get_db)):
    """Obtener lista única de órganos convocantes (nivel 1, 2, 3 y el más específico)"""
    organos_nivel1 = [o[0] for o in db.query(distinct(Subvencion.organo_nivel1)).filter(Subvencion.organo_nivel1 != None, Subvencion.organo_nivel1 != '').all()]
    organos_nivel2 = [o[0] for o in db.query(distinct(Subvencion.organo_nivel2)).filter(Subvencion.organo_nivel2 != None, Subvencion.organo_nivel2 != '').all()]
    organos_nivel3 = [o[0] for o in db.query(distinct(Subvencion.organo_nivel3)).filter(Subvencion.organo_nivel3 != None, Subvencion.organo_nivel3 != '').all()]
    organos_especificos = [o[0] for o in db.query(distinct(Subvencion.organo_convocante)).filter(Subvencion.organo_convocante != None, Subvencion.organo_convocante != '').all()]
    
    all_organos = sorted(list(set(organos_nivel1 + organos_nivel2 + organos_nivel3 + organos_especificos)))
    return all_organos


@router.get("/valores/tipos-convocatoria", response_model=List[str])
async def listar_valores_tipos_convocatoria(db: Session = Depends(get_db)):
    """Obtener lista única de tipos de convocatoria"""
    tipos = db.query(distinct(Subvencion.tipo_convocatoria)).filter(Subvencion.tipo_convocatoria != None, Subvencion.tipo_convocatoria != '').order_by(Subvencion.tipo_convocatoria).all()
    return [t[0] for t in tipos if t[0]]


@router.get("/valores/instrumentos", response_model=List[str])
async def listar_valores_instrumentos(db: Session = Depends(get_db)):
    """Obtener lista única de instrumentos de ayuda"""
    # Extraer valores de arrays JSON
    instrumentos_raw = db.query(Subvencion.instrumentos).filter(Subvencion.instrumentos != None).all()
    all_instrumentos = set()
    for row in instrumentos_raw:
        if row[0]:
            for item in row[0]:
                if isinstance(item, dict) and 'descripcion' in item:
                    all_instrumentos.add(item['descripcion'])
    return sorted(list(all_instrumentos))


@router.get("/valores/sectores", response_model=List[str])
async def listar_valores_sectores(db: Session = Depends(get_db)):
    """Obtener lista única de sectores económicos"""
    # Extraer valores de arrays JSON
    sectores_raw = db.query(Subvencion.sectores).filter(Subvencion.sectores != None).all()
    all_sectores = set()
    for row in sectores_raw:
        if row[0]:
            for item in row[0]:
                if isinstance(item, dict) and 'descripcion' in item:
                    all_sectores.add(item['descripcion'])
    return sorted(list(all_sectores))


@router.get("/valores/finalidades", response_model=List[str])
async def listar_valores_finalidades(db: Session = Depends(get_db)):
    """Obtener lista única de finalidades (política de gasto)"""
    finalidades = db.query(distinct(Subvencion.finalidad_nombre)).filter(Subvencion.finalidad_nombre != None, Subvencion.finalidad_nombre != '').order_by(Subvencion.finalidad_nombre).all()
    return [f[0] for f in finalidades if f[0]]


@router.get("/{subvencion_id}", response_model=schemas.Subvencion)
async def obtener_subvencion(subvencion_id: int, db: Session = Depends(get_db)):
    """Obtener detalle de una subvención"""
    subvencion = db.query(Subvencion).filter(Subvencion.id == subvencion_id).first()
    
    if not subvencion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subvención no encontrada"
        )
    
    return subvencion
