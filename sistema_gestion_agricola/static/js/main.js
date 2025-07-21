// static/js/main.js
import { initTheme } from './theme.js';
import { showCurrentDate } from './date.js';
import { animateElements } from './animations.js';
import { enableTooltips } from './tooltips.js';
import { enableNavigation } from './navigation.js';
import { cargarClima } from './clima.js';
import { initMachineFilters, initComponentFilters, clearFilters } from './filters.js';
import {  } from './view.js';

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  showCurrentDate();

  // Animar index cards
  const grid = document.querySelector('#dashboard-grid');

  if (grid) {
    const msnry = new Masonry(grid, {
      itemSelector: '.dashboard-card, .weather-card',
      columnWidth: 244,
      gutter: 24,
      percentPosition: true,
    });

    imagesLoaded(grid, () => {
      msnry.layout();

      // Animar los elementos
      animateElements('.dashboard-card, .weather-card');
    });
  }

  // Animar cards, stats y secciones al inicio, según tu vista default
  animateElements('.hidden-item');

  enableTooltips();
  enableNavigation();
  cargarClima();
  initMachineFilters();
  initComponentFilters();

  // Exponer función global para limpiar filtros y cambiar vista
  window.clearFilters = clearFilters;
});
