export function enableNavigation() {
  document.querySelectorAll('.clickable-row').forEach(row => {
    row.addEventListener('click', e => {
      if (e.target.closest('.action-cell') || e.target.closest('.btn')) return;

      const { machineId, componentId, stockId, proveedorId } = row.dataset;

      if (row.classList.contains('maquina-row') && machineId) {
        window.location.href = `/maquina/${machineId}`;
      } else if (row.classList.contains('component-row') && componentId) {
        window.location.href = `/componente/${componentId}?next=${encodeURIComponent(window.location.pathname)}`;
      } else if (row.classList.contains('stock-row') && stockId) {
        window.location.href = `/componente/${stockId}`;
      } else if (row.classList.contains('proveedor-row') && proveedorId) {
        window.location.href = `/pagos/proveedor/${proveedorId}`;
      }
    });
  });

  document.querySelectorAll('.clickable-card').forEach(card => {
    card.addEventListener('click', e => {
      if (e.target.closest('.btn') || e.target.tagName === 'A') return;

      const id = card.dataset.id;

      if (card.classList.contains('component-card')) {
        window.location.href = `/componente/${id}`;
      } else if (card.classList.contains('maquina-card')) {
        window.location.href = `/maquina/${id}`;
      } else if (card.classList.contains('stock-card')) {
        window.location.href = `/stock/${id}`;
      }
    });
  });
}
