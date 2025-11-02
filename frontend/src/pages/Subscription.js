import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import Card from '../components/common/Card';
import { 
  Check, X, Crown, Star, Zap, Shield, 
  TrendingUp, Users, BarChart3, Sparkles,
  CreditCard, Gift
} from 'lucide-react';

const Subscription = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState('free');
  const [loading, setLoading] = useState(true);
  const [billingCycle, setBillingCycle] = useState('monthly'); // monthly ou yearly

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Récupérer les plans d'abonnement
      const plansRes = await api.get('/api/subscription-plans');
      setPlans(plansRes.data.plans || []);

      // Récupérer le plan actuel de l'utilisateur
      if (user?.role === 'influencer') {
        const influencerRes = await api.get('/api/influencer/profile');
        setCurrentPlan(influencerRes.data.subscription_plan || 'free');
      } else if (user?.role === 'merchant') {
        const merchantRes = await api.get('/api/merchant/profile');
        setCurrentPlan(merchantRes.data.subscription_plan || 'free');
      }
    } catch (error) {
      console.error('Error fetching subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Plans détaillés pour influenceurs
  const influencerPlans = [
    {
      id: 'free',
      name: 'Gratuit',
      subtitle: 'Pour débuter',
      price: 0,
      icon: <Gift className="w-8 h-8" />,
      color: 'gray',
      features: [
        { text: '10 liens d\'affiliation actifs', included: true },
        { text: 'Rapports basiques', included: true },
        { text: 'Commission standard', included: true },
        { text: 'Support par email', included: true },
        { text: 'Analytics avancés', included: false },
        { text: 'IA Marketing', included: false },
        { text: 'Support prioritaire', included: false },
        { text: 'Formations exclusives', included: false },
      ],
    },
    {
      id: 'starter',
      name: 'Starter',
      subtitle: 'Pour croître',
      price: 49,
      yearlyPrice: 490, // ~2 mois gratuits
      icon: <Star className="w-8 h-8" />,
      color: 'indigo',
      popular: false,
      features: [
        { text: '100 liens d\'affiliation actifs', included: true },
        { text: 'Rapports avancés', included: true },
        { text: 'Commission +5%', included: true },
        { text: 'Support prioritaire', included: true },
        { text: 'Analytics avancés', included: true },
        { text: 'Widgets personnalisés', included: true },
        { text: 'IA Marketing', included: false },
        { text: 'Formations exclusives', included: false },
      ],
    },
    {
      id: 'pro',
      name: 'Pro',
      subtitle: 'Pour les experts',
      price: 149,
      yearlyPrice: 1490, // ~2 mois gratuits
      icon: <Crown className="w-8 h-8" />,
      color: 'purple',
      popular: true,
      features: [
        { text: 'Liens illimités', included: true },
        { text: 'Rapports experts + export', included: true },
        { text: 'Commission +10%', included: true },
        { text: 'Support prioritaire 24/7', included: true },
        { text: 'Analytics en temps réel', included: true },
        { text: 'IA Marketing avancé', included: true },
        { text: 'API complète', included: true },
        { text: 'Formations exclusives', included: true },
        { text: 'Manager dédié', included: true },
      ],
    },
  ];

  // Plans détaillés pour marchands
  const merchantPlans = [
    {
      id: 'free',
      name: 'Essai Gratuit',
      subtitle: 'Testez la plateforme',
      price: 0,
      icon: <Gift className="w-8 h-8" />,
      color: 'gray',
      features: [
        { text: '3 produits maximum', included: true },
        { text: '10 affiliés actifs', included: true },
        { text: 'Rapports basiques', included: true },
        { text: 'Commission standard 5%', included: true },
        { text: 'Dashboard analytique', included: false },
        { text: 'Support prioritaire', included: false },
        { text: 'API et webhooks', included: false },
        { text: 'White label', included: false },
      ],
    },
    {
      id: 'starter',
      name: 'Starter',
      subtitle: 'Pour PME',
      price: 99,
      yearlyPrice: 990,
      icon: <TrendingUp className="w-8 h-8" />,
      color: 'green',
      popular: false,
      features: [
        { text: '20 produits', included: true },
        { text: '50 affiliés actifs', included: true },
        { text: 'Rapports avancés', included: true },
        { text: 'Commission 3%', included: true },
        { text: 'Dashboard analytique', included: true },
        { text: 'Support par email', included: true },
        { text: 'Intégrations basiques', included: true },
        { text: 'API et webhooks', included: false },
        { text: 'White label', included: false },
      ],
    },
    {
      id: 'pro',
      name: 'Business',
      subtitle: 'Pour entreprises',
      price: 299,
      yearlyPrice: 2990,
      icon: <BarChart3 className="w-8 h-8" />,
      color: 'indigo',
      popular: true,
      features: [
        { text: '100 produits', included: true },
        { text: '200 affiliés actifs', included: true },
        { text: 'Rapports experts + export', included: true },
        { text: 'Commission 2%', included: true },
        { text: 'Analytics avancés IA', included: true },
        { text: 'Support prioritaire 24/7', included: true },
        { text: 'Toutes intégrations', included: true },
        { text: 'API complète', included: true },
        { text: 'White label partiel', included: true },
      ],
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      subtitle: 'Solution sur mesure',
      price: 'Sur devis',
      icon: <Shield className="w-8 h-8" />,
      color: 'yellow',
      popular: false,
      features: [
        { text: 'Produits illimités', included: true },
        { text: 'Affiliés illimités', included: true },
        { text: 'Rapports personnalisés', included: true },
        { text: 'Commission négociée', included: true },
        { text: 'Analytics personnalisés', included: true },
        { text: 'Manager dédié', included: true },
        { text: 'Intégrations sur mesure', included: true },
        { text: 'API dédiée', included: true },
        { text: 'White label complet', included: true },
        { text: 'Infrastructure dédiée', included: true },
      ],
    },
  ];

  // Choisir les plans selon le rôle
  const availablePlans = user?.role === 'merchant' ? merchantPlans : influencerPlans;

  const getColorClasses = (color, variant = 'bg') => {
    const colors = {
      gray: {
        bg: 'bg-gray-600',
        bgLight: 'bg-gray-100',
        text: 'text-gray-600',
        border: 'border-gray-300',
        button: 'bg-gray-600 hover:bg-gray-700',
      },
      indigo: {
        bg: 'bg-indigo-600',
        bgLight: 'bg-indigo-100',
        text: 'text-indigo-600',
        border: 'border-indigo-300',
        button: 'bg-indigo-600 hover:bg-indigo-700',
      },
      purple: {
        bg: 'bg-purple-600',
        bgLight: 'bg-purple-100',
        text: 'text-purple-600',
        border: 'border-purple-300',
        button: 'bg-purple-600 hover:bg-purple-700',
      },
      green: {
        bg: 'bg-green-600',
        bgLight: 'bg-green-100',
        text: 'text-green-600',
        border: 'border-green-300',
        button: 'bg-green-600 hover:bg-green-700',
      },
      yellow: {
        bg: 'bg-yellow-600',
        bgLight: 'bg-yellow-100',
        text: 'text-yellow-600',
        border: 'border-yellow-300',
        button: 'bg-yellow-600 hover:bg-yellow-700',
      },
    };
    return colors[color] || colors.gray;
  };

  const handleUpgrade = (planId) => {
    if (planId === 'enterprise') {
      // Rediriger vers la page de contact
      navigate('/support');
    } else {
      // Simuler l'upgrade (à implémenter avec un vrai système de paiement)
      toast.info(`Mise à niveau vers le plan ${planId}. Intégration de paiement à venir !`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Choisissez votre Abonnement
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          {user?.role === 'merchant' 
            ? 'Développez votre réseau d\'affiliés et boostez vos ventes'
            : 'Maximisez vos revenus avec les meilleurs outils d\'affiliation'}
        </p>

        {/* Billing Cycle Toggle */}
        <div className="inline-flex items-center bg-gray-100 rounded-lg p-1 mb-8">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-6 py-2 rounded-lg transition ${
              billingCycle === 'monthly'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600'
            }`}
          >
            Mensuel
          </button>
          <button
            onClick={() => setBillingCycle('yearly')}
            className={`px-6 py-2 rounded-lg transition flex items-center gap-2 ${
              billingCycle === 'yearly'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600'
            }`}
          >
            Annuel
            <span className="bg-green-100 text-green-700 text-xs font-semibold px-2 py-1 rounded">
              -20%
            </span>
          </button>
        </div>
      </div>

      {/* Current Plan Badge */}
      <div className="max-w-3xl mx-auto bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl p-6 text-center">
        <div className="flex items-center justify-center gap-3 mb-2">
          <Sparkles className="w-6 h-6" />
          <span className="text-lg font-semibold">Plan Actuel</span>
        </div>
        <div className="text-3xl font-bold capitalize">{currentPlan}</div>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
        {availablePlans.map((plan) => {
          const colors = getColorClasses(plan.color);
          const isCurrentPlan = currentPlan === plan.id;
          const displayPrice = billingCycle === 'yearly' && plan.yearlyPrice 
            ? Math.round(plan.yearlyPrice / 12) 
            : plan.price;

          return (
            <div
              key={plan.id}
              className={`relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 ${
                plan.popular ? 'ring-4 ring-purple-500 scale-105' : ''
              } ${isCurrentPlan ? 'ring-4 ring-green-500' : ''}`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-1 rounded-full text-sm font-semibold shadow-lg">
                    ⭐ Plus Populaire
                  </span>
                </div>
              )}

              {/* Current Plan Badge */}
              {isCurrentPlan && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-green-500 text-white px-4 py-1 rounded-full text-sm font-semibold shadow-lg">
                    ✓ Plan Actuel
                  </span>
                </div>
              )}

              <div className="p-8">
                {/* Icon */}
                <div className={`${colors.bgLight} ${colors.text} w-16 h-16 rounded-2xl flex items-center justify-center mb-4`}>
                  {plan.icon}
                </div>

                {/* Name & Subtitle */}
                <h3 className="text-2xl font-bold text-gray-900 mb-1">{plan.name}</h3>
                <p className="text-sm text-gray-600 mb-6">{plan.subtitle}</p>

                {/* Price */}
                <div className="mb-6">
                  {typeof plan.price === 'number' ? (
                    <>
                      <div className="flex items-baseline">
                        <span className="text-5xl font-bold text-gray-900">{displayPrice}</span>
                        <span className="text-xl text-gray-600 ml-2">€</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        par mois {billingCycle === 'yearly' && plan.yearlyPrice && '(facturé annuellement)'}
                      </div>
                      {billingCycle === 'yearly' && plan.yearlyPrice && (
                        <div className="text-xs text-green-600 font-semibold mt-1">
                          Économisez {(plan.price * 12 - plan.yearlyPrice).toFixed(0)}€/an
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="text-3xl font-bold text-gray-900">{plan.price}</div>
                  )}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={isCurrentPlan}
                  className={`w-full py-3 rounded-lg font-semibold transition mb-6 ${
                    isCurrentPlan
                      ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                      : `${colors.button} text-white`
                  }`}
                >
                  {isCurrentPlan ? 'Plan Actif' : plan.id === 'enterprise' ? 'Nous Contacter' : 'Passer au ' + plan.name}
                </button>

                {/* Features List */}
                <ul className="space-y-3">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      {feature.included ? (
                        <Check className={`w-5 h-5 ${colors.text} flex-shrink-0 mt-0.5`} />
                      ) : (
                        <X className="w-5 h-5 text-gray-300 flex-shrink-0 mt-0.5" />
                      )}
                      <span className={`text-sm ${feature.included ? 'text-gray-700' : 'text-gray-400'}`}>
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>

      {/* FAQ Section */}
      <div className="max-w-4xl mx-auto mt-16">
        <h2 className="text-3xl font-bold text-center mb-8">Questions Fréquentes</h2>
        <div className="space-y-6">
          <Card>
            <h3 className="text-lg font-semibold mb-2">Puis-je changer de plan à tout moment ?</h3>
            <p className="text-gray-600">
              Oui, vous pouvez passer à un plan supérieur ou inférieur à tout moment. 
              Les changements prennent effet immédiatement et sont calculés au prorata.
            </p>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-2">Comment fonctionne la facturation annuelle ?</h3>
            <p className="text-gray-600">
              Avec la facturation annuelle, vous économisez environ 20% par rapport au paiement mensuel. 
              Vous êtes facturé une fois par an et bénéficiez de 2 mois gratuits.
            </p>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-2">Puis-je annuler mon abonnement ?</h3>
            <p className="text-gray-600">
              Oui, vous pouvez annuler votre abonnement à tout moment depuis vos paramètres. 
              Aucun frais d'annulation. Vous gardez l'accès jusqu'à la fin de votre période payée.
            </p>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-2">Quels moyens de paiement acceptez-vous ?</h3>
            <p className="text-gray-600">
              Nous acceptons les cartes bancaires (Visa, Mastercard), PayPal, et les virements bancaires 
              pour les plans Enterprise. Tous les paiements sont sécurisés.
            </p>
          </Card>
        </div>
      </div>

      {/* Support CTA */}
      <div className="max-w-4xl mx-auto mt-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white text-center">
        <h2 className="text-2xl font-bold mb-4">Besoin d'aide pour choisir ?</h2>
        <p className="text-lg mb-6">
          Notre équipe est là pour vous accompagner dans le choix du plan le plus adapté à vos besoins.
        </p>
        <button
          onClick={() => navigate('/support')}
          className="bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold hover:bg-indigo-50 transition"
        >
          Contacter le Support
        </button>
      </div>
    </div>
  );
};

export default Subscription;
