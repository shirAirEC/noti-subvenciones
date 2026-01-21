# ✅ Checklist de Producción

Lista de verificación antes de desplegar a producción.

## Pre-despliegue

### Configuración de Google Cloud
- [ ] Proyecto de Google Cloud creado
- [ ] Calendar API habilitada
- [ ] Service Account creada
- [ ] Credenciales JSON descargadas
- [ ] Calendario compartido creado (ejecutar `setup_calendar.py`)
- [ ] Calendario compartido con la cuenta de servicio
- [ ] CALENDAR_ID copiado

### Configuración de Email
- [ ] Gmail con 2FA habilitado
- [ ] App Password generado
- [ ] Email de prueba enviado correctamente

### Código
- [ ] Código en GitHub (rama main)
- [ ] `.gitignore` configurado (credentials/ excluido)
- [ ] README.md actualizado
- [ ] Archivo `config.js` actualizado con URL del backend

## Despliegue en Railway

### Configuración
- [ ] Cuenta de Railway creada
- [ ] Proyecto creado desde GitHub
- [ ] PostgreSQL añadido
- [ ] Variables de entorno configuradas:
  - [ ] BDNS_API_URL
  - [ ] GOOGLE_SERVICE_ACCOUNT_FILE
  - [ ] CALENDAR_ID
  - [ ] GOOGLE_CREDENTIALS_JSON (contenido completo del JSON)
  - [ ] EMAIL_FROM
  - [ ] SMTP_HOST
  - [ ] SMTP_PORT
  - [ ] SMTP_USER
  - [ ] SMTP_PASSWORD
  - [ ] FRONTEND_URL
  - [ ] SCHEDULER_ENABLED=true
  - [ ] SCHEDULER_HOUR=8
  - [ ] SCHEDULER_MINUTE=0
  - [ ] LOG_LEVEL=INFO

### Verificación
- [ ] Deploy exitoso (verde)
- [ ] Logs sin errores críticos
- [ ] Health check funciona: `/health` devuelve `{"status":"healthy"}`
- [ ] API Docs accesibles: `/docs`
- [ ] Catálogos poblados (ejecutar `populate_catalogs.py`)

## Despliegue en Vercel

### Configuración
- [ ] Cuenta de Vercel creada
- [ ] Proyecto importado desde GitHub
- [ ] Build settings configurados
- [ ] Output Directory: `frontend`

### Verificación
- [ ] Deploy exitoso
- [ ] Página principal carga correctamente
- [ ] Formulario visible y funcional
- [ ] Console sin errores (F12 → Console)

## Integración Frontend-Backend

### Actualizar URLs
- [ ] `frontend/config.js` actualizado con URL de Railway
- [ ] Variable `FRONTEND_URL` en Railway apunta a Vercel
- [ ] CORS configurado correctamente

### Probar conexión
- [ ] Frontend puede hacer peticiones al backend
- [ ] No hay errores de CORS en console
- [ ] Catálogos se cargan (regiones, áreas)

## Pruebas End-to-End

### Flujo completo de suscripción
- [ ] Abrir frontend en Vercel
- [ ] Llenar formulario con email real
- [ ] Submit exitoso
- [ ] Email de confirmación recibido
- [ ] Link de confirmación funciona
- [ ] Confirmación exitosa

### Prueba de sincronización
- [ ] Ejecutar sincronización manual (Railway CLI o console)
- [ ] Verificar logs de sincronización
- [ ] Verificar que se crean eventos en Calendar
- [ ] Verificar que se envían emails

### Prueba de scheduler
- [ ] Esperar hasta la hora configurada (o cambiar hora para probar)
- [ ] Verificar que ejecuta automáticamente
- [ ] Revisar logs del scheduler

## Monitoreo Post-Despliegue

### Primeras 24 horas
- [ ] Revisar logs cada hora
- [ ] Verificar uso de memoria/CPU en Railway
- [ ] Verificar que scheduler ejecuta a la hora programada
- [ ] Probar con múltiples suscripciones

### Primera semana
- [ ] Revisar logs diariamente
- [ ] Verificar emails se envían correctamente
- [ ] Verificar eventos en Calendar
- [ ] Monitorear créditos de Railway

### Métricas a observar
- [ ] Número de suscripciones creadas
- [ ] Número de emails enviados
- [ ] Número de eventos en Calendar
- [ ] Errores en logs
- [ ] Uso de recursos (Railway dashboard)

## Seguridad

- [ ] Variables de entorno NO están en el código
- [ ] Credenciales NO están en GitHub
- [ ] Endpoints sensibles protegidos
- [ ] HTTPS activo (Railway y Vercel lo hacen automático)
- [ ] CORS configurado correctamente

## Documentación

- [ ] README actualizado con URLs de producción
- [ ] DEPLOY_RAILWAY_VERCEL.md verificado
- [ ] URLs de ejemplo reemplazadas con URLs reales
- [ ] Instrucciones para usuarios finales documentadas

## Backup

- [ ] Script de backup de BD configurado (Railway CLI)
- [ ] Primera backup manual realizada
- [ ] Proceso de restauración documentado

## Soporte

- [ ] Email de soporte configurado
- [ ] Proceso para reportar bugs definido
- [ ] Plan de respuesta a incidentes

## Optimizaciones Futuras (Opcional)

- [ ] Dominio personalizado configurado
- [ ] CDN para frontend (Vercel lo incluye)
- [ ] Monitoreo con Sentry u otro servicio
- [ ] Analytics configurado
- [ ] Rate limiting implementado

---

## 🚨 Si algo falla

1. **Revisar logs primero**: Railway logs y Browser console
2. **Verificar variables de entorno**: Typos son comunes
3. **Probar endpoints manualmente**: Usar Postman o curl
4. **Rollback si es necesario**: Railway permite volver a deploy anterior
5. **Consultar documentación**: DEPLOY_RAILWAY_VERCEL.md

---

## ✅ Checklist Rápido para Re-despliegues

Cuando hagas cambios y redepliegues:

- [ ] Commit y push a GitHub
- [ ] Verificar que Railway/Vercel detectan el cambio
- [ ] Esperar a que termine el build
- [ ] Verificar logs
- [ ] Probar cambio específico
- [ ] Monitorear por 30 minutos

---

**Fecha de último despliegue**: _______

**Desplegado por**: _______

**Notas adicionales**: _______
