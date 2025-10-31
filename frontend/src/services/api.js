import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url;

    // Gestion détaillée des erreurs
    if (status === 401) {
      console.error('🚫 Erreur 401: Non autorisé -', url);

      // Éviter les boucles de redirection
      if (!window.location.pathname.includes('/login')) {
        console.log('🔄 Redirection vers /login?session_expired=true');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login?session_expired=true';
      }
    } else if (status === 403) {
      console.error('🚫 Erreur 403: Accès interdit -', url);
    } else if (status === 404) {
      console.error('🔍 Erreur 404: Ressource non trouvée -', url);
    } else if (status >= 500) {
      console.error('💥 Erreur serveur', status, '-', url);
    } else {
      console.error('❌ Erreur API:', status, error.response?.data?.detail || error.message);
    }

    return Promise.reject(error);
  }
);

// Fonction utilitaire pour vérifier la santé de l'API
export const checkAPIHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('❌ API non disponible:', error.message);
    return null;
  }
};

export default api;
