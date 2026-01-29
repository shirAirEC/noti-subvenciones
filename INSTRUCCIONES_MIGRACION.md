# 🔧 Instrucciones de Migración - Filtros Avanzados

## 📋 Cambios Realizados

### 1. **Modelo de Subvencion actualizado**
Se añadieron los siguientes campos:

- `organo_nivel1`, `organo_nivel2`, `organo_nivel3` - Jerarquía de órganos (3 niveles)
- `tipo_convocatoria` - Tipo de convocatoria según BDNS
- `instrumentos` (JSON) - Array con instrumentos de ayuda
- `sectores` (JSON) - Array con sectores económicos del beneficiario

### 2. **Nuevos endpoints de filtros**
- `GET /api/subvenciones` - Listado con filtros avanzados
- `GET /api/subvenciones/valores/organos` - Valores únicos de órganos (3 niveles)
- `GET /api/subvenciones/valores/tipos-convocatoria` - Tipos de convocatoria
- `GET /api/subvenciones/valores/instrumentos` - Instrumentos de ayuda
- `GET /api/subvenciones/valores/sectores` - Sectores económicos
- `GET /api/subvenciones/valores/finalidades` - Finalidades (políticas de gasto)

### 3. **Frontend rehecho**
- Filtros según especificaciones:
  - Órgano convocante (3 niveles jerárquicos)
  - Tipo de convocatoria
  - Instrumento de ayuda
  - Sector económico del beneficiario
  - Finalidad (política de gasto)
  - Presupuesto mínimo
  - Palabras clave
- Diseño limpio y directo
- Vista previa en tiempo real

## 🗄️ Migración de Base de Datos

### ⚠️ EJECUTAR EN RAILWAY DATABASE CONSOLE:

```sql
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
```

### Verificar columnas creadas:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'subvenciones' 
AND column_name IN ('organo_nivel1', 'organo_nivel2', 'organo_nivel3', 'tipo_convocatoria', 'instrumentos', 'sectores');
```

Debe mostrar 6 filas.

## 🔄 IMPORTANTE: Re-sincronizar Datos

Después de aplicar la migración, **es obligatorio volver a sincronizar** para llenar los nuevos campos:

### Borrar datos actuales y re-sincronizar

```sql
-- PRECAUCIÓN: Esto borra todas las subvenciones y eventos
TRUNCATE TABLE subvenciones CASCADE;
```

Luego esperar la sincronización automática diaria (08:00) o forzar con:

```bash
# Desde terminal con acceso a Railway
# (Esto requeriría crear un endpoint admin, no implementado aún)
```

**Recomendado**: Simplemente esperar a la próxima sincronización automática (08:00 diaria).

## 📝 Notas Técnicas

1. **Filtros aplicados en backend**: Los filtros por `tipo_convocatoria`, `instrumento`, `sector` y `finalidad` se aplican sobre los datos en la BD, **NO en la API de BDNS**

2. **Arrays JSON**: Los campos `instrumentos` y `sectores` son arrays JSON. La búsqueda se hace con `CAST(... AS String)` para buscar texto dentro del array

3. **Jerarquía de órganos**: Se almacenan los 3 niveles para permitir búsquedas flexibles. El filtro `organo_nivel` busca en los 3 niveles simultáneamente

4. **Región**: El sistema sincroniza España y Canarias según los filtros configurados en el sync. Los usuarios pueden filtrar por órgano para enfocarse en sus regiones de interés.

## ✅ Verificación Post-Migración

1. **Columnas creadas**:
```sql
SELECT COUNT(*) FROM information_schema.columns 
WHERE table_name = 'subvenciones' 
AND column_name IN ('organo_nivel1', 'tipo_convocatoria', 'instrumentos', 'sectores');
```
Debe devolver 4.

2. **Datos poblados** (después de sincronización):
```sql
SELECT COUNT(*) FROM subvenciones WHERE organo_nivel1 IS NOT NULL;
SELECT COUNT(*) FROM subvenciones WHERE tipo_convocatoria IS NOT NULL;
SELECT COUNT(*) FROM subvenciones WHERE instrumentos IS NOT NULL;
```

3. **Endpoints funcionando**:
   - https://noti-subvenciones-production.up.railway.app/api/subvenciones
   - https://noti-subvenciones-production.up.railway.app/api/subvenciones/valores/organos

## 🚀 Despliegue Frontend en Vercel

Variables de entorno necesarias:
```
VITE_API_URL=https://noti-subvenciones-production.up.railway.app
```

Configuración:
- Root directory: `frontend`
- Build command: `node build.js`
- Output directory: `.` (punto)
