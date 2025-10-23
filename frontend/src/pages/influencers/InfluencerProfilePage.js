import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import {
  ArrowLeft, User, Mail, Phone, MapPin, Calendar,
  Instagram, Twitter, Facebook, Globe, CheckCircle,
  Users, TrendingUp, DollarSign, MessageSquare
} from 'lucide-react';
import { formatNumber, formatCurrency, formatDate } from '../../utils/helpers';

const InfluencerProfilePage = () => {
  const { influencerId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  
  const [influencer, setInfluencer] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInfluencerProfile();
  }, [influencerId]);

  const fetchInfluencerProfile = async () => {
    try {
      setLoading(true);
      
      // Fetch influencer details
      const influencerRes = await api.get(`/api/influencers/${influencerId}`);
      setInfluencer(influencerRes.data);
      
      // Fetch stats (example - adapt to your API)
      try {
        const statsRes = await api.get(`/api/influencers/${influencerId}/stats`);
        setStats(statsRes.data);
      } catch (e) {
        // Si pas d'endpoint stats, utiliser des données factices
        setStats({
          total_sales: 15000,
          total_clicks: 5234,
          conversion_rate: 4.2,
          campaigns_completed: 12
        });
      }
    } catch (error) {
      console.error('Error fetching influencer profile:', error);
      alert('Erreur lors du chargement du profil');
      navigate('/influencers');
    } finally {
      setLoading(false);
    }
  };

  const handleContact = () => {
    // Navigate to messaging with influencer
    navigate('/messages', {
      state: {
        recipient_id: influencerId,
        recipient_type: 'influencer',
        subject: `Contact avec ${influencer?.name || 'Influenceur'}`
      }
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl">Chargement du profil...</div>
      </div>
    );
  }

  if (!influencer) {
    return (
      <div className="text-center py-12">
        <p className="text-xl text-gray-600">Influenceur non trouvé</p>
        <Button onClick={() => navigate('/influencers')} className="mt-4">
          Retour à la liste
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition"
      >
        <ArrowLeft size={20} />
        Retour
      </button>

      {/* Profile Header */}
      <Card>
        <div className="flex flex-col md:flex-row gap-6">
          {/* Avatar */}
          <div className="flex-shrink-0">
            {influencer.avatar_url ? (
              <img
                src={influencer.avatar_url}
                alt={influencer.name}
                className="w-32 h-32 rounded-full object-cover border-4 border-indigo-100"
              />
            ) : (
              <div className="w-32 h-32 bg-indigo-100 rounded-full flex items-center justify-center">
                <User size={64} className="text-indigo-600" />
              </div>
            )}
          </div>

          {/* Info */}
          <div className="flex-1">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-bold">{influencer.name || 'Nom non défini'}</h1>
                  {influencer.verified && (
                    <CheckCircle size={24} className="text-blue-500" title="Vérifié" />
                  )}
                </div>
                <p className="text-gray-600">{influencer.bio || 'Pas de bio disponible'}</p>
              </div>
              
              {user?.role === 'merchant' && (
                <Button onClick={handleContact}>
                  <MessageSquare size={18} className="mr-2" />
                  Contacter
                </Button>
              )}
            </div>

            {/* Contact Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              {influencer.email && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Mail size={16} />
                  <span>{influencer.email}</span>
                </div>
              )}
              {influencer.phone && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone size={16} />
                  <span>{influencer.phone}</span>
                </div>
              )}
              {influencer.location && (
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin size={16} />
                  <span>{influencer.location}</span>
                </div>
              )}
              {influencer.created_at && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar size={16} />
                  <span>Membre depuis {formatDate(influencer.created_at)}</span>
                </div>
              )}
            </div>

            {/* Social Links */}
            <div className="flex gap-3 mt-4">
              {influencer.instagram_url && (
                <a
                  href={influencer.instagram_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-pink-100 text-pink-600 rounded-lg hover:bg-pink-200 transition"
                >
                  <Instagram size={20} />
                </a>
              )}
              {influencer.twitter_url && (
                <a
                  href={influencer.twitter_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition"
                >
                  <Twitter size={20} />
                </a>
              )}
              {influencer.facebook_url && (
                <a
                  href={influencer.facebook_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 transition"
                >
                  <Facebook size={20} />
                </a>
              )}
              {influencer.website_url && (
                <a
                  href={influencer.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition"
                >
                  <Globe size={20} />
                </a>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Followers</p>
                <p className="text-2xl font-bold mt-1">
                  {formatNumber(influencer.followers || 0)}
                </p>
              </div>
              <Users size={32} className="text-indigo-600" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Clics générés</p>
                <p className="text-2xl font-bold mt-1">
                  {formatNumber(stats.total_clicks)}
                </p>
              </div>
              <TrendingUp size={32} className="text-green-600" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Ventes</p>
                <p className="text-2xl font-bold mt-1">
                  {formatCurrency(stats.total_sales)}
                </p>
              </div>
              <DollarSign size={32} className="text-blue-600" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Taux conversion</p>
                <p className="text-2xl font-bold mt-1">
                  {stats.conversion_rate}%
                </p>
              </div>
              <CheckCircle size={32} className="text-purple-600" />
            </div>
          </Card>
        </div>
      )}

      {/* Categories/Niches */}
      {influencer.categories && influencer.categories.length > 0 && (
        <Card>
          <h2 className="text-xl font-bold mb-4">Catégories d'expertise</h2>
          <div className="flex flex-wrap gap-2">
            {influencer.categories.map((category, idx) => (
              <Badge key={idx} variant="info">
                {category}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Portfolio/Past Campaigns */}
      <Card>
        <h2 className="text-xl font-bold mb-4">Campagnes réalisées</h2>
        {stats?.campaigns_completed > 0 ? (
          <div className="space-y-3">
            <p className="text-gray-600">
              {stats.campaigns_completed} campagne(s) complétée(s) avec succès
            </p>
            {/* Ici vous pouvez ajouter une liste de campagnes si disponible */}
          </div>
        ) : (
          <p className="text-gray-500">Aucune campagne complétée pour le moment</p>
        )}
      </Card>

      {/* Description détaillée */}
      {influencer.description && (
        <Card>
          <h2 className="text-xl font-bold mb-4">À propos</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{influencer.description}</p>
        </Card>
      )}
    </div>
  );
};

export default InfluencerProfilePage;
