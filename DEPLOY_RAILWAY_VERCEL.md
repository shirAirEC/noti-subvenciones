# Guía de Despliegue: Railway + Vercel

Despliegue **GRATUITO** del Sistema de Notificaciones de Subvenciones usando Railway (backend) y Vercel (frontend).

## 🎯 Resumen

- **Railway**: Backend FastAPI + PostgreSQL (Gratis: $5 crédito/mes)
- **Vercel**: Frontend estático (Gratis: ilimitado para hobby)
- **Costo Total**: $0/mes (dentro de límites gratuitos)

---

## PARTE 1: Desplegar Backend en Railway (20 minutos)

### Paso 1: Crear cuenta en Railway

1. Ve a: https://railway.app
2. Clic en "Start a New Project"
3. Conecta con GitHub (recomendado) o email

### Paso 2: Subir tu código a GitHub

Si no lo has hecho:

```bash
cd C:\Users\acruexp\Desktop\proyectos\rrhh_ull\noti-subvenciones

# Inicializar git
git init
git add .
git commit -m "Initial commit"

# Crear repositorio en GitHub y pushearlo
# Ve a https://github.com/new
# Luego:
git remote add origin https://github.com/tu-usuario/noti-subvenciones.git
git branch -M main
git push -u origin main
```

### Paso 3: Crear proyecto en Railway

1. En Railway, clic en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Conecta tu GitHub y selecciona el repositorio `noti-subvenciones`
4. Railway detectará automáticamente Python

### Paso 4: Añadir PostgreSQL

1. En tu proyecto de Railway, clic en "+ New"
2. Selecciona "Database" → "Add PostgreSQL"
3. Railway creará la base de datos automáticamente

### Paso 5: Configurar Variables de Entorno

En Railway, ve a tu servicio backend → "Variables":

**Añade estas variables:**

```env
# Database (Railway lo proporciona automáticamente como DATABASE_URL)
# No necesitas configurar DATABASE_URL manualmente

# BDNS API
BDNS_API_URL=https://www.infosubvenciones.es/bdnstrans/api

# Google Calendar
GOOGLE_SERVICE_ACCOUNT_FILE=/app/credentials/service-account.json
CALENDAR_ID=tu-calendar-id@group.calendar.google.com

# Google Credentials (contenido completo del archivo JSON)
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}

# Email
EMAIL_FROM=tu-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password

# Application
APP_HOST=0.0.0.0
APP_PORT=$PORT
FRONTEND_URL=https://tu-app.vercel.app

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_HOUR=8
SCHEDULER_MINUTE=0

# Logging
LOG_LEVEL=INFO

# Python
PYTHONUNBUFFERED=1
```

**⚠️ IMPORTANTE para GOOGLE_CREDENTIALS_JSON:**

Abre tu archivo `credentials/service-account.json` y copia TODO el contenido (debe ser una sola línea):

```json
{"type":"service_account","project_id":"tu-proyecto","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
```

Pégalo como valor de `GOOGLE_CREDENTIALS_JSON`.

### Paso 6: Configurar Dominio del Backend

1. Railway te asigna un dominio automáticamente como: `tu-proyecto.up.railway.app`
2. Cópialo, lo necesitarás para Vercel

### Paso 7: Poblar Catálogos (después del despliegue)

Una vez desplegado, en Railway:

1. Ve a tu servicio → "Deployments" → Último deployment
2. Abre la consola/shell o usa Railway CLI
3. Ejecuta:

```bash
python backend/scripts/populate_catalogs.py
```

---

## PARTE 2: Desplegar Frontend en Vercel (10 minutos)

### Paso 1: Crear cuenta en Vercel

1. Ve a: https://vercel.com
2. Clic en "Sign Up"
3. Conecta con GitHub

### Paso 2: Importar Proyecto

1. En Vercel, clic en "Add New" → "Project"
2. Selecciona tu repositorio `noti-subvenciones`
3. Vercel detectará la configuración de `vercel.json`

### Paso 3: Configurar Build Settings

**Root Directory**: Dejar en raíz (`.`)

**Build Command**: 
```bash
echo "No build needed for static site"
```

**Output Directory**: 
```
frontend
```

**Install Command**:
```bash
echo "No install needed"
```

### Paso 4: Configurar Variables de Entorno

En la sección "Environment Variables":

```env
VITE_API_URL=https://tu-proyecto.up.railway.app
```

