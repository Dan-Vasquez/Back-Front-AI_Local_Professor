import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Crear contexto
const AuthContext = createContext();

// Hook personalizado para utilizar el contexto
export const useAuth = () => useContext(AuthContext);

// Proveedor del contexto
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Verificar si hay un token almacenado al cargar la página
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          setLoading(true);
          // Verificar si el token es válido
          const response = await axios.get(`${API_URL}/users/me`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          setUser(response.data);
        } catch (error) {
          console.error('Error al verificar la autenticación:', error);
          localStorage.removeItem('token');
          setUser(null);
        } finally {
          setLoading(false);
        }
      } else {
        setUser(null);
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Función para iniciar sesión
  const login = async (username, password) => {
    try {
      setLoading(true);
      setError(null);

      // Formato requerido por FastAPI
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post(`${API_URL}/token`, formData);
      const { access_token } = response.data;

      // Guardar token en localStorage
      localStorage.setItem('token', access_token);

      // Obtener información del usuario
      const userResponse = await axios.get(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${access_token}`
        }
      });

      setUser(userResponse.data);
      return true;
    } catch (error) {
      console.error('Error al iniciar sesión:', error);
      setError(error.response?.data?.detail || 'Error al iniciar sesión');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Función para registrarse
  const register = async (username, email, password) => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.post(`${API_URL}/register`, {
        username,
        email,
        password
      });

      const { access_token } = response.data;

      // Guardar token en localStorage
      localStorage.setItem('token', access_token);

      // Obtener información del usuario
      const userResponse = await axios.get(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${access_token}`
        }
      });

      setUser(userResponse.data);
      return true;
    } catch (error) {
      console.error('Error al registrarse:', error);
      setError(error.response?.data?.detail || 'Error al registrarse');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Función para cerrar sesión
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  // Función para entrar como invitado
  const guestLogin = () => {
    setUser({ username: 'Invitado', isGuest: true });
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    guestLogin
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 