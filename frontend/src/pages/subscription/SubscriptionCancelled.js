import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './SubscriptionCancelled.css';

function SubscriptionCancelled() {
  const navigate = useNavigate();
  const location = useLocation();
  const { cancelType, effectiveDate } = location.state || {};

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="subscription-cancelled">
      <div className="cancelled-container">
        <div className="cancelled-icon">
          {cancelType === 'immediate' ? '🔴' : '⏸️'}
        </div>

        <h1>Abonnement annulé</h1>

        {cancelType === 'immediate' ? (
          <div className="cancelled-message immediate">
            <p>
              Votre abonnement a été <strong>annulé immédiatement</strong>.
            </p>
            <p>
              Vous avez perdu l'accès aux fonctionnalités premium et êtes maintenant sur le plan <strong>Freemium</strong>.
            </p>
          </div>
        ) : (
          <div className="cancelled-message end-of-period">
            <p>
              Votre abonnement sera annulé le <strong>{formatDate(effectiveDate)}</strong>.
            </p>
            <p>
              Vous conservez l'accès à toutes les fonctionnalités premium jusqu'à cette date.
            </p>
          </div>
        )}

        <div className="next-steps-card">
          <h2>Et maintenant ?</h2>
          <div className="steps-list">
            <div className="step-item">
              <div className="step-icon">📧</div>
              <div className="step-content">
                <h3>Email de confirmation</h3>
                <p>Vous recevrez un email récapitulatif de votre annulation</p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-icon">💰</div>
              <div className="step-content">
                <h3>Pas de remboursement</h3>
                <p>Les frais déjà payés ne sont pas remboursables selon nos CGV</p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-icon">🔄</div>
              <div className="step-content">
                <h3>Réactivation possible</h3>
                <p>Vous pouvez vous réabonner à tout moment depuis les paramètres</p>
              </div>
            </div>
          </div>
        </div>

        <div className="feedback-thanks">
          <h3>🙏 Merci pour vos retours</h3>
          <p>
            Vos commentaires nous aident à améliorer notre service. Nous espérons vous revoir bientôt !
          </p>
        </div>

        <div className="action-buttons">
          <button
            onClick={() => navigate('/dashboard')}
            className="primary-button"
          >
            Retour au tableau de bord
          </button>
          <button
            onClick={() => navigate('/subscription/plans')}
            className="secondary-button"
          >
            Voir les plans
          </button>
        </div>

        <div className="support-message">
          <p>
            Des questions ? Contactez notre support à{' '}
            <a href="mailto:support@getyourshare.com">support@getyourshare.com</a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default SubscriptionCancelled;
