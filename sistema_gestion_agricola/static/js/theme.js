export function initTheme() {
  const htmlElement = document.body;
  const themeIcon = document.getElementById('themeIcon');
  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('theme') || 'light';

  htmlElement.setAttribute('data-bs-theme', savedTheme);
  if (themeIcon) {
    themeIcon.classList.replace('bi-moon-fill', savedTheme === 'dark' ? 'bi-sun-fill' : 'bi-moon-fill');
  }

  if (themeToggle && themeIcon) {
    themeToggle.addEventListener('click', () => {
      const isDark = htmlElement.getAttribute('data-bs-theme') === 'dark';
      htmlElement.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
      themeIcon.classList.replace(
        isDark ? 'bi-sun-fill' : 'bi-moon-fill',
        isDark ? 'bi-moon-fill' : 'bi-sun-fill'
      );
      localStorage.setItem('theme', isDark ? 'light' : 'dark');
    });
  }
}
