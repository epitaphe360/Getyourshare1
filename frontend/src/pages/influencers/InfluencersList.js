import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import { 
  Search, Filter, Users, TrendingUp, 
  DollarSign, Target, Eye, MoreVertical,
  Instagram, Youtube, Award, Sparkles
} from 'lucide-react';

const InfluencersList = () => {
  const navigate = useNavigate();
  const [influencers, setInfluencers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    fetchInfluencers();
  }, []);

  const fetchInfluencers = async () => {
    try {
      const response = await api.get('/api/influencers');
      setInfluencers(response.data.influencers || []);
    } catch (error) {
      console.error('Error fetching influencers:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredInfluencers = influencers.filter(influencer => {
    const matchesSearch = influencer.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         influencer.username?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || influencer.influencer_type === filterType;
    return matchesSearch && matchesType;
  });

  const types = [
    { id: 'all', name: 'Tous', color: 'gray' },
    { id: 'nano', name: 'Nano (<10K)', color: 'blue' },
    { id: 'micro', name: 'Micro (10K-100K)', color: 'green' },
    { id: 'macro', name: 'Macro (100K-1M)', color: 'purple' },
    { id: 'mega', name: 'Mega (>1M)', color: 'pink' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Influenceurs</h1>
          <p className="text-gray-600 mt-2">Gérez tous vos partenaires influenceurs</p>
        </div>
        <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition font-semibold">
          + Inviter Influenceur
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center space-x-3">
            <div className="bg-purple-100 p-3 rounded-lg">
              <Users className="text-purple-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{influencers.length}</div>
              <div className="text-sm text-gray-600">Influenceurs Totaux</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <div className="bg-green-100 p-3 rounded-lg">
              <DollarSign className="text-green-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {influencers.reduce((sum, i) => sum + (i.total_earnings || 0), 0).toLocaleString()}€
              </div>
              <div className="text-sm text-gray-600">Gains Totaux</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-100 p-3 rounded-lg">
              <Target className="text-indigo-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {influencers.reduce((sum, i) => sum + (i.total_clicks || 0), 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Clics Totaux</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <div className="bg-orange-100 p-3 rounded-lg">
              <TrendingUp className="text-orange-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">5.2%</div>
              <div className="text-sm text-gray-600">Taux Conv. Moyen</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher un influenceur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          {/* Type Filter */}
          <div className="flex flex-wrap gap-2">
            {types.map((type) => (
              <button
                key={type.id}
                onClick={() => setFilterType(type.id)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  filterType === type.id
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {type.name}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Influencers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredInfluencers.map((influencer) => (
          <Card key={influencer.id}>
            <div className="text-center">
              {/* Avatar */}
              <div className="relative inline-block mb-4">
                {influencer.profile_picture_url ? (
                  <img 
                    src={influencer.profile_picture_url} 
                    alt={influencer.full_name}
                    className="w-20 h-20 rounded-full mx-auto"
                  />
                ) : (
                  <div className="w-20 h-20 rounded-full bg-purple-100 flex items-center justify-center mx-auto">
                    <Users className="text-purple-600" size={32} />
                  </div>
                )}
                <div className="absolute -bottom-2 -right-2 bg-white rounded-full p-1 shadow-lg">
                  {influencer.influencer_type === 'mega' && <Award className="text-pink-500" size={20} />}
                  {influencer.influencer_type === 'macro' && <Sparkles className="text-purple-500" size={20} />}
                  {influencer.influencer_type === 'micro' && <TrendingUp className="text-green-500" size={20} />}
                  {influencer.influencer_type === 'nano' && <Target className="text-blue-500" size={20} />}
                </div>
              </div>

              {/* Info */}
              <h3 className="text-lg font-bold text-gray-900 mb-1">{influencer.full_name}</h3>
              <p className="text-sm text-gray-600 mb-2">@{influencer.username}</p>
              
              <div className="flex items-center justify-center space-x-2 mb-4">
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                  influencer.influencer_type === 'mega' ? 'bg-pink-100 text-pink-800' :
                  influencer.influencer_type === 'macro' ? 'bg-purple-100 text-purple-800' :
                  influencer.influencer_type === 'micro' ? 'bg-green-100 text-green-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {influencer.influencer_type}
                </span>
                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                  {influencer.category}
                </span>
              </div>

              {/* Social Links */}
              {influencer.social_links && (
                <div className="flex items-center justify-center space-x-3 mb-4">
                  {influencer.social_links.instagram && (
                    <a href={influencer.social_links.instagram} target="_blank" rel="noopener noreferrer" className="text-pink-600 hover:text-pink-700">
                      <Instagram size={20} />
                    </a>
                  )}
                  {influencer.social_links.youtube && (
                    <a href={influencer.social_links.youtube} target="_blank" rel="noopener noreferrer" className="text-red-600 hover:text-red-700">
                      <Youtube size={20} />
                    </a>
                  )}
                </div>
              )}

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-4 pt-4 border-t border-gray-200">
                <div>
                  <div className="text-lg font-bold text-gray-900">
                    {influencer.audience_size?.toLocaleString() || 0}
                  </div>
                  <div className="text-xs text-gray-600">Abonnés</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900">
                    {influencer.engagement_rate || 0}%
                  </div>
                  <div className="text-xs text-gray-600">Engagement</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-green-600">
                    {influencer.total_earnings?.toLocaleString() || 0}€
                  </div>
                  <div className="text-xs text-gray-600">Gains</div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <button
                  onClick={() => navigate(`/influencers/${influencer.id}`)}
                  className="flex-1 bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition text-sm font-semibold"
                >
                  Voir Profil
                </button>
                <button className="px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition">
                  <MoreVertical size={16} />
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default InfluencersList;
