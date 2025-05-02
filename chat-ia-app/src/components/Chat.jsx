import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Message from './Message';
import ModelSelector from './ModelSelector';
import AgentSelector from './AgentSelector';
import { sendMessage, markModuleCompleted } from '../api';
import { useAuth } from '../context/AuthContext';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState('local');
  const [selectedAgent, setSelectedAgent] = useState('profesor_ingles');
  const [showConfig, setShowConfig] = useState(false);
  const [moduleInfo, setModuleInfo] = useState({ id: null, title: null });
  const [moduleMarkedCompleted, setModuleMarkedCompleted] = useState(false);
  const messagesEndRef = useRef(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Efecto para extraer información del módulo de la URL y enviar mensaje inicial
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const moduleId = searchParams.get('moduleId');
    const moduleTitle = searchParams.get('moduleTitle');
    const moduleDescription = searchParams.get('moduleDescription');
    
    if (moduleId && moduleTitle) {
      setModuleInfo({
        id: moduleId,
        title: decodeURIComponent(moduleTitle),
        description: moduleDescription ? decodeURIComponent(moduleDescription) : ''
      });
      
      // Configurar mensaje inicial con información del módulo
      if (messages.length === 0) {
        const description = moduleDescription ? decodeURIComponent(moduleDescription) : '';
        
        const systemMessage = {
          role: 'system',
          content: `Como profesor de inglés, estás enseñando específicamente el módulo: "${decodeURIComponent(moduleTitle)}".
          
Descripción del módulo: "${description}"

Este módulo es parte del plan de estudios organizado por niveles (A1-C1) del Marco Común Europeo de Referencia. Tu objetivo es guiar al estudiante a través del contenido de este módulo específico, proporcionando explicaciones claras, ejemplos prácticos y ejercicios interactivos.

Cada vez que el estudiante escriba, debes:
1. Responder centrándote en el tema de este módulo
2. Adaptar tu nivel de idioma según la complejidad del tema (usando español cuando sea necesario para niveles básicos)
3. Corregir errores de manera constructiva
4. Proporcionar retroalimentación positiva y motivadora

Al final de la interacción, el estudiante debería haber comprendido y practicado los conceptos principales de este módulo específico.`
        };
        
        // Iniciar el chat con estos mensajes
        setMessages([systemMessage]);
        
        // Enviar un mensaje automático del profesor después de un breve retraso
        const welcomeMessageTimer = setTimeout(() => {
          const welcomeMessage = {
            role: 'assistant',
            content: `¡Bienvenido al módulo "${decodeURIComponent(moduleTitle)}"! 

Vamos a trabajar juntos en este tema. Te guiaré a través de los conceptos principales, proporcionaré ejemplos prácticos y realizaremos ejercicios para que puedas practicar lo aprendido.

Comencemos con una breve introducción al tema. ¿Estás listo para empezar?`
          };
          
          setMessages(prevMessages => [...prevMessages, welcomeMessage]);
          
          // Auto-enviar un primer mensaje de la IA con la lección inicial
          const initialLessonTimer = setTimeout(async () => {
            try {
              setIsLoading(true);
              const initialPromptMessage = {
                role: 'user',
                content: `Por favor, comienza la lección sobre "${decodeURIComponent(moduleTitle)}". Explica brevemente de qué trata este módulo y cuáles son los conceptos principales que vamos a aprender.`
              };
              
              // No agregamos este mensaje a la UI para que no se vea
              const allMessages = [systemMessage, welcomeMessage, initialPromptMessage];
              
              const response = await sendMessage(allMessages, selectedModel, selectedAgent);
              
              setMessages(prevMessages => [
                ...prevMessages,
                { role: 'assistant', content: response.response }
              ]);
            } catch (error) {
              console.error('Error al cargar la lección inicial:', error);
            } finally {
              setIsLoading(false);
            }
          }, 1000);
          
          return () => clearTimeout(initialLessonTimer);
        }, 500);
        
        return () => clearTimeout(welcomeMessageTimer);
      }
    }
  }, [location.search, selectedModel, selectedAgent]);

  // Efecto para hacer scroll al final cuando hay nuevos mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;
    
    const userMessage = { role: 'user', content: inputMessage.trim() };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInputMessage('');
    setError(null);
    setIsLoading(true);
    
    try {
      // Preparamos todos los mensajes para enviar al backend
      const allMessages = [...messages, userMessage];
      
      const response = await sendMessage(allMessages, selectedModel, selectedAgent);
      
      // Agregamos la respuesta del asistente
      setMessages(prevMessages => [
        ...prevMessages, 
        { role: 'assistant', content: response.response }
      ]);
      
      // Marcar el módulo como completado si no se ha marcado aún
      if (moduleInfo.id && !moduleMarkedCompleted && user) {
        try {
          await markModuleCompleted(moduleInfo.id);
          setModuleMarkedCompleted(true);
        } catch (error) {
          console.error("Error al marcar el módulo como completado:", error);
        }
      }
      
    } catch (error) {
      console.error('Error:', error);
      setError('Hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleConfig = () => {
    setShowConfig(!showConfig);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleBackToModules = () => {
    navigate('/modules');
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="header-content">
          <div className="header-title">
            <button className="back-button" onClick={handleBackToModules}>
              ← Volver a módulos
            </button>
            <h2>
              {moduleInfo.title ? moduleInfo.title : 'Chat con IA'}
            </h2>
          </div>
          <div className="user-info">
            <span className="username">{user?.username || 'Invitado'}</span>
          </div>
          <button className="config-button" onClick={toggleConfig}>
            {showConfig ? "Ocultar configuración" : "Mostrar configuración"}
          </button>
        </div>
        
        {showConfig && (
          <div className="selection-panel">
            <ModelSelector 
              selectedModel={selectedModel} 
              onSelectModel={setSelectedModel} 
            />
            <AgentSelector
              selectedAgent={selectedAgent}
              onSelectAgent={setSelectedAgent}
            />
          </div>
        )}
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <p>¡Hola, {user?.username || 'Invitado'}! Comienza tu clase de inglés del módulo "{moduleInfo.title}"</p>
            <p className="chat-info">Modelo actual: <strong>{selectedModel === 'local' ? 'Local (Llama 3.2)' : 'API (Nube)'}</strong></p>
            <p className="chat-info">Profesor: <strong>Profesor de Inglés</strong></p>
          </div>
        ) : (
          messages.map((message, index) => (
            message.role !== 'system' && <Message key={index} message={message} />
          ))
        )}
        
        {isLoading && (
          <div className="loading-message">
            <p>La IA está pensando...</p>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Escribe un mensaje..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !inputMessage.trim()}>
          Enviar
        </button>
      </form>
    </div>
  );
};

export default Chat;