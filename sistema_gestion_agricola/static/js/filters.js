// static/js/filters.js
export function initMachineFilters() {
  const searchInput = document.getElementById('searchInput');
  const filterEstado = document.getElementById('filterEstado');
  const filterMarca = document.getElementById('filterMarca');

  function filtrarMaquinas() {
    const textoBusqueda = searchInput.value.toLowerCase();
    const estadoSeleccionado = filterEstado.value.toLowerCase();
    const marcaSeleccionada = filterMarca.value.toLowerCase();

    const maquinaCards = document.querySelectorAll('.maquina-card');
    const maquinaRows = document.querySelectorAll('.maquina-row');

    [...maquinaCards, ...maquinaRows].forEach(maquina => {
      const nombre = (maquina.dataset.name || '').toLowerCase();
      const marca = (maquina.dataset.marca || '').toLowerCase();
      const estado = (maquina.dataset.estado || '').toLowerCase();

      const coincideBusqueda = nombre.includes(textoBusqueda);
      const coincideEstado = !estadoSeleccionado || estado === estadoSeleccionado;
      const coincideMarca = !marcaSeleccionada || marca === marcaSeleccionada;

      maquina.style.display = (coincideBusqueda && coincideEstado && coincideMarca) ? '' : 'none';
    });
  }

  searchInput?.addEventListener('input', filtrarMaquinas);
  filterEstado?.addEventListener('change', filtrarMaquinas);
  filterMarca?.addEventListener('change', filtrarMaquinas);
}

export function initComponentFilters() {
    const inputs = document.querySelectorAll('.filter-input');
    const rows = document.querySelectorAll('.component-row');
    const cards = document.querySelectorAll('.component-card');

    inputs.forEach(input => {
        input.addEventListener('input', () => {
            const filters = {};
            inputs.forEach(i => {
                const field = i.dataset.field;
                const value = i.value.toLowerCase().trim();
                if (value) filters[field] = value;
            });

            // Función común para aplicar filtros a cualquier tipo de elemento (fila o carta)
            function applyFiltersTo(elements) {
                elements.forEach(el => {
                    let visible = true;

                    for (const field in filters) {
                        const dataValue = el.dataset[field]?.toLowerCase() || '';
                        if (!dataValue.includes(filters[field])) {
                            visible = false;
                            break;
                        }
                    }

                    el.style.display = visible ? '' : 'none';
                });
            }

            applyFiltersTo(rows);
            applyFiltersTo(cards);
        });
    });
}

export function clearFilters() {
  document.getElementById('searchInput').value = '';
  document.getElementById('filterEstado').value = '';
  document.getElementById('filterMarca').value = '';

  const eventInput = new Event('input');
  const eventChange = new Event('change');

  document.getElementById('searchInput').dispatchEvent(eventInput);
  document.getElementById('filterEstado').dispatchEvent(eventChange);
  document.getElementById('filterMarca').dispatchEvent(eventChange);
}
