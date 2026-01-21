"""
Modelo de Usuario
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Usuario(Base):
    """Modelo de usuario suscrito"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre = Column(String(200))
    
    # Estado
    activo = Column(Boolean, default=True)
    confirmado = Column(Boolean, default=False)
    token_confirmacion = Column(String(100), unique=True)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_acceso = Column(DateTime)
    
    # Relaciones
    suscripciones = relationship("Suscripcion", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario {self.email}>"
