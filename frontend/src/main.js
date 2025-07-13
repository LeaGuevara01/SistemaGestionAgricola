import './styles/variables.css'
import './styles/theme.css'

console.log("✅ Vite funcionando desde Flask")

fetch('http://localhost:5000/api/componentes')
  .then(res => res.json())
  .then(data => console.log(data));

document.getElementById('app').innerText = 'Hello from Vite'