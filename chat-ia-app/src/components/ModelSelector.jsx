import React, { useEffect, useState } from 'react';
import { checkLocalModel } from '../api';

const ModelSelector = ({ selectedModel, onSelectModel }) => {
  const [localModelStatus, setLocalModelStatus] = useState({ status: 'checking', message: 'Verificando modelo local...' });

  useEffect(() => {
    const verifyLocalModel = async () => {
      try {
        const status = await checkLocalModel();
        setLocalModelStatus(status);
      } catch (error) {
        setLocalModelStatus({ 
          status: 'error', 
          message: 'Error al verificar el modelo local' 
        });
      }
    };

    verifyLocalModel();
  }, []);

  return (
    <div className="model-selector">
      <h3>Selecciona el modelo de IA</h3>
      
      <div className="model-options">
        <div className="model-option">
          <input
            type="radio"
            id="local-model"
            name="model"
            value="local"
            checked={selectedModel === 'local'}
            onChange={() => onSelectModel('local')}
            disabled={localModelStatus.status !== 'available'}
          />
          <label htmlFor="local-model">
            Modelo Local (Llama 3.2)
            {localModelStatus.status !== 'available' && (
              <span className="model-status">{localModelStatus.message}</span>
            )}
          </label>
        </div>
        
        <div className="model-option">
          <input
            type="radio"
            id="api-model"
            name="model"
            value="api"
            checked={selectedModel === 'api'}
            onChange={() => onSelectModel('api')}
          />
          <label htmlFor="api-model">API (Modelo en la nube)</label>
        </div>
      </div>
      
      <div className="model-parameters">
        <small>Parámetros avanzados (próximamente)</small>
      </div>
    </div>
  );
};

export default ModelSelector;