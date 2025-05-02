// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Creamos la raíz para renderizar nuestra aplicación utilizando la API de React 18
const root = ReactDOM.createRoot(document.getElementById('root'));

// Renderizamos el componente App dentro de StrictMode
// StrictMode es una herramienta para destacar problemas potenciales en la aplicación
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Si quieres comenzar a medir el rendimiento de tu aplicación,
// puedes utilizar reportWebVitals que viene preconfigurado con create-react-app
// Para enviar resultados de análisis a un punto final, aprende más en: https://bit.ly/CRA-vitals
reportWebVitals();