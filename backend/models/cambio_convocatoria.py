"""
Modelo para historial de cambios de convocatorias
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class CambioConvocatoria(Base):
    """Historial de cambios detectados en convocatorias"""
    __tablename__ = "historial_cambios"
    
    id = Column(Integer, primary_key=True, index=True)
    subvencion_id = Column(Integer, ForeignKey("subvenciones.id"), nullable=False)
    
    # Tipo de cambio
    tipo_cambio = Column(String(50))  # 'fecha_extendida', 'presupuesto_modificado', 'documento_nuevo', etc.
    descripcion_cambio = Column(Text)
    
    # Valores
    valor_anterior = Column(JSON)
    valor_nuevo = Column(JSON)
    
    # Control
    fecha_cambio = Column(DateTime, default=datetime.utcnow, index=True)
    notificado = Column(Boolean, default=False)
    fecha_notificacion = Column(DateTime)
    
    # Relaciones
    subvencion = relationship("Subvencion", back_populates="historial_cambios")
    
    def __repr__(self):
        return f"<CambioConvocatoria {self.id}: {self.tipo_cambio}>"
