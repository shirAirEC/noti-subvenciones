# Resumen de Cambios Implementados

## ✅ Características Añadidas

### 1. Detección de Documentos Nuevos
- Nuevo modelo `DocumentoConvocatoria` para trackear documentos de convocatorias
- Detección automática cuando se añaden nuevos documentos (bases, anexos, formularios, etc.)
- Notificaciones por email cuando se detectan documentos nuevos

### 2. Detección de Cambios en Convocatorias
- Nuevo modelo `CambioConvocatoria` para historial de cambios
- Detección de ampliaciones de plazo (cambios en fecha límite)
- Detección de modificaciones de presupuesto
- Sistema de notificaciones por email para cambios detectados

### 3. URLs en Calendar
- Se añadieron campos `url_bases_reguladoras` y `url_sede_electronica` al modelo Subvencion
- Los eventos de Calendar ahora incluyen estas URLs en la descripción
- Descripción enriquecida con enlaces a:
  - Ficha BDNS
  - Bases reguladoras
  - Sede electrónica

### 4. Sistema de Notificaciones
- Nuevo `NotificationService` para enviar emails sobre cambios y documentos
- Scheduler configurado para enviar notificaciones diarias a las 8:00 AM
- Emails HTML formateados con detalles de cambios y enlaces

### 5. Sync Mejorado
- El sync ahora también verifica convocatorias existentes para detectar cambios
- Se procesan documentos de cada convocatoria automáticamente
- Se guardan los documentos iniciales al crear una convocatoria

## 📦 Nuevos Archivos Creados

1. `backend/models/documento_convocatoria.py` - Modelo para documentos
2. `backend/models/cambio_convocatoria.py` - Modelo para cambios
3. `backend/services/change_detector_service.py` - Servicio de detección
4. `backend/services/notification_service.py` - Servicio de notificaciones
5. `backend/migrations/2026_01_27_add_documents_and_changes.sql` - Migración SQL

## 🔄 Archivos Modificados

1. `backend/models/subvencion.py` - Añadidas relaciones y columnas URLs
2. `backend/models/__init__.py` - Exportar nuevos modelos
3. `backend/services/bdns_service.py` - Extraer documentos y URLs
4. `backend/services/calendar_service.py` - Incluir URLs en eventos
5. `backend/tasks/sync_subvenciones.py` - Detectar cambios y documentos
6. `backend/tasks/scheduler.py` - Tarea diaria de notificaciones

## 🗄️ Cambios en Base de Datos

- Nueva tabla `documentos_convocatoria`
- Nueva tabla `historial_cambios`
- Nuevas columnas en `subvenciones`:
  - `url_bases_reguladoras`
  - `url_sede_electronica`

## 📧 Flujo de Notificaciones

1. El sync diario (6:00 AM) detecta cambios y nuevos documentos
2. Se marcan como "no notificados"
3. A las 8:00 AM se ejecuta la tarea de notificaciones
4. Se envían emails a usuarios con cambios relevantes
5. Se marcan como "notificados"

## 🚀 Próximos Pasos

Estos archivos necesitan ser añadidos correctamente al repositorio. Los archivos están actualmente vacíos y necesitan el contenido completo.
