// Service de paiement pour ShareYourSales
// Supporte CMI (Maroc), Stripe et PayPal

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class PaymentService {
  constructor() {
    this.providers = {
      CMI: 'cmi',
      STRIPE: 'stripe',
      PAYPAL: 'paypal'
    };
  }

  /**
   * Initie un paiement d'abonnement
   * @param {Object} subscriptionData - Données de l'abonnement
   * @param {string} provider - Fournisseur de paiement ('cmi', 'stripe', 'paypal')
   * @returns {Promise<Object>} - Résultat du paiement
   */
  async initiateSubscriptionPayment(subscriptionData, provider = 'cmi') {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/init-subscription`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...subscriptionData,
          provider: provider
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de l\'initialisation du paiement');
      }

      const data = await response.json();
      
      // Redirection vers la page de paiement selon le provider
      if (provider === this.providers.CMI && data.payment_url) {
        window.location.href = data.payment_url;
      } else if (provider === this.providers.STRIPE && data.session_id) {
        // Redirection Stripe Checkout
        const stripe = window.Stripe(data.stripe_public_key);
        await stripe.redirectToCheckout({ sessionId: data.session_id });
      } else if (provider === this.providers.PAYPAL && data.approval_url) {
        window.location.href = data.approval_url;
      }

      return data;
    } catch (error) {
      console.error('Erreur paiement:', error);
      throw error;
    }
  }

  /**
   * Vérifie le statut d'un paiement
   * @param {string} paymentId - ID du paiement
   * @returns {Promise<Object>} - Statut du paiement
   */
  async checkPaymentStatus(paymentId) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/status/${paymentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la vérification du paiement');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur vérification paiement:', error);
      throw error;
    }
  }

  /**
   * Annule un abonnement
   * @returns {Promise<Object>} - Confirmation d'annulation
   */
  async cancelSubscription() {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/subscriptions/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de l\'annulation');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur annulation:', error);
      throw error;
    }
  }

  /**
   * Récupère l'historique des paiements
   * @returns {Promise<Array>} - Liste des paiements
   */
  async getPaymentHistory() {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/history`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la récupération de l\'historique');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur historique:', error);
      throw error;
    }
  }

  /**
   * Demande un remboursement
   * @param {string} paymentId - ID du paiement à rembourser
   * @param {string} reason - Raison du remboursement
   * @returns {Promise<Object>} - Résultat de la demande
   */
  async requestRefund(paymentId, reason) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/refund`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          payment_id: paymentId,
          reason: reason
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de la demande de remboursement');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur remboursement:', error);
      throw error;
    }
  }

  /**
   * Traite le paiement d'une commission (pour les entreprises)
   * @param {Object} commissionData - Données de la commission
   * @returns {Promise<Object>} - Résultat du paiement
   */
  async payCommission(commissionData) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/pay-commission`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(commissionData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors du paiement de la commission');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur paiement commission:', error);
      throw error;
    }
  }

  /**
   * Demande un retrait (pour les influenceurs)
   * @param {number} amount - Montant à retirer
   * @param {string} method - Méthode de retrait ('bank', 'paypal')
   * @returns {Promise<Object>} - Résultat de la demande
   */
  async requestPayout(amount, method = 'bank') {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/payouts/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          amount: amount,
          payout_method: method
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de la demande de retrait');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur retrait:', error);
      throw error;
    }
  }

  /**
   * Récupère les méthodes de paiement disponibles
   * @returns {Promise<Array>} - Liste des méthodes
   */
  async getAvailablePaymentMethods() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/methods`);

      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des méthodes de paiement');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur méthodes paiement:', error);
      // Retourne les méthodes par défaut en cas d'erreur
      return [
        { id: 'cmi', name: 'CMI (Carte Bancaire Maroc)', logo: '/images/cmi-logo.png', available: true },
        { id: 'stripe', name: 'Stripe (International)', logo: '/images/stripe-logo.png', available: true },
        { id: 'paypal', name: 'PayPal', logo: '/images/paypal-logo.png', available: false }
      ];
    }
  }
}

// Export singleton
const paymentService = new PaymentService();
export default paymentService;
