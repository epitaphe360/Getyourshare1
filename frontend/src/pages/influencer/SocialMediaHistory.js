/**
 * Page d'historique des statistiques des réseaux sociaux
 *
 * Affiche:
 * - Graphiques d'évolution des followers
 * - Graphiques d'évolution de l'engagement
 * - Top posts par plateforme
 * - Comparaison entre plateformes
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import api from '../../services/api';

const SocialMediaHistory = () => {
  const navigate = useNavigate();
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [timeRange, setTimeRange] = useState(30); // jours
  const [statsHistory, setStatsHistory] = useState([]);
  const [topPosts, setTopPosts] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchConnections();
  }, []);

  useEffect(() => {
    if (connections.length > 0) {
      fetchStatsHistory();
      fetchTopPosts();
    }
  }, [selectedPlatform, timeRange, connections]);

  const fetchConnections = async () => {
    try {
      const response = await api.get('/api/social-media/connections');
      setConnections(response.data);
      if (response.data.length > 0) {
        setSelectedPlatform(response.data[0].platform);
      }
    } catch (err) {
      console.error('Error fetching connections:', err);
      setError('Erreur lors du chargement des connexions');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatsHistory = async () => {
    if (selectedPlatform === 'all') return;

    try {
      const response = await api.get('/api/social-media/stats/history', {
        params: {
          platform: selectedPlatform,
          days: timeRange,
        },
      });

      // Formatter les données pour les graphiques
      const formattedData = response.data.map((stat) => ({
        date: new Date(stat.synced_at).toLocaleDateString('fr-FR', {
          day: '2-digit',
          month: 'short',
        }),
        followers: stat.followers_count,
        engagement: stat.engagement_rate,
        likes: stat.average_likes_per_post,
        comments: stat.average_comments_per_post,
      }));

      setStatsHistory(formattedData);
    } catch (err) {
      console.error('Error fetching stats history:', err);
    }
  };

  const fetchTopPosts = async () => {
    try {
      const response = await api.get('/api/social-media/posts/top', {
        params: {
          platform: selectedPlatform === 'all' ? undefined : selectedPlatform,
          limit: 12,
          sort_by: 'engagement_rate',
        },
      });

      setTopPosts(response.data.posts || []);
    } catch (err) {
      console.error('Error fetching top posts:', err);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num;
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      instagram: '📷',
      tiktok: '🎵',
      facebook: '👤',
      youtube: '📺',
      twitter: '🐦',
    };
    return icons[platform] || '🌐';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (connections.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Aucun compte connecté
            </h2>
            <p className="text-gray-600 mb-6">
              Connectez vos réseaux sociaux pour voir vos statistiques et votre historique
            </p>
            <button
              onClick={() => navigate('/influencer/social-media')}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Connecter mes comptes
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/influencer/social-media')}
            className="text-primary-600 hover:text-primary-700 mb-4 flex items-center gap-2"
          >
            ← Retour aux connexions
          </button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Historique de mes Statistiques
          </h1>
          <p className="text-gray-600">
            Suivez l'évolution de vos performances sur les réseaux sociaux
          </p>
        </div>

        {/* Filtres */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-wrap gap-4">
            {/* Sélecteur de plateforme */}
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Plateforme
              </label>
              <select
                value={selectedPlatform}
                onChange={(e) => setSelectedPlatform(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                {connections.map((conn) => (
                  <option key={conn.id} value={conn.platform}>
                    {getPlatformIcon(conn.platform)} {conn.platform.charAt(0).toUpperCase() + conn.platform.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Sélecteur de période */}
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Période
              </label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value={7}>7 derniers jours</option>
                <option value={30}>30 derniers jours</option>
                <option value={90}>90 derniers jours</option>
                <option value={180}>6 derniers mois</option>
                <option value={365}>1 an</option>
              </select>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Graphiques */}
        {statsHistory.length > 0 ? (
          <div className="space-y-6">

            {/* Graphique Followers */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Évolution des Followers
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={statsHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="followers"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    name="Followers"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Graphique Engagement */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Taux d'Engagement (%)
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={statsHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="engagement"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Engagement %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Graphique Likes & Comments */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Moyennes par Post
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={statsHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="likes" fill="#f59e0b" name="Likes moyens" />
                  <Bar dataKey="comments" fill="#3b82f6" name="Commentaires moyens" />
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600">
              Pas assez de données historiques pour afficher les graphiques.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Les statistiques sont collectées quotidiennement. Revenez bientôt !
            </p>
          </div>
        )}

        {/* Top Posts */}
        {topPosts.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Mes Meilleures Publications
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {topPosts.map((post) => (
                <div key={post.platform_post_id} className="bg-white rounded-lg shadow overflow-hidden">
                  {/* Thumbnail */}
                  {post.thumbnail_url && (
                    <div className="aspect-square">
                      <img
                        src={post.thumbnail_url}
                        alt="Post"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}

                  {/* Stats */}
                  <div className="p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">{getPlatformIcon(post.platform)}</span>
                      <span className="text-xs text-gray-500 capitalize">{post.post_type}</span>
                    </div>

                    <div className="space-y-1 text-sm">
                      {post.likes_count > 0 && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">❤️ Likes:</span>
                          <span className="font-semibold">{formatNumber(post.likes_count)}</span>
                        </div>
                      )}
                      {post.comments_count > 0 && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">💬 Comments:</span>
                          <span className="font-semibold">{formatNumber(post.comments_count)}</span>
                        </div>
                      )}
                      {post.views_count > 0 && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">👁️ Vues:</span>
                          <span className="font-semibold">{formatNumber(post.views_count)}</span>
                        </div>
                      )}
                      {post.engagement_rate && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">📊 Engagement:</span>
                          <span className="font-semibold text-primary-600">{post.engagement_rate.toFixed(1)}%</span>
                        </div>
                      )}
                    </div>

                    {/* Lien vers le post */}
                    {post.permalink && (
                      <a
                        href={post.permalink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-3 block text-center text-xs text-primary-600 hover:text-primary-700"
                      >
                        Voir le post →
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Conseils */}
        <div className="mt-8 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
          <h3 className="font-semibold text-purple-900 mb-3">💡 Conseils pour améliorer vos statistiques</h3>
          <ul className="space-y-2 text-sm text-purple-800">
            <li>✓ Postez régulièrement (au moins 3-4 fois par semaine)</li>
            <li>✓ Interagissez avec votre audience (répondez aux commentaires)</li>
            <li>✓ Utilisez des hashtags pertinents et tendances</li>
            <li>✓ Analysez vos meilleurs posts et reproduisez leur succès</li>
            <li>✓ Postez aux heures de forte activité de votre audience</li>
          </ul>
        </div>

      </div>
    </div>
  );
};

export default SocialMediaHistory;
