export function cargarClima() {
  const climaCont = document.getElementById('clima-container');
  const ts = document.getElementById('clima-timestamp');
  if (!climaCont) return;

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
          </div>`;
        if (ts) ts.textContent = new Date().toLocaleTimeString();
      } else {
        mostrarErrorClima(data.message);
      }
    })
    .catch(err => mostrarErrorClima(err.message));

  function mostrarErrorClima(msg) {
    climaCont.innerHTML = `
      <div class="alert alert-warning">
        <i class="bi bi-exclamation-triangle"></i> ${msg || 'Error al cargar clima'}
      </div>`;
  }
}
