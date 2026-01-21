#!/usr/bin/env node

/**
 * Script de build para generar config.js con variables de entorno
 * Se ejecuta en Vercel antes del deployment
 */

const fs = require('fs');
const path = require('path');

// Leer variable de entorno
const API_URL = process.env.VITE_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

console.log('🔧 Generando config.js con API_URL:', API_URL);

// Generar contenido del config.js
const configContent = `/**
 * Configuración del frontend
 * Generado automáticamente durante el build
 */

// Configuración
const config = {
    // URL del backend (configurada vía variable de entorno en Vercel)
    API_BASE_URL: '${API_URL}',
    
    // Otras configuraciones
    APP_NAME: 'Sistema de Notificaciones de Subvenciones',
    APP_VERSION: '1.0.0'
};

// Exportar configuración
window.APP_CONFIG = config;

console.log('🔧 Configuración cargada:', {
    apiUrl: config.API_BASE_URL
});
`;

// Escribir archivo
const outputPath = path.join(__dirname, 'config.js');
fs.writeFileSync(outputPath, configContent, 'utf8');

console.log('✅ config.js generado exitosamente en:', outputPath);
