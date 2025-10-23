import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { Search, Filter, X, Users, MapPin, TrendingUp, CheckCircle, ArrowLeft, Mail } from 'lucide-react';

const InfluencerSearchPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [influencers, setInfluencers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(true);
  
  const [filters, setFilters] = useState({
    category: '',
    min_followers: '',
    max_followers: '',
    min_engagement: '',
    platform: '',
    location: '',
    verified_only: false,
    sort_by: 'followers',
    order: 'desc'
  });

  useEffect(() => {
    fetchStats();
    searchInfluencers();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/influencers/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const searchInfluencers = async () => {
    setLoading(true);
    try {
      const params = Object.entries(filters)
        .filter(([_, value]) => value !== '' && value !== false)
        .reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {});
      
      const response = await api.get('/api/influencers/search', { params });
      setInfluencers(response.data.influencers || []);
    } catch (error) {
      console.error('Error searching influencers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const clearFilters = () => {
    setFilters({
      category: '',
      min_followers: '',
      max_followers: '',
      min_engagement: '',
      platform: '',
      location: '',
      verified_only: false,
      sort_by: 'followers',
      order: 'desc'
    });
  };

  const handleContactInfluencer = async (influencer) => {
    // TODO: Implémenter système de messagerie
    alert(`Contacter ${influencer.full_name} - Fonctionnalité à venir`);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="w-8 h-8 text-purple-600" />
            Recherche d'Influenceurs
          </h1>
          {stats && (
            <p className="text-gray-600 mt-1">
              {stats.total_influencers} influenceurs disponibles sur la plateforme
            </p>
          )}
        </div>
        
        <Button
          onClick={() => setShowFilters(!showFilters)}
          variant={showFilters ? "primary" : "secondary"}
        >
          <Filter className="w-4 h-4 mr-2" />
          {showFilters ? 'Masquer' : 'Afficher'} filtres
        </Button>
      </div>

      {/* Panneau de filtres */}
      {showFilters && (
        <Card>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Filter className="w-5 h-5 text-indigo-600" />
                Filtres de recherche avancée
              </h3>
              <button
                onClick={clearFilters}
                className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1 px-3 py-1 rounded-lg hover:bg-gray-100"
              >
                <X className="w-4 h-4" />
                Réinitialiser
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Catégorie */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Catégorie / Niche
                </label>
                <select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Toutes les catégories</option>
                  {stats?.categories?.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              {/* Plateforme */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Plateforme principale
                </label>
                <select
                  value={filters.platform}
                  onChange={(e) => handleFilterChange('platform', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Toutes les plateformes</option>
                  {stats?.platforms?.map(plat => (
                    <option key={plat} value={plat}>{plat}</option>
                  ))}
                </select>
              </div>

              {/* Localisation */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Localisation
                </label>
                <input
                  type="text"
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                  placeholder="Ex: Paris, France"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Min Followers */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Followers minimum
                </label>
                <input
                  type="number"
                  value={filters.min_followers}
                  onChange={(e) => handleFilterChange('min_followers', e.target.value)}
                  placeholder="Ex: 10000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Max Followers */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Followers maximum
                </label>
                <input
                  type="number"
                  value={filters.max_followers}
                  onChange={(e) => handleFilterChange('max_followers', e.target.value)}
                  placeholder="Ex: 1000000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Min Engagement */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Engagement minimum (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={filters.min_engagement}
                  onChange={(e) => handleFilterChange('min_engagement', e.target.value)}
                  placeholder="Ex: 2.5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Trier par */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Trier par
                </label>
                <select
                  value={filters.sort_by}
                  onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="followers">Nombre de followers</option>
                  <option value="engagement_rate">Taux d'engagement</option>
                  <option value="total_sales">Ventes totales</option>
                </select>
              </div>

              {/* Ordre */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ordre
                </label>
                <select
                  value={filters.order}
                  onChange={(e) => handleFilterChange('order', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="desc">Décroissant</option>
                  <option value="asc">Croissant</option>
                </select>
              </div>

              {/* Vérifié seulement */}
              <div className="flex items-center pt-6">
                <input
                  type="checkbox"
                  id="verified_only"
                  checked={filters.verified_only}
                  onChange={(e) => handleFilterChange('verified_only', e.target.checked)}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <label htmlFor="verified_only" className="ml-2 text-sm font-medium text-gray-700">
                  Comptes vérifiés uniquement
                </label>
              </div>
            </div>

            <div className="pt-4 border-t">
              <Button onClick={searchInfluencers} disabled={loading}>
                <Search className="w-4 h-4 mr-2" />
                {loading ? 'Recherche...' : 'Lancer la recherche'}
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Résultats */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <p className="text-gray-700 font-medium">
            {influencers.length} influenceur{influencers.length > 1 ? 's' : ''} trouvé{influencers.length > 1 ? 's' : ''}
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Recherche en cours...</p>
          </div>
        ) : influencers.length === 0 ? (
          <Card>
            <div className="p-12 text-center text-gray-500">
              <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium text-gray-900">Aucun influenceur trouvé</p>
              <p className="text-sm mt-2">Essayez d'ajuster vos critères de recherche</p>
              <Button onClick={clearFilters} variant="secondary" className="mt-4">
                Réinitialiser les filtres
              </Button>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {influencers.map(influencer => (
              <Card key={influencer.user_id} className="hover:shadow-xl transition-all duration-300">
                <div className="p-5">
                  <div className="flex items-start gap-3 mb-3">
                    <img
                      src={influencer.profile_image || 'https://via.placeholder.com/50'}
                      alt={influencer.full_name}
                      className="w-16 h-16 rounded-full object-cover border-2 border-purple-100"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-lg truncate text-gray-900">
                          {influencer.full_name}
                        </h3>
                        {influencer.is_verified && (
                          <CheckCircle className="w-5 h-5 text-blue-500 flex-shrink-0" />
                        )}
                      </div>
                      <p className="text-sm text-purple-600 font-medium">{influencer.category}</p>
                    </div>
                  </div>

                  <p className="text-sm text-gray-700 mt-3 line-clamp-2 min-h-[40px]">
                    {influencer.bio || 'Aucune biographie'}
                  </p>

                  <div className="mt-4 space-y-2 bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        Followers
                      </span>
                      <span className="font-bold text-gray-900">
                        {formatNumber(influencer.followers_count)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 flex items-center gap-1">
                        <TrendingUp className="w-4 h-4" />
                        Engagement
                      </span>
                      <span className="font-bold text-green-600">
                        {influencer.engagement_rate}%
                      </span>
                    </div>

                    {influencer.location && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          Localisation
                        </span>
                        <span className="text-sm font-medium text-gray-700 truncate ml-2">
                          {influencer.location}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 flex gap-2">
                    <Button
                      onClick={() => navigate(`/influencers/${influencer.user_id}`)}
                      className="flex-1"
                      variant="secondary"
                    >
                      Voir profil
                    </Button>
                    <Button
                      onClick={() => handleContactInfluencer(influencer)}
                      className="flex-1"
                    >
                      <Mail className="w-4 h-4 mr-1" />
                      Contacter
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default InfluencerSearchPage;
