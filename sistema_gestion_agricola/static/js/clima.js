// static/js/clima.js
export function cargarClima() {
  const climaCont = document.getElementById('clima-container');
  const ts = document.getElementById('clima-timestamp');
  if (!climaCont) return;

  fetch('/api/clima/')
    .then(res => {
      // Check if response is JSON
      const contentType = res.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error(`Respuesta no es JSON. Status: ${res.status}`);
      }
      return res.json();
    })
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
  
  fetch('/api/clima/')
  .then(async res => {
    let data;
    try {
      data = await res.json();
    } catch (e) {
      throw new Error(`Respuesta inválida. Código: ${res.status}`);
    }

    if (!res.ok) {
      throw new Error(data.message || `Error ${res.status}`);
    }

    return data;
  })
  .then(data => {
    // mostrar clima
  })
  .catch(err => mostrarErrorClima(err.message));

}
