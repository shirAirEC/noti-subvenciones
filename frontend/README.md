# Frontend - Sistema de Notificaciones de Subvenciones

## 🚀 Despliegue en Vercel

### Variables de Entorno Requeridas

Configura las siguientes variables en Vercel Dashboard → Settings → Environment Variables:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `VITE_API_URL` | URL del backend en Railway | `https://tu-proyecto.up.railway.app` |

### Configuración en Vercel

1. **Root Directory:** `frontend`
2. **Framework Preset:** Other
3. **Build Command:** `node build.js` (se lee de vercel.json)
4. **Output Directory:** `.` (se lee de vercel.json)

### Variables de Entorno

#### Producción
```bash
VITE_API_URL=https://tu-proyecto-production.up.railway.app
```

#### Development (opcional)
```bash
VITE_API_URL=http://localhost:8000
```

## 🛠️ Desarrollo Local

```bash
# Generar config.js con URL local
VITE_API_URL=http://localhost:8000 node build.js

# Servir archivos (con cualquier servidor estático)
python -m http.server 8080
# o
npx serve .
```

## 📝 Notas

- El archivo `config.js` se genera automáticamente durante el build
- La URL del backend se configura mediante variable de entorno
- No edites `config.js` manualmente, ya que se sobrescribe en cada build
