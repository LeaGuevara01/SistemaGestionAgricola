let searchInput, filterEstado, filterMarca;

export function initMachineFilters() {
  searchInput = document.getElementById('searchInput');
  filterEstado = document.getElementById('filterEstado');
  filterMarca = document.getElementById('filterMarca');

  if (searchInput) searchInput.addEventListener('input', filterMachines);
  if (filterEstado) filterEstado.addEventListener('change', filterMachines);
  if (filterMarca) filterMarca.addEventListener('change', filterMachines);
}

export function clearFilters() {
  if (searchInput) searchInput.value = '';
  if (filterEstado) filterEstado.value = '';
  if (filterMarca) filterMarca.value = '';
  filterMachines();
}

function filterMachines() {
  const searchTerm = (searchInput?.value || '').toLowerCase();
  const estadoVal = filterEstado?.value || '';
  const marcaVal = filterMarca?.value || '';

  document.querySelectorAll('.maquina-row, .machine-card-wrapper').forEach(el => {
    const name = el.dataset.name?.toLowerCase() || '';
    const marca = el.dataset.marca?.toLowerCase() || '';
    const modelo = el.dataset.modelo?.toLowerCase() || '';
    const estado = el.dataset.estado || '';

    const matches = name.includes(searchTerm) || marca.includes(searchTerm) || modelo.includes(searchTerm);
    const matchesEstado = !estadoVal || estado === estadoVal;
    const matchesMarca = !marcaVal || marca.includes(marcaVal.toLowerCase());

    el.style.display = matches && matchesEstado && matchesMarca ? '' : 'none';
  });
}
