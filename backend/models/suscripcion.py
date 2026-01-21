"""
Modelo de Suscripción
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Suscripcion(Base):
    """Modelo de suscripción con filtros personalizados"""
    __tablename__ = "suscripciones"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Filtros
    regiones = Column(JSON)  # Lista de IDs de regiones, null = todas
    areas_tematicas = Column(JSON)  # Lista de IDs de áreas temáticas
    presupuesto_min = Column(Numeric(15, 2))
    presupuesto_max = Column(Numeric(15, 2))
    tipos_beneficiario = Column(JSON)  # Lista de tipos de beneficiarios
    
    # Preferencias de notificación
    notificar_email = Column(Boolean, default=True)
    frecuencia_email = Column(String(20), default="inmediata")  # inmediata, diaria, semanal
    
    # Estado
    activa = Column(Boolean, default=True)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="suscripciones")
    
    def __repr__(self):
        return f"<Suscripcion {self.id} - Usuario {self.usuario_id}>"
