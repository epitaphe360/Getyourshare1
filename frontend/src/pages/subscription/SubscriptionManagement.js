import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  Clock, 
  AlertCircle, 
  Check, 
  X, 
  TrendingUp,
  Users,
  Package,
  Target,
  Link as LinkIcon,
  Crown,
  Zap,
  Shield
} from 'lucide-react';
import api from '../../services/api';

const SubscriptionManagement = () => {
  const [subscription, setSubscription] = useState(null);
  const [usage, setUsage] = useState(null);
  const [availablePlans, setAvailablePlans] = useState({ merchants: [], influencers: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      setLoading(true);
      const [subRes, usageRes, plansRes] = await Promise.all([
        api.get('/api/subscriptions/current'),
        api.get('/api/subscriptions/usage'),
        api.get('/api/subscriptions/plans')
      ]);

      setSubscription(subRes.data);
      setUsage(usageRes.data);
      setAvailablePlans(plansRes.data);
    } catch (err) {
      console.error('Error fetching subscription:', err);
      setError('Impossible de charger les données d\'abonnement');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planCode) => {
    try {
      const response = await api.post('/api/subscriptions/upgrade', {
        new_plan: planCode
      });
      
      if (response.data.redirect_to_payment) {
        // Rediriger vers la page de paiement
        window.location.href = '/pricing';
      } else {
        alert(response.data.message);
        fetchSubscriptionData();
      }
    } catch (err) {
      alert('Erreur lors du changement de plan: ' + err.response?.data?.detail);
    }
  };

  const handleCancelSubscription = async () => {
    try {
      await api.post('/api/subscriptions/cancel', {
        reason: cancelReason,
        immediate: false
      });
      
      alert('Votre abonnement sera annulé à la fin de la période en cours');
      setShowCancelModal(false);
      fetchSubscriptionData();
    } catch (err) {
      alert('Erreur lors de l\'annulation: ' + err.response?.data?.detail);
    }
  };

  const getPlanIcon = (planCode) => {
    const icons = {
      free: Shield,
      starter: Zap,
      pro: Crown,
      enterprise: Crown,
      elite: Crown
    };
    return icons[planCode] || Shield;
  };

  const getPlanColor = (planCode) => {
    const colors = {
      free: 'text-gray-500',
      starter: 'text-blue-500',
      pro: 'text-purple-500',
      enterprise: 'text-yellow-500',
      elite: 'text-pink-500'
    };
    return colors[planCode] || 'text-gray-500';
  };

  const getUsagePercentage = (current, limit) => {
    if (!limit) return 0;
    return Math.round((current / limit) * 100);
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Erreur</h2>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={fetchSubscriptionData}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  const PlanIcon = getPlanIcon(subscription?.plan_code);
  const currentPlans = subscription?.type === 'merchant' 
    ? availablePlans.merchants 
    : availablePlans.influencers;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`p-3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500`}>
                <PlanIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Plan {subscription?.plan_name}
                </h1>
                <p className="text-gray-600 mt-1">
                  {subscription?.monthly_fee === 0 
                    ? 'Gratuit' 
                    : `${subscription?.monthly_fee} MAD / mois`}
                </p>
              </div>
            </div>
            
            <div className="text-right">
              <span className={`inline-flex px-3 py-1 rounded-full text-sm font-semibold ${
                subscription?.status === 'active' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {subscription?.status === 'active' ? 'Actif' : subscription?.status}
              </span>
            </div>
          </div>
        </div>

        {/* Usage Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {usage && Object.entries(usage).map(([key, stat]) => {
            if (typeof stat !== 'object' || key === 'plan_name' || key === 'plan_code') return null;
            
            const icons = {
              products: Package,
              campaigns: Target,
              affiliates: Users,
              links: LinkIcon
            };
            
            const Icon = icons[key] || Package;
            const percentage = stat.percentage || 0;
            
            return (
              <div key={key} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Icon className="h-6 w-6 text-indigo-600" />
                    <h3 className="text-lg font-semibold text-gray-900 capitalize">
                      {key}
                    </h3>
                  </div>
                  <span className="text-2xl font-bold text-gray-900">
                    {stat.current} / {stat.limit || '∞'}
                  </span>
                </div>
                
                {stat.limit && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getUsageColor(percentage)} transition-all duration-300`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    ></div>
                  </div>
                )}
                
                <div className="mt-2 flex items-center justify-between text-sm">
                  <span className="text-gray-600">
                    {stat.available !== null 
                      ? `${stat.available} disponible${stat.available > 1 ? 's' : ''}`
                      : 'Illimité'}
                  </span>
                  <span className={`font-semibold ${
                    percentage >= 90 ? 'text-red-600' : 
                    percentage >= 70 ? 'text-yellow-600' : 
                    'text-green-600'
                  }`}>
                    {percentage}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Features List */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Fonctionnalités incluses</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {subscription?.features?.map((feature, index) => (
              <div key={index} className="flex items-start space-x-3">
                <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700">{feature}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Available Plans */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Plans disponibles</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {currentPlans.map((plan) => {
              const isCurrentPlan = plan.code === subscription?.plan_code;
              const PlanIconComp = getPlanIcon(plan.code);
              
              return (
                <div
                  key={plan.code}
                  className={`bg-white rounded-lg shadow-lg p-6 transition-all ${
                    isCurrentPlan 
                      ? 'ring-2 ring-indigo-600 transform scale-105' 
                      : 'hover:shadow-xl'
                  }`}
                >
                  <div className="text-center mb-4">
                    <PlanIconComp className={`h-12 w-12 mx-auto mb-3 ${getPlanColor(plan.code)}`} />
                    <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                    <p className="text-3xl font-bold text-indigo-600 mt-2">
                      {plan.price_mad === 0 ? 'Gratuit' : `${plan.price_mad} MAD`}
                    </p>
                    {plan.price_mad > 0 && (
                      <p className="text-sm text-gray-600">par mois</p>
                    )}
                  </div>

                  <div className="space-y-2 mb-6">
                    {plan.max_products && (
                      <div className="text-sm text-gray-600">
                        • {plan.max_products} produits
                      </div>
                    )}
                    {plan.max_campaigns && (
                      <div className="text-sm text-gray-600">
                        • {plan.max_campaigns} campagnes
                      </div>
                    )}
                    {plan.max_affiliates && (
                      <div className="text-sm text-gray-600">
                        • {plan.max_affiliates} affiliés
                      </div>
                    )}
                    {plan.commission_rate && (
                      <div className="text-sm text-gray-600">
                        • Commission: {plan.commission_rate}%
                      </div>
                    )}
                    {plan.platform_fee_rate && (
                      <div className="text-sm text-gray-600">
                        • Frais: {plan.platform_fee_rate}%
                      </div>
                    )}
                  </div>

                  {isCurrentPlan ? (
                    <button
                      disabled
                      className="w-full py-2 px-4 bg-gray-300 text-gray-600 rounded-lg font-semibold cursor-not-allowed"
                    >
                      Plan Actuel
                    </button>
                  ) : (
                    <button
                      onClick={() => handleUpgrade(plan.code)}
                      className="w-full py-2 px-4 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                    >
                      {plan.price_mad > (subscription?.monthly_fee || 0) 
                        ? 'Upgrader' 
                        : 'Changer'}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Cancel Section */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Zone de danger</h2>
          <p className="text-gray-600 mb-4">
            Vous pouvez annuler votre abonnement à tout moment. 
            L'annulation prendra effet à la fin de votre période de facturation actuelle.
          </p>
          <button
            onClick={() => setShowCancelModal(true)}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Annuler mon abonnement
          </button>
        </div>

        {/* Cancel Modal */}
        {showCancelModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">Annuler l'abonnement</h3>
                <button
                  onClick={() => setShowCancelModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <p className="text-gray-600 mb-4">
                Êtes-vous sûr de vouloir annuler votre abonnement ? 
                Vous perdrez l'accès aux fonctionnalités premium.
              </p>

              <textarea
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                placeholder="Dites-nous pourquoi vous partez (optionnel)..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent mb-4"
                rows="4"
              />

              <div className="flex space-x-4">
                <button
                  onClick={() => setShowCancelModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Retour
                </button>
                <button
                  onClick={handleCancelSubscription}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Confirmer l'annulation
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default SubscriptionManagement;
