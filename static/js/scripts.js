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
    // Actualizar el widget del clima
    if (typeof cargarClima === 'function') {
        cargarClima();
    }
    // Mostrar header, clima y cartas con retardo
    const header = document.querySelector('.dashboard-header');
    const weather = document.querySelector('.clima-card');
    let cards = document.querySelectorAll('.card-section');
    // Ensure cards is an array
    console.log('Cards found:', cards.length);
    cards = Array.from(cards);
    // Function to reveal hidden elements with delay
    function showElement(element, delay) {
        if (!element) return;
        setTimeout(() => {
            console.log('Showing element:', element.className);
            element.classList.remove('hidden-item');
            // Force reflow to restart CSS transition
            void element.offsetWidth;
            element.classList.add('visible-item');
        }, delay);
    }
    // Initialize elements as hidden
    if (header) {
        header.classList.add('hidden-item');
        console.log('Header hidden initially');
    }
    if (weather) {
        weather.classList.add('hidden-item');
        console.log('Weather hidden initially');
    }
    if (cards && cards.length) {
        cards.forEach(card => {
            card.classList.add('hidden-item');
            console.log('Card hidden initially:', card.className);
        });
    } else {
        console.log('No cards found with class "card-section"');
    }
    // Show elements gradually in correct order
    showElement(header, 0);
    showElement(weather, 600);
    cards.forEach((card, index) => {
        showElement(card, 1200 + index * 300);
    });

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
});
// Clima
function cargarClima() {
    const cont = document.getElementById('clima-container');
    const ts = document.getElementById('clima-timestamp');
    
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
                
                // Simple fade and replace
                const spinner = cont.querySelector('.spinner-border');
                if (spinner) {
                    spinner.style.opacity = '0';
                    setTimeout(() => {
                        cont.innerHTML = newContent;
                    }, 300);
                } else {
                    cont.innerHTML = newContent;
                }
                
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
