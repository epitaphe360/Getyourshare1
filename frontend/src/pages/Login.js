import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, Sparkles, AlertCircle, Shield } from 'lucide-react';
import Button from '../components/common/Button';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [twoFACode, setTwoFACode] = useState('');
  const [tempToken, setTempToken] = useState('');
  const [requires2FA, setRequires2FA] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);
    
    if (result.success) {
      navigate('/dashboard');
    } else if (result.requires2FA) {
      // 2FA requis
      setRequires2FA(true);
      setTempToken(result.tempToken);
      setError('');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleVerify2FA = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${API_URL}/api/auth/verify-2fa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          code: twoFACode,
          temp_token: tempToken
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Stocker le token et l'utilisateur
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
        window.location.reload(); // Reload pour mettre à jour le context
      } else {
        setError(data.detail || 'Code 2FA incorrect');
      }
    } catch (err) {
      setError('Erreur lors de la vérification du code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-2">
            <Sparkles className="h-10 w-10 text-indigo-600" />
            <span className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              ShareYourSales
            </span>
          </Link>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {!requires2FA ? (
            // Step 1: Email & Password
            <>
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900">Connexion</h2>
                <p className="text-gray-600 mt-2">Accédez à votre tableau de bord</p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-center" data-testid="error-message">
                  <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                  {error}
            </div>
          )}

          <div>
            <Button
              type="submit"
              disabled={loading}
              className="w-full"
              data-testid="login-button"
            >
              {loading ? 'Connexion...' : 'Se connecter'}
            </Button>
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-xs text-gray-700 font-semibold mb-2">Comptes de démo:</p>
            <div className="space-y-1 text-xs text-gray-600">
              <p><strong>Manager:</strong> admin@tracknow.io / admin123</p>
              <p><strong>Annonceur:</strong> advertiser@example.com / adv123</p>
              <p><strong>Affilié:</strong> affiliate@example.com / aff123</p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
