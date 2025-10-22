import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../utils/api';

const AuthContext = createContext(null);

// Intervalle de vérification de session (5 minutes)
const SESSION_CHECK_INTERVAL = 5 * 60 * 1000;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionStatus, setSessionStatus] = useState('checking'); // 'checking', 'active', 'expired'

  // Fonction pour vérifier la session auprès du backend
  const verifySession = async () => {
    const token = localStorage.getItem('token');

    if (!token) {
      console.log('❌ Aucun token trouvé');
      setLoading(false);
      setSessionStatus('expired');
      return false;
    }

    try {
      console.log('🔍 Vérification de la session...');
      const response = await api.get('/api/auth/me');

      if (response.data) {
        console.log('✅ Session vérifiée et valide');
        setUser(response.data);
        localStorage.setItem('user', JSON.stringify(response.data));
        setSessionStatus('active');
        return true;
      }
    } catch (error) {
      console.error('❌ Session invalide ou expirée:', error.response?.data?.detail);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      setSessionStatus('expired');
      return false;
    } finally {
      setLoading(false);
    }

    return false;
  };

  useEffect(() => {
    // Vérifier la session au chargement
    verifySession();

    // Vérification périodique de la session
    const intervalId = setInterval(() => {
      const token = localStorage.getItem('token');
      if (token && user) {
        console.log('🔄 Vérification périodique de la session...');
        verifySession();
      }
    }, SESSION_CHECK_INTERVAL);

    // Cleanup
    return () => clearInterval(intervalId);
  }, [user]);

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login', { email, password });

      // Check if 2FA is required
      if (response.data.requires_2fa) {
        return {
          success: false,
          requires2FA: true,
          tempToken: response.data.temp_token,
          message: response.data.message || 'Code 2FA envoyé'
        };
      }

      // No 2FA required, login directly
      const { access_token, user: userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      setSessionStatus('active');

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Connexion échouée'
      };
    }
  };

  const logout = async () => {
    try {
      // Appeler le backend pour déconnexion côté serveur
      console.log('🚪 Déconnexion en cours...');
      await api.post('/api/auth/logout');
      console.log('✅ Déconnexion réussie côté serveur');
    } catch (error) {
      console.error('⚠️ Erreur lors de la déconnexion backend:', error.message);
      // Continue même si le backend échoue
    } finally {
      // Nettoyer le localStorage et l'état
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      setSessionStatus('expired');
      console.log('✅ Session locale nettoyée');
    }
  };

  // Fonction pour rafraîchir manuellement la session
  const refreshSession = async () => {
    return await verifySession();
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      loading,
      sessionStatus,
      refreshSession
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
