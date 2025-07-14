export function showCurrentDate() {
  const dateEl = document.getElementById('current-date');
  if (dateEl) {
    const opciones = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    dateEl.textContent = new Date().toLocaleDateString('es-ES', opciones);
  }
}
