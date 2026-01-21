"""
Modelo de Notificación Enviada
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from backend.database import Base


class NotificacionEnviada(Base):
    """Registro de notificaciones enviadas para evitar duplicados"""
    __tablename__ = "notificaciones_enviadas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    subvencion_id = Column(Integer, ForeignKey("subvenciones.id"), nullable=False)
    
    # Tipo de notificación
    tipo = Column(String(20), default="email")  # email, push, sms
    
    # Estado
    enviada = Column(Boolean, default=False)
    fecha_envio = Column(DateTime)
    error = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificacionEnviada {self.id}>"
