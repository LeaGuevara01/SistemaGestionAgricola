import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

import './styles/variables.css';
import './styles/theme.css';
import './styles/custom.css';

ReactDOM.createRoot(document.getElementById("react-root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
