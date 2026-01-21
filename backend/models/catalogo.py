"""
Modelos de Catálogos
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.database import Base


class Region(Base):
    """Catálogo de regiones de BDNS"""
    __tablename__ = "regiones"
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True)
    nombre = Column(String(200), nullable=False)
    tipo = Column(String(50))  # CCAA, Provincia, Nacional, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Region {self.codigo}: {self.nombre}>"


class AreaTematica(Base):
    """Áreas temáticas personalizadas (mapeo de finalidades BDNS)"""
    __tablename__ = "areas_tematicas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String(500))
    
    # Mapeo a finalidades de BDNS
    finalidades_bdns = Column(String(200))  # IDs separados por comas
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AreaTematica {self.nombre}>"


class Finalidad(Base):
    """Catálogo de finalidades de BDNS"""
    __tablename__ = "finalidades"
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True)
    nombre = Column(String(300), nullable=False)
    descripcion = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Finalidad {self.codigo}: {self.nombre}>"
