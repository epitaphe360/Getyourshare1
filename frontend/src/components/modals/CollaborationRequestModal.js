import React, { useState } from 'react';
import { X, Send, Package, TrendingUp, DollarSign, Calendar } from 'lucide-react';
import api from '../../utils/api';

const CollaborationRequestModal = ({ isOpen, onClose, product, influencer, onSuccess }) => {
  const [formData, setFormData] = useState({
    commission_rate: 15,
    message: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/collaborations/requests', {
        influencer_id: influencer.id,
        product_id: product.id,
        commission_rate: parseFloat(formData.commission_rate),
        message: formData.message
      });

      if (response.data.success) {
        onSuccess && onSuccess(response.data);
        onClose();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'envoi de la demande');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold mb-2">Demande de Collaboration</h2>
              <p className="text-indigo-100">Proposez une collaboration à {influencer.first_name}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-full p-2 transition"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Product Info */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Package size={20} className="text-indigo-600" />
              <h3 className="font-semibold text-gray-900">Produit à promouvoir</h3>
            </div>
            <div className="flex gap-4">
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-20 h-20 object-cover rounded-lg"
                />
              )}
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{product.name}</h4>
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                  {product.description}
                </p>
                <p className="text-lg font-bold text-indigo-600 mt-2">
                  {product.price} MAD
                </p>
              </div>
            </div>
          </div>

          {/* Influencer Info */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp size={20} className="text-indigo-600" />
              <h3 className="font-semibold text-gray-900">Influenceur</h3>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                {influencer.first_name?.[0]}{influencer.last_name?.[0]}
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  {influencer.first_name} {influencer.last_name}
                </p>
                <p className="text-sm text-gray-600">{influencer.email}</p>
                {influencer.username && (
                  <p className="text-sm text-gray-500">@{influencer.username}</p>
                )}
              </div>
            </div>
          </div>

          {/* Commission Rate */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <DollarSign size={18} className="text-indigo-600" />
              Taux de commission (%)
            </label>
            <input
              type="number"
              min="5"
              max="50"
              step="0.5"
              value={formData.commission_rate}
              onChange={(e) => setFormData({ ...formData, commission_rate: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
            <div className="mt-2 flex items-center justify-between text-sm">
              <span className="text-gray-600">
                Commission par vente: <strong>{((product.price * formData.commission_rate) / 100).toFixed(2)} MAD</strong>
              </span>
              <span className="text-indigo-600 font-medium">
                {formData.commission_rate}% du prix
              </span>
            </div>
          </div>

          {/* Duration Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-blue-700 mb-2">
              <Calendar size={18} />
              <span className="font-medium">Durée de la collaboration</span>
            </div>
            <p className="text-sm text-blue-600">
              12 mois renouvelables automatiquement
            </p>
          </div>

          {/* Message */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Send size={18} className="text-indigo-600" />
              Message personnalisé (optionnel)
            </label>
            <textarea
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              rows="4"
              placeholder="Expliquez pourquoi vous souhaitez collaborer avec cet influenceur..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">
              Ce message sera visible par l'influenceur
            </p>
          </div>

          {/* Important Info */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-medium text-yellow-800 mb-2">⚠️ Points importants</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• L'influenceur aura 30 jours pour répondre</li>
              <li>• Il pourra accepter, refuser ou faire une contre-offre</li>
              <li>• Un contrat devra être signé avant la génération du lien d'affiliation</li>
              <li>• La commission sera versée après chaque vente validée</li>
            </ul>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition font-medium shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Envoi...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Send size={18} />
                  Envoyer la demande
                </span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CollaborationRequestModal;
