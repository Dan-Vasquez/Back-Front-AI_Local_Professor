import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import ModulesList from './pages/ModulesList';
import Chat from './components/Chat';
import './App.css';

// Componente para rutas protegidas
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading-container">Cargando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
};

// Componente de la aplicación
const AppContent = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading-container">Cargando...</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Aplicación de Chat con IA para Aprendizaje de Inglés</h1>
      </header>
      <main>
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/modules" /> : <Login />} />
          <Route path="/register" element={user ? <Navigate to="/modules" /> : <Register />} />
          <Route
            path="/modules"
            element={
              <ProtectedRoute>
                <ModulesList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <Chat />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to={user ? "/modules" : "/login"} />} />
        </Routes>
      </main>
      <footer className="app-footer">
        <p>Desarrollado con React y FastAPI</p>
      </footer>
    </div>
  );
};

// Componente principal con el proveedor de autenticación
function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;