import React, { useState, useEffect } from 'react';
import { useToast } from '../context/ToastContext';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Table from '../components/common/Table';
import Modal from '../components/common/Modal';
import api from '../utils/api';
import { 
  Plus, Copy, Link as LinkIcon, TrendingUp, 
  Eye, MousePointer, Zap, BarChart3, Activity, Clock,
  CheckCircle, AlertCircle, ArrowUpRight, Sparkles,
  Share2, Target
} from 'lucide-react';

const TrackingLinks = () => {
  const toast = useToast();
  const [links, setLinks] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const [animatedStats, setAnimatedStats] = useState({
    totalClicks: 0,
    totalConversions: 0,
    totalRevenue: 0,
  });
  
  const [realtimeActivity, setRealtimeActivity] = useState([]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedLink, setSelectedLink] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedProduct, setSelectedProduct] = useState('');
  const [requestMessage, setRequestMessage] = useState('');
  const [pendingRequests, setPendingRequests] = useState([]);

  // Charger les liens de tracking depuis l'API
  useEffect(() => {
    fetchTrackingLinks();
    fetchProducts();
    fetchAffiliationRequests();
  }, []);

  const fetchTrackingLinks = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/influencer/tracking-links');
      setLinks(response.data || []);
    } catch (error) {
      console.error('Erreur lors du chargement des liens:', error);
      toast.error('Impossible de charger les liens de tracking');
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get('/api/products');
      // S'assurer que response.data est un tableau
      const productsData = Array.isArray(response.data) ? response.data : [];
      setProducts(productsData);
    } catch (error) {
      console.error('Erreur lors du chargement des produits:', error);
      setProducts([]); // Toujours définir un tableau vide en cas d'erreur
    }
  };

  const fetchAffiliationRequests = async () => {
    try {
      // Charger toutes les demandes d'affiliation (tous statuts)
      const [pendingRes, activeRes, rejectedRes, cancelledRes] = await Promise.all([
        api.get('/api/influencer/affiliation-requests?status=pending_approval'),
        api.get('/api/influencer/affiliation-requests?status=active'),
        api.get('/api/influencer/affiliation-requests?status=rejected'),
        api.get('/api/influencer/affiliation-requests?status=cancelled')
      ]);

      const allRequests = [
        ...(pendingRes.data || []),
        ...(activeRes.data || []),
        ...(rejectedRes.data || []),
        ...(cancelledRes.data || [])
      ];

      setPendingRequests(allRequests);
    } catch (error) {
      console.error('Erreur lors du chargement des demandes:', error);
      setPendingRequests([]);
    }
  };

  // Animation des statistiques au chargement
  useEffect(() => {
    const totalClicks = links.reduce((sum, l) => sum + l.clicks, 0);
    const totalConversions = links.reduce((sum, l) => sum + l.conversions, 0);
    const totalRevenue = links.reduce((sum, l) => sum + (l.revenue || 0), 0);

    // Animation progressive
    let clicksProgress = 0;
    let conversionsProgress = 0;
    let revenueProgress = 0;

    const interval = setInterval(() => {
      if (clicksProgress < totalClicks) {
        clicksProgress += Math.ceil(totalClicks / 50);
        if (clicksProgress > totalClicks) clicksProgress = totalClicks;
      }
      if (conversionsProgress < totalConversions) {
        conversionsProgress += Math.ceil(totalConversions / 50);
        if (conversionsProgress > totalConversions) conversionsProgress = totalConversions;
      }
      if (revenueProgress < totalRevenue) {
        revenueProgress += Math.ceil(totalRevenue / 50);
        if (revenueProgress > totalRevenue) revenueProgress = totalRevenue;
      }

      setAnimatedStats({
        totalClicks: clicksProgress,
        totalConversions: conversionsProgress,
        totalRevenue: revenueProgress,
      });

      if (clicksProgress >= totalClicks && conversionsProgress >= totalConversions && revenueProgress >= totalRevenue) {
        clearInterval(interval);
      }
    }, 20);

    return () => clearInterval(interval);
  }, [links]);

  // Simulation d'activité en temps réel
  useEffect(() => {
    const activities = [
      { icon: '👀', text: 'Nouveau clic sur', link: 'Campagne Été 2024', time: 'Il y a 2s', color: 'text-blue-500' },
      { icon: '✅', text: 'Conversion sur', link: 'Promo Black Friday', time: 'Il y a 5s', color: 'text-green-500' },
      { icon: '🔗', text: 'Lien partagé:', link: 'Collection Printemps', time: 'Il y a 8s', color: 'text-purple-500' },
    ];

    setRealtimeActivity(activities);

    // Ajouter une nouvelle activité toutes les 5 secondes (seulement si des liens existent)
    if (links.length === 0) return;

    const interval = setInterval(() => {
      const randomLink = links[Math.floor(Math.random() * links.length)];
      const randomActivity = [
        { icon: '👀', text: 'Nouveau clic sur', color: 'text-blue-500' },
        { icon: '✅', text: 'Conversion sur', color: 'text-green-500' },
        { icon: '📊', text: 'Vue détaillée:', color: 'text-indigo-500' },
      ][Math.floor(Math.random() * 3)];

      setRealtimeActivity(prev => [
        { ...randomActivity, link: randomLink?.name || 'Lien inconnu', time: 'À l\'instant', color: randomActivity.color },
        ...prev.slice(0, 4)
      ]);
    }, 5000);

    return () => clearInterval(interval);
  }, [links]);

  const handleCopy = async (link) => {
    try {
      await navigator.clipboard.writeText(link);
      toast.success('Lien copié dans le presse-papier!');
    } catch (error) {
      toast.error('Erreur lors de la copie du lien');
    }
  };

  const handleGenerate = async () => {
    if (!selectedProduct) {
      toast.error('Veuillez sélectionner un produit');
      return;
    }

    if (!requestMessage.trim()) {
      toast.error('Veuillez ajouter un message au marchand');
      return;
    }

    try {
      setLoading(true);
      
      // Créer une demande d'affiliation au lieu de générer directement
      const response = await api.post('/api/affiliation/request', {
        product_id: selectedProduct,
        message: requestMessage,
        stats: {
          // TODO: Récupérer les vraies stats du profil utilisateur
          followers: 0,
          engagement_rate: 0,
          platforms: []
        }
      });

      if (response.data) {
        toast.success('🎉 Demande d\'affiliation envoyée ! Le marchand va l\'examiner.');
        setIsModalOpen(false);
        setSelectedProduct('');
        setRequestMessage('');
        
        // Recharger les demandes
        await fetchAffiliationRequests();
      }
    } catch (error) {
      console.error('Erreur lors de la demande:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'envoi de la demande');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      header: 'Lien',
      accessor: 'name',
      render: (row) => (
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-br from-indigo-100 to-purple-100 p-2 rounded-lg">
            <LinkIcon className="text-indigo-600" size={20} />
          </div>
          <div>
            <div className="font-semibold text-gray-900">{row.name}</div>
            <div className="text-xs text-gray-500 flex items-center space-x-2">
              <span>{row.campaign}</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                row.status === 'active' 
                  ? 'bg-green-100 text-green-700' 
                  : row.status === 'pending_approval'
                  ? 'bg-yellow-100 text-yellow-700'
                  : row.status === 'rejected'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {row.status === 'active' ? '● Actif' : 
                 row.status === 'pending_approval' ? '⏳ En attente' :
                 row.status === 'rejected' ? '✗ Refusé' :
                 row.status === 'cancelled' ? '✖ Annulé' :
                 row.status === 'inactive' ? '○ Inactif' : '○ Pausé'}
              </span>
            </div>
          </div>
        </div>
      ),
    },
    {
      header: 'Lien Court',
      accessor: 'short_link',
      render: (row) => (
        <div className="flex items-center space-x-2">
          {row.status === 'active' && row.short_link ? (
            <>
              <code className="text-sm bg-gray-100 px-3 py-1 rounded-lg font-mono text-indigo-600">
                {row.short_link.replace('https://', '')}
              </code>
              <button 
                onClick={() => handleCopy(row.short_link)} 
                className="p-2 hover:bg-indigo-50 rounded-lg transition text-gray-400 hover:text-indigo-600"
                title="Copier le lien"
              >
                <Copy size={16} />
              </button>
            </>
          ) : row.status === 'pending_approval' ? (
            <span className="text-sm text-gray-400 italic">En attente d'approbation</span>
          ) : row.status === 'rejected' ? (
            <span className="text-sm text-red-400 italic">Demande refusée</span>
          ) : row.status === 'cancelled' ? (
            <span className="text-sm text-gray-400 italic">Demande annulée</span>
          ) : (
            <span className="text-sm text-gray-400 italic">Lien inactif</span>
          )}
        </div>
      ),
    },
    {
      header: 'Performance',
      accessor: 'clicks',
      render: (row) => (
        row.status === 'active' ? (
          <div className="space-y-2">
            <div className="flex items-center space-x-3">
              <div className="text-center">
                <div className="text-sm font-bold text-gray-900">{row.clicks}</div>
                <div className="text-xs text-gray-500">Clics</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-bold text-green-600">{row.conversions}</div>
                <div className="text-xs text-gray-500">Conv.</div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min((row.conversions / row.clicks) * 100, 100)}%` }}
                />
              </div>
              <span className="text-xs font-medium text-gray-600">
                {((row.conversions / row.clicks) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-400 text-sm italic">
            {row.status === 'pending_approval' ? 'En attente' : 
             row.status === 'rejected' ? 'Refusé' :
             row.status === 'cancelled' ? 'Annulé' : 'Inactif'}
          </div>
        )
      ),
    },
    {
      header: 'Revenus',
      accessor: 'revenue',
      render: (row) => (
        row.status === 'active' ? (
          <div className="text-right">
            <div className="text-lg font-bold text-purple-600">
              {row.revenue?.toLocaleString()}€
            </div>
            <div className="flex items-center justify-end space-x-1 text-xs text-green-600">
              <TrendingUp size={12} />
              <span>+{row.performance}%</span>
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-400 text-sm italic">
            -
          </div>
        )
      ),
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <div className="flex space-x-2">
          {row.status === 'active' && row.short_link ? (
            <>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={() => handleCopy(row.full_link)}
                className="hover:bg-indigo-50 hover:border-indigo-300"
              >
                <Copy size={16} className="mr-1" />
                Copier
              </Button>
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => setSelectedLink(row)}
                className="hover:bg-purple-50 hover:border-purple-300"
              >
                <BarChart3 size={16} className="mr-1" />
                Stats
              </Button>
            </>
          ) : row.status === 'pending_approval' ? (
            <div className="text-xs text-gray-500 flex items-center">
              <Clock size={14} className="mr-1" />
              En attente d'approbation
            </div>
          ) : row.status === 'rejected' ? (
            <div className="text-xs text-red-500 flex items-center">
              <AlertCircle size={14} className="mr-1" />
              Demande refusée
            </div>
          ) : row.status === 'cancelled' ? (
            <div className="text-xs text-gray-500 flex items-center">
              <AlertCircle size={14} className="mr-1" />
              Demande annulée
            </div>
          ) : (
            <div className="text-xs text-gray-400">
              Lien inactif
            </div>
          )}
        </div>
      ),
    },
  ];

  const conversionRate = animatedStats.totalClicks > 0 
    ? ((animatedStats.totalConversions / animatedStats.totalClicks) * 100).toFixed(1) 
    : 0;

  const filteredLinks = filterStatus === 'all' 
    ? links 
    : links.filter(l => l.status === filterStatus);

  return (
    <div className="space-y-6" data-testid="tracking-links">
      {/* Header Dynamique */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="absolute -right-10 -top-10 w-40 h-40 bg-white opacity-10 rounded-full animate-pulse"></div>
        <div className="absolute -left-10 -bottom-10 w-32 h-32 bg-white opacity-10 rounded-full animate-pulse"></div>
        
        <div className="relative z-10">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <Sparkles className="animate-spin" size={32} />
                <h1 className="text-4xl font-bold">Liens de Tracking</h1>
              </div>
              <p className="text-indigo-100 text-lg mb-4">
                Générez, gérez et analysez vos liens de suivi en temps réel
              </p>
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
                  <Activity className="animate-pulse" size={16} />
                  <span>Surveillance en Direct</span>
                </div>
                <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
                  <Zap size={16} />
                  <span>{links.length} Liens Actifs</span>
                </div>
              </div>
            </div>
            <Button 
              onClick={() => setIsModalOpen(true)}
              className="bg-white text-indigo-600 hover:bg-indigo-50 shadow-lg"
            >
              <Plus size={20} className="mr-2" />
              Demander un Lien
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Dynamiques avec Animations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-xl transition-all duration-300 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <MousePointer className="text-blue-500" size={20} />
                <p className="text-sm text-gray-600 font-medium">Total Clics</p>
              </div>
              <p className="text-4xl font-bold text-blue-600 animate-pulse">
                {animatedStats.totalClicks.toLocaleString()}
              </p>
              <div className="flex items-center space-x-1 mt-2 text-green-500 text-xs">
                <TrendingUp size={14} />
                <span>+12% ce mois</span>
              </div>
            </div>
            <div className="bg-blue-100 p-4 rounded-full">
              <Eye className="text-blue-600" size={32} />
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-xl transition-all duration-300 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Target className="text-green-500" size={20} />
                <p className="text-sm text-gray-600 font-medium">Conversions</p>
              </div>
              <p className="text-4xl font-bold text-green-600 animate-pulse">
                {animatedStats.totalConversions.toLocaleString()}
              </p>
              <div className="flex items-center space-x-1 mt-2 text-green-500 text-xs">
                <ArrowUpRight size={14} />
                <span>{conversionRate}% taux</span>
              </div>
            </div>
            <div className="bg-green-100 p-4 rounded-full">
              <CheckCircle className="text-green-600" size={32} />
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-xl transition-all duration-300 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <BarChart3 className="text-purple-500" size={20} />
                <p className="text-sm text-gray-600 font-medium">Revenus</p>
              </div>
              <p className="text-4xl font-bold text-purple-600 animate-pulse">
                {animatedStats.totalRevenue.toLocaleString()}€
              </p>
              <div className="flex items-center space-x-1 mt-2 text-green-500 text-xs">
                <TrendingUp size={14} />
                <span>+23% ce mois</span>
              </div>
            </div>
            <div className="bg-purple-100 p-4 rounded-full">
              <Sparkles className="text-purple-600" size={32} />
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-xl transition-all duration-300 border-l-4 border-orange-500">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <LinkIcon className="text-orange-500" size={20} />
                <p className="text-sm text-gray-600 font-medium">Liens Actifs</p>
              </div>
              <p className="text-4xl font-bold text-orange-600">
                {links.length}
              </p>
              <div className="flex items-center space-x-1 mt-2 text-blue-500 text-xs">
                <Activity size={14} className="animate-pulse" />
                <span>En surveillance</span>
              </div>
            </div>
            <div className="bg-orange-100 p-4 rounded-full">
              <Share2 className="text-orange-600" size={32} />
            </div>
          </div>
        </Card>
      </div>

      {/* Activité en Temps Réel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Mes Liens de Tracking</h2>
              <div className="flex space-x-2">
                {[
                  { key: 'all', label: 'Tous' },
                  { key: 'pending_approval', label: 'En attente' },
                  { key: 'active', label: 'Actifs' },
                  { key: 'rejected', label: 'Refusés' },
                  { key: 'cancelled', label: 'Annulés' },
                  { key: 'inactive', label: 'Inactifs' }
                ].map(status => (
                  <button
                    key={status.key}
                    onClick={() => setFilterStatus(status.key)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                      filterStatus === status.key
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {status.label}
                  </button>
                ))}
              </div>
            </div>
            <Table columns={columns} data={filteredLinks} />
          </Card>
        </div>

        <Card className="bg-gradient-to-br from-gray-50 to-gray-100">
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="text-green-500 animate-pulse" size={20} />
            <h3 className="text-lg font-bold text-gray-900">Activité en Direct</h3>
          </div>
          <div className="space-y-3">
            {realtimeActivity.map((activity, index) => (
              <div 
                key={index}
                className="bg-white p-3 rounded-lg shadow-sm hover:shadow-md transition-all animate-fade-in"
              >
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{activity.icon}</span>
                  <div className="flex-1">
                    <p className="text-sm">
                      <span className="text-gray-700">{activity.text}</span>
                      <span className={`font-semibold ${activity.color}`}> {activity.link}</span>
                    </p>
                    <div className="flex items-center space-x-1 mt-1 text-xs text-gray-500">
                      <Clock size={12} />
                      <span>{activity.time}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {realtimeActivity.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                <Activity size={48} className="mx-auto mb-2 animate-pulse" />
                <p>En attente d'activité...</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
      `}</style>

      {/* Generate Link Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedProduct('');
          setRequestMessage('');
        }}
        title="Demander un Lien d'Affiliation"
        size="md"
      >
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-lg border border-indigo-200">
            <div className="flex items-start space-x-3">
              <Sparkles className="text-indigo-600 mt-1" size={20} />
              <div>
                <h3 className="font-semibold text-indigo-900 mb-1">
                  Comment ça fonctionne ?
                </h3>
                <p className="text-sm text-indigo-700">
                  Sélectionnez un produit et présentez-vous au marchand. Si votre demande est approuvée, 
                  un lien de tracking sera automatiquement créé pour vous.
                </p>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sélectionnez un produit *
            </label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              disabled={loading}
            >
              <option value="">Choisir un produit...</option>
              {products.map(product => (
                <option key={product.id} value={product.id}>
                  {product.name} - Commission: {product.commission_rate}%
                </option>
              ))}
            </select>
            {products.length === 0 && !loading && (
              <p className="text-sm text-gray-500 mt-2">
                Aucun produit disponible. Visitez le Marketplace pour découvrir les produits.
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message au marchand *
            </label>
            <textarea
              value={requestMessage}
              onChange={(e) => setRequestMessage(e.target.value)}
              placeholder="Présentez-vous et expliquez pourquoi vous souhaitez promouvoir ce produit..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              disabled={loading}
            />
            <p className="text-xs text-gray-500 mt-1">
              Incluez vos réseaux sociaux, nombre de followers, niche, etc.
            </p>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
            <div className="flex items-start space-x-2">
              <AlertCircle className="text-yellow-600 mt-0.5" size={18} />
              <div>
                <p className="text-sm font-medium text-yellow-900 mb-1">
                  Important à savoir
                </p>
                <ul className="text-sm text-yellow-800 space-y-1 list-disc list-inside">
                  <li>Le marchand va examiner votre demande</li>
                  <li>Vous recevrez une notification de sa décision</li>
                  <li>Si approuvé, le lien sera créé automatiquement</li>
                  <li>Vous pourrez suivre toutes vos demandes dans l'onglet "En attente"</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <Button 
              variant="secondary" 
              onClick={() => {
                setIsModalOpen(false);
                setSelectedProduct('');
                setRequestMessage('');
              }}
              disabled={loading}
            >
              Annuler
            </Button>
            <Button 
              onClick={handleGenerate}
              disabled={!selectedProduct || !requestMessage.trim() || loading}
              className="flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Envoi...</span>
                </>
              ) : (
                <>
                  <Zap size={18} />
                  <span>Envoyer la Demande</span>
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TrackingLinks;
