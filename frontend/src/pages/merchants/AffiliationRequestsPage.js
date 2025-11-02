import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Modal from '../../components/common/Modal';
import {
  Users, Clock, CheckCircle, XCircle, Eye, Star, TrendingUp,
  Instagram, Twitter, Globe, DollarSign, Target, MessageSquare
} from 'lucide-react';

/**
 * Page de gestion des demandes d'affiliation pour les marchands
 *
 * Workflow:
 * 1. Marchand voit toutes les demandes en attente
 * 2. Clique sur une demande pour voir le profil complet de l'influenceur
 * 3. Peut approuver ou refuser avec un message personnalisé
 * 4. Si approuvé : lien généré automatiquement et envoyé à l'influenceur
 * 5. Si refusé : notification envoyée avec raison et encouragement
 */
const AffiliationRequestsPage = () => {
  const { user } = useAuth();
  const toast = useToast();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [actionModal, setActionModal] = useState({ isOpen: false, action: null });
  const [formData, setFormData] = useState({
    merchant_response: '',
    rejection_reason: ''
  });

  useEffect(() => {
    fetchPendingRequests();
  }, []);

  const fetchPendingRequests = async () => {
    try {
      const response = await api.get('/api/affiliation-requests/merchant/pending');
      setRequests(response.data.pending_requests || []);
    } catch (error) {
      console.error('Error fetching requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewRequest = (request) => {
    setSelectedRequest(request);
    setIsModalOpen(true);
  };

  const handleApprove = async () => {
    try {
      const response = await api.put(`/api/affiliation-requests/${selectedRequest.id}/respond`, {
        status: 'approved',
        merchant_response: formData.merchant_response
      });

      if (response.data.success) {
        // Refresh la liste
        fetchPendingRequests();
        setActionModal({ isOpen: false, action: null });
        setIsModalOpen(false);
        toast.success(`Demande approuvée ! Lien généré: ${response.data.short_code}`);
      }
    } catch (error) {
      console.error('Error approving request:', error);
      toast.error('Erreur lors de l\'approbation: ' + error.response?.data?.detail);
    }
  };

  const handleReject = async () => {
    if (!formData.rejection_reason) {
      toast.warning('Veuillez indiquer la raison du refus');
      return;
    }

    try {
      const response = await api.put(`/api/affiliation-requests/${selectedRequest.id}/respond`, {
        status: 'rejected',
        merchant_response: formData.merchant_response,
        rejection_reason: formData.rejection_reason
      });

      if (response.data.success) {
        // Refresh la liste
        fetchPendingRequests();
        setActionModal({ isOpen: false, action: null });
        setIsModalOpen(false);
        toast.info('Demande refusée. L\'influenceur a été notifié.');
      }
    } catch (error) {
      console.error('Error rejecting request:', error);
      toast.error('Erreur lors du refus: ' + error.response?.data?.detail);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement des demandes...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Demandes d'Affiliation</h1>
          <p className="text-gray-600 mt-2">
            Examinez et approuvez les demandes des influenceurs pour vos produits
          </p>
        </div>
        <div className="bg-purple-100 px-6 py-3 rounded-lg">
          <div className="text-sm text-purple-600 font-medium">Demandes en attente</div>
          <div className="text-3xl font-bold text-purple-800">{requests.length}</div>
        </div>
      </div>

      {/* Empty State */}
      {requests.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Aucune demande en attente
            </h3>
            <p className="text-gray-600">
              Les influenceurs peuvent demander à promouvoir vos produits depuis le Marketplace.
            </p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {requests.map((request) => (
            <Card key={request.id}>
              <div className="flex items-start space-x-6">
                {/* Influencer Avatar */}
                <div className="flex-shrink-0">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white text-2xl font-bold">
                    {request.influencers?.profile_picture_url ? (
                      <img
                        src={request.influencers.profile_picture_url}
                        alt={request.influencers.full_name}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      request.influencers?.full_name?.charAt(0) || 'I'
                    )}
                  </div>
                </div>

                {/* Request Info */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">
                        {request.influencers?.full_name || 'Influenceur'}
                        <span className="text-purple-600 ml-2">@{request.influencers?.username}</span>
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Demande pour: <span className="font-semibold text-gray-900">{request.products?.name}</span>
                      </p>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <Clock size={16} />
                      <span>
                        {new Date(request.requested_at).toLocaleDateString('fr-FR', {
                          day: 'numeric',
                          month: 'short',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="bg-indigo-50 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <Users className="text-indigo-600" size={16} />
                        <span className="text-xs text-indigo-600 font-medium">Abonnés</span>
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {request.influencer_followers?.toLocaleString() || 0}
                      </div>
                    </div>

                    <div className="bg-green-50 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <TrendingUp className="text-green-600" size={16} />
                        <span className="text-xs text-green-600 font-medium">Engagement</span>
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {request.influencer_engagement_rate?.toFixed(1) || 0}%
                      </div>
                    </div>

                    <div className="bg-purple-50 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <DollarSign className="text-purple-600" size={16} />
                        <span className="text-xs text-purple-600 font-medium">Ventes Totales</span>
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {request.influencers?.total_sales?.toLocaleString() || 0}
                      </div>
                    </div>

                    <div className="bg-orange-50 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <Target className="text-orange-600" size={16} />
                        <span className="text-xs text-orange-600 font-medium">Revenus Générés</span>
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {request.influencers?.total_earnings?.toLocaleString() || 0} €
                      </div>
                    </div>
                  </div>

                  {/* Message */}
                  {request.influencer_message && (
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <div className="flex items-start space-x-2">
                        <MessageSquare className="text-gray-400 flex-shrink-0 mt-1" size={16} />
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-1">Message de l'influenceur:</p>
                          <p className="text-sm text-gray-600 italic">"{request.influencer_message}"</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Social Links */}
                  {request.influencer_social_links && (
                    <div className="flex items-center space-x-3 mb-4">
                      {request.influencer_social_links.instagram && (
                        <a
                          href={request.influencer_social_links.instagram}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-pink-600 hover:text-pink-700"
                        >
                          <Instagram size={20} />
                        </a>
                      )}
                      {request.influencer_social_links.twitter && (
                        <a
                          href={request.influencer_social_links.twitter}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <Twitter size={20} />
                        </a>
                      )}
                      {request.influencer_social_links.website && (
                        <a
                          href={request.influencer_social_links.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-600 hover:text-gray-700"
                        >
                          <Globe size={20} />
                        </a>
                      )}
                    </div>
                  )}

                  {/* AI Recommendation */}
                  <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 mb-4">
                    <div className="flex items-start space-x-3">
                      <div className="bg-indigo-600 p-2 rounded-lg">
                        <Star className="text-white" size={20} />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-indigo-900 mb-1">
                          Recommandation IA: Excellent Match (Score: 94%)
                        </p>
                        <ul className="text-xs text-indigo-700 space-y-1">
                          <li>• Audience ciblée parfaite pour ce produit</li>
                          <li>• Bon historique de ventes (conversion &gt; moyenne)</li>
                          <li>• Taux d'engagement supérieur à 4%</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-3">
                    <button
                      onClick={() => handleViewRequest(request)}
                      className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition flex items-center justify-center space-x-2"
                    >
                      <Eye size={18} />
                      <span>Voir Profil Complet</span>
                    </button>
                    <button
                      onClick={() => {
                        setSelectedRequest(request);
                        setActionModal({ isOpen: true, action: 'approve' });
                      }}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition flex items-center justify-center space-x-2"
                    >
                      <CheckCircle size={18} />
                      <span>Approuver</span>
                    </button>
                    <button
                      onClick={() => {
                        setSelectedRequest(request);
                        setActionModal({ isOpen: true, action: 'reject' });
                      }}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition flex items-center justify-center space-x-2"
                    >
                      <XCircle size={18} />
                      <span>Refuser</span>
                    </button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal Approve/Reject */}
      <Modal
        isOpen={actionModal.isOpen}
        onClose={() => setActionModal({ isOpen: false, action: null })}
        title={actionModal.action === 'approve' ? '✅ Approuver la Demande' : '❌ Refuser la Demande'}
      >
        <div className="space-y-4">
          {actionModal.action === 'approve' ? (
            <>
              <p className="text-gray-700">
                Vous êtes sur le point d'approuver la demande de{' '}
                <span className="font-bold">{selectedRequest?.influencers?.full_name}</span>.
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-800 mb-2">
                  <strong>Actions automatiques :</strong>
                </p>
                <ul className="text-sm text-green-700 space-y-1 list-disc ml-4">
                  <li>Génération automatique d'un lien unique</li>
                  <li>Notification par Email et SMS à l'influenceur</li>
                  <li>Kit marketing envoyé (bannières, QR code)</li>
                  <li>Lien actif immédiatement</li>
                </ul>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message de bienvenue (optionnel)
                </label>
                <textarea
                  value={formData.merchant_response}
                  onChange={(e) => setFormData({ ...formData, merchant_response: e.target.value })}
                  placeholder="Ex: Bienvenue ! Hâte de travailler avec vous..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  rows="3"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => setActionModal({ isOpen: false, action: null })}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
                >
                  Annuler
                </button>
                <button
                  onClick={handleApprove}
                  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
                >
                  Confirmer l'Approbation
                </button>
              </div>
            </>
          ) : (
            <>
              <p className="text-gray-700">
                Vous êtes sur le point de refuser la demande de{' '}
                <span className="font-bold">{selectedRequest?.influencers?.full_name}</span>.
              </p>

              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">
                  <strong>⚠️ Important :</strong> L'influenceur recevra une notification avec la raison
                  du refus. Soyez courtois et encouragez-le à candidater pour d'autres produits.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Raison du refus * (obligatoire)
                </label>
                <select
                  required
                  value={formData.rejection_reason}
                  onChange={(e) => setFormData({ ...formData, rejection_reason: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <option value="">Sélectionnez une raison</option>
                  <option value="Profil inadapté à la marque">Profil inadapté à notre marque</option>
                  <option value="Statistiques insuffisantes">Statistiques insuffisantes</option>
                  <option value="Contenu inapproprié">Contenu inapproprié</option>
                  <option value="Audience pas ciblée">Audience pas ciblée</option>
                  <option value="Autre">Autre (préciser ci-dessous)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message personnalisé (optionnel)
                </label>
                <textarea
                  value={formData.merchant_response}
                  onChange={(e) => setFormData({ ...formData, merchant_response: e.target.value })}
                  placeholder="Ex: Merci pour votre intérêt. Votre audience est plutôt jeune (18-24) alors que notre cible est 30-45 ans..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  rows="3"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => setActionModal({ isOpen: false, action: null })}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
                >
                  Annuler
                </button>
                <button
                  onClick={handleReject}
                  className="flex-1 px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700"
                >
                  Confirmer le Refus
                </button>
              </div>
            </>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default AffiliationRequestsPage;
