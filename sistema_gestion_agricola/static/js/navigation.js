export function enableNavigation() {
  document.querySelectorAll('.clickable-row').forEach(row => {
    row.addEventListener('click', e => {
      if (e.target.closest('.action-cell') || e.target.closest('.btn')) return;

      const { machineId, componentId, stockId } = row.dataset;

      if (row.classList.contains('maquina-row') && machineId) {
        window.location.href = `/maquina/${machineId}`;
      } else if (row.classList.contains('component-row') && componentId) {
        window.location.href = `/componente/${componentId}?next=${encodeURIComponent(window.location.pathname)}`;
      } else if (row.classList.contains('stock-row') && stockId) {
        window.location.href = `/componente/${stockId}`;
      }
    });
  });

  document.querySelectorAll('.clickable-card').forEach(card => {
    card.addEventListener('click', e => {
      if (e.target.closest('.action-cell') || e.target.closest('.btn')) return;

      const { machineId, componentId, stockId } = card.dataset;

      if (card.classList.contains('maquina-card') && machineId) {
        window.location.href = `/maquina/${machineId}`;
      } else if (card.classList.contains('component-card') && componentId) {
        const url = machineId
          ? `/componente/${componentId}?id_maquina=${machineId}`
          : `/componente/${componentId}`;
        window.location.href = url;
      } else if (card.classList.contains('stock-card') && stockId) {
        window.location.href = `/componente/${stockId}`;
      }
    });
  });
}
