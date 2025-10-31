import React, { useState, useEffect } from 'react';
import { useI18n } from '../../i18n/i18n';
import api from '../../utils/api';
import {
  Music, Eye, MousePointer, ShoppingCart, TrendingUp,
  DollarSign, Users, Video, Heart, MessageCircle, Share2
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

/**
 * Dashboard Analytics TikTok Shop
 *
 * Affiche les métriques de performance TikTok:
 * - Vues, clics, conversions
 * - Ventes et revenus
 * - Performance des lives
 * - Produits tendance
 */
const TikTokAnalyticsDashboard = ({ startDate, endDate }) => {
  const { t } = useI18n();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [liveStats, setLiveStats] = useState([]);
  const [trendingProducts, setTrendingProducts] = useState([]);

  useEffect(() => {
    fetchAnalytics();
  }, [startDate, endDate]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);

      const start = startDate || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      const end = endDate || new Date();

      const formatDate = (date) => date.toISOString().split('T')[0];

      // Récupérer les analytics
      const response = await api.get('/api/tiktok-shop/analytics', {
        params: {
          start_date: formatDate(start),
          end_date: formatDate(end)
        }
      });

      setAnalytics(response.data);
    } catch (error) {
      console.error('Erreur chargement analytics TikTok:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Music className="w-12 h-12 text-gray-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Chargement des analytics TikTok...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Aucune donnée disponible</p>
      </div>
    );
  }

  const summary = analytics.summary || {};
  const dailyData = analytics.daily_data || [];

  return (
    <div className="space-y-6">
      {/* Header avec logo TikTok */}
      <div className="bg-gradient-to-r from-pink-500 via-red-500 to-purple-600 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center">
              <Music className="text-black" size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold">TikTok Shop Analytics</h2>
              <p className="text-pink-100">
                {analytics.period?.start} - {analytics.period?.end}
              </p>
            </div>
          </div>
          {analytics.demo_mode && (
            <div className="px-4 py-2 bg-white/20 rounded-lg backdrop-blur-sm">
              <p className="text-sm font-medium">Mode Démo</p>
            </div>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<Eye size={24} />}
          title="Vues Totales"
          value={summary.total_views?.toLocaleString() || '0'}
          color="blue"
          growth="+12%"
        />
        <StatCard
          icon={<MousePointer size={24} />}
          title="Clics Produits"
          value={summary.total_clicks?.toLocaleString() || '0'}
          color="indigo"
          growth="+8%"
        />
        <StatCard
          icon={<ShoppingCart size={24} />}
          title="Achats"
          value={summary.total_purchases?.toLocaleString() || '0'}
          color="purple"
          growth="+15%"
        />
        <StatCard
          icon={<DollarSign size={24} />}
          title="GMV (Revenu)"
          value={`${summary.total_gmv?.toLocaleString() || '0'} MAD`}
          color="green"
          growth="+22%"
        />
      </div>

      {/* Taux de conversion */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Taux de Conversion</h3>
          <div className="flex items-center gap-2 text-green-600">
            <TrendingUp size={20} />
            <span className="font-semibold">{summary.average_conversion_rate?.toFixed(2) || '0'}%</span>
          </div>
        </div>

        <div className="bg-gray-100 rounded-lg h-4 overflow-hidden">
          <div
            className="bg-gradient-to-r from-pink-500 to-purple-600 h-full transition-all duration-500"
            style={{ width: `${Math.min(summary.average_conversion_rate || 0, 100)}%` }}
          />
        </div>

        <p className="text-sm text-gray-600 mt-2">
          {summary.total_clicks > 0
            ? `${summary.total_purchases} ventes sur ${summary.total_clicks} clics`
            : 'Aucune donnée disponible'}
        </p>
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Evolution des vues */}
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Évolution des Vues</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dailyData}>
              <defs>
                <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ec4899" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#ec4899" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="views"
                stroke="#ec4899"
                fillOpacity={1}
                fill="url(#colorViews)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Commerciale */}
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Performance Commerciale</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="clicks" fill="#8b5cf6" name="Clics" />
              <Bar dataKey="purchases" fill="#10b981" name="Achats" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Revenus */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h3 className="text-lg font-semibold mb-4">Évolution du GMV (Revenus)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={dailyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip formatter={(value) => `${value.toLocaleString()} MAD`} />
            <Line
              type="monotone"
              dataKey="gmv"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Conseils */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="text-purple-600" />
          Conseils pour Améliorer vos Performances
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <TipCard
            title="Meilleur Moment pour Poster"
            tip="18h-22h (engagement maximum)"
            icon="⏰"
          />
          <TipCard
            title="Durée Vidéo Idéale"
            tip="15-30 secondes (taux de complétion optimal)"
            icon="⏱️"
          />
          <TipCard
            title="Hashtags Recommandés"
            tip="#tiktokshop #maroc #fyp + hashtag produit"
            icon="#️⃣"
          />
          <TipCard
            title="Fréquence de Publication"
            tip="1-3 vidéos/jour pour l'algorithme"
            icon="📅"
          />
        </div>
      </div>
    </div>
  );
};

// Composant StatCard
const StatCard = ({ icon, title, value, color, growth }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    indigo: 'bg-indigo-100 text-indigo-600',
    purple: 'bg-purple-100 text-purple-600',
    green: 'bg-green-100 text-green-600',
    pink: 'bg-pink-100 text-pink-600'
  };

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
        {growth && (
          <span className="text-sm font-medium text-green-600">{growth}</span>
        )}
      </div>
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
};

// Composant TipCard
const TipCard = ({ title, tip, icon }) => (
  <div className="bg-white rounded-lg p-4 border border-purple-200">
    <div className="flex items-start gap-3">
      <span className="text-2xl">{icon}</span>
      <div>
        <p className="font-medium text-gray-900 mb-1">{title}</p>
        <p className="text-sm text-gray-600">{tip}</p>
      </div>
    </div>
  </div>
);

export default TikTokAnalyticsDashboard;
