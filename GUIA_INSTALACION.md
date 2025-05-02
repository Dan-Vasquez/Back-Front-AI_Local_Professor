# Guía de Instalación y Configuración del Chat con IA para el Aprendizaje de Inglés

## Descripción del Proyecto

Este proyecto implementa una plataforma de aprendizaje de inglés asistida por Inteligencia Artificial. El sistema cuenta con las siguientes características:

- **Chat Interactivo con IA**: Permite a los usuarios conversar con diferentes modelos de IA para practicar inglés.
- **Módulos de Aprendizaje**: Organización por niveles (principiante, intermedio, avanzado) con material estructurado.
- **Seguimiento de Progreso**: Sistema de registro que permite a los usuarios seguir su avance.
- **Agentes Personalizados**: Diferentes personalidades de IA con comportamientos específicos para distintos tipos de aprendizaje.
- **Soporte para Modelos Locales o en la Nube**: Flexibilidad para usar modelos locales (Ollama) o APIs externas.

La plataforma consta de un backend desarrollado con FastAPI y un frontend en React, con autenticación de usuarios y persistencia de datos en SQLite.

## Requisitos Previos

1. **Python**
   - Python 3.8 o superior
   - pip (gestor de paquetes de Python)

2. **Node.js**
   - Node.js 14.0 o superior
   - npm (viene incluido con Node.js)

3. **Ollama** (opcional, solo si quieres usar el modelo local)
   - Instalar Ollama desde https://ollama.ai/
   - Descargar el modelo llama3.2 usando: `ollama pull llama3.2`

## Estructura del Proyecto

```
Back-Front-AI/
├── chat-ia-app/         # Frontend (React)
├── agent_prompts/       # Directorio con comportamientos para diferentes agentes
├── app_sqlite.py        # Backend principal con FastAPI (versión completa)
├── app.py               # Versión simplificada del backend sin autenticación 
├── auth.py              # Funciones de autenticación
├── db_sqlite.py         # Modelos de base de datos SQLite
├── load_modules.py      # Script para cargar módulos de inglés
├── Modulos.txt          # Datos de módulos de inglés
└── .env                 # Variables de entorno
```

### Estructura del Frontend
```
/src
    /components
        /Chat.jsx
        /Message.jsx
        /ModelSelector.jsx
    /App.jsx
    /index.js
    /index.css
    /App.css
    /api.js
    /reportWebVitals.js
```
## Pasos de Instalación

### 1. Configuración del Backend (FastAPI)

1. Crear un entorno virtual:
   ```bash
   python -m venv venv
   ```

2. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Instalar dependencias del backend:
   ```bash
   pip install fastapi uvicorn httpx python-dotenv sqlalchemy passlib[bcrypt] pyjwt
   ```

4. Crear archivo `.env` en la raíz del proyecto:
   ```
   NLPCLOUD_API_KEY=tu_api_key_aquí
   ```

5. Cargar los módulos de inglés:
   ```bash
   python load_modules.py
   ```

6. Iniciar el servidor backend:
   ```bash
   uvicorn app_sqlite:app --reload --host 0.0.0.0 --port 8000
   ```

### 2. Configuración del Frontend (React)

1. Crear la aplicación React:
   ```bash
   npx create-react-app chat-ia-app
   cd chat-ia-app
   ```

2. Instalar dependencias adicionales:
   ```bash
   npm install @mui/material @emotion/react @emotion/styled @mui/icons-material axios
   ```

3. Iniciar la aplicación React:
   ```bash
   npm start
   ```

## Verificación de la Instalación

1. **Backend**
   - Abrir http://localhost:8000/health
   - Debería mostrar un mensaje de estado "ok"

2. **Frontend**
   - Abrir http://localhost:3000
   - Deberías ver la interfaz del chat

## Uso del Sistema

1. **Registro y Autenticación**
   - Crea una cuenta utilizando el formulario de registro
   - Inicia sesión para acceder a todas las funcionalidades

2. **Módulos de Aprendizaje**
   - Navega por los módulos organizados por nivel
   - Marca los módulos completados para seguir tu progreso

3. **Selección del Modelo**
   - **Modelo Local**: Requiere tener Ollama instalado y ejecutándose
   - **Modelo API**: Usa la API en la nube (requiere API key)

4. **Envío de Mensajes**
   - Escribe tu mensaje en el campo de texto
   - Presiona "Enviar" o Enter
   - Selecciona diferentes agentes para diferentes estilos de enseñanza

## Solución de Problemas Comunes

1. **Error "Connection Refused" en el Frontend**
   - Verificar que el backend esté corriendo en el puerto 8000
   - Verificar que no haya conflictos de CORS

2. **Error con el Modelo Local**
   - Verificar que Ollama esté instalado y ejecutándose
   - Verificar que el modelo llama3.2 esté descargado

3. **Error con la API**
   - Verificar que la API key esté correctamente configurada en el archivo .env

## Notas Adicionales

- El backend debe estar corriendo antes de iniciar el frontend
- Para desarrollo, mantener ambos servidores (frontend y backend) ejecutándose
- Para producción, se recomienda configurar un servidor web como Nginx

## Recursos Adicionales

- Documentación de FastAPI: https://fastapi.tiangolo.com/
- Documentación de React: https://reactjs.org/
- Documentación de Ollama: https://ollama.ai/docs 