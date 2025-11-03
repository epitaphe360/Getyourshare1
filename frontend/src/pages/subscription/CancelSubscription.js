import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './CancelSubscription.css';

function CancelSubscription() {
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [cancelFeedback, setCancelFeedback] = useState('');
  const [cancelType, setCancelType] = useState('end_of_period'); // 'immediate' or 'end_of_period'
  const [error, setError] = useState(null);

  const cancelReasons = [
    { value: 'too_expensive', label: 'Trop cher' },
    { value: 'missing_features', label: 'Fonctionnalités manquantes' },
    { value: 'not_using', label: 'Je ne l\'utilise pas assez' },
    { value: 'found_alternative', label: 'J\'ai trouvé une alternative' },
    { value: 'technical_issues', label: 'Problèmes techniques' },
    { value: 'bad_support', label: 'Support client insuffisant' },
    { value: 'temporary', label: 'Pause temporaire' },
    { value: 'other', label: 'Autre raison' }
  ];

  useEffect(() => {
    fetchCurrentSubscription();
  }, []);

  const fetchCurrentSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/subscriptions/current', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.data.success) {
        setSubscription(response.data.subscription);
      }
    } catch (err) {
      console.error('Erreur:', err);
      setError('Impossible de charger votre abonnement');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelClick = () => {
    if (!cancelReason) {
      alert('Veuillez sélectionner une raison d\'annulation');
      return;
    }
    setShowConfirmation(true);
  };

  const handleConfirmCancel = async () => {
    setCancelling(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/subscriptions/cancel',
        {
          reason: cancelReason,
          feedback: cancelFeedback,
          cancel_type: cancelType
        },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.data.success) {
        // Rediriger vers une page de confirmation
        navigate('/subscription/cancelled', {
          state: {
            cancelType: cancelType,
            effectiveDate: response.data.effective_date
          }
        });
      }
    } catch (err) {
      console.error('Erreur annulation:', err);
      setError(err.response?.data?.detail || 'Erreur lors de l\'annulation');
      setShowConfirmation(false);
    } finally {
      setCancelling(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="cancel-subscription">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  if (!subscription || subscription.plan_code === 'merchant_freemium' || subscription.plan_code === 'influencer_freemium') {
    return (
      <div className="cancel-subscription">
        <div className="info-container">
          <div className="info-icon">ℹ️</div>
          <h2>Aucun abonnement actif</h2>
          <p>Vous êtes actuellement sur le plan gratuit.</p>
          <button onClick={() => navigate('/subscription/plans')} className="primary-button">
            Voir les plans
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="cancel-subscription">
      <div className="cancel-container">
        {/* Header */}
        <div className="cancel-header">
          <div className="sad-icon">😔</div>
          <h1>Vous souhaitez annuler votre abonnement ?</h1>
          <p className="cancel-subtitle">
            Nous sommes désolés de vous voir partir. Aidez-nous à nous améliorer en nous disant pourquoi.
          </p>
        </div>

        {/* Current Subscription Info */}
        <div className="subscription-info-card">
          <h3>Votre abonnement actuel</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Plan:</span>
              <span className="info-value">{subscription.plan_name}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Prix:</span>
              <span className="info-value">
                {subscription.price} {subscription.currency} / {subscription.billing_cycle === 'monthly' ? 'mois' : 'an'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Date de renouvellement:</span>
              <span className="info-value">{formatDate(subscription.current_period_end)}</span>
            </div>
          </div>
        </div>

        {/* Cancel Form */}
        <div className="cancel-form">
          <div className="form-section">
            <label className="form-label">
              Pourquoi annulez-vous ? <span className="required">*</span>
            </label>
            <select
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              className="form-select"
            >
              <option value="">Sélectionnez une raison</option>
              {cancelReasons.map((reason) => (
                <option key={reason.value} value={reason.value}>
                  {reason.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-section">
            <label className="form-label">
              Dites-nous en plus (optionnel)
            </label>
            <textarea
              value={cancelFeedback}
              onChange={(e) => setCancelFeedback(e.target.value)}
              className="form-textarea"
              placeholder="Vos commentaires nous aident à améliorer notre service..."
              rows="4"
            />
          </div>

          <div className="form-section">
            <label className="form-label">Type d'annulation</label>
            <div className="radio-group">
              <label className="radio-option">
                <input
                  type="radio"
                  value="end_of_period"
                  checked={cancelType === 'end_of_period'}
                  onChange={(e) => setCancelType(e.target.value)}
                />
                <div className="radio-content">
                  <span className="radio-title">Annuler à la fin de la période</span>
                  <span className="radio-description">
                    Vous gardez l'accès jusqu'au {formatDate(subscription.current_period_end)}
                  </span>
                </div>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  value="immediate"
                  checked={cancelType === 'immediate'}
                  onChange={(e) => setCancelType(e.target.value)}
                />
                <div className="radio-content">
                  <span className="radio-title">Annuler immédiatement</span>
                  <span className="radio-description warning">
                    Accès coupé instantanément, pas de remboursement
                  </span>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* What You'll Lose */}
        <div className="lose-access-card">
          <h3>⚠️ Ce que vous perdrez</h3>
          <ul className="lose-list">
            <li>Accès à toutes les fonctionnalités premium</li>
            <li>Limites augmentées (produits, campagnes, affiliés)</li>
            <li>Support prioritaire</li>
            <li>Analyses avancées et rapports</li>
            <li>Intégrations tierces</li>
          </ul>
          <div className="downgrade-notice">
            Vous serez automatiquement basculé sur le plan <strong>Freemium</strong> après l'annulation.
          </div>
        </div>

        {/* Alternative Offers */}
        <div className="alternatives-card">
          <h3>💡 Avant de partir, avez-vous considéré ?</h3>
          <div className="alternatives-grid">
            <div className="alternative-option">
              <div className="alternative-icon">⏸️</div>
              <h4>Passer au plan inférieur</h4>
              <p>Gardez l'essentiel à moindre coût</p>
              <button
                onClick={() => navigate('/subscription/plans')}
                className="alternative-button"
              >
                Voir les plans
              </button>
            </div>
            <div className="alternative-option">
              <div className="alternative-icon">💬</div>
              <h4>Parler à notre équipe</h4>
              <p>Nous pouvons vous aider à résoudre vos problèmes</p>
              <button
                onClick={() => window.location.href = 'mailto:support@getyourshare.com'}
                className="alternative-button"
              >
                Contacter le support
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          <button
            onClick={() => navigate(-1)}
            className="secondary-button"
          >
            Retour
          </button>
          <button
            onClick={handleCancelClick}
            className="danger-button"
            disabled={!cancelReason}
          >
            Continuer l'annulation
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && (
        <div className="modal-overlay">
          <div className="confirmation-modal">
            <div className="modal-header">
              <h2>Confirmer l'annulation</h2>
            </div>
            <div className="modal-body">
              <p className="confirmation-text">
                {cancelType === 'immediate' ? (
                  <>
                    Votre abonnement sera <strong>annulé immédiatement</strong>. 
                    Vous perdrez l'accès à toutes les fonctionnalités premium maintenant.
                  </>
                ) : (
                  <>
                    Votre abonnement sera annulé à la fin de la période actuelle 
                    le <strong>{formatDate(subscription.current_period_end)}</strong>. 
                    Vous garderez l'accès jusqu'à cette date.
                  </>
                )}
              </p>
              <div className="confirmation-warning">
                Cette action ne peut pas être annulée.
              </div>
            </div>
            <div className="modal-footer">
              <button
                onClick={() => setShowConfirmation(false)}
                className="modal-button secondary"
                disabled={cancelling}
              >
                Annuler
              </button>
              <button
                onClick={handleConfirmCancel}
                className="modal-button danger"
                disabled={cancelling}
              >
                {cancelling ? (
                  <>
                    <span className="spinner-small"></span>
                    Annulation en cours...
                  </>
                ) : (
                  'Confirmer l\'annulation'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CancelSubscription;
