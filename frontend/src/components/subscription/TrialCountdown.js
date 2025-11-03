import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './TrialCountdown.css';

function TrialCountdown() {
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState(null);
  const [daysLeft, setDaysLeft] = useState(null);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/subscriptions/current', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.data.success && response.data.subscription) {
        const sub = response.data.subscription;
        
        // Vérifier si en période d'essai
        if (sub.status === 'trialing' && sub.trial_end) {
          const trialEnd = new Date(sub.trial_end);
          const now = new Date();
          const diffTime = trialEnd - now;
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

          if (diffDays > 0 && diffDays <= 14) {
            setSubscription(sub);
            setDaysLeft(diffDays);
            setShowBanner(true);
          }
        }
      }
    } catch (err) {
      console.error('Erreur lors de la récupération de l\'abonnement:', err);
    }
  };

  const handleUpgrade = () => {
    navigate('/subscription/plans');
    setShowBanner(false);
  };

  const handleDismiss = () => {
    setShowBanner(false);
    // Sauvegarder dans localStorage pour ne pas réafficher pendant 24h
    localStorage.setItem('trialBannerDismissed', Date.now().toString());
  };

  // Vérifier si banner a été dismissed récemment
  useEffect(() => {
    const dismissed = localStorage.getItem('trialBannerDismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed);
      const now = Date.now();
      const hoursPassed = (now - dismissedTime) / (1000 * 60 * 60);
      
      if (hoursPassed < 24) {
        setShowBanner(false);
      }
    }
  }, []);

  if (!showBanner || !subscription || daysLeft === null) {
    return null;
  }

  // Déterminer le niveau d'urgence
  const getUrgencyLevel = () => {
    if (daysLeft <= 3) return 'critical';
    if (daysLeft <= 7) return 'warning';
    return 'info';
  };

  const urgencyLevel = getUrgencyLevel();

  return (
    <div className={`trial-countdown-banner ${urgencyLevel}`}>
      <div className="trial-content">
        <div className="trial-icon">
          {urgencyLevel === 'critical' ? '⏰' : urgencyLevel === 'warning' ? '⚠️' : '🎁'}
        </div>
        
        <div className="trial-message">
          <h4 className="trial-title">
            {urgencyLevel === 'critical' 
              ? '⚡ Essai gratuit bientôt terminé !'
              : urgencyLevel === 'warning'
              ? '⏳ Votre essai gratuit se termine bientôt'
              : '🎉 Profitez de votre essai gratuit'
            }
          </h4>
          <p className="trial-text">
            {daysLeft === 1 
              ? `Plus qu'1 jour pour profiter de toutes les fonctionnalités premium !`
              : `Il vous reste ${daysLeft} jours d'essai gratuit sur le plan ${subscription.plan_name}.`
            }
          </p>
        </div>

        <div className="trial-actions">
          <button onClick={handleUpgrade} className="trial-button-upgrade">
            {urgencyLevel === 'critical' ? '🚀 Activer maintenant' : '💎 Voir les plans'}
          </button>
          <button onClick={handleDismiss} className="trial-button-dismiss">
            Plus tard
          </button>
        </div>
      </div>

      {urgencyLevel === 'critical' && (
        <div className="trial-countdown-timer">
          <div className="countdown-item">
            <span className="countdown-value">{daysLeft}</span>
            <span className="countdown-label">jour{daysLeft > 1 ? 's' : ''}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default TrialCountdown;
