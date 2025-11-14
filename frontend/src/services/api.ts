import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // Aumentado a 60 segundos para requests de LLM
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor para agregar token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('chatbot_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor para manejo global de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);

      // Si es 401 (no autenticado), limpiar sesión y redirigir a login
      if (error.response.status === 401) {
        localStorage.removeItem('chatbot_token');
        localStorage.removeItem('chatbot_user');

        // Solo redirigir si no estamos ya en login/register
        if (!window.location.pathname.includes('/login') &&
            !window.location.pathname.includes('/register')) {
          window.location.href = '/login';
        }
      }
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
