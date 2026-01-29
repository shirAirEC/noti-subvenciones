-- Migración: 2026_01_29_add_campos_filtro.sql
-- Añadir campos para filtros avanzados de subvenciones

-- Añadir niveles de órgano convocante
ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS organo_nivel1 VARCHAR(300);
ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS organo_nivel2 VARCHAR(300);
ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS organo_nivel3 VARCHAR(300);

-- Añadir tipo de convocatoria
ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS tipo_convocatoria VARCHAR(200);

-- Añadir instrumentos de ayuda (JSON)
ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS instrumentos JSON;

-- Añadir sectores económicos (JSON)
ALTER TABLE subvenciones ADD COLUMN IF NOT EXISTS sectores JSON;

-- Crear índices para búsquedas
CREATE INDEX IF NOT EXISTS idx_subvenciones_organo_nivel1 ON subvenciones (organo_nivel1);
CREATE INDEX IF NOT EXISTS idx_subvenciones_organo_nivel2 ON subvenciones (organo_nivel2);
CREATE INDEX IF NOT EXISTS idx_subvenciones_organo_nivel3 ON subvenciones (organo_nivel3);
CREATE INDEX IF NOT EXISTS idx_subvenciones_tipo_convocatoria ON subvenciones (tipo_convocatoria);
CREATE INDEX IF NOT EXISTS idx_subvenciones_finalidad_nombre ON subvenciones (finalidad_nombre);

-- Comentarios
COMMENT ON COLUMN subvenciones.organo_nivel1 IS 'Primer nivel jerárquico del órgano (más general)';
COMMENT ON COLUMN subvenciones.organo_nivel2 IS 'Segundo nivel jerárquico del órgano';
COMMENT ON COLUMN subvenciones.organo_nivel3 IS 'Tercer nivel jerárquico del órgano (más específico)';
COMMENT ON COLUMN subvenciones.tipo_convocatoria IS 'Tipo de convocatoria según BDNS';
COMMENT ON COLUMN subvenciones.instrumentos IS 'Array JSON con instrumentos de ayuda';
COMMENT ON COLUMN subvenciones.sectores IS 'Array JSON con sectores económicos del beneficiario';
