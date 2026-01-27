-- Añadir campos nuevos a subvenciones
ALTER TABLE subvenciones
ADD COLUMN IF NOT EXISTS fecha_ultima_actualizacion TIMESTAMP,
ADD COLUMN IF NOT EXISTS nivel1 VARCHAR(200),
ADD COLUMN IF NOT EXISTS nivel2 VARCHAR(300),
ADD COLUMN IF NOT EXISTS nivel3 VARCHAR(300),
ADD COLUMN IF NOT EXISTS region_impacto VARCHAR(200),
ADD COLUMN IF NOT EXISTS url_bases_reguladoras VARCHAR(500),
ADD COLUMN IF NOT EXISTS url_sede_electronica VARCHAR(500),
ADD COLUMN IF NOT EXISTS sector_economico VARCHAR(200),
ADD COLUMN IF NOT EXISTS contenido_hash VARCHAR(64);

-- Crear tabla documentos_convocatoria
CREATE TABLE IF NOT EXISTS documentos_convocatoria (
    id SERIAL PRIMARY KEY,
    subvencion_id INTEGER NOT NULL REFERENCES subvenciones(id) ON DELETE CASCADE,
    documento_id INTEGER,
    titulo VARCHAR(500),
    url VARCHAR(500),
    tipo VARCHAR(100),
    fecha_documento TIMESTAMP,
    fecha_deteccion TIMESTAMP DEFAULT NOW(),
    hash_documento VARCHAR(64),
    notificacion_enviada BOOLEAN DEFAULT FALSE
);

-- Crear tabla historial_cambios
CREATE TABLE IF NOT EXISTS historial_cambios (
    id SERIAL PRIMARY KEY,
    subvencion_id INTEGER NOT NULL REFERENCES subvenciones(id) ON DELETE CASCADE,
    tipo_cambio VARCHAR(50),
    descripcion_cambio TEXT,
    valor_anterior JSONB,
    valor_nuevo JSONB,
    fecha_cambio TIMESTAMP DEFAULT NOW(),
    notificado BOOLEAN DEFAULT FALSE
);

-- Índices para rendimiento
CREATE INDEX IF NOT EXISTS idx_subvenciones_nivel3 ON subvenciones(nivel3);
CREATE INDEX IF NOT EXISTS idx_subvenciones_region_impacto ON subvenciones(region_impacto);
CREATE INDEX IF NOT EXISTS idx_documentos_convocatoria_doc_id ON documentos_convocatoria(documento_id);
CREATE INDEX IF NOT EXISTS idx_historial_cambios_fecha ON historial_cambios(fecha_cambio DESC);
