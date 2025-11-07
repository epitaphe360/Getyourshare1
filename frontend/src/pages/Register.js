import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Phone, Building, Sparkles, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';
import { validateEmail, validatePassword, validatePhone, validateRequired, validatePasswordMatch } from '../utils/validation';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Register = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [role, setRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState({});
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
    // Merchant specific
    company_name: '',
    // Influencer specific
    username: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    setValidationErrors(prev => ({...prev, [e.target.name]: ''}));
  };

  const handleRoleSelection = (selectedRole) => {
    setRole(selectedRole);
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setValidationErrors({});
    setLoading(true);

    // VALIDATION côté client
    const errors = {};
    
    // Email
    const emailValidation = validateEmail(formData.email);
    if (!emailValidation.valid) errors.email = emailValidation.error;
    
    // Password
    const passwordValidation = validatePassword(formData.password, { 
      minLength: 8, 
      requireUppercase: true, 
      requireLowercase: true, 
      requireNumber: true 
    });
    if (!passwordValidation.valid) errors.password = passwordValidation.error;
    
    // Password Match
    const matchValidation = validatePasswordMatch(formData.password, formData.confirmPassword);
    if (!matchValidation.valid) errors.confirmPassword = matchValidation.error;
    
    // First Name
    const firstNameValidation = validateRequired(formData.first_name, "Le prénom");
    if (!firstNameValidation.valid) errors.first_name = firstNameValidation.error;
    
    // Last Name
    const lastNameValidation = validateRequired(formData.last_name, "Le nom");
    if (!lastNameValidation.valid) errors.last_name = lastNameValidation.error;
    
    // Phone (facultatif mais validé si fourni)
    if (formData.phone) {
      const phoneValidation = validatePhone(formData.phone);
      if (!phoneValidation.valid) errors.phone = phoneValidation.error;
    }
    
    // Company Name (si merchant)
    if (role === 'merchant') {
      const companyValidation = validateRequired(formData.company_name, "Le nom de l'entreprise");
      if (!companyValidation.valid) errors.company_name = companyValidation.error;
    }
    
    // Username (si influencer)
    if (role === 'influencer') {
      const usernameValidation = validateRequired(formData.username, "Le nom d'utilisateur");
      if (!usernameValidation.valid) errors.username = usernameValidation.error;
    }
    
    // Si erreurs de validation, arrêter
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      setLoading(false);
      return;
    }

    try {
      const registerData = {
        email: formData.email,
        password: formData.password,
        role: role,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        ...(role === 'merchant' && { company_name: formData.company_name }),
        ...(role === 'influencer' && { username: formData.username })
      };

      const response = await axios.post(`${API_URL}/api/auth/register`, registerData);
      
      if (response.data.success) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold mb-4">Inscription réussie ! 🎉</h2>
          <p className="text-gray-600 mb-4">
            Votre compte a été créé avec succès. Vous allez être redirigé vers la page de connexion...
          </p>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden max-w-4xl w-full">
        <div className="flex flex-col md:flex-row">
          {/* Left Side - Branding */}
          <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-12 md:w-1/2 text-white">
            <Link to="/" className="flex items-center space-x-2 mb-8">
              <Sparkles className="h-8 w-8" />
              <span className="text-2xl font-bold">ShareYourSales</span>
            </Link>
            <h2 className="text-3xl font-bold mb-4">
              Rejoignez la révolution du marketing d'affiliation
            </h2>
            <p className="text-indigo-100 mb-8">
              Plus de 10,000 entreprises et influenceurs nous font confiance pour maximiser leurs revenus
            </p>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-6 h-6 flex-shrink-0 mt-1" />
                <div>
                  <div className="font-semibold">Tracking en temps réel</div>
                  <div className="text-sm text-indigo-100">Suivez vos performances instantanément</div>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-6 h-6 flex-shrink-0 mt-1" />
                <div>
                  <div className="font-semibold">Paiements sécurisés</div>
                  <div className="text-sm text-indigo-100">Recevez vos commissions rapidement</div>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-6 h-6 flex-shrink-0 mt-1" />
                <div>
                  <div className="font-semibold">Support 24/7</div>
                  <div className="text-sm text-indigo-100">Une équipe dédiée à votre succès</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Form */}
          <div className="p-12 md:w-1/2">
            {/* Step 1: Role Selection */}
            {step === 1 && (
              <div>
                <h2 className="text-3xl font-bold mb-2">Créer un compte</h2>
                <p className="text-gray-600 mb-8">Vous êtes ?</p>

                <div className="space-y-4">
                  <button
                    onClick={() => handleRoleSelection('merchant')}
                    className="w-full p-6 border-2 border-gray-200 rounded-xl hover:border-indigo-600 hover:bg-indigo-50 transition group"
                  >
                    <Building className="w-12 h-12 text-indigo-600 mb-3 mx-auto" />
                    <h3 className="text-xl font-semibold mb-2">Entreprise</h3>
                    <p className="text-gray-600 text-sm">
                      Je souhaite proposer mes produits/services et travailler avec des influenceurs
                    </p>
                  </button>

                  <button
                    onClick={() => handleRoleSelection('influencer')}
                    className="w-full p-6 border-2 border-gray-200 rounded-xl hover:border-purple-600 hover:bg-purple-50 transition group"
                  >
                    <Sparkles className="w-12 h-12 text-purple-600 mb-3 mx-auto" />
                    <h3 className="text-xl font-semibold mb-2">Influenceur / Commercial</h3>
                    <p className="text-gray-600 text-sm">
                      Je souhaite promouvoir des produits et gagner des commissions
                    </p>
                  </button>
                </div>

                <div className="mt-8 text-center">
                  <p className="text-gray-600">
                    Vous avez déjà un compte ?{' '}
                    <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-semibold">
                      Se connecter
                    </Link>
                  </p>
                </div>
              </div>
            )}

            {/* Step 2: Registration Form */}
            {step === 2 && (
              <div>
                <button
                  onClick={() => setStep(1)}
                  className="text-gray-600 hover:text-gray-900 mb-4 flex items-center"
                >
                  ← Retour
                </button>

                <h2 className="text-3xl font-bold mb-2">
                  {role === 'merchant' ? 'Inscription Entreprise' : 'Inscription Influenceur'}
                </h2>
                <p className="text-gray-600 mb-6">Complétez vos informations</p>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Nom et Prénom */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Prénom
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="text"
                          name="first_name"
                          value={formData.first_name}
                          onChange={handleChange}
                          className={`pl-10 w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                            validationErrors.first_name ? 'border-red-500' : 'border-gray-300'
                          }`}
                          placeholder="Jean"
                          required
                        />
                      </div>
                      {validationErrors.first_name && (
                        <p className="mt-1 text-sm text-red-600">{validationErrors.first_name}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nom
                      </label>
                      <input
                        type="text"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                          validationErrors.last_name ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="Dupont"
                        required
                      />
                      {validationErrors.last_name && (
                        <p className="mt-1 text-sm text-red-600">{validationErrors.last_name}</p>
                      )}
                    </div>
                  </div>

                  {/* Company Name (Merchant only) */}
                  {role === 'merchant' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nom de l'entreprise
                      </label>
                      <div className="relative">
                        <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="text"
                          name="company_name"
                          value={formData.company_name}
                          onChange={handleChange}
                          className={`pl-10 w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                            validationErrors.company_name ? 'border-red-500' : 'border-gray-300'
                          }`}
                          placeholder="Mon Entreprise SAS"
                          required
                        />
                      </div>
                      {validationErrors.company_name && (
                        <p className="mt-1 text-sm text-red-600">{validationErrors.company_name}</p>
                      )}
                    </div>
                  )}

                  {/* Username (Influencer only) */}
                  {role === 'influencer' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nom d'utilisateur
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="text"
                          name="username"
                          value={formData.username}
                          onChange={handleChange}
                          className={`pl-10 w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                            validationErrors.username ? 'border-red-500' : 'border-gray-300'
                          }`}
                          placeholder="mon_username"
                          required
                        />
                      </div>
                      {validationErrors.username && (
                        <p className="mt-1 text-sm text-red-600">{validationErrors.username}</p>
                      )}
                    </div>
                  )}

                  {/* Email */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        className={`pl-10 w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                          validationErrors.email ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="email@exemple.com"
                        required
                      />
                    </div>
                    {validationErrors.email && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.email}</p>
                    )}
                  </div>

                  {/* Phone */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Téléphone
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        className={`pl-10 w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                          validationErrors.phone ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="+212600000000"
                      />
                    </div>
                    {validationErrors.phone && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.phone}</p>
                    )}
                  </div>

                  {/* Password */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Mot de passe
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        className={`pl-10 w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                          validationErrors.password ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="••••••••"
                        required
                      />
                    </div>
                    {validationErrors.password && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.password}</p>
                    )}
                  </div>

                  {/* Confirm Password */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Confirmer le mot de passe
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="password"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        className={`pl-10 w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                          validationErrors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="••••••••"
                        required
                      />
                    </div>
                    {validationErrors.confirmPassword && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.confirmPassword}</p>
                    )}
                  </div>

                  {/* Terms */}
                  <div className="flex items-start">
                    <input
                      type="checkbox"
                      id="terms"
                      className="mt-1 w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                      required
                    />
                    <label htmlFor="terms" className="ml-2 text-sm text-gray-600">
                      J'accepte les{' '}
                      <a href="#" className="text-indigo-600 hover:text-indigo-700">
                        conditions générales d'utilisation
                      </a>
                    </label>
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading}
                    className={`w-full py-3 rounded-lg font-semibold text-white transition ${
                      role === 'merchant'
                        ? 'bg-indigo-600 hover:bg-indigo-700'
                        : 'bg-purple-600 hover:bg-purple-700'
                    } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {loading ? 'Inscription en cours...' : 'Créer mon compte'}
                  </button>
                </form>

                <div className="mt-6 text-center">
                  <p className="text-gray-600">
                    Vous avez déjà un compte ?{' '}
                    <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-semibold">
                      Se connecter
                    </Link>
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
