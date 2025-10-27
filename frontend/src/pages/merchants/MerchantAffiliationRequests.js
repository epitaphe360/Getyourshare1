import React, { useState, useEffect } from 'react';
import { useToast } from '../../context/ToastContext';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import api from '../../utils/api';
import {
  Users, CheckCircle, XCircle, Clock, TrendingUp,
  Mail, Instagram, AlertCircle, MessageSquare, Star,
  BarChart3, Package, Target
} from 'lucide-react';

const MerchantAffiliationRequests = () => {
  const toast = useToast();
  const [requests, setRequests] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState('pending_approval');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [merchantResponse, setMerchantResponse] = useState('');
  const [actionType, setActionType] = useState(''); // 'approve' or 'reject'

  useEffect(() => {
    fetchRequests();
    fetchStats();
  }, [filterStatus]);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const url = filterStatus === 'all' 
        ? '/api/merchant/affiliation-requests'
        : `/api/merchant/affiliation-requests?status=${filterStatus}`;
      
      const response = await api.get(url);
      setRequests(response.data || []);
    } catch (error) {
      console.error('Erreur lors du chargement des demandes:', error);
      toast.error('Impossible de charger les demandes');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/merchant/affiliation-requests/stats');
      setStats(response.data || {});
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    }
  };

  const openModal = (request, type) => {
    setSelectedRequest(request);
    setActionType(type);
    setMerchantResponse('');
    setIsModalOpen(true);
  };

  const handleApprove = async () => {
    if (!selectedRequest) return;

    try {
      setLoading(true);
      await api.post(`/api/merchant/affiliation-requests/${selectedRequest.id}/approve`, {
        merchant_response: merchantResponse
      });

      toast.success('✅ Demande approuvée ! Le lien de tracking a été créé automatiquement.');
      setIsModalOpen(false);
      setSelectedRequest(null);
      setMerchantResponse('');
      
      // Recharger les données
      await fetchRequests();
      await fetchStats();
    } catch (error) {
      console.error('Erreur lors de l\'approbation:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'approbation');
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedRequest) return;

    if (!merchantResponse.trim()) {
      toast.error('Veuillez fournir une raison pour le refus');
      return;
    }

    try {
      setLoading(true);
      await api.post(`/api/merchant/affiliation-requests/${selectedRequest.id}/reject`, {
        merchant_response: merchantResponse
      });

      toast.success('Demande refusée.');
      setIsModalOpen(false);
      setSelectedRequest(null);
      setMerchantResponse('');
      
      // Recharger les données
      await fetchRequests();
      await fetchStats();
    } catch (error) {
      console.error('Erreur lors du refus:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors du refus');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending_approval: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: '⏳', label: 'En attente' },
      active: { bg: 'bg-green-100', text: 'text-green-800', icon: '✅', label: 'Approuvée' },
      rejected: { bg: 'bg-red-100', text: 'text-red-800', icon: '❌', label: 'Refusée' },
      cancelled: { bg: 'bg-gray-100', text: 'text-gray-600', icon: '✖', label: 'Annulée' },
      inactive: { bg: 'bg-gray-100', text: 'text-gray-800', icon: '○', label: 'Inactive' },
    };
    const badge = badges[status] || badges.pending_approval;
    
    return (
      <span className={`${badge.bg} ${badge.text} px-3 py-1 rounded-full text-xs font-medium inline-flex items-center space-x-1`}>
        <span>{badge.icon}</span>
        <span>{badge.label}</span>
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Demandes d'Affiliation</h1>
            <p className="text-purple-100">
              Examinez et approuvez les demandes des influenceurs
            </p>
          </div>
          <div className="bg-white/20 p-4 rounded-lg backdrop-blur-sm">
            <Users size={40} className="text-white" />
          </div>
        </div>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Demandes</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total_requests || 0}</p>
            </div>
            <BarChart3 className="text-blue-500" size={32} />
          </div>
        </Card>

        <Card className="border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">En Attente</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.pending_requests || 0}</p>
            </div>
            <Clock className="text-yellow-500" size={32} />
          </div>
        </Card>

        <Card className="border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Approuvées</p>
              <p className="text-3xl font-bold text-green-600">{stats.approved_requests || 0}</p>
            </div>
            <CheckCircle className="text-green-500" size={32} />
          </div>
        </Card>

        <Card className="border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Taux d'Approbation</p>
              <p className="text-3xl font-bold text-purple-600">{stats.approval_rate || 0}%</p>
            </div>
            <TrendingUp className="text-purple-500" size={32} />
          </div>
        </Card>
      </div>

      {/* Filtres */}
      <Card>
        <div className="flex space-x-2">
          {[
            { value: 'pending_approval', label: 'En Attente', icon: Clock },
            { value: 'active', label: 'Approuvées', icon: CheckCircle },
            { value: 'rejected', label: 'Refusées', icon: XCircle },
            { value: 'cancelled', label: 'Annulées', icon: AlertCircle },
            { value: 'all', label: 'Toutes', icon: BarChart3 }
          ].map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              onClick={() => setFilterStatus(value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition flex items-center space-x-2 ${
                filterStatus === value
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Icon size={16} />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </Card>

      {/* Liste des Demandes */}
      <div className="space-y-4">
        {loading && requests.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement des demandes...</p>
            </div>
          </Card>
        ) : requests.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <AlertCircle className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600 text-lg">Aucune demande pour le moment</p>
              <p className="text-gray-500 text-sm mt-2">
                Les demandes d'affiliation des influenceurs apparaîtront ici
              </p>
            </div>
          </Card>
        ) : (
          requests.map((request) => (
            <Card key={request.id} className="hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  {/* Avatar Influenceur */}
                  <div className="flex-shrink-0">
                    {request.influencer_avatar ? (
                      <img
                        src={request.influencer_avatar}
                        alt={request.influencer_name}
                        className="w-16 h-16 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-400 to-indigo-500 flex items-center justify-center">
                        <Users className="text-white" size={32} />
                      </div>
                    )}
                  </div>

                  {/* Informations */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-bold text-gray-900">
                        {request.influencer_name || 'Influenceur'}
                      </h3>
                      {getStatusBadge(request.status)}
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center space-x-1">
                        <Mail size={14} />
                        <span>{request.influencer_email}</span>
                      </div>
                      {request.followers_count && (
                        <div className="flex items-center space-x-1">
                          <Users size={14} />
                          <span>{request.followers_count.toLocaleString()} followers</span>
                        </div>
                      )}
                      {request.engagement_rate && (
                        <div className="flex items-center space-x-1">
                          <Target size={14} />
                          <span>{request.engagement_rate}% engagement</span>
                        </div>
                      )}
                    </div>

                    {/* Produit */}
                    <div className="bg-gray-50 p-3 rounded-lg mb-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <Package size={16} className="text-indigo-600" />
                        <span className="font-semibold text-gray-900">{request.product_name}</span>
                      </div>
                      <p className="text-sm text-gray-600">
                        Commission: {request.commission_rate}% • Prix: {request.product_price}€
                      </p>
                    </div>

                    {/* Message */}
                    <div className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded">
                      <div className="flex items-start space-x-2">
                        <MessageSquare className="text-blue-600 mt-0.5 flex-shrink-0" size={16} />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-blue-900 mb-1">Message:</p>
                          <p className="text-sm text-blue-800">{request.message}</p>
                        </div>
                      </div>
                    </div>

                    {/* Réponse du marchand (si existe) */}
                    {request.merchant_response && (
                      <div className={`mt-3 p-3 rounded border-l-4 ${
                        request.status === 'active' 
                          ? 'bg-green-50 border-green-500' 
                          : 'bg-red-50 border-red-500'
                      }`}>
                        <p className="text-sm font-medium text-gray-900 mb-1">Votre réponse:</p>
                        <p className="text-sm text-gray-700">{request.merchant_response}</p>
                        {request.reviewed_at && (
                          <p className="text-xs text-gray-500 mt-1">
                            Répondu le {new Date(request.reviewed_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    )}

                    <p className="text-xs text-gray-500 mt-3">
                      Demandé le {new Date(request.created_at).toLocaleDateString()} à {new Date(request.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>

                {/* Actions (seulement si en attente) */}
                {request.status === 'pending_approval' && (
                  <div className="flex flex-col space-y-2 ml-4">
                    <Button
                      onClick={() => openModal(request, 'approve')}
                      className="bg-green-600 hover:bg-green-700 flex items-center space-x-2"
                    >
                      <CheckCircle size={18} />
                      <span>Approuver</span>
                    </Button>
                    <Button
                      onClick={() => openModal(request, 'reject')}
                      variant="secondary"
                      className="bg-red-100 text-red-700 hover:bg-red-200 flex items-center space-x-2"
                    >
                      <XCircle size={18} />
                      <span>Refuser</span>
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Modal Approbation/Refus */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedRequest(null);
          setMerchantResponse('');
        }}
        title={actionType === 'approve' ? 'Approuver la Demande' : 'Refuser la Demande'}
        size="md"
      >
        {selectedRequest && (
          <div className="space-y-4">
            <div className={`p-4 rounded-lg border-l-4 ${
              actionType === 'approve' 
                ? 'bg-green-50 border-green-500' 
                : 'bg-red-50 border-red-500'
            }`}>
              <p className="font-semibold text-gray-900 mb-2">
                {selectedRequest.influencer_name}
              </p>
              <p className="text-sm text-gray-700 mb-1">
                Produit: {selectedRequest.product_name}
              </p>
              <p className="text-sm text-gray-600">
                {selectedRequest.message}
              </p>
            </div>

            {actionType === 'approve' ? (
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="text-blue-600 mt-0.5" size={18} />
                  <div>
                    <p className="text-sm font-medium text-blue-900 mb-1">
                      Action automatique
                    </p>
                    <p className="text-sm text-blue-800">
                      En approuvant cette demande, un lien de tracking sera automatiquement créé pour cet influenceur.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="text-yellow-600 mt-0.5" size={18} />
                  <div>
                    <p className="text-sm font-medium text-yellow-900 mb-1">
                      Raison requise
                    </p>
                    <p className="text-sm text-yellow-800">
                      L'influenceur ne pourra pas redemander ce produit avant 30 jours.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message {actionType === 'reject' ? '(requis)' : '(optionnel)'}
              </label>
              <textarea
                value={merchantResponse}
                onChange={(e) => setMerchantResponse(e.target.value)}
                placeholder={
                  actionType === 'approve'
                    ? 'Bienvenue dans notre programme d\'affiliation !'
                    : 'Expliquez pourquoi vous refusez cette demande...'
                }
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <Button
                variant="secondary"
                onClick={() => {
                  setIsModalOpen(false);
                  setSelectedRequest(null);
                  setMerchantResponse('');
                }}
                disabled={loading}
              >
                Annuler
              </Button>
              <Button
                onClick={actionType === 'approve' ? handleApprove : handleReject}
                disabled={loading || (actionType === 'reject' && !merchantResponse.trim())}
                className={
                  actionType === 'approve'
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-red-600 hover:bg-red-700'
                }
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Traitement...
                  </>
                ) : actionType === 'approve' ? (
                  <>
                    <CheckCircle size={18} className="mr-2" />
                    Confirmer l'Approbation
                  </>
                ) : (
                  <>
                    <XCircle size={18} className="mr-2" />
                    Confirmer le Refus
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default MerchantAffiliationRequests;
