-- Script SQL de inicialización (alternativo a SQLAlchemy)
-- Este script puede usarse para crear las tablas manualmente si es necesario

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    confirmado BOOLEAN DEFAULT FALSE,
    token_confirmacion VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    ultimo_acceso TIMESTAMP
);

CREATE INDEX idx_usuarios_email ON usuarios(email);

-- Tabla de subvenciones
CREATE TABLE IF NOT EXISTS subvenciones (
    id SERIAL PRIMARY KEY,
    id_bdns VARCHAR(50) UNIQUE NOT NULL,
    titulo VARCHAR(500) NOT NULL,
    descripcion TEXT,
    fecha_publicacion TIMESTAMP,
    fecha_inicio_solicitud TIMESTAMP,
    fecha_fin_solicitud TIMESTAMP,
    fecha_resolucion TIMESTAMP,
    finalidad_id INTEGER,
    finalidad_nombre VARCHAR(200),
    region_id INTEGER,
    region_nombre VARCHAR(200),
    organo_convocante VARCHAR(300),
    tipo_administracion VARCHAR(10),
    presupuesto_total NUMERIC(15, 2),
    url_bdns VARCHAR(500),
    url_convocatoria VARCHAR(500),
    tipos_beneficiario JSONB,
    activa BOOLEAN DEFAULT TRUE,
    calendar_event_id VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_subvenciones_id_bdns ON subvenciones(id_bdns);
CREATE INDEX idx_subvenciones_fecha_fin ON subvenciones(fecha_fin_solicitud);

-- Tabla de suscripciones
CREATE TABLE IF NOT EXISTS suscripciones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    regiones JSONB,
    areas_tematicas JSONB,
    presupuesto_min NUMERIC(15, 2),
    presupuesto_max NUMERIC(15, 2),
    tipos_beneficiario JSONB,
    notificar_email BOOLEAN DEFAULT TRUE,
    frecuencia_email VARCHAR(20) DEFAULT 'inmediata',
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_suscripciones_usuario ON suscripciones(usuario_id);

-- Tabla de notificaciones enviadas
CREATE TABLE IF NOT EXISTS notificaciones_enviadas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    subvencion_id INTEGER NOT NULL REFERENCES subvenciones(id) ON DELETE CASCADE,
    tipo VARCHAR(20) DEFAULT 'email',
    enviada BOOLEAN DEFAULT FALSE,
    fecha_envio TIMESTAMP,
    error VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notificaciones_usuario ON notificaciones_enviadas(usuario_id);
CREATE INDEX idx_notificaciones_subvencion ON notificaciones_enviadas(subvencion_id);

-- Tabla de regiones
CREATE TABLE IF NOT EXISTS regiones (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de áreas temáticas
CREATE TABLE IF NOT EXISTS areas_tematicas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion VARCHAR(500),
    finalidades_bdns VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de finalidades BDNS
CREATE TABLE IF NOT EXISTS finalidades (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE,
    nombre VARCHAR(300) NOT NULL,
    descripcion VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Comentarios de tablas
COMMENT ON TABLE usuarios IS 'Usuarios suscritos al sistema';
COMMENT ON TABLE subvenciones IS 'Subvenciones obtenidas de BDNS';
COMMENT ON TABLE suscripciones IS 'Suscripciones con filtros personalizados';
COMMENT ON TABLE notificaciones_enviadas IS 'Registro de notificaciones enviadas';
COMMENT ON TABLE regiones IS 'Catálogo de regiones de BDNS';
COMMENT ON TABLE areas_tematicas IS 'Áreas temáticas personalizadas';
COMMENT ON TABLE finalidades IS 'Catálogo de finalidades de BDNS';
