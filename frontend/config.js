// Configuración de la aplicación
// Detectar entorno automáticamente
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// Configurar URL del backend según el entorno
window.API_BASE_URL = isDevelopment 
    ? 'http://localhost:8000'  // Desarrollo local
    : 'https://noti-subvenciones-production.up.railway.app';  // Producción

console.log('🔧 Frontend conectando a:', window.API_BASE_URL);
