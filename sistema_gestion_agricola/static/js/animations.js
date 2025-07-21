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
