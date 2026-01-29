// Configuración de la API
const API_BASE_URL = window.API_BASE_URL || 'https://noti-subvenciones-production.up.railway.app';

// Estado de la aplicación
let filtrosDisponibles = {
    organos: [],
    tiposConvocatoria: [],
    instrumentos: [],
    sectores: [],
    finalidades: []
};

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
    await cargarFiltros();
    await cargarSubvenciones();
    
    // Event listeners
    document.getElementById('filtersForm').addEventListener('submit', handleSearch);
    document.getElementById('clearBtn').addEventListener('click', handleClear);
    
    // Cargar URL del calendario
    cargarCalendarLink();
});

// Cargar opciones de filtros desde la API
async function cargarFiltros() {
    try {
        const [organos, tipos, instrumentos, sectores, finalidades] = await Promise.all([
            fetch(`${API_BASE_URL}/api/subvenciones/valores/organos`).then(r => r.json()),
            fetch(`${API_BASE_URL}/api/subvenciones/valores/tipos-convocatoria`).then(r => r.json()),
            fetch(`${API_BASE_URL}/api/subvenciones/valores/instrumentos`).then(r => r.json()),
            fetch(`${API_BASE_URL}/api/subvenciones/valores/sectores`).then(r => r.json()),
            fetch(`${API_BASE_URL}/api/subvenciones/valores/finalidades`).then(r => r.json())
        ]);
        
        filtrosDisponibles = { organos, tiposConvocatoria: tipos, instrumentos, sectores, finalidades };
        
        // Poblar los selects
        poblarSelect('organo', organos);
        poblarSelect('tipo_convocatoria', tipos);
        poblarSelect('instrumento', instrumentos);
        poblarSelect('sector', sectores);
        poblarSelect('finalidad', finalidades);
        
    } catch (error) {
        console.error('Error al cargar filtros:', error);
        mostrarError('No se pudieron cargar los filtros. Por favor, recarga la página.');
    }
}

// Poblar un select con opciones
function poblarSelect(selectId, opciones) {
    const select = document.getElementById(selectId);
    const defaultOption = select.querySelector('option[value=""]');
    
    // Limpiar opciones existentes excepto la primera
    select.innerHTML = '';
    select.appendChild(defaultOption);
    
    // Añadir nuevas opciones
    opciones.forEach(opcion => {
        const option = document.createElement('option');
        option.value = opcion;
        option.textContent = opcion;
        select.appendChild(option);
    });
}

// Cargar subvenciones con filtros
async function cargarSubvenciones(filtros = {}) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    const noResults = document.getElementById('noResults');
    const resultsCount = document.getElementById('resultsCount');
    
    // Mostrar loading
    loadingIndicator.style.display = 'block';
    resultsContainer.style.display = 'none';
    noResults.style.display = 'none';
    
    try {
        // Construir query params
        const params = new URLSearchParams();
        params.append('limit', '50');
        params.append('activa', 'true');
        
        Object.entries(filtros).forEach(([key, value]) => {
            if (value) params.append(key, value);
        });
        
        const response = await fetch(`${API_BASE_URL}/api/subvenciones?${params}`);
        const subvenciones = await response.json();
        
        // Ocultar loading
        loadingIndicator.style.display = 'none';
        
        if (subvenciones.length === 0) {
            noResults.style.display = 'block';
            resultsCount.textContent = '0 resultados';
        } else {
            resultsContainer.style.display = 'block';
            resultsCount.textContent = `${subvenciones.length} resultado${subvenciones.length !== 1 ? 's' : ''}`;
            renderizarSubvenciones(subvenciones);
        }
        
    } catch (error) {
        console.error('Error al cargar subvenciones:', error);
        loadingIndicator.style.display = 'none';
        mostrarError('Error al cargar las subvenciones. Por favor, inténtalo de nuevo.');
    }
}

// Renderizar lista de subvenciones
function renderizarSubvenciones(subvenciones) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';
    
    subvenciones.forEach(sub => {
        const card = crearCardSubvencion(sub);
        container.appendChild(card);
    });
}

// Crear card de subvención
function crearCardSubvencion(sub) {
    const card = document.createElement('div');
    card.className = 'subvencion-card';
    
    // Formatear fechas
    const fechaInicio = sub.fecha_inicio_solicitud ? formatearFecha(sub.fecha_inicio_solicitud) : null;
    const fechaFin = sub.fecha_fin_solicitud ? formatearFecha(sub.fecha_fin_solicitud) : 'No especificada';
    
    // Formatear presupuesto
    const presupuesto = sub.presupuesto_total ? formatearPresupuesto(sub.presupuesto_total) : 'No especificado';
    
    card.innerHTML = `
        <div class="subvencion-header">
            <h4 class="subvencion-title">${sub.titulo || 'Sin título'}</h4>
            <div class="subvencion-meta">
                ${sub.organo_convocante ? `<span class="meta-item">🏛️ ${sub.organo_convocante}</span>` : ''}
                ${fechaFin !== 'No especificada' ? `<span class="meta-item">📅 Plazo: ${fechaFin}</span>` : ''}
                ${presupuesto !== 'No especificado' ? `<span class="meta-item">💰 ${presupuesto}</span>` : ''}
            </div>
        </div>
        
        <div class="subvencion-body">
            ${sub.descripcion ? `<p class="subvencion-description">${truncarTexto(sub.descripcion, 200)}</p>` : ''}
            
            <div class="subvencion-tags">
                ${sub.tipo_convocatoria ? `<span class="tag">📋 ${sub.tipo_convocatoria}</span>` : ''}
                ${sub.finalidad_nombre ? `<span class="tag">🎯 ${sub.finalidad_nombre}</span>` : ''}
                ${sub.region_nombre ? `<span class="tag">📍 ${sub.region_nombre}</span>` : ''}
            </div>
        </div>
        
        <div class="subvencion-footer">
            ${sub.url_bdns ? `<a href="${sub.url_bdns}" target="_blank" class="btn btn-primary btn-small">Ver en BDNS</a>` : ''}
            ${sub.url_bases_reguladoras ? `<a href="${sub.url_bases_reguladoras}" target="_blank" class="btn btn-secondary btn-small">Bases Reguladoras</a>` : ''}
            ${sub.url_sede_electronica ? `<a href="${sub.url_sede_electronica}" target="_blank" class="btn btn-secondary btn-small">Sede Electrónica</a>` : ''}
        </div>
    `;
    
    return card;
}

// Manejar búsqueda
function handleSearch(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const filtros = {};
    
    formData.forEach((value, key) => {
        if (value) filtros[key] = value;
    });
    
    cargarSubvenciones(filtros);
}

// Limpiar filtros
function handleClear() {
    document.getElementById('filtersForm').reset();
    cargarSubvenciones();
}

// Cargar link del calendario
async function cargarCalendarLink() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/calendar/url`);
        const data = await response.json();
        
        if (data.url) {
            document.getElementById('calendarLink').href = data.url;
        }
    } catch (error) {
        console.error('Error al cargar URL del calendario:', error);
    }
}

// Utilidades
function formatearFecha(fecha) {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function formatearPresupuesto(cantidad) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        maximumFractionDigits: 0
    }).format(cantidad);
}

function truncarTexto(texto, maxLength) {
    if (!texto) return '';
    if (texto.length <= maxLength) return texto;
    return texto.substring(0, maxLength) + '...';
}

function mostrarError(mensaje) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = `
        <div class="no-results">
            <p>⚠️ ${mensaje}</p>
        </div>
    `;
    resultsContainer.style.display = 'block';
}
