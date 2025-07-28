// Script para generar favicon básico
const fs = require('fs');

// SVG simple de tractor
const svgContent = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="#16a34a"/>
  <text x="16" y="24" font-family="Arial" font-size="20" text-anchor="middle" fill="white">🚜</text>
</svg>`;

fs.writeFileSync('./public/favicon.svg', svgContent);
console.log('✅ Favicon SVG creado en public/favicon.svg');