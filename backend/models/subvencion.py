"""
Modelo de Subvención
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, JSON
from datetime import datetime
from backend.database import Base


class Subvencion(Base):
    """Modelo de subvención de BDNS"""
    __tablename__ = "subvenciones"
    
    id = Column(Integer, primary_key=True, index=True)
    id_bdns = Column(String(50), unique=True, index=True, nullable=False)
    titulo = Column(String(500), nullable=False)
    descripcion = Column(Text)
    
    # Fechas
    fecha_publicacion = Column(DateTime)
    fecha_inicio_solicitud = Column(DateTime)
    fecha_fin_solicitud = Column(DateTime, index=True)
    fecha_resolucion = Column(DateTime)
    
    # Clasificación
    finalidad_id = Column(Integer)
    finalidad_nombre = Column(String(200))
    region_id = Column(Integer)
    region_nombre = Column(String(200))
    
    # Organismo
    organo_convocante = Column(String(300))
    tipo_administracion = Column(String(10))
    
    # Presupuesto
    presupuesto_total = Column(Numeric(15, 2))
    
    # Enlaces
    url_bdns = Column(String(500))
    url_convocatoria = Column(String(500))
    
    # Beneficiarios
    tipos_beneficiario = Column(JSON)  # Lista de tipos de beneficiarios
    
    # Metadata
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ID del evento en Google Calendar
    calendar_event_id = Column(String(200))
    
    def __repr__(self):
        return f"<Subvencion {self.id_bdns}: {self.titulo[:50]}>"
