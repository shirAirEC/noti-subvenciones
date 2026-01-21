"""
Modelos de base de datos
"""
from backend.models.subvencion import Subvencion
from backend.models.usuario import Usuario
from backend.models.suscripcion import Suscripcion
from backend.models.notificacion_enviada import NotificacionEnviada
from backend.models.catalogo import Region, AreaTematica, Finalidad

__all__ = [
    "Subvencion",
    "Usuario",
    "Suscripcion",
    "NotificacionEnviada",
    "Region",
    "AreaTematica",
    "Finalidad",
]
