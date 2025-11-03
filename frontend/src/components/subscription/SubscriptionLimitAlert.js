import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './SubscriptionLimitAlert.css';

const SubscriptionLimitAlert = () => {
  const navigate = useNavigate();
  const [usage, setUsage] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [showBanner, setShowBanner] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchUsage();
  }, []);

  const fetchUsage = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/api/subscriptions/usage',
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }
      );
      setUsage(response.data);
      checkLimits(response.data);
    } catch (error) {
      console.error('Erreur récupération usage:', error);
    }
  };

  const checkLimits = (usageData) => {
    const newAlerts = [];

    Object.entries(usageData).forEach(([resource, data]) => {
      if (resource === 'api_calls_this_month' || resource === 'campaigns_this_month') {
        return; // Skip ces compteurs
      }

      const percentage = data.percentage;
      
      if (percentage >= 100) {
        newAlerts.push({
          resource,
          level: 'critical',
          percentage: 100,
          current: data.current,
          limit: data.limit,
          message: `Limite atteinte pour ${getResourceName(resource)} (${data.current}/${data.limit})`
        });
        setShowModal(true);
      } else if (percentage >= 90) {
        newAlerts.push({
          resource,
          level: 'high',
          percentage,
          current: data.current,
          limit: data.limit,
          message: `Presque plein: ${getResourceName(resource)} (${data.current}/${data.limit})`
        });
        setShowBanner(true);
      } else if (percentage >= 80) {
        newAlerts.push({
          resource,
          level: 'medium',
          percentage,
          current: data.current,
          limit: data.limit,
          message: `Attention: ${getResourceName(resource)} à ${percentage}% (${data.current}/${data.limit})`
        });
        setShowBanner(true);
      }
    });

    setAlerts(newAlerts);
  };

  const getResourceName = (resource) => {
    const names = {
      products: 'Produits',
      campaigns: 'Campagnes',
      affiliates: 'Affiliés'
    };
    return names[resource] || resource;
  };

  const handleUpgrade = () => {
    navigate('/subscription/plans');
  };

  const closeBanner = () => {
    setShowBanner(false);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  if (!alerts.length) {
    return null;
  }

  const criticalAlerts = alerts.filter(a => a.level === 'critical');
  const highAlerts = alerts.filter(a => a.level === 'high');
  const mediumAlerts = alerts.filter(a => a.level === 'medium');

  return (
    <>
      {/* Banner d'alerte (80% - 90%) */}
      {showBanner && !showModal && (mediumAlerts.length > 0 || highAlerts.length > 0) && (
        <div className={`limit-alert-banner ${highAlerts.length > 0 ? 'high' : 'medium'}`}>
          <div className="alert-banner-content">
            <div className="alert-icon">
              {highAlerts.length > 0 ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
            <div className="alert-text">
              <strong>Limite d'abonnement approchée</strong>
              <p>{[...mediumAlerts, ...highAlerts][0]?.message}</p>
            </div>
            <button className="alert-upgrade-btn" onClick={handleUpgrade}>
              Upgrader maintenant
            </button>
            <button className="alert-close-btn" onClick={closeBanner}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Modal d'alerte critique (100%) */}
      {showModal && criticalAlerts.length > 0 && (
        <div className="limit-alert-modal-overlay" onClick={closeModal}>
          <div className="limit-alert-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon critical">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            
            <h2>Limite atteinte !</h2>
            <p className="modal-description">
              Vous avez atteint la limite de votre plan actuel pour :
            </p>

            <div className="critical-alerts-list">
              {criticalAlerts.map((alert, index) => (
                <div key={index} className="critical-alert-item">
                  <span className="resource-name">{getResourceName(alert.resource)}</span>
                  <span className="resource-limit">{alert.current} / {alert.limit}</span>
                  <div className="progress-bar full">
                    <div className="progress-fill" style={{ width: '100%' }}></div>
                  </div>
                </div>
              ))}
            </div>

            <p className="modal-upgrade-text">
              Pour continuer à créer des {getResourceName(criticalAlerts[0]?.resource).toLowerCase()}, 
              veuillez upgrader vers un plan supérieur.
            </p>

            <div className="modal-actions">
              <button className="modal-upgrade-btn" onClick={handleUpgrade}>
                Voir les plans
              </button>
              <button className="modal-close-btn" onClick={closeModal}>
                Plus tard
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default SubscriptionLimitAlert;
