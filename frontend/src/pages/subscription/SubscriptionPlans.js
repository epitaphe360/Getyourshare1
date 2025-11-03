import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import './SubscriptionPlans.css';

const SubscriptionPlans = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [loading, setLoading] = useState(true);
  const [processingPlanId, setProcessingPlanId] = useState(null);

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const userType = user?.role || 'merchant';
      const response = await axios.get(
        `http://localhost:8000/api/subscriptions/plans?user_type=${userType}`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }
      );
      setPlans(response.data.plans || []);
    } catch (error) {
      console.error('Erreur chargement plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/api/subscriptions/current',
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }
      );
      setCurrentSubscription(response.data);
    } catch (error) {
      console.error('Erreur abonnement actuel:', error);
    }
  };

  const handleSelectPlan = async (plan) => {
    // Si c'est le plan gratuit, pas besoin de paiement
    if (plan.price_monthly === 0 && plan.price_yearly === 0) {
      alert('Vous êtes déjà sur le plan gratuit');
      return;
    }

    setProcessingPlanId(plan.id);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/stripe/create-checkout-session',
        {
          plan_id: plan.id,
          billing_cycle: billingCycle
        },
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }
      );

      if (response.data.success && response.data.checkout_url) {
        // Rediriger vers Stripe Checkout
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      console.error('Erreur création checkout:', error);
      alert('Erreur lors de la création de la session de paiement');
      setProcessingPlanId(null);
    }
  };

  const getPrice = (plan) => {
    return billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  };

  const isCurrentPlan = (plan) => {
    return currentSubscription?.plan_code === plan.code;
  };

  if (loading) {
    return (
      <div className="subscription-plans-container">
        <div className="loading">Chargement des plans...</div>
      </div>
    );
  }

  return (
    <div className="subscription-plans-container">
      <div className="subscription-plans-header">
        <h1>Choisissez votre plan</h1>
        <p>Sélectionnez le plan qui correspond le mieux à vos besoins</p>

        {/* Toggle Mensuel/Annuel */}
        <div className="billing-cycle-toggle">
          <button
            className={billingCycle === 'monthly' ? 'active' : ''}
            onClick={() => setBillingCycle('monthly')}
          >
            Mensuel
          </button>
          <button
            className={billingCycle === 'yearly' ? 'active' : ''}
            onClick={() => setBillingCycle('yearly')}
          >
            Annuel
            <span className="badge">-20%</span>
          </button>
        </div>
      </div>

      <div className="plans-grid">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`plan-card ${isCurrentPlan(plan) ? 'current' : ''} ${
              plan.name === 'Premium' || plan.name === 'Pro' ? 'popular' : ''
            }`}
          >
            {(plan.name === 'Premium' || plan.name === 'Pro') && (
              <div className="popular-badge">Populaire</div>
            )}

            {isCurrentPlan(plan) && (
              <div className="current-badge">Plan actuel</div>
            )}

            <div className="plan-header">
              <h3>{plan.name}</h3>
              <p className="plan-description">{plan.description}</p>
            </div>

            <div className="plan-price">
              <span className="price-amount">{getPrice(plan)}€</span>
              <span className="price-period">
                / {billingCycle === 'monthly' ? 'mois' : 'an'}
              </span>
            </div>

            {billingCycle === 'yearly' && plan.price_yearly > 0 && (
              <div className="savings">
                Économisez{' '}
                {Math.round(plan.price_monthly * 12 - plan.price_yearly)}€/an
              </div>
            )}

            <ul className="plan-features">
              {plan.features?.map((feature, index) => (
                <li key={index}>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path
                      d="M16.6667 5L7.50004 14.1667L3.33337 10"
                      stroke="#10b981"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>

            <div className="plan-limits">
              {plan.max_products && (
                <div className="limit-item">
                  <span className="limit-label">Produits:</span>
                  <span className="limit-value">
                    {plan.max_products === -1 ? 'Illimité' : plan.max_products}
                  </span>
                </div>
              )}
              {plan.max_campaigns && (
                <div className="limit-item">
                  <span className="limit-label">Campagnes:</span>
                  <span className="limit-value">
                    {plan.max_campaigns === -1 ? 'Illimité' : plan.max_campaigns}
                  </span>
                </div>
              )}
              {plan.max_affiliates && (
                <div className="limit-item">
                  <span className="limit-label">Affiliés:</span>
                  <span className="limit-value">
                    {plan.max_affiliates === -1 ? 'Illimité' : plan.max_affiliates}
                  </span>
                </div>
              )}
              {plan.commission_rate && (
                <div className="limit-item">
                  <span className="limit-label">Commission:</span>
                  <span className="limit-value">{plan.commission_rate}%</span>
                </div>
              )}
            </div>

            <button
              className={`plan-button ${
                isCurrentPlan(plan) ? 'current' : 'upgrade'
              }`}
              onClick={() => handleSelectPlan(plan)}
              disabled={isCurrentPlan(plan) || processingPlanId === plan.id}
            >
              {processingPlanId === plan.id ? (
                'Chargement...'
              ) : isCurrentPlan(plan) ? (
                'Plan actuel'
              ) : getPrice(plan) === 0 ? (
                'Gratuit'
              ) : (
                'Choisir ce plan'
              )}
            </button>
          </div>
        ))}
      </div>

      <div className="subscription-footer">
        <p>
          <strong>Tous les plans incluent:</strong> Support client, Mises à
          jour gratuites, Sécurité renforcée
        </p>
        <p className="help-text">
          Des questions ?{' '}
          <a href="mailto:support@shareyoursales.ma">Contactez-nous</a>
        </p>
      </div>
    </div>
  );
};

export default SubscriptionPlans;