(Reemplaza con la URL de tu backend en Railway)

### Paso 5: Deploy

1. Clic en "Deploy"
2. Vercel desplegará tu frontend en ~1 minuto
3. Te dará una URL como: `tu-app.vercel.app`

### Paso 6: Actualizar Frontend con URL de Backend

Necesitas modificar el archivo `frontend/app.js` para usar la URL de producción:

```javascript
// En app.js, línea 6:
// Cambiar de:
const API_BASE_URL = 'http://localhost:8000';

// A:
const API_BASE_URL = 'https://tu-proyecto.up.railway.app';
```

Commit y push:

```bash
git add frontend/app.js
git commit -m "Update API URL for production"
git push
```

Vercel redesplegará automáticamente.

### Paso 7: Actualizar Variable en Railway

Vuelve a Railway y actualiza:

```env
FRONTEND_URL=https://tu-app.vercel.app
```

---

## PARTE 3: Configurar Dominio Personalizado (Opcional)

### En Vercel:

1. Settings → Domains
2. Añade tu dominio (ej: `subvenciones.tu-dominio.com`)
3. Configura DNS según instrucciones de Vercel

### En Railway:

1. Settings → Networking
2. Añade dominio personalizado (ej: `api.tu-dominio.com`)
3. Configura DNS según instrucciones

---

## ✅ Verificación

1. **Backend**: Abre `https://tu-proyecto.up.railway.app/health`
   - Deberías ver: `{"status":"healthy"}`

2. **Frontend**: Abre `https://tu-app.vercel.app`
   - Deberías ver la página de suscripción

3. **API Docs**: `https://tu-proyecto.up.railway.app/docs`

4. **Prueba completa**:
   - Crear una suscripción
   - Verificar que llega el email
   - Confirmar suscripción

---

## 🔧 Monitoreo

### Railway:

- **Logs**: En tu proyecto → "Deployments" → Clic en deployment → "View Logs"
- **Métricas**: Tab "Metrics" muestra uso de CPU, memoria, red
- **Créditos**: Dashboard principal muestra uso mensual

### Vercel:

- **Deployments**: Ver historial de despliegues
- **Analytics**: Métricas de visitantes (requiere plan pro)

---

## 💰 Límites Gratuitos

### Railway (Hobby Plan):

- ✅ $5 crédito/mes gratis
- ✅ 500 horas de ejecución/mes
- ✅ PostgreSQL incluido (1GB)
- ⚠️ Proyecto se pausa si se acaba el crédito

### Vercel (Hobby Plan):

- ✅ 100 GB bandwidth/mes
- ✅ Despliegues ilimitados
- ✅ SSL automático
- ✅ Sin límite de proyectos

### Con tráfico bajo (~100 usuarios):
- Railway: ~$2-3/mes (dentro del crédito gratuito)
- Vercel: $0/mes
- **Total: GRATIS**

---

## 🆘 Troubleshooting

### Error 503 en Railway

- Verifica logs: `railway logs`
- Verifica que PostgreSQL está conectado
- Revisa variables de entorno

### Error de CORS en frontend

- Verifica que `FRONTEND_URL` en Railway es correcto
- Verifica que el backend permite tu dominio de Vercel

### Emails no se envían

- Verifica `SMTP_PASSWORD` (App Password de Gmail)
- Revisa logs de Railway: buscar "email"

### Scheduler no ejecuta

- Verifica `SCHEDULER_ENABLED=true`
- Verifica que el proyecto no se pausa (Railway)

---

## 📱 Railway CLI (Opcional pero útil)

Instalar:

```bash
npm i -g @railway/cli
```

Usar:

```bash
# Login
railway login

# Ver logs en tiempo real
railway logs

# Ejecutar comandos
railway run python backend/scripts/populate_catalogs.py

# Variables
railway variables
```

---

## 🚀 Próximos Pasos

1. ✅ Configurar dominio personalizado
2. ✅ Configurar emails transaccionales profesionales
3. ✅ Monitorear uso de créditos en Railway
4. ✅ Configurar alertas si el sistema falla

---

## 🎉 ¡Listo!

Tu sistema está desplegado y funcionando en:

- **Frontend**: https://tu-app.vercel.app
- **Backend**: https://tu-proyecto.up.railway.app
- **Costo**: $0/mes (dentro de planes gratuitos)

¿Necesitas ayuda con algún paso? Consulta los logs o abre un issue.
