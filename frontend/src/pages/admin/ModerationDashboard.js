import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import {
  Shield, AlertTriangle, CheckCircle, XCircle, Eye, Filter,
  Clock, TrendingUp, Package, User, Calendar, MessageSquare,
  AlertOctagon, Info, RefreshCw, Search, ChevronRight
} from 'lucide-react';

const ModerationDashboard = () => {
  const navigate = useNavigate();
  const toast = useToast();
  
  const [pendingProducts, setPendingProducts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterRisk, setFilterRisk] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [reviewComment, setReviewComment] = useState('');
  const [processingIds, setProcessingIds] = useState(new Set());

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [filterRisk]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch pending products
      const params = filterRisk !== 'all' ? `?risk_level=${filterRisk}` : '';
      const pendingRes = await api.get(`/api/admin/moderation/pending${params}`);
      setPendingProducts(pendingRes.data.data || []);
      
      // Fetch stats
      const statsRes = await api.get('/api/admin/moderation/stats?period=today');
      setStats(statsRes.data);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching moderation data:', error);
      toast?.error('Erreur lors du chargement des données');
      setLoading(false);
    }
  };

  const handleReview = async (moderationId, decision) => {
    if (processingIds.has(moderationId)) return;
    
    try {
      setProcessingIds(prev => new Set(prev).add(moderationId));
      
      await api.post('/api/admin/moderation/review', {
        moderation_id: moderationId,
        decision,
        comment: reviewComment || `Produit ${decision === 'approve' ? 'approuvé' : 'rejeté'} par admin`
      });
      
      toast?.success(`Produit ${decision === 'approve' ? 'approuvé' : 'rejeté'} avec succès`);
      setReviewComment('');
      setShowDetailsModal(false);
      fetchData();
    } catch (error) {
      console.error('Error reviewing product:', error);
      toast?.error(error.response?.data?.detail || 'Erreur lors de la révision');
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(moderationId);
        return newSet;
      });
    }
  };

  const getRiskBadge = (riskLevel) => {
    const styles = {
      critical: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-green-100 text-green-800 border-green-300'
    };
    
    const icons = {
      critical: <AlertOctagon className="w-4 h-4" />,
      high: <AlertTriangle className="w-4 h-4" />,
      medium: <Info className="w-4 h-4" />,
      low: <CheckCircle className="w-4 h-4" />
    };
    
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border ${styles[riskLevel] || styles.low}`}>
        {icons[riskLevel]}
        {riskLevel?.toUpperCase()}
      </span>
    );
  };

  const getConfidenceBadge = (confidence) => {
    const percentage = (confidence * 100).toFixed(0);
    const color = confidence > 0.8 ? 'green' : confidence > 0.6 ? 'yellow' : 'red';
    const styles = {
      green: 'bg-green-100 text-green-800',
      yellow: 'bg-yellow-100 text-yellow-800',
      red: 'bg-red-100 text-red-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[color]}`}>
        {percentage}% confiance
      </span>
    );
  };

  const filteredProducts = pendingProducts.filter(product =>
    product.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.merchant_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Shield className="w-8 h-8 text-blue-600" />
            Modération IA des Produits
          </h1>
          <p className="text-gray-600 mt-1">
            Validation automatique des produits avec intelligence artificielle
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Actualiser
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 font-medium">Total Aujourd'hui</p>
                <p className="text-3xl font-bold text-blue-900 mt-1">{stats.total || 0}</p>
              </div>
              <Package className="w-12 h-12 text-blue-400 opacity-50" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-yellow-600 font-medium">En Attente</p>
                <p className="text-3xl font-bold text-yellow-900 mt-1">{stats.pending || 0}</p>
              </div>
              <Clock className="w-12 h-12 text-yellow-400 opacity-50" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600 font-medium">Approuvés</p>
                <p className="text-3xl font-bold text-green-900 mt-1">{stats.approved || 0}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-400 opacity-50" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-red-600 font-medium">Rejetés</p>
                <p className="text-3xl font-bold text-red-900 mt-1">{stats.rejected || 0}</p>
              </div>
              <XCircle className="w-12 h-12 text-red-400 opacity-50" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 font-medium">Taux Approbation</p>
                <p className="text-3xl font-bold text-purple-900 mt-1">
                  {stats.approval_rate ? (stats.approval_rate * 100).toFixed(0) : 0}%
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-400 opacity-50" />
            </div>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher un produit ou merchant..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => setFilterRisk('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filterRisk === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Tous
            </button>
            <button
              onClick={() => setFilterRisk('critical')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filterRisk === 'critical'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🔴 Critical
            </button>
            <button
              onClick={() => setFilterRisk('high')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filterRisk === 'high'
                  ? 'bg-orange-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🟠 High
            </button>
            <button
              onClick={() => setFilterRisk('medium')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filterRisk === 'medium'
                  ? 'bg-yellow-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🟡 Medium
            </button>
            <button
              onClick={() => setFilterRisk('low')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filterRisk === 'low'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🟢 Low
            </button>
          </div>
        </div>
      </Card>

      {/* Products List */}
      <Card>
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Produits en Attente ({filteredProducts.length})
          </h2>

          {filteredProducts.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <p className="text-xl font-semibold text-gray-700">Aucun produit en attente</p>
              <p className="text-gray-500 mt-2">Tous les produits ont été traités ✨</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start gap-4">
                    {/* Product Image */}
                    <div className="w-20 h-20 bg-gray-100 rounded-lg flex-shrink-0 overflow-hidden">
                      {product.product_images && product.product_images[0] ? (
                        <img
                          src={product.product_images[0]}
                          alt={product.product_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <Package className="w-full h-full p-4 text-gray-400" />
                      )}
                    </div>

                    {/* Product Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-1">
                            {product.product_name}
                          </h3>
                          <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                            {product.product_description}
                          </p>
                          
                          <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                            <span className="flex items-center gap-1">
                              <User className="w-4 h-4" />
                              {product.merchant_name}
                            </span>
                            <span className="flex items-center gap-1">
                              <Package className="w-4 h-4" />
                              {product.product_category}
                            </span>
                            <span className="flex items-center gap-1 font-semibold text-gray-700">
                              {product.product_price?.toFixed(2)} MAD
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {product.hours_pending ? `${product.hours_pending.toFixed(1)}h` : 'Récent'}
                            </span>
                          </div>
                        </div>

                        <div className="flex flex-col items-end gap-2">
                          {getRiskBadge(product.ai_risk_level)}
                          {getConfidenceBadge(product.ai_confidence)}
                        </div>
                      </div>

                      {/* AI Analysis */}
                      {product.ai_flags && product.ai_flags.length > 0 && (
                        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                          <p className="text-sm font-semibold text-red-800 mb-1 flex items-center gap-1">
                            <AlertTriangle className="w-4 h-4" />
                            Drapeaux Détectés
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {product.ai_flags.map((flag, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full"
                              >
                                {flag}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {product.ai_reason && (
                        <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <p className="text-sm text-yellow-800">
                            <strong>Analyse IA:</strong> {product.ai_reason}
                          </p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="mt-4 flex items-center gap-3">
                        <button
                          onClick={() => {
                            setSelectedProduct(product);
                            setShowDetailsModal(true);
                          }}
                          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                          Détails
                        </button>

                        <button
                          onClick={() => handleReview(product.id, 'approve')}
                          disabled={processingIds.has(product.id)}
                          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                        >
                          <CheckCircle className="w-4 h-4" />
                          Approuver
                        </button>

                        <button
                          onClick={() => handleReview(product.id, 'reject')}
                          disabled={processingIds.has(product.id)}
                          className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                        >
                          <XCircle className="w-4 h-4" />
                          Rejeter
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Details Modal */}
      {showDetailsModal && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-2xl font-bold text-gray-900">Détails du Produit</h3>
              <button
                onClick={() => {
                  setShowDetailsModal(false);
                  setReviewComment('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Product Details */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Informations Produit</h4>
                <div className="space-y-2 text-sm">
                  <p><strong>Nom:</strong> {selectedProduct.product_name}</p>
                  <p><strong>Description:</strong> {selectedProduct.product_description}</p>
                  <p><strong>Catégorie:</strong> {selectedProduct.product_category}</p>
                  <p><strong>Prix:</strong> {selectedProduct.product_price} MAD</p>
                  <p><strong>Merchant:</strong> {selectedProduct.merchant_name}</p>
                  <p><strong>Email Merchant:</strong> {selectedProduct.merchant_email}</p>
                </div>
              </div>

              {/* AI Analysis */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Analyse IA</h4>
                <div className="space-y-3">
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">Niveau de Risque:</span>
                    {getRiskBadge(selectedProduct.ai_risk_level)}
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">Confiance IA:</span>
                    {getConfidenceBadge(selectedProduct.ai_confidence)}
                  </div>
                  {selectedProduct.ai_flags && selectedProduct.ai_flags.length > 0 && (
                    <div>
                      <span className="text-sm text-gray-600 block mb-2">Drapeaux:</span>
                      <div className="flex flex-wrap gap-2">
                        {selectedProduct.ai_flags.map((flag, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-full"
                          >
                            {flag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {selectedProduct.ai_reason && (
                    <div>
                      <span className="text-sm text-gray-600 block mb-1">Raison:</span>
                      <p className="text-sm text-gray-800 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                        {selectedProduct.ai_reason}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Review Comment */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Commentaire (optionnel)
                </label>
                <textarea
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  rows="3"
                  placeholder="Ajoutez un commentaire pour le merchant..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => handleReview(selectedProduct.id, 'approve')}
                  disabled={processingIds.has(selectedProduct.id)}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-semibold"
                >
                  <CheckCircle className="w-5 h-5" />
                  Approuver le Produit
                </button>

                <button
                  onClick={() => handleReview(selectedProduct.id, 'reject')}
                  disabled={processingIds.has(selectedProduct.id)}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 font-semibold"
                >
                  <XCircle className="w-5 h-5" />
                  Rejeter le Produit
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModerationDashboard;
