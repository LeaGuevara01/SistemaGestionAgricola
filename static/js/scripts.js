// Modo oscuro / claro
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const htmlElement = document.documentElement;

const savedTheme = localStorage.getItem('theme') || 'light';
if (savedTheme === 'dark') {
    htmlElement.setAttribute('data-bs-theme', 'dark');
    themeIcon.classList.replace('bi-moon-fill', 'bi-sun-fill');
}

themeToggle?.addEventListener('click', () => {
    const isDark = htmlElement.getAttribute('data-bs-theme') === 'dark';
    htmlElement.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
    themeIcon.classList.replace(isDark ? 'bi-sun-fill' : 'bi-moon-fill', isDark ? 'bi-moon-fill' : 'bi-sun-fill');
    localStorage.setItem('theme', isDark ? 'light' : 'dark');
});

// Mostrar fecha
const currentDate = document.getElementById('current-date');
if (currentDate) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    currentDate.textContent = new Date().toLocaleDateString('es-ES', options);
}

// Listener
document.addEventListener('DOMContentLoaded', () => {
    // Mostrar header y clima con retardo
    const dash = document.querySelector('.dashboard-header');
    const weather = document.querySelector('.clima-card');

    if (dash) setTimeout(() => dash.style.opacity = '1', 500); // Retardo de 500ms
    if (weather) setTimeout(() => weather.style.opacity = '1', 700); // Retardo de 700ms

    // Animación para secciones
    document.querySelectorAll('.card-section').forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
        }, index * 100);
    });

    // Animación para botones
    document.querySelectorAll('.btn-dashboard').forEach((btn, index) => {
        setTimeout(() => {
            btn.classList.add('visible');
        }, 200 + index * 100);
    });

    // Hacer clic en una fila de máquina para redireccionar
    document.querySelectorAll('.maquina-row').forEach(row => {
        row.addEventListener('click', () => {
            const id = row.dataset.id;
            if (id) {
                window.location.href = `/maquina/${id}`;
            }
        });
    });
    
    // Llamar a cargarClima para actualizar el widget del clima
    if (typeof cargarClima === 'function') {
        cargarClima();
    }
});

// Clima
function cargarClima() {
    fetch('/api/clima')
        .then(res => res.json())
        .then(data => {
            const cont = document.getElementById('clima-container');
            const ts = document.getElementById('clima-timestamp');

            if (data.status === 'success') {
                const c = data.data;
                cont.innerHTML = `
                    <div class="weather-icon display-1"><i class="bi ${c.icono}"></i></div>
                    <h3>${c.temperatura}°C</h3>
                    <p>${c.condicion}</p>
                    <div class="row">
                        <div class="col"><i class="bi bi-droplet"></i> ${c.humedad}%</div>
                        <div class="col"><i class="bi bi-wind"></i> ${c.viento_kmh} km/h</div>
                    </div>
                `;
                ts.textContent = new Date().toLocaleTimeString();
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
