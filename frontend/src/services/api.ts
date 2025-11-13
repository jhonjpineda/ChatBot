import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // Aumentado a 60 segundos para requests de LLM
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor para agregar token si existe
api.interceptors.request.use(
  (config) => {
    // Aquí podrías agregar autenticación en el futuro
    // const token = localStorage.getItem('token');
    // if (token) config.headers.Authorization = `Bearer ${token}`;
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
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
