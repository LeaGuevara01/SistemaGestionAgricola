import React, { useEffect, useState } from "react";

export default function App() {
  const [maquinas, setMaquinas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/maquinas')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Error fetching maquinas');
        }
        return response.json();
      })
      .then((data) => {
        setMaquinas(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Cargando máquinas...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="app-container">
      <h2>🌽 Bienvenido al panel agrícola con React</h2>
      <p>Este contenido fue renderizado por React y Vite.</p>
      <h3>Lista de Máquinas</h3>
      <ul>
        {maquinas.map((maquina) => (
          <li key={maquina.ID}>
            <strong>{maquina.Nombre}</strong>: {maquina.Descripcion || 'Sin descripción'}
          </li>
        ))}
      </ul>
    </div>
  );
}
