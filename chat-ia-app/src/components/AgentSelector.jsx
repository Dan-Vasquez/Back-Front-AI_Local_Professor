import React, { useEffect, useState } from 'react';
import { getAvailableAgents } from '../api';

const AgentSelector = ({ selectedAgent, onSelectAgent }) => {
  const [availableAgents, setAvailableAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setIsLoading(true);
        const data = await getAvailableAgents();
        setAvailableAgents(data.agents || []);
        setError(null);
      } catch (error) {
        console.error('Error al cargar los agentes:', error);
        setError('No se pudieron cargar los agentes disponibles');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAgents();
  }, []);

  // Funciones para formatear los nombres de los agentes para mostrarlos
  const formatAgentName = (name) => {
    // Capitaliza la primera letra y reemplaza guiones bajos con espacios
    return name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, ' ');
  };

  if (isLoading) {
    return <p>Cargando agentes disponibles...</p>;
  }

  if (error) {
    return <p className="error-message">{error}</p>;
  }

  return (
    <div className="agent-selector">
      <h3>Selecciona el tipo de asistente</h3>
      <div className="agent-options">
        {availableAgents.map((agent) => (
          <div key={agent} className="agent-option">
            <input
              type="radio"
              id={`agent-${agent}`}
              name="agent"
              value={agent}
              checked={selectedAgent === agent}
              onChange={() => onSelectAgent(agent)}
            />
            <label htmlFor={`agent-${agent}`}>{formatAgentName(agent)}</label>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentSelector; 