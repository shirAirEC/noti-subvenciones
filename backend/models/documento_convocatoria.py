"""
Modelo para documentos de convocatorias
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class DocumentoConvocatoria(Base):
    """Documentos asociados a una convocatoria"""
    __tablename__ = "documentos_convocatoria"
    
    id = Column(Integer, primary_key=True, index=True)
    subvencion_id = Column(Integer, ForeignKey("subvenciones.id"), nullable=False)
    
    # Identificación del documento
    documento_id = Column(Integer)  # ID del documento en BDNS
    titulo = Column(String(500))
    url = Column(String(500))
    tipo = Column(String(100))
    
    # Control de cambios
    fecha_documento = Column(DateTime, index=True)
    hash_documento = Column(String(64))  # Hash del contenido para detectar cambios
    
    # Notificaciones
    notificacion_enviada = Column(Boolean, default=False)
    fecha_notificacion = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    subvencion = relationship("Subvencion", back_populates="documentos")
    
    def __repr__(self):
        return f"<DocumentoConvocatoria {self.id}: {self.titulo[:50]}>"
