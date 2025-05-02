const API_URL = 'http://localhost:8000';

// Función auxiliar para obtener los headers con el token de autenticación
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token
    ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
    : { 'Content-Type': 'application/json' };
};

export const sendMessage = async (messages, modelChoice, agentType = 'default', maxTokens = 1000, temperature = 0.7) => {
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        messages,
        model_choice: modelChoice,
        agent_type: agentType,
        max_tokens: maxTokens,
        temperature
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error al enviar el mensaje');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en la API:', error);
    throw error;
  }
};

export const checkLocalModel = async () => {
  try {
    const response = await fetch(`${API_URL}/check-local-model`, {
      headers: getAuthHeaders()
    });
    return await response.json();
  } catch (error) {
    console.error('Error al verificar el modelo local:', error);
    return { status: 'error', message: 'No se pudo verificar el modelo local' };
  }
};

export const getAvailableAgents = async () => {
  try {
    const response = await fetch(`${API_URL}/available-agents`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error('Error al obtener los agentes disponibles');
    }
    return await response.json();
  } catch (error) {
    console.error('Error al obtener los agentes disponibles:', error);
    return { agents: ['default'] }; // Devuelve al menos el agente por defecto en caso de error
  }
};

export const fetchModules = async (level = null) => {
  try {
    const url = level ? `${API_URL}/modules/${level}` : `${API_URL}/modules`;
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Error al obtener los módulos');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error al obtener los módulos:', error);
    throw error;
  }
};

export const markModuleCompleted = async (moduleId) => {
  try {
    const response = await fetch(`${API_URL}/modules/complete`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        module_id: moduleId
      })
    });
    
    if (!response.ok) {
      throw new Error('Error al marcar el módulo como completado');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error al marcar el módulo como completado:', error);
    throw error;
  }
};