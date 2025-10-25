import React, { useState } from 'react';
import { X, Send, AlertCircle, CheckCircle } from 'lucide-react';
import api from '../../utils/api';

/**
 * Modal de demande d'affiliation pour influenceurs
 *
 * Workflow:
 * 1. Influenceur clique "Générer Mon Lien" sur un produit
 * 2. Modal s'ouvre avec formulaire de demande
 * 3. Influenceur remplit ses motivations et stats
 * 4. Envoi de la demande au marchand
 * 5. Notification au marchand (Email + SMS + Dashboard)
 * 6. Attente de réponse (48h max)
 */
const RequestAffiliationModal = ({ isOpen, onClose, product, influencerProfile }) => {
  const [formData, setFormData] = useState({
    influencer_message: '',
    influencer_followers: influencerProfile?.audience_size || 0,
    influencer_engagement_rate: influencerProfile?.engagement_rate || 0,
    influencer_social_links: influencerProfile?.social_links || {}
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/affiliation-requests/request', {
        product_id: product.id,
        ...formData
      });

      if (response.data.success) {
        setSuccess(true);
        setTimeout(() => {
          onClose();
          // Rediriger vers la page "Mes Demandes"
          window.location.href = '/influencer/my-requests';
        }, 2000);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'envoi de la demande');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 rounded-t-2xl flex justify-between items-center">
          <h2 className="text-2xl font-bold">Demande d'Affiliation</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-6 py-4 flex items-center space-x-3">
            <CheckCircle size={24} />
            <div>
              <p className="font-semibold">Demande envoyée avec succès !</p>
              <p className="text-sm">Le marchand a 48h pour répondre. Vous serez notifié par email.</p>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 flex items-center space-x-3">
            <AlertCircle size={24} />
            <div>
              <p className="font-semibold">Erreur</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Product Info */}
        <div className="px-6 py-4 bg-gray-50 border-b">
          <div className="flex items-start space-x-4">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg flex items-center justify-center">
              {product.images && product.images[0] ? (
                <img
                  src={product.images[0]}
                  alt={product.name}
                  className="w-full h-full object-cover rounded-lg"
                />
              ) : (
                <span className="text-3xl">📦</span>
              )}
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900">{product.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{product.description?.substring(0, 100)}...</p>
              <div className="flex items-center space-x-4 mt-2">
                <span className="text-lg font-bold text-gray-900">
                  {product.price?.toLocaleString()} {product.currency || '€'}
                </span>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-semibold">
                  Commission: {product.commission_rate}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-6 space-y-6">
          {/* Message to Merchant */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pourquoi ce produit vous intéresse ? *
            </label>
            <textarea
              required
              value={formData.influencer_message}
              onChange={(e) => setFormData({ ...formData, influencer_message: e.target.value })}
              placeholder="Exemple: Ce produit correspond parfaitement à mon audience mode féminine 25-35 ans. Mes followers adorent les pièces élégantes comme celle-ci..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              rows="4"
              maxLength="500"
            />
            <div className="text-right text-xs text-gray-500 mt-1">
              {formData.influencer_message.length}/500 caractères
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre d'abonnés
              </label>
              <input
                type="number"
                value={formData.influencer_followers}
                onChange={(e) => setFormData({ ...formData, influencer_followers: parseInt(e.target.value) })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                min="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Taux d'engagement (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.influencer_engagement_rate}
                onChange={(e) => setFormData({ ...formData, influencer_engagement_rate: parseFloat(e.target.value) })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                min="0"
                max="100"
              />
            </div>
          </div>

          {/* Social Links */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Vos réseaux sociaux
            </label>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <span className="w-24 text-sm text-gray-600">📸 Instagram</span>
                <input
                  type="url"
                  placeholder="https://instagram.com/..."
                  value={formData.influencer_social_links?.instagram || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    influencer_social_links: { ...formData.influencer_social_links, instagram: e.target.value }
                  })}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div className="flex items-center space-x-3">
                <span className="w-24 text-sm text-gray-600">🎬 TikTok</span>
                <input
                  type="url"
                  placeholder="https://tiktok.com/@..."
                  value={formData.influencer_social_links?.tiktok || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    influencer_social_links: { ...formData.influencer_social_links, tiktok: e.target.value }
                  })}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div className="flex items-center space-x-3">
                <span className="w-24 text-sm text-gray-600">🐦 Twitter</span>
                <input
                  type="url"
                  placeholder="https://twitter.com/..."
                  value={formData.influencer_social_links?.twitter || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    influencer_social_links: { ...formData.influencer_social_links, twitter: e.target.value }
                  })}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
              <div className="text-sm text-blue-800">
                <p className="font-semibold mb-1">Processus de validation</p>
                <ul className="list-disc ml-4 space-y-1">
                  <li>Le marchand recevra une notification (Email + SMS + Dashboard)</li>
                  <li>Il consultera votre profil complet et vos statistiques</li>
                  <li>Il a 48 heures pour approuver ou refuser votre demande</li>
                  <li>Si approuvé : vous recevrez votre lien unique immédiatement</li>
                  <li>Si refusé : vous pourrez candidater à d'autres produits</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              disabled={loading || success}
            >
              {loading ? (
                <span>Envoi en cours...</span>
              ) : (
                <>
                  <Send size={20} />
                  <span>Envoyer la Demande</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RequestAffiliationModal;
