// Modo oscuro / claro
const htmlElement = document.body;
const themeIcon = document.getElementById('themeIcon');
const themeToggle = document.getElementById('themeToggle');
if (themeToggle && themeIcon) {
    themeToggle.addEventListener('click', () => {
        const isDark = htmlElement.getAttribute('data-bs-theme') === 'dark';
        htmlElement.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
        themeIcon.classList.replace(isDark ? 'bi-sun-fill' : 'bi-moon-fill', isDark ? 'bi-moon-fill' : 'bi-sun-fill');
        localStorage.setItem('theme', isDark ? 'light' : 'dark');
    });
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        htmlElement.setAttribute('data-bs-theme', 'dark');
        themeIcon.classList.replace('bi-moon-fill', 'bi-sun-fill');
    }
}

// Fecha actual
function setCurrentDate() {
    const el = document.getElementById('current-date');
    if (el) {
        const opciones = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        el.textContent = new Date().toLocaleDateString('es-ES', opciones);
    }
}
setCurrentDate();

// Animaciones de entrada
document.addEventListener('DOMContentLoaded', () => {
    // Animar header
    setTimeout(() => {
        document.querySelector('.dashboard-header')?.classList.add('show');
    }, 100);
    // Animar .card-section
    document.querySelectorAll('.card-section').forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
            section.style.transition = `all 0.5s cubic-bezier(.4,2,.6,1) ${index * 80}ms`;
        }, 200 + index * 80);
    });
});

// Filas y cards clickeables
function setupClickableRows() {
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', function(e) {
            if (e.target.closest('.action-cell') || e.target.closest('.btn')) return;
            const id = this.dataset.machineId || this.dataset.componentId || this.dataset.stockId;
            if (this.classList.contains('maquina-row')) {
                window.location.href = `/maquinas/${id}`;
            } else if (this.classList.contains('component-row') || this.classList.contains('stock-row')) {
                window.location.href = `/componente/${id}`;
            }
        });
    });
    document.querySelectorAll('.clickable-card').forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.closest('.action-cell') || e.target.closest('.btn')) return;
            const id = this.dataset.machineId || this.dataset.componentId || this.dataset.stockId;
            if (this.classList.contains('maquina-card')) {
                window.location.href = `/maquinas/${id}`;
            } else if (this.classList.contains('component-card') || this.classList.contains('stock-card')) {
                window.location.href = `/componente/${id}`;
            }
        });
    });
}
document.addEventListener('DOMContentLoaded', setupClickableRows);

// Tooltips Bootstrap
document.addEventListener('DOMContentLoaded', () => {
    if (window.bootstrap) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    }
});

// Vista previa de imagen reutilizable
function setupImagePreview(inputId, previewId, placeholderId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        const preview = document.getElementById(previewId);
        const placeholder = document.getElementById(placeholderId);
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                if (preview) {
                    preview.src = e.target.result;
                } else if (placeholder) {
                    const newImg = document.createElement('img');
                    newImg.src = e.target.result;
                    newImg.className = 'img-fluid rounded shadow';
                    newImg.id = previewId;
                    newImg.alt = 'Vista previa';
                    placeholder.replaceWith(newImg);
                }
            };
            reader.readAsDataURL(file);
        }
    });
}

// setupImagePreview('foto', 'imagePreview', 'imagePlaceholder');

// Validación de formularios reutilizable
function setupFormValidation(formId, requiredFields) {
    const form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener('submit', function(e) {
        for (const fieldId of requiredFields) {
            const field = document.getElementById(fieldId);
            if (field && !field.value.trim()) {
                e.preventDefault();
                alert(`El campo ${fieldId} es obligatorio`);
                field.focus();
                return false;
            }
        }
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Guardando...';
            submitBtn.disabled = true;
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 3000);
        }
    });
}
// Ejemplo de uso:
// setupFormValidation('editMachineForm', ['nombre']);
// setupFormValidation('editComponentForm', ['nombre']);

// Confirmación de eliminación reutilizable
function confirmDelete(url, msg) {
    if (confirm(msg || '¿Estás seguro de que querés eliminar este elemento? Esta acción no se puede deshacer.')) {
        window.location.href = url;
    }
}
// Ejemplo de uso en template:
// <button onclick="confirmDelete('{{ url_for('eliminar_componente', id=componente.ID) }}', '¿Eliminar este componente?')">Eliminar</button>

