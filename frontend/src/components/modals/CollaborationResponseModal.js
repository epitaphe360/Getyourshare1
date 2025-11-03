import React, { useState } from 'react';
import { X, Package, Percent, MessageSquare, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import api from '../../utils/api';
import ContractModal from './ContractModal';

const CollaborationResponseModal = ({ isOpen, onClose, request, onRespond }) => {
  const [action, setAction] = useState(null); // 'accept', 'reject', 'counter'
  const [counterCommission, setCounterCommission] = useState(request?.proposed_commission || 15);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showContract, setShowContract] = useState(false);

  if (!isOpen || !request) return null;

  const handleAccept = () => {
    setAction('accept');
    setShowContract(true);
  };

  const handleReject = async () => {
    if (!message.trim()) {
      setError('Veuillez fournir une raison de refus');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.put(`/api/collaborations/requests/${request.id}/reject`, {
        message: message.trim()
      });

      onRespond && onRespond({ status: 'rejected' });
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du refus');
    } finally {
      setLoading(false);
    }
  };

  const handleCounterOffer = async () => {
    if (counterCommission < 5 || counterCommission > 50) {
      setError('La commission doit être entre 5% et 50%');
      return;
    }

    if (!message.trim()) {
      setError('Veuillez justifier votre contre-proposition');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.put(`/api/collaborations/requests/${request.id}/counter-offer`, {
        counter_commission: counterCommission,
        message: message.trim()
      });

      onRespond && onRespond({ status: 'counter_offer', counter_commission: counterCommission });
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la contre-proposition');
    } finally {
      setLoading(false);
    }
  };

  const handleContractSigned = async (signedData) => {
    onRespond && onRespond({ status: 'active', ...signedData });
    onClose();
  };

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6 text-white">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold mb-2">Demande de Collaboration</h2>
                <p className="text-purple-100">
                  De: <span className="font-semibold">{request.merchant_name}</span>
                </p>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:bg-white/20 rounded-full p-2 transition"
              >
                <X size={24} />
              </button>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {/* Request Details */}
            <div className="space-y-4">
              {/* Products */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Package size={20} className="text-indigo-600" />
                  Produits concernés ({request.products?.length || 0})
                </h3>
                <div className="grid grid-cols-1 gap-3">
                  {request.products?.map((product) => (
                    <div
                      key={product.id}
                      className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:border-indigo-300 transition"
                    >
                      {product.image_url && (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="w-16 h-16 object-cover rounded"
                        />
                      )}
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{product.name}</p>
                        <p className="text-sm text-gray-600">{product.price} DH</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Commission */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Percent size={20} className="text-green-600" />
                  Commission proposée
                </h3>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-green-600">
                    {request.proposed_commission}%
                  </span>
                  <span className="text-sm text-gray-600">par vente</span>
                </div>
              </div>

              {/* Message from Merchant */}
              {request.message && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <MessageSquare size={20} className="text-blue-600" />
                    Message du marchand
                  </h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{request.message}</p>
                </div>
              )}
            </div>

            {/* Action Selection */}
            {!action && (
              <div className="space-y-3 pt-4 border-t">
                <p className="text-sm font-medium text-gray-700 mb-3">
                  Que souhaitez-vous faire ?
                </p>

                <button
                  onClick={handleAccept}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
                >
                  <CheckCircle size={20} />
                  Accepter la collaboration
                </button>

                <button
                  onClick={() => setAction('counter')}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition font-medium"
                >
                  <TrendingUp size={20} />
                  Faire une contre-proposition
                </button>

                <button
                  onClick={() => setAction('reject')}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
                >
                  <XCircle size={20} />
                  Refuser la demande
                </button>
              </div>
            )}

            {/* Counter Offer Form */}
            {action === 'counter' && (
              <div className="space-y-4 pt-4 border-t">
                <h3 className="font-semibold text-gray-900">Contre-proposition</h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nouvelle commission (%)
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="5"
                      max="50"
                      value={counterCommission}
                      onChange={(e) => setCounterCommission(Number(e.target.value))}
                      className="flex-1"
                    />
                    <span className="text-2xl font-bold text-indigo-600 w-20 text-right">
                      {counterCommission}%
                    </span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>5%</span>
                    <span>50%</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Justification *
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    rows={4}
                    placeholder="Expliquez pourquoi vous proposez cette commission..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                    required
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setAction(null)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                  >
                    Retour
                  </button>
                  <button
                    onClick={handleCounterOffer}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition disabled:opacity-50"
                  >
                    {loading ? 'Envoi...' : 'Envoyer la contre-proposition'}
                  </button>
                </div>
              </div>
            )}

            {/* Reject Form */}
            {action === 'reject' && (
              <div className="space-y-4 pt-4 border-t">
                <h3 className="font-semibold text-gray-900">Motif du refus</h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message au marchand *
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    rows={4}
                    placeholder="Expliquez pourquoi vous refusez cette collaboration..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                    required
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setAction(null)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                  >
                    Retour
                  </button>
                  <button
                    onClick={handleReject}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50"
                  >
                    {loading ? 'Envoi...' : 'Confirmer le refus'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Contract Modal */}
      <ContractModal
        isOpen={showContract}
        onClose={() => setShowContract(false)}
        requestId={request.id}
        userRole="influencer"
        onSigned={handleContractSigned}
      />
    </>
  );
};

export default CollaborationResponseModal;
