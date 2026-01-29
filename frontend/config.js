/**
 * Configuración del frontend
 * Detecta automáticamente si está en desarrollo o producción
 */

// Detectar entorno
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// Configuración según entorno
const config = {
    // URL del backend
    API_BASE_URL: isDevelopment 
        ? 'http://localhost:8000'  // Desarrollo local
        : window.location.origin.includes('vercel.app')
            ? 'https://noti-subvenciones-production.up.railway.app'  // Producción Railway
            : 'http://localhost:8000',  // Fallback
    
    // Otras configuraciones
    APP_NAME: 'Sistema de Notificaciones de Subvenciones',
    APP_VERSION: '1.0.0'
};

// Exportar configuración
window.APP_CONFIG = config;

console.log('🔧 Configuración cargada:', {
    entorno: isDevelopment ? 'Desarrollo' : 'Producción',
    apiUrl: config.API_BASE_URL
});
