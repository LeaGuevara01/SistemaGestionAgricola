import { animateElements } from './animations.js';

// Función toggleView para cambiar entre cards y tabla
export function toggleView(view) {
  const cardsView = document.getElementById('cardsView');
  const tableView = document.getElementById('tableView');

  if (view === 'cards') {
    tableView.style.display = 'none';
    cardsView.style.display = 'block';

    // Forzar reflow para que el CSS detecte el cambio y permita la animación
    void cardsView.offsetWidth;

    cardsView.style.opacity = '1';
    cardsView.style.transform = 'translateY(0)';

    animateElements('#cardsView .card'); // animar las cards
  } else {
    // Ocultar cards con animación y luego mostrar tabla
    cardsView.style.opacity = '0';
    cardsView.style.transform = 'translateY(20px)';

    setTimeout(() => {
        cardsView.style.display = 'none';
        tableView.style.display = 'block';

        // Resetear las cards para la próxima vez que se muestren
        document.querySelectorAll('#cardsView .card').forEach(card => {
            card.classList.remove('animate-in');
            card.classList.remove('show');  // para limpiar bien animación
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.animationDelay = '';
        });
    }, 400); // Debe coincidir con la duración de la animación CSS
  }
}

// Al cargar la página, iniciar en tabla y animar stats y secciones
document.addEventListener('DOMContentLoaded', () => {
  const cardsView = document.getElementById('cardsView');
  const tableView = document.getElementById('tableView');

  if (cardsView && tableView) {
    cardsView.style.display = 'none';
    tableView.style.display = 'block';

    animateElements('.stat-card');
    animateElements('.card-section');
  } else {
    console.warn("No se encontró cardsView o tableView en el DOM.");
  }
});