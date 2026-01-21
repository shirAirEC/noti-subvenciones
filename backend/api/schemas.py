"""
Esquemas Pydantic para la API
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    pass


class Usuario(UsuarioBase):
    id: int
    activo: bool
    confirmado: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SuscripcionBase(BaseModel):
    regiones: Optional[List[int]] = None
    areas_tematicas: Optional[List[int]] = None
    presupuesto_min: Optional[float] = None
    presupuesto_max: Optional[float] = None
    tipos_beneficiario: Optional[List[int]] = None
    notificar_email: bool = True
    frecuencia_email: str = "inmediata"


class SuscripcionCreate(BaseModel):
    email: EmailStr
    nombre: Optional[str] = None
    regiones: Optional[List[int]] = None
    areas_tematicas: Optional[List[int]] = None
    presupuesto_min: Optional[float] = None
    presupuesto_max: Optional[float] = None
    tipos_beneficiario: Optional[List[int]] = None


class SuscripcionUpdate(SuscripcionBase):
    pass


class Suscripcion(SuscripcionBase):
    id: int
    usuario_id: int
    activa: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubvencionBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    fecha_inicio_solicitud: Optional[datetime] = None
    fecha_fin_solicitud: Optional[datetime] = None
    organo_convocante: Optional[str] = None
    region_nombre: Optional[str] = None
    presupuesto_total: Optional[float] = None
    url_bdns: Optional[str] = None


class Subvencion(SubvencionBase):
    id: int
    id_bdns: str
    activa: bool
    calendar_event_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RegionSchema(BaseModel):
    id: int
    codigo: str
    nombre: str
    tipo: Optional[str] = None
    
    class Config:
        from_attributes = True


class AreaTematicaSchema(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class SuscripcionResponse(BaseModel):
    message: str
    suscripcion_id: int
    calendar_url: str
    success: bool = True
