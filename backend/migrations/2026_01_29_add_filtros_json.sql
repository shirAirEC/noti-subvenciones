-- Migración: 2026_01_29_add_filtros_json.sql
-- Añadir campo filtros_json a la tabla suscripciones

ALTER TABLE suscripciones
ADD COLUMN filtros_json JSONB;

-- Comentario explicativo
COMMENT ON COLUMN suscripciones.filtros_json IS 'Filtros personalizados en formato JSON flexible para cada suscripción';
