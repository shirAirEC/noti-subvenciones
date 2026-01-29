/**
 * Frontend JavaScript - Sistema de Notificaciones de Subvenciones
 */

// Configuración - usar config.js para detectar automáticamente el entorno
const API_BASE_URL = window.APP_CONFIG?.API_BASE_URL || 'http://localhost:8000';

// Elementos del DOM
const form = document.getElementById('subscriptionForm');
const submitBtn = document.getElementById('submitBtn');
const responseMessage = document.getElementById('responseMessage');
const calendarLink = document.getElementById('calendarLink');

/**
 * Inicializar aplicación
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Aplicación iniciada');
    
    // Cargar catálogos
    await cargarCatalogos();
    
    // Configurar formulario
    form.addEventListener('submit', handleSubmit);
    
    // Configurar enlaces de calendario
    // TODO: Obtener URL real del calendario desde API
    if (calendarLink) {
        calendarLink.href = '#';
    }
});

/**
 * Cargar catálogos desde API
 */
async function cargarCatalogos() {
    try {
        // Cargar regiones
        const regiones = await fetchAPI('/api/regiones');
        if (regiones && regiones.length > 0) {
            actualizarRegiones(regiones);
        }
        
        // Cargar áreas temáticas
        const areas = await fetchAPI('/api/areas');
        if (areas && areas.length > 0) {
            actualizarAreas(areas);
        }
    } catch (error) {
        console.warn('No se pudieron cargar los catálogos:', error);
    }
}

/**
 * Actualizar checkboxes de regiones
 */
function actualizarRegiones(regiones) {
    const regionesGroup = document.getElementById('regionesGroup');
    regionesGroup.innerHTML = '';
    
    regiones.forEach(region => {
        const label = document.createElement('label');
        label.className = 'checkbox-label';
        label.innerHTML = `
            <input type="checkbox" name="regiones" value="${region.id}">
            <span>${region.nombre}</span>
        `;
        regionesGroup.appendChild(label);
    });
}

/**
 * Actualizar checkboxes de áreas temáticas
 */
function actualizarAreas(areas) {
    const areasGroup = document.getElementById('areasGroup');
    areasGroup.innerHTML = '';
    
    areas.forEach(area => {
        const label = document.createElement('label');
        label.className = 'checkbox-label';
        label.innerHTML = `
            <input type="checkbox" name="areas" value="${area.id}">
            <span>${area.nombre}</span>
        `;
        areasGroup.appendChild(label);
    });
}

/**
 * Manejar envío del formulario
 */
async function handleSubmit(e) {
    e.preventDefault();
    
    // Deshabilitar botón
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Procesando...';
    
    // Ocultar mensajes anteriores
    responseMessage.style.display = 'none';
    
    try {
        // Recopilar datos del formulario
        const formData = {
            email: document.getElementById('email').value.trim(),
            nombre: document.getElementById('nombre').value.trim() || null,
            regiones: getSelectedValues('regiones'),
            areas_tematicas: getSelectedValues('areas'),
            presupuesto_min: parseFloat(document.getElementById('presupuesto_min').value) || null,
            presupuesto_max: parseFloat(document.getElementById('presupuesto_max').value) || null,
        };
        
        // Validar datos
        if (!formData.email) {
            throw new Error('El email es obligatorio');
        }
        
        // Enviar a API
        const response = await fetchAPI('/api/suscripcion/crear', {
            method: 'POST',
            body: JSON.stringify(formData),
        });
        
        // Mostrar mensaje de éxito
        showMessage(
            `✅ ¡Suscripción creada! Revisa tu email para confirmar. 
            <br><br>
            <a href="${response.calendar_url}" target="_blank">Ver Calendario</a>`,
            'success'
        );
        
        // Limpiar formulario
        form.reset();
        
    } catch (error) {
        console.error('Error al crear suscripción:', error);
        showMessage(
            `❌ Error: ${error.message}`,
            'error'
        );
    } finally {
        // Rehabilitar botón
        submitBtn.disabled = false;
        submitBtn.textContent = 'Suscribirme';
    }
}

/**
 * Obtener valores seleccionados de checkboxes
 */
function getSelectedValues(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
    const values = Array.from(checkboxes).map(cb => {
        const value = cb.value;
        // Convertir a número si es posible
        return isNaN(value) ? value : parseInt(value);
    });
    return values.length > 0 ? values : null;
}

/**
 * Mostrar mensaje de respuesta
 */
function showMessage(message, type) {
    responseMessage.innerHTML = message;
    responseMessage.className = `response-message ${type}`;
    responseMessage.style.display = 'block';
    
    // Scroll al mensaje
    responseMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Realizar petición a la API
 */
async function fetchAPI(endpoint, options = {}) {
    // Asegurar que no haya doble barra en la URL
    const baseUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${baseUrl}${cleanEndpoint}`;
    
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Error HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error en petición API:', error);
        throw error;
    }
}

/**
 * Manejar confirmación de suscripción desde URL
 */
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

if (token) {
    // Confirmar suscripción automáticamente
    (async () => {
        try {
            await fetchAPI(`/api/suscripcion/confirmar?token=${token}`, {
                method: 'POST',
            });
            
            showMessage(
                '✅ ¡Suscripción confirmada! Ya estás recibiendo notificaciones.',
                'success'
            );
        } catch (error) {
            showMessage(
                `❌ Error al confirmar suscripción: ${error.message}`,
                'error'
            );
        }
    })();
}
