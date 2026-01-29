# 🔧 Migración Automática - Filtros Avanzados

## ✅ Migración Automática Configurada

**La migración se ejecuta automáticamente** al iniciar el backend. No requiere acción manual.

El sistema verifica al arrancar si faltan las columnas:
- `organo_nivel1`, `organo_nivel2`, `organo_nivel3`
- `tipo_convocatoria`
- `instrumentos` (JSON)
- `sectores` (JSON)

Si detecta que faltan, las crea automáticamente junto con sus índices.

## 📋 Cambios Implementados

### Modelo de Subvencion
- **Órgano jerárquico**: 3 niveles (nivel1, nivel2, nivel3)
- **Tipo de convocatoria**: Según BDNS
- **Instrumentos**: Array JSON con tipos de ayuda
- **Sectores**: Array JSON con sectores económicos

### Nuevos Endpoints
- `GET /api/subvenciones` - Con filtros avanzados
- `GET /api/subvenciones/valores/organos` - Valores únicos (3 niveles)
- `GET /api/subvenciones/valores/tipos-convocatoria`
- `GET /api/subvenciones/valores/instrumentos`
- `GET /api/subvenciones/valores/sectores`
- `GET /api/subvenciones/valores/finalidades`

### Frontend
6 filtros implementados:
1. Órgano convocante (busca en 3 niveles)
2. Tipo de convocatoria
3. Instrumento de ayuda
4. Sector económico del beneficiario
5. Finalidad (política de gasto)
6. Presupuesto mínimo
7. Palabras clave

## 🔄 Re-sincronización Requerida

Después del despliegue con la migración, **es necesario re-sincronizar** para llenar los campos nuevos.

### Opción 1: Vaciar y esperar sync automático

```sql
-- Conectarse a Railway y ejecutar:
TRUNCATE TABLE subvenciones CASCADE;
```

Luego esperar la sincronización automática diaria (08:00).

### Opción 2: Esperar próxima sincronización

Simplemente esperar hasta las 08:00 del día siguiente. Las subvenciones existentes no tendrán los campos nuevos, pero las nuevas sí.

## ✅ Verificación

Después de la migración automática (visible en los logs de Railway):

```
🔧 Ejecutando migración automática para: ['organo_nivel1', 'organo_nivel2', ...]
✅ Migración completada automáticamente
```

## 📝 Notas

- La migración solo se ejecuta UNA VEZ (cuando detecta que faltan columnas)
- No afecta el rendimiento después de la primera ejecución
- Los filtros se aplican sobre la BD local, NO sobre la API de BDNS
- El sistema sincroniza España y Canarias según configuración actual
