// Animación basada en animaciones CSS con .animate-in y animation-delay
export function animateWithDelay(selector) {
  const elements = document.querySelectorAll(selector);
  elements.forEach((el, i) => {
    const delay = el.dataset.delay ? parseInt(el.dataset.delay) : i * 60;
    el.style.animationDelay = `${delay}ms`;
    el.classList.add('animate-in');
  });
}

// Animación basada en transform y clase .show
export function animateElements(selector) {
  const elements = document.querySelectorAll(selector);
  elements.forEach((el, i) => {
    el.classList.remove('show'); // reset para reanimar
    const delay = el.dataset.delay ? parseInt(el.dataset.delay) : i * 80;
    setTimeout(() => {
      el.classList.add('show');
    }, delay);
  });
}