// Filtros y búsqueda
function filterComponents() {
    const searchInput = document.getElementById('searchInput');
    const filterType = document.getElementById('filterType');
    if (!searchInput || !filterType) return;
    const searchTerm = searchInput.value.toLowerCase();
    const typeValue = filterType.value;

    document.querySelectorAll('.component-row').forEach(row => {
        const name = row.dataset.name || '';
        const description = row.dataset.description || '';
        const type = row.dataset.type || '';
        const matchesSearch = name.includes(searchTerm) || description.includes(searchTerm);
        const matchesType = !typeValue || type === typeValue;
        row.style.display = matchesSearch && matchesType ? '' : 'none';
    });

    document.querySelectorAll('.component-card-wrapper').forEach(wrapper => {
        const name = wrapper.dataset.name || '';
        const description = wrapper.dataset.description || '';
        const type = wrapper.dataset.type || '';
        const matchesSearch = name.includes(searchTerm) || description.includes(searchTerm);
        const matchesType = !typeValue || type === typeValue;
        wrapper.style.display = matchesSearch && matchesType ? '' : 'none';
    });
}
window.filterComponents = filterComponents; // Para usar en HTML

function clearFilters() {
    const searchInput = document.getElementById('searchInput');
    const filterType = document.getElementById('filterType');
    if (searchInput) searchInput.value = '';
    if (filterType) filterType.value = '';
    filterComponents();
}
window.clearFilters = clearFilters;

// Cambiar vista tabla/cards
function toggleView(view) {
    const tableView = document.getElementById('tableView');
    const cardsView = document.getElementById('cardsView');
    const tableBtn = document.getElementById('tableViewBtn');
    const cardsBtn = document.getElementById('cardsViewBtn');
    if (!tableView || !cardsView || !tableBtn || !cardsBtn) return;
    if (view === 'table') {
        tableView.classList.remove('d-none');
        cardsView.classList.add('d-none');
        tableBtn.classList.add('active');
        cardsBtn.classList.remove('active');
    } else {
        tableView.classList.add('d-none');
        cardsView.classList.remove('d-none');
        tableBtn.classList.remove('active');
        cardsBtn.classList.add('active');
    }
}
window.toggleView = toggleView;

