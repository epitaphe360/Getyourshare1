import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import SocialPublishModal from '../../components/influencer/SocialPublishModal';
import {
  Link as LinkIcon, Copy, Eye, MousePointerClick,
  DollarSign, TrendingUp, Share2, QrCode,
  Package, ExternalLink, Calendar, Trash2,
  Instagram, Facebook, Youtube, Twitter,
  CheckCircle, XCircle, Clock
} from 'lucide-react';

/**
 * My Affiliate Links Page - For Influencers
 * Shows all generated affiliate links with stats and social publishing
 */
const MyLinks = () => {
  const { user } = useAuth();
  const toast = useToast();

  const [links, setLinks] = useState([]);
  const [publications, setPublications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [selectedLink, setSelectedLink] = useState(null);

  useEffect(() => {
    if (user?.role === 'influencer') {
      fetchMyLinks();
      fetchPublications();
    }
  }, [user]);

  const fetchMyLinks = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/affiliate/my-links');
      if (response.data.success) {
        setLinks(response.data.links || []);
      }
    } catch (error) {
      console.error('Error fetching links:', error);
      toast.error('Erreur lors du chargement des liens');
    } finally {
      setLoading(false);
    }
  };

  const fetchPublications = async () => {
    try {
      const response = await api.get('/api/affiliate/publications');
      if (response.data.success) {
        setPublications(response.data.publications || []);
      }
    } catch (error) {
      console.error('Error fetching publications:', error);
    }
  };

  const handleCopyLink = async (linkUrl) => {
    try {
      await navigator.clipboard.writeText(linkUrl);
      toast.success('Lien copié dans le presse-papier!');
    } catch (error) {
      toast.error('Erreur lors de la copie du lien');
    }
  };

  const handlePublishClick = (link) => {
    setSelectedLink(link);
    setShowPublishModal(true);
  };

  const handlePublishSuccess = () => {
    toast.success('Publié avec succès sur les réseaux sociaux!');
    setShowPublishModal(false);
    setSelectedLink(null);
    fetchPublications();
  };

  const handleDeleteLink = async (linkId) => {
    if (!confirm('Êtes-vous sûr de vouloir désactiver ce lien?')) {
      return;
    }

    try {
      const response = await api.delete(`/api/affiliate/link/${linkId}`);
      if (response.data.success) {
        toast.success('Lien désactivé');
        fetchMyLinks();
      }
    } catch (error) {
      toast.error('Erreur lors de la désactivation du lien');
    }
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'instagram':
        return <Instagram className="w-5 h-5" />;
      case 'facebook':
        return <Facebook className="w-5 h-5" />;
      case 'tiktok':
        return <span className="text-sm font-bold">TT</span>;
      case 'twitter':
        return <Twitter className="w-5 h-5" />;
      default:
        return null;
    }
  };

  const getPlatformColor = (platform) => {
    switch (platform) {
      case 'instagram':
        return 'bg-gradient-to-br from-purple-600 to-pink-600';
      case 'facebook':
        return 'bg-blue-600';
      case 'tiktok':
        return 'bg-black';
      case 'twitter':
        return 'bg-sky-500';
      default:
        return 'bg-gray-600';
    }
  };

  if (user?.role !== 'influencer') {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <Package className="w-16 h-16 text-gray-300 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Accès Réservé aux Influenceurs
        </h2>
        <p className="text-gray-600">Cette page est réservée aux influenceurs</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement de vos liens...</div>
      </div>
    );
  }

  // Calculer statistiques globales
  const totalClicks = links.reduce((sum, link) => sum + (link.stats?.clicks || 0), 0);
  const totalConversions = links.reduce((sum, link) => sum + (link.stats?.conversions || 0), 0);
  const totalCommissions = links.reduce(
    (sum, link) => sum + (link.stats?.total_commissions || 0),
    0
  );
  const avgConversionRate =
    links.length > 0
      ? links.reduce((sum, link) => sum + (link.stats?.conversion_rate || 0), 0) / links.length
      : 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mes Liens d'Affiliation</h1>
          <p className="text-gray-600 mt-1">
            Gérez vos liens et publiez sur vos réseaux sociaux
          </p>
        </div>
      </div>

      {/* Global Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Liens Actifs</p>
              <p className="text-3xl font-bold text-gray-900">{links.length}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <LinkIcon className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Clics Totaux</p>
              <p className="text-3xl font-bold text-gray-900">{totalClicks.toLocaleString()}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <MousePointerClick className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Conversions</p>
              <p className="text-3xl font-bold text-gray-900">{totalConversions}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Commissions</p>
              <p className="text-3xl font-bold text-gray-900">
                {totalCommissions.toLocaleString()} DH
              </p>
            </div>
            <div className="bg-orange-100 p-3 rounded-lg">
              <DollarSign className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Links List */}
      {links.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <LinkIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun lien d'affiliation</h3>
            <p className="text-gray-600 mb-4">
              Allez sur le marketplace et générez votre premier lien d'affiliation
            </p>
            <a
              href="/marketplace"
              className="inline-block px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Parcourir le Marketplace
            </a>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {links.map((link) => (
            <Card key={link.id} className="hover:shadow-lg transition-shadow">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Product Info - Left Side */}
                <div className="lg:col-span-4 flex items-start space-x-4">
                  {/* Product Image */}
                  {link.product?.images && link.product.images.length > 0 ? (
                    <img
                      src={link.product.images[0]}
                      alt={link.product.name}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                  ) : (
                    <div className="w-20 h-20 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Package className="w-10 h-10 text-purple-400" />
                    </div>
                  )}

                  {/* Product Details */}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {link.product?.name || 'Produit'}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                      Prix: {link.product?.discounted_price?.toLocaleString() || 'N/A'} DH
                    </p>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleCopyLink(link.full_url)}
                        className="text-sm text-purple-600 hover:text-purple-700 flex items-center"
                      >
                        <Copy className="w-4 h-4 mr-1" />
                        Copier
                      </button>
                      <a
                        href={link.qr_code_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-purple-600 hover:text-purple-700 flex items-center"
                      >
                        <QrCode className="w-4 h-4 mr-1" />
                        QR Code
                      </a>
                    </div>
                  </div>
                </div>

                {/* Stats - Middle */}
                <div className="lg:col-span-4 grid grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                      <Eye className="w-4 h-4 text-gray-400" />
                    </div>
                    <div className="text-xl font-bold text-gray-900">
                      {link.stats?.clicks || 0}
                    </div>
                    <div className="text-xs text-gray-600">Clics</div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                      <TrendingUp className="w-4 h-4 text-gray-400" />
                    </div>
                    <div className="text-xl font-bold text-gray-900">
                      {link.stats?.conversions || 0}
                    </div>
                    <div className="text-xs text-gray-600">Ventes</div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                      <DollarSign className="w-4 h-4 text-gray-400" />
                    </div>
                    <div className="text-xl font-bold text-green-600">
                      {link.stats?.total_commissions?.toLocaleString() || 0}
                    </div>
                    <div className="text-xs text-gray-600">DH</div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                      <TrendingUp className="w-4 h-4 text-gray-400" />
                    </div>
                    <div className="text-xl font-bold text-purple-600">
                      {link.stats?.conversion_rate?.toFixed(1) || 0}%
                    </div>
                    <div className="text-xs text-gray-600">Taux</div>
                  </div>
                </div>

                {/* Actions - Right */}
                <div className="lg:col-span-4 flex flex-col justify-between">
                  {/* Link URL */}
                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-1">Lien d'affiliation:</div>
                    <div className="flex items-center space-x-2">
                      <code className="flex-1 text-xs bg-gray-100 px-3 py-2 rounded overflow-hidden text-ellipsis">
                        {link.full_url}
                      </code>
                      <button
                        onClick={() => handleCopyLink(link.full_url)}
                        className="p-2 bg-gray-100 rounded hover:bg-gray-200"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handlePublishClick(link)}
                      className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2 px-4 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition flex items-center justify-center"
                    >
                      <Share2 className="w-4 h-4 mr-2" />
                      Publier
                    </button>
                    <button
                      onClick={() => window.open(link.full_url, '_blank')}
                      className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                    >
                      <ExternalLink className="w-5 h-5 text-gray-600" />
                    </button>
                    <button
                      onClick={() => handleDeleteLink(link.id)}
                      className="p-2 bg-red-100 rounded-lg hover:bg-red-200"
                    >
                      <Trash2 className="w-5 h-5 text-red-600" />
                    </button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Publications History */}
      {publications.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Historique des Publications</h2>
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Produit
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Plateforme
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Date
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Stats
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Statut
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {publications.slice(0, 10).map((pub) => (
                    <tr key={pub.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="font-medium text-gray-900">
                          {pub.product?.name || 'Produit'}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div
                          className={`inline-flex items-center space-x-1 text-white px-3 py-1 rounded-full text-sm ${getPlatformColor(
                            pub.platform
                          )}`}
                        >
                          {getPlatformIcon(pub.platform)}
                          <span className="capitalize">{pub.platform}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="w-4 h-4 mr-1" />
                          {new Date(pub.published_at).toLocaleDateString('fr-FR')}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-sm text-gray-600">
                          {pub.views_count || 0} vues • {pub.clicks_count || 0} clics
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        {pub.status === 'published' ? (
                          <span className="inline-flex items-center text-green-600 text-sm">
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Publié
                          </span>
                        ) : pub.status === 'scheduled' ? (
                          <span className="inline-flex items-center text-orange-600 text-sm">
                            <Clock className="w-4 h-4 mr-1" />
                            Programmé
                          </span>
                        ) : (
                          <span className="inline-flex items-center text-red-600 text-sm">
                            <XCircle className="w-4 h-4 mr-1" />
                            Échec
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* Social Publish Modal */}
      {showPublishModal && selectedLink && (
        <SocialPublishModal
          link={selectedLink}
          onClose={() => {
            setShowPublishModal(false);
            setSelectedLink(null);
          }}
          onSuccess={handlePublishSuccess}
        />
      )}
    </div>
  );
};

export default MyLinks;
