import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fetchModules } from '../api';
import '../styles/ModulesList.css';

const ModulesList = () => {
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState('all');
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  useEffect(() => {
    const loadModules = async () => {
      try {
        setLoading(true);
        const data = await fetchModules();
        setModules(data);
        setError(null);
      } catch (err) {
        console.error("Error al cargar los módulos:", err);
        setError("No se pudieron cargar los módulos. Por favor, intenta de nuevo más tarde.");
      } finally {
        setLoading(false);
      }
    };

    loadModules();
  }, []);

  const handleModuleClick = (moduleId, moduleTitle, moduleDescription) => {
    // Navegar al chat con el ID, título y descripción del módulo como parámetros
    navigate(`/chat?moduleId=${moduleId}&moduleTitle=${encodeURIComponent(moduleTitle)}&moduleDescription=${encodeURIComponent(moduleDescription)}`);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Obtener niveles únicos para el filtro
  const levels = [...new Set(modules.map(module => module.level))].sort();

  // Filtrar módulos por nivel
  const filteredModules = selectedLevel === 'all' 
    ? modules 
    : modules.filter(module => module.level === selectedLevel);

  // Calcular estadísticas de progreso
  const completedModulesCount = modules.filter(module => module.completed).length;
  const totalModulesCount = modules.length;
  const progressPercentage = totalModulesCount > 0 
    ? Math.round((completedModulesCount / totalModulesCount) * 100) 
    : 0;

  return (
    <div className="modules-container">
      <div className="modules-header">
        <h1>Módulos de Aprendizaje de Inglés</h1>
        
        <div className="user-header">
          <div className="user-info">
            <span>Bienvenido, <strong>{user ? user.username : 'Invitado'}</strong></span>
            <div className="user-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              <span className="progress-text">
                {completedModulesCount} de {totalModulesCount} módulos completados ({progressPercentage}%)
              </span>
            </div>
          </div>
          <button className="logout-button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
        
        <div className="level-filter">
          <label htmlFor="level-select">Filtrar por nivel:</label>
          <select 
            id="level-select" 
            value={selectedLevel} 
            onChange={(e) => setSelectedLevel(e.target.value)}
          >
            <option value="all">Todos los niveles</option>
            {levels.map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">Cargando módulos...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <div className="modules-grid">
          {filteredModules.map((module) => (
            <div 
              key={module.id} 
              className={`module-card ${module.completed ? 'module-completed' : ''}`}
              onClick={() => handleModuleClick(module.id, module.title, module.description)}
            >
              <div className="module-level">{module.level}</div>
              {module.completed && (
                <div className="completed-badge">
                  <span className="checkmark">✓</span>
                </div>
              )}
              <h3 className="module-title">{module.title}</h3>
              <p className="module-description">{module.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModulesList; 