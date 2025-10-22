import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Check, X, Zap, TrendingUp, Users, Shield, Sparkles, ArrowRight } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Pricing = () => {
  const [subscriptionPlans, setSubscriptionPlans] = useState({ merchants: [], influencers: [] });
  const [selectedPlan, setSelectedPlan] = useState('merchants');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSubscriptionPlans();
  }, []);

  const fetchSubscriptionPlans = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/subscription-plans`);
      setSubscriptionPlans(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Erreur lors du chargement des plans:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-8 w-8 text-indigo-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                ShareYourSales
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-gray-700 hover:text-indigo-600 transition">
                Accueil
              </Link>
              <Link to="/login" className="text-gray-700 hover:text-indigo-600 transition">
                Connexion
              </Link>
              <Link
                to="/register"
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
              >
                S'inscrire
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="pt-16 pb-12 text-center">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Maximisez chaque clic, générez des revenus automatiques
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Choisissez le plan qui correspond à vos ambitions
          </p>
          
          {/* Plan Toggle */}
          <div className="inline-flex bg-white rounded-xl shadow-lg p-2 mb-12">
            <button
              onClick={() => setSelectedPlan('merchants')}
              className={`px-8 py-3 rounded-lg font-medium transition ${
                selectedPlan === 'merchants'
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Users className="inline-block w-5 h-5 mr-2" />
              Pour les Entreprises
            </button>
            <button
              onClick={() => setSelectedPlan('influencers')}
              className={`px-8 py-3 rounded-lg font-medium transition ${
                selectedPlan === 'influencers'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Zap className="inline-block w-5 h-5 mr-2" />
              Pour les Influenceurs
            </button>
          </div>
        </div>
      </div>

      {/* Pricing Cards - Merchants */}
      {selectedPlan === 'merchants' && (
        <div className="max-w-7xl mx-auto px-4 pb-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {subscriptionPlans.merchants.map((plan, index) => (
              <div
                key={plan.id}
                className={`bg-white rounded-2xl shadow-xl overflow-hidden transform hover:scale-105 transition ${
                  index === 2 ? 'ring-4 ring-indigo-600' : ''
                }`}
              >
                {index === 2 && (
                  <div className="bg-indigo-600 text-white text-center py-2 text-sm font-semibold">
                    ⭐ POPULAIRE
                  </div>
                )}
                
                <div className="p-8">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="mb-6">
                    {plan.price !== null ? (
                      <>
                        <span className="text-4xl font-bold">{plan.price}€</span>
                        <span className="text-gray-600">/mois</span>
                      </>
                    ) : (
                      <span className="text-3xl font-bold text-indigo-600">Sur devis</span>
                    )}
                  </div>
                  
                  <div className="mb-6">
                    <div className="text-sm text-gray-600 mb-2">Commission par vente</div>
                    <div className="text-2xl font-bold text-indigo-600">{plan.commission_rate}%</div>
                  </div>

                  <div className="space-y-3 mb-8">
                    <div className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{plan.features.user_accounts} compte(s) utilisateur</span>
                    </div>
                    <div className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{plan.features.trackable_links_per_month} liens traçables/mois</span>
                    </div>
                    <div className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Rapports {plan.features.reports}</span>
                    </div>
                    {plan.features.ai_tools && (
                      <div className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">Outils IA Marketing</span>
                      </div>
                    )}
                    {plan.features.dedicated_manager && (
                      <div className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">Manager dédié</span>
                      </div>
                    )}
                    <div className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Support {plan.features.support}</span>
                    </div>
                  </div>

                  <Link
                    to="/register"
                    className={`block w-full text-center py-3 rounded-lg font-semibold transition ${
                      index === 2
                        ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    }`}
                  >
                    {plan.price === 0 ? 'Commencer gratuitement' : 'Choisir ce plan'}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pricing Cards - Influencers */}
      {selectedPlan === 'influencers' && (
        <div className="max-w-5xl mx-auto px-4 pb-16">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {subscriptionPlans.influencers.map((plan, index) => (
              <div
                key={plan.id}
                className={`bg-white rounded-2xl shadow-xl overflow-hidden transform hover:scale-105 transition ${
                  index === 1 ? 'ring-4 ring-purple-600' : ''
                }`}
              >
                {index === 1 && (
                  <div className="bg-purple-600 text-white text-center py-2 text-sm font-semibold">
                    ⭐ RECOMMANDÉ
                  </div>
                )}
                
                <div className="p-8">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="mb-6">
                    <span className="text-4xl font-bold">{plan.price}€</span>
                    <span className="text-gray-600">/mois</span>
                  </div>
                  
                  <div className="mb-6">
                    <div className="text-sm text-gray-600 mb-2">Frais de plateforme</div>
                    <div className="text-2xl font-bold text-purple-600">{plan.platform_fee_rate}%</div>
                  </div>

                  <div className="space-y-3 mb-8">
                    <div className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Outils IA: {plan.features.ai_tools}</span>
                    </div>
                    <div className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Campagnes: {plan.features.campaigns_per_month}</span>
                    </div>
                    <div className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Paiements: {plan.features.payments}</span>
                    </div>
                    <div className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Analytics: {plan.features.analytics}</span>
                    </div>
                    {plan.features.priority_support && (
                      <div className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">Support prioritaire</span>
                      </div>
                    )}
                  </div>

                  <Link
                    to="/register"
                    className={`block w-full text-center py-3 rounded-lg font-semibold transition ${
                      index === 1
                        ? 'bg-purple-600 text-white hover:bg-purple-700'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    }`}
                  >
                    Choisir ce plan
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Features Section */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            Pourquoi choisir ShareYourSales ?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">ROI Garanti</h3>
              <p className="text-gray-600">
                Optimisez vos investissements marketing avec des analyses en temps réel
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Transparence Totale</h3>
              <p className="text-gray-600">
                Rapports détaillés et tracking précis de toutes vos performances
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Paiements Rapides</h3>
              <p className="text-gray-600">
                Recevez vos commissions rapidement et en toute sécurité
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl font-bold text-white mb-4">
            Prêt à maximiser vos revenus ?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Rejoignez des milliers d'entreprises et d'influenceurs qui font confiance à ShareYourSales
          </p>
          <Link
            to="/register"
            className="inline-flex items-center bg-white text-indigo-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition"
          >
            Commencer maintenant
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-gray-400">
            © 2024 ShareYourSales. Tous droits réservés.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Pricing;