// Widget de clima
function cargarClima() {
    const cont = document.getElementById('clima-container');
    const ts = document.getElementById('clima-timestamp');
    if (!cont) return;
    fetch('/api/clima')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                const c = data.data;
                const newContent = `
                    <div class="weather-icon"><i class="bi ${c.icono}"></i></div>
                    <h3>${c.temperatura}°C</h3>
                    <p>${c.condicion}</p>
                    <div class="row">
                        <div class="col"><i class="bi bi-droplet"></i> ${c.humedad}%</div>
                        <div class="col"><i class="bi bi-wind"></i> ${c.viento_kmh} km/h</div>
                    </div>
                `;
                const spinner = cont.querySelector('.spinner-border');
                if (spinner) {
                    spinner.style.opacity = '0';
                    setTimeout(() => { cont.innerHTML = newContent; }, 300);
                } else {
                    cont.innerHTML = newContent;
                }
                if (ts) ts.textContent = new Date().toLocaleTimeString();
            } else {
                mostrarErrorClima(data.message);
            }
        })
        .catch(err => mostrarErrorClima(err.message));
}
function mostrarErrorClima(msg) {
    const cont = document.getElementById('clima-container');
    if (cont) {
        cont.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> ${msg || 'Error al cargar clima'}
            </div>
        `;
    }
}
document.addEventListener('DOMContentLoaded', () => {
    if (typeof cargarClima === 'function') cargarClima();
});
// Animación gradual para las estadísticas
document.addEventListener('DOMContentLoaded', function() {
    // Animar header primero
    setTimeout(() => {
        const header = document.querySelector('.dashboard-header');
        if (header) {
            header.style.opacity = '1';
        }
    }, 100);
    
    // Animar estadísticas con delay escalonado
    const statCards = document.querySelectorAll('.stat-card.hidden-item');
    statCards.forEach((card, index) => {
        const delay = parseInt(card.dataset.delay) || (index + 1) * 150;
        setTimeout(() => {
            card.classList.remove('hidden-item');
            card.classList.add('visible-item');
        }, delay + 300);
    });
    
    // Animar filtros después de las estadísticas
    setTimeout(() => {
        const filterSection = document.querySelector('.card-section.hidden-item');
        if (filterSection) {
            filterSection.classList.remove('hidden-item');
            filterSection.classList.add('visible-item');
        }
    }, 800);
    
    // Animar tabla/cards al final
    setTimeout(() => {
        const tableSection = document.querySelector('.card-section.hidden-item:last-of-type');
        if (tableSection) {
            tableSection.classList.remove('hidden-item');
            tableSection.classList.add('visible-item');
        }
    }, 1000);
    
    // Hacer filas clickeables
    const clickableRows = document.querySelectorAll('.clickable-row');
    clickableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // No redirigir si se hace click en la columna de acciones
            if (e.target.closest('.action-cell') || e.target.closest('.btn')) {
                return;
            }
            
            const machineId = this.dataset.machineId;
            if (machineId) {
                window.location.href = `/maquina/${machineId}`;
            }
        });
    });
    
    // Hacer cards clickeables
    const clickableCards = document.querySelectorAll('.clickable-card');
    clickableCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // No redirigir si se hace click en la zona de acciones
            if (e.target.closest('.action-cell') || e.target.closest('.btn')) {
                return;
            }
            
            const machineId = this.dataset.machineId;
            if (machineId) {
                window.location.href = `/maquina/${machineId}`;
            }
        });
    });
});

// Funcionalidad de búsqueda y filtros
document.getElementById('searchInput').addEventListener('input', filterMachines);
document.getElementById('filterEstado').addEventListener('change', filterMachines);
document.getElementById('filterMarca').addEventListener('change', filterMachines);

function filterMachines() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const estadoFilter = document.getElementById('filterEstado').value;
    const marcaFilter = document.getElementById('filterMarca').value;
    
    // Filtrar tabla
    const tableRows = document.querySelectorAll('.maquina-row');
    tableRows.forEach(row => {
        const name = row.dataset.name;
        const marca = row.dataset.marca;
        const modelo = row.dataset.modelo;
        const estado = row.dataset.estado;
        
        const matchesSearch = name.includes(searchTerm) || marca.includes(searchTerm) || modelo.includes(searchTerm);
        const matchesEstado = !estadoFilter || estado === estadoFilter;
        const matchesMarca = !marcaFilter || marca.includes(marcaFilter.toLowerCase());
        
        row.style.display = matchesSearch && matchesEstado && matchesMarca ? '' : 'none';
    });
    
    // Filtrar cards
    const cardWrappers = document.querySelectorAll('.machine-card-wrapper');
    cardWrappers.forEach(wrapper => {
        const name = wrapper.dataset.name;
        const marca = wrapper.dataset.marca;
        const modelo = wrapper.dataset.modelo;
        const estado = wrapper.dataset.estado;
        
        const matchesSearch = name.includes(searchTerm) || marca.includes(searchTerm) || modelo.includes(searchTerm);
        const matchesEstado = !estadoFilter || estado === estadoFilter;
        const matchesMarca = !marcaFilter || marca.includes(marcaFilter.toLowerCase());
        
        wrapper.style.display = matchesSearch && matchesEstado && matchesMarca ? '' : 'none';
    });
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('filterEstado').value = '';
    document.getElementById('filterMarca').value = '';
    filterMachines();
}

function toggleView(view) {
    const tableView = document.getElementById('tableView');
    const cardsView = document.getElementById('cardsView');
    const tableBtn = document.getElementById('tableViewBtn');
    const cardsBtn = document.getElementById('cardsViewBtn');
    
    if (view === 'table') {
        tableView.classList.remove('d-none');
        cardsView.classList.add('d-none');
        tableBtn.classList.add('active');
        cardsBtn.classList.remove('active');
    } else {
        tableView.classList.add('d-none');
        cardsView.classList.remove('d-none');
        tableBtn.classList.remove('active');
        cardsBtn.classList.add('active');
    }
}