import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import {
  DollarSign, MousePointer, ShoppingCart, TrendingUp,
  Eye, Target, Award, Link as LinkIcon, Sparkles
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const InfluencerDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [links, setLinks] = useState([]);
  const [earningsData, setEarningsData] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Utiliser Promise.allSettled au lieu de Promise.all
      const results = await Promise.allSettled([
        api.get('/api/analytics/overview'),
        api.get('/api/affiliate-links'),
        api.get('/api/analytics/influencer/earnings-chart')
      ]);

      const [statsRes, linksRes, earningsRes] = results;

      // Gérer les statistiques
      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value.data);
      } else {
        console.error('Error loading stats:', statsRes.reason);
        toast.error('Erreur lors du chargement des statistiques');
        setStats({
          total_earnings: 0,
          total_clicks: 0,
          total_sales: 0,
          balance: 0
        });
      }

      // Gérer les liens
      if (linksRes.status === 'fulfilled') {
        setLinks(linksRes.value.data.links || []);
      } else {
        console.error('Error loading links:', linksRes.reason);
        setLinks([]);
      }

      // Gérer les données de gains
      if (earningsRes.status === 'fulfilled') {
        const earningsDataResult = earningsRes.value.data.data || [];
        setEarningsData(earningsDataResult);

        // Créer les données de performance basées sur les gains réels
        const perfData = earningsDataResult.map(day => ({
          date: day.date,
          clics: day.clics || 0,
          conversions: day.conversions || 0
        }));
        setPerformanceData(perfData);
      } else {
        console.error('Error loading earnings:', earningsRes.reason);
        setEarningsData([]);
        setPerformanceData([]);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

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
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Influenceur</h1>
          <p className="text-gray-600 mt-2">
            Bienvenue {user?.first_name} ! Voici vos performances 🚀
          </p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={() => navigate('/marketplace')}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            🛍️ Marketplace
          </button>
          <button 
            onClick={() => navigate('/ai-marketing')}
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition"
          >
            ✨ IA Marketing
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Gains Totaux"
          value={stats?.total_earnings || 0}
          isCurrency={true}
          icon={<DollarSign className="text-green-600" size={24} />}
          trend={stats?.earnings_growth || 0}
        />
        <StatCard
          title="Clics Générés"
          value={stats?.total_clicks || 0}
          icon={<MousePointer className="text-indigo-600" size={24} />}
          trend={stats?.clicks_growth || 0}
        />
        <StatCard
          title="Ventes Réalisées"
          value={stats?.total_sales || 0}
          icon={<ShoppingCart className="text-purple-600" size={24} />}
          trend={stats?.sales_growth || 0}
        />
        <StatCard
          title="Taux de Conversion"
          value={(() => {
            const clicks = stats?.total_clicks || 0;
            const sales = stats?.total_sales || 0;
            if (clicks === 0) return '0.00%';
            return `${((sales / clicks) * 100).toFixed(2)}%`;
          })()}
          icon={<Target className="text-orange-600" size={24} />}
        />
      </div>

      {/* Balance Card */}
      <div className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl p-8 text-white">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-purple-100 mb-2">Solde Disponible</div>
            <div className="text-5xl font-bold mb-4">
              {(stats?.balance || 0).toLocaleString()} €
            </div>
            <button
              onClick={() => {
                toast.info('Fonctionnalité de demande de paiement bientôt disponible');
              }}
              className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-purple-50 transition"
              title="Demander un paiement (bientôt disponible)"
            >
              Demander un Paiement
            </button>
          </div>
          <div className="text-right">
            <div className="text-purple-100 mb-2">Gains ce Mois</div>
            <div className="text-3xl font-bold">
              {((stats?.total_earnings || 0) * 0.25).toLocaleString()} €
            </div>
            <div className="text-purple-200 text-sm mt-1">
              {stats?.monthly_growth ? `+${stats.monthly_growth}%` : '+0%'} vs mois dernier
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Earnings Chart */}
        <Card title="Évolution des Gains (7 jours)" icon={<TrendingUp size={20} />}>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={earningsData}>
              <defs>
                <linearGradient id="colorGains" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => `${value} €`} />
              <Area 
                type="monotone" 
                dataKey="gains" 
                stroke="#10b981" 
                fillOpacity={1} 
                fill="url(#colorGains)" 
                name="Gains (€)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Performance Chart */}
        <Card title="Clics & Conversions" icon={<Eye size={20} />}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="clics" 
                stroke="#6366f1" 
                strokeWidth={2}
                name="Clics"
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="conversions" 
                stroke="#10b981" 
                strokeWidth={2}
                name="Conversions"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* My Links Performance */}
      <Card title="Mes Liens d'Affiliation" icon={<LinkIcon size={20} />}>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Produit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Lien Court
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Clics
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conversions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Taux Conv.
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Commission
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {links.map((link) => (
                <tr key={link.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{link.product_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded">{link.short_link}</code>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {link.clicks?.toLocaleString() || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {link.conversions?.toLocaleString() || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      (link.conversion_rate || 0) > 10 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {(link.conversion_rate || 0).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600">
                    {(link.commission_earned || 0).toLocaleString()} €
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button 
                      onClick={() => navigator.clipboard.writeText(link.full_link)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Copier
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <button
          onClick={() => navigate('/marketplace')}
          className="p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 transition"
        >
          <Sparkles className="w-8 h-8 mb-3" />
          <div className="text-xl font-bold">Explorer Marketplace</div>
          <div className="text-sm text-purple-100 mt-1">Découvrir nouveaux produits</div>
        </button>

        <button
          onClick={() => navigate('/tracking-links')}
          className="p-6 bg-gradient-to-br from-indigo-500 to-indigo-600 text-white rounded-xl hover:from-indigo-600 hover:to-indigo-700 transition"
        >
          <LinkIcon className="w-8 h-8 mb-3" />
          <div className="text-xl font-bold">Générer Lien</div>
          <div className="text-sm text-indigo-100 mt-1">Créer lien d'affiliation</div>
        </button>

        <button
          onClick={() => navigate('/ai-marketing')}
          className="p-6 bg-gradient-to-br from-pink-500 to-rose-600 text-white rounded-xl hover:from-pink-600 hover:to-rose-700 transition"
        >
          <Award className="w-8 h-8 mb-3" />
          <div className="text-xl font-bold">IA Marketing</div>
          <div className="text-sm text-pink-100 mt-1">Optimiser vos campagnes</div>
        </button>
      </div>
    </div>
  );
};

export default InfluencerDashboard;
