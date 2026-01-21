# 🚀 Despliegue Rápido: Railway + Vercel

Guía ultra-rápida para desplegar en 30 minutos.

## ✅ Requisitos Previos (10 min)

### 1. Credenciales de Google
- [ ] Proyecto en Google Cloud creado
- [ ] Calendar API habilitada
- [ ] Service Account creada y JSON descargado
- [ ] Archivo `credentials/service-account.json` guardado localmente

### 2. Crear calendario
```bash
# Local (asegúrate que .env está configurado)
python backend/scripts/setup_calendar.py
```

**Copia el CALENDAR_ID que te devuelva**: `abc123@group.calendar.google.com`

### 3. Gmail App Password
- [ ] 2FA habilitado en Gmail
- [ ] App Password generado
- [ ] Password guardado

## 🎯 Despliegue (20 min)

### PASO 1: Subir a GitHub (2 min)

```bash
cd C:\Users\acruexp\Desktop\proyectos\rrhh_ull\noti-subvenciones

git init
git add .
git commit -m "Initial commit"

# Crear repo en https://github.com/new
# Luego:
git remote add origin https://github.com/TU-USUARIO/noti-subvenciones.git
git branch -M main
git push -u origin main
```

### PASO 2: Railway - Backend (10 min)

1. **Ir a** https://railway.app
2. **Login** con GitHub
3. **New Project** → "Deploy from GitHub repo"
4. **Seleccionar** `noti-subvenciones`
5. **Add PostgreSQL** (botón + New → Database → PostgreSQL)
6. **Variables de entorno** (clic en el servicio → Variables tab):

```env
BDNS_API_URL=https://www.infosubvenciones.es/bdnstrans/api
GOOGLE_SERVICE_ACCOUNT_FILE=/app/credentials/service-account.json
CALENDAR_ID=TU-CALENDAR-ID-AQUI@group.calendar.google.com
EMAIL_FROM=tu-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password-aqui
FRONTEND_URL=https://TEMPORAL.vercel.app
SCHEDULER_ENABLED=true
SCHEDULER_HOUR=8
SCHEDULER_MINUTE=0
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

7. **GOOGLE_CREDENTIALS_JSON**: Abre tu `credentials/service-account.json`, copia TODO (debe quedar en una línea), y pégalo como variable

8. **Esperar deploy** (~3 min)

9. **Copiar URL** de Railway: `https://tu-proyecto.up.railway.app`

### PASO 3: Actualizar config.js (1 min)

Edita `frontend/config.js` línea 12:

```javascript
? 'https://TU-PROYECTO.up.railway.app'  // ← PONER TU URL DE RAILWAY
```

Commit:
```bash
git add frontend/config.js
git commit -m "Update Railway URL"
git push
```

### PASO 4: Vercel - Frontend (5 min)

1. **Ir a** https://vercel.com
2. **Login** con GitHub
3. **Add New** → Project
4. **Import** `noti-subvenciones`
5. **Configure**:
   - Root Directory: `.` (raíz)
   - Output Directory: `frontend`
   - Build Command: `echo "Static site"`
6. **Deploy**
7. **Copiar URL**: `https://tu-app.vercel.app`

### PASO 5: Actualizar Railway (1 min)

Vuelve a Railway → Variables → Editar:

```env
FRONTEND_URL=https://tu-app.vercel.app
```

### PASO 6: Poblar catálogos (1 min)

En Railway:
1. Servicio → Deployments → último deployment
2. Ver → Three dots → Shell/Console
3. Ejecutar:
```bash
python backend/scripts/populate_catalogs.py
```

## ✅ Verificar

- **Backend health**: https://tu-proyecto.up.railway.app/health
- **API docs**: https://tu-proyecto.up.railway.app/docs
- **Frontend**: https://tu-app.vercel.app
- **Prueba**: Crear una suscripción de prueba

## 🎉 ¡Listo!

Tu sistema está desplegado en producción:

| Servicio | URL | Costo |
|----------|-----|-------|
| Backend | https://tu-proyecto.up.railway.app | $0/mes* |
| Frontend | https://tu-app.vercel.app | $0/mes |
| PostgreSQL | Incluido en Railway | $0/mes* |

*Dentro de $5 crédito gratis/mes de Railway

## 📱 Siguiente Paso: Probar

1. Abre tu app: `https://tu-app.vercel.app`
2. Crea una suscripción con tu email
3. Revisa tu bandeja de entrada
4. Confirma haciendo clic en el enlace
5. Espera a que lleguen notificaciones

## 🔧 Comandos Útiles

```bash
# Ver logs de Railway
railway logs -f

# Ejecutar comando en Railway
railway run python backend/scripts/populate_catalogs.py

# Re-deployar
git push  # Ambos servicios re-deployarán automáticamente
```

## 🆘 Problemas Comunes

### "Module not found"
- Verifica que `requirements.txt` está en la raíz
- Redeploya en Railway

### "Calendar API error"
- Verifica `GOOGLE_CREDENTIALS_JSON` (debe ser TODO el JSON en una línea)
- Verifica que el calendario está compartido con la service account

### "CORS error"
- Verifica `FRONTEND_URL` en Railway
- Debe coincidir exactamente con tu URL de Vercel

### "Email no se envía"
- Verifica Gmail App Password
- Revisa logs: `railway logs | grep email`

## 📚 Más Info

- Guía completa: [DEPLOY_RAILWAY_VERCEL.md](DEPLOY_RAILWAY_VERCEL.md)
- Checklist: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
- Instalación local: [INSTALL.md](INSTALL.md)
