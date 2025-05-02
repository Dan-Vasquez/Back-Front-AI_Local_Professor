# 🎓 AI Local Professor - Plataforma de Aprendizaje de Inglés

Una plataforma de aprendizaje de inglés asistida por inteligencia artificial, que permite a los usuarios conversar con diferentes modelos de IA y seguir módulos estructurados para mejorar sus habilidades en inglés.

## 🚀 Características

- **Chat Interactivo con IA**: Conversaciones en tiempo real con modelos de IA para practicar inglés
- **Módulos Estructurados**: Contenido organizado por niveles (principiante, intermedio, avanzado)
- **Seguimiento de Progreso**: Sistema de registro que permite a los usuarios seguir su avance
- **Agentes Personalizados**: Diferentes personalidades de IA con comportamientos específicos para distintos tipos de aprendizaje
- **Soporte para Modelos Locales o en la Nube**: Flexibilidad para usar modelos locales (Ollama) o APIs externas
- **Autenticación de Usuarios**: Sistema completo de registro y login

## 🛠️ Tecnologías

### Backend
- FastAPI
- SQLAlchemy (SQLite)
- JWT para autenticación
- Ollama para modelos locales
- APIs externas para modelos en la nube

### Frontend
- React
- Material UI
- Axios para comunicación con el backend

## 📋 Prerrequisitos

- Python 3.8+
- Node.js 14+
- Ollama (opcional, para modelos locales)

## 🔧 Instalación

Consulta [GUIA_INSTALACION.md](./GUIA_INSTALACION.md) para instrucciones detalladas de instalación y configuración.

## 📚 Estructura del Proyecto

```
Back-Front-AI/
├── chat-ia-app/         # Frontend (React)
├── agent_prompts/       # Comportamientos para diferentes agentes
├── app_sqlite.py        # Backend principal (versión completa)
├── app.py               # Versión simplificada sin autenticación 
├── auth.py              # Funciones de autenticación
├── db_sqlite.py         # Modelos de base de datos
├── load_modules.py      # Script para cargar módulos
├── Modulos.txt          # Datos de módulos de inglés
└── .env                 # Variables de entorno
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un Fork del proyecto
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 📞 Contacto

Dan Vásquez - [@dan_vasquez](https://twitter.com/dan_vasquez) - dan.vasquez@ejemplo.com 