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
        // Utiliser window.location.href pour un rechargement propre
        window.location.href = '/dashboard';
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

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="votre@email.com"
                      required
                      data-testid="email-input"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Mot de passe
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="••••••••"
                      required
                      data-testid="password-input"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
                  data-testid="login-button"
                >
                  {loading ? 'Connexion...' : 'Se connecter'}
                </button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-gray-600">
                  Pas encore de compte ?{' '}
                  <Link to="/register" className="text-indigo-600 hover:text-indigo-700 font-semibold">
                    S'inscrire
                  </Link>
                </p>
              </div>

              <div className="mt-6 p-4 bg-indigo-50 rounded-lg">
                <p className="text-xs text-gray-700 font-semibold mb-2">💡 Comptes de test :</p>
                <div className="space-y-1 text-xs text-gray-600">
                  <p><strong>Admin:</strong> admin@shareyoursales.com / admin123</p>
                  <p><strong>Merchant:</strong> contact@techstyle.fr / merchant123</p>
                  <p><strong>Influenceur:</strong> emma.style@instagram.com / influencer123</p>
                  <p className="text-indigo-600 mt-2"><strong>Code 2FA:</strong> 123456</p>
                </div>
              </div>
            </>
          ) : (
            // Step 2: 2FA Verification
            <>
              <div className="text-center mb-8">
                <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="w-8 h-8 text-indigo-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Vérification 2FA</h2>
                <p className="text-gray-600 mt-2">
                  Un code de vérification a été envoyé à votre téléphone
                </p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                  {error}
                </div>
              )}

              <form onSubmit={handleVerify2FA} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Code à 6 chiffres
                  </label>
                  <input
                    type="text"
                    value={twoFACode}
                    onChange={(e) => setTwoFACode(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-2xl font-bold tracking-widest focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="000000"
                    maxLength="6"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
                >
                  {loading ? 'Vérification...' : 'Vérifier le code'}
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setRequires2FA(false);
                    setTwoFACode('');
                    setError('');
                  }}
                  className="w-full text-gray-600 hover:text-gray-900 py-2"
                >
                  ← Retour
                </button>
              </form>

              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <p className="text-xs text-green-800">
                  <strong>💡 Mode démo :</strong> Utilisez le code <strong>123456</strong> pour la vérification
                </p>
              </div>
            </>
          )}
        </div>

        {/* Links */}
        <div className="mt-6 text-center space-x-4">
          <Link to="/" className="text-gray-600 hover:text-indigo-600 text-sm">
            Retour à l'accueil
          </Link>
          <Link to="/pricing" className="text-gray-600 hover:text-indigo-600 text-sm">
            Voir les tarifs
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
