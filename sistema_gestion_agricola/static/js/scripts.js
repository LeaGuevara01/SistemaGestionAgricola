document.addEventListener('DOMContentLoaded', () => {
    // --------- Tema oscuro / claro ----------
    const htmlElement = document.body;
    const themeIcon = document.getElementById('themeIcon');
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('theme') || 'light';

    htmlElement.setAttribute('data-bs-theme', savedTheme);
    if (themeIcon) {
        themeIcon.classList.replace('bi-moon-fill', savedTheme === 'dark' ? 'bi-sun-fill' : 'bi-moon-fill');
    }

    if (themeToggle && themeIcon) {
        themeToggle.addEventListener('click', () => {
            const isDark = htmlElement.getAttribute('data-bs-theme') === 'dark';
            htmlElement.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
            themeIcon.classList.replace(
                isDark ? 'bi-sun-fill' : 'bi-moon-fill',
                isDark ? 'bi-moon-fill' : 'bi-sun-fill'
            );
            localStorage.setItem('theme', isDark ? 'light' : 'dark');
        });
    }

    // --------- Fecha actual ----------
    const dateEl = document.getElementById('current-date');
    if (dateEl) {
        const opciones = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        dateEl.textContent = new Date().toLocaleDateString('es-ES', opciones);
    }

    // --------- Animaciones ---------
    setTimeout(() => {
        document.querySelector('.dashboard-header')?.classList.add('show');
    }, 100);

    document.querySelectorAll('.card-section').forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
            section.style.transition = `all 0.5s cubic-bezier(.4,2,.6,1) ${index * 80}ms`;
        }, 200 + index * 80);
    });

    document.querySelectorAll('.stat-card.hidden-item').forEach(card => {
        const delay = parseInt(card.dataset.delay) || 0;
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.classList.add('show');
            card.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        }, delay);
    });

    // --------- Tooltips Bootstrap ----------
    if (window.bootstrap) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    }

    // --------- Filas y Cards clickeables ----------
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', function(e) {
            if (e.target.closest('.action-cell') || e.target.closest('.btn')) return;

            const machineId = this.dataset.machineId;
            const componentId = this.dataset.componentId;
            const stockId = this.dataset.stockId;

            if (this.classList.contains('maquina-row') && machineId) {
                window.location.href = `/maquina/${machineId}`;
            } else if (this.classList.contains('component-row') && componentId) {
                const url = `/componente/${componentId}?next=${encodeURIComponent(window.location.pathname)}`;
                window.location.href = url;
            } else if (this.classList.contains('stock-row') && stockId) {
                window.location.href = `/componente/${stockId}`;
            }
        });
    });

    document.querySelectorAll('.clickable-card').forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.closest('.action-cell') || e.target.closest('.btn')) return;

            const componentId = this.dataset.componentId;
            const machineId = this.dataset.machineId;
            const stockId = this.dataset.stockId;

            if (this.classList.contains('maquina-card') && machineId) {
                window.location.href = `/maquina/${machineId}`;
            } else if (this.classList.contains('component-card') && componentId) {
                const url = machineId
                    ? `/componente/${componentId}?id_maquina=${machineId}`
                    : `/componente/${componentId}`;
                window.location.href = url;
            } else if (this.classList.contains('stock-card') && stockId) {
                window.location.href = `/componente/${stockId}`;
            }
        });
    });

    // --------- Clima API ----------
    const climaCont = document.getElementById('clima-container');
    if (climaCont) cargarClima();

    function cargarClima() {
        const ts = document.getElementById('clima-timestamp');
        fetch('/api/clima')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    const c = data.data;
                    climaCont.innerHTML = `
                        <div class="weather-icon"><i class="bi ${c.icono}"></i></div>
                        <h3>${c.temperatura}°C</h3>
                        <p>${c.condicion}</p>
                        <div class="row">
                            <div class="col"><i class="bi bi-droplet"></i> ${c.humedad}%</div>
                            <div class="col"><i class="bi bi-wind"></i> ${c.viento_kmh} km/h</div>
                        </div>
                    `;
                    if (ts) ts.textContent = new Date().toLocaleTimeString();
                } else {
                    mostrarErrorClima(data.message);
                }
            })
            .catch(err => mostrarErrorClima(err.message));
    }

    function mostrarErrorClima(msg) {
        climaCont.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> ${msg || 'Error al cargar clima'}
            </div>
        `;
    }

    // --------- Filtros de búsqueda (máquinas) ----------
    const searchInput = document.getElementById('searchInput');
    const filterEstado = document.getElementById('filterEstado');
    const filterMarca = document.getElementById('filterMarca');

    if (searchInput) searchInput.addEventListener('input', filterMachines);
    if (filterEstado) filterEstado.addEventListener('change', filterMachines);
    if (filterMarca) filterMarca.addEventListener('change', filterMachines);

    function filterMachines() {
        const searchTerm = (searchInput?.value || '').toLowerCase();
        const estadoVal = filterEstado?.value || '';
        const marcaVal = filterMarca?.value || '';

        document.querySelectorAll('.maquina-row').forEach(row => {
            const name = row.dataset.name || '';
            const marca = row.dataset.marca || '';
            const modelo = row.dataset.modelo || '';
            const estado = row.dataset.estado || '';

            const matches = name.includes(searchTerm) || marca.includes(searchTerm) || modelo.includes(searchTerm);
            const matchesEstado = !estadoVal || estado === estadoVal;
            const matchesMarca = !marcaVal || marca.includes(marcaVal.toLowerCase());

            row.style.display = matches && matchesEstado && matchesMarca ? '' : 'none';
        });

        document.querySelectorAll('.machine-card-wrapper').forEach(wrapper => {
            const name = wrapper.dataset.name || '';
            const marca = wrapper.dataset.marca || '';
            const modelo = wrapper.dataset.modelo || '';
            const estado = wrapper.dataset.estado || '';

            const matches = name.includes(searchTerm) || marca.includes(searchTerm) || modelo.includes(searchTerm);
            const matchesEstado = !estadoVal || estado === estadoVal;
            const matchesMarca = !marcaVal || marca.includes(marcaVal.toLowerCase());

            wrapper.style.display = matches && matchesEstado && matchesMarca ? '' : 'none';
        });
    }

    // --------- Limpiar filtros ----------
    window.clearFilters = function() {
        searchInput && (searchInput.value = '');
        filterEstado && (filterEstado.value = '');
        filterMarca && (filterMarca.value = '');
        filterMachines(); // Refiltra después de limpiar
    };

    // --------- Cambiar vista cards/tabla ----------
    window.toggleView = function(view) {
        const tableView = document.getElementById('tableView');
        const cardsView = document.getElementById('cardsView');
        const tableBtn = document.getElementById('tableViewBtn');
        const cardsBtn = document.getElementById('cardsViewBtn');

        if (!tableView || !cardsView || !tableBtn || !cardsBtn) return;
        const isTable = view === 'table';
        tableView.classList.toggle('d-none', !isTable);
        cardsView.classList.toggle('d-none', isTable);
        tableBtn.classList.toggle('active', isTable);
        cardsBtn.classList.toggle('active', !isTable);
    };
});
