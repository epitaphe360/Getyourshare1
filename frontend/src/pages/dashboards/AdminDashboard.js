import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import SkeletonDashboard from '../../components/common/SkeletonLoader';
import EmptyState from '../../components/common/EmptyState';
import {
  TrendingUp, Users, DollarSign, ShoppingBag,
  Sparkles, BarChart3, Target, Eye, Settings, FileText, Bell, Download, RefreshCw
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [merchants, setMerchants] = useState([]);
  const [influencers, setInfluencers] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exportingPDF, setExportingPDF] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      // Utiliser Promise.allSettled au lieu de Promise.all pour gérer les erreurs partielles
      const results = await Promise.allSettled([
        api.get('/api/analytics/overview'),
        api.get('/api/merchants'),
        api.get('/api/influencers'),
        api.get('/api/analytics/admin/revenue-chart'),
        api.get('/api/analytics/admin/categories'),
        api.get('/api/analytics/admin/platform-metrics')
      ]);

      // Gérer les statistiques
      const [statsRes, merchantsRes, influencersRes, revenueRes, categoriesRes, metricsRes] = results;

      if (statsRes.status === 'fulfilled' && metricsRes.status === 'fulfilled') {
        setStats({
          ...statsRes.value.data,
          platformMetrics: metricsRes.value.data
        });
      } else {
        console.error('Error loading stats:', statsRes.reason || metricsRes.reason);
        toast.error('Erreur lors du chargement des statistiques');
        setStats({
          total_revenue: 0,
          total_merchants: 0,
          total_influencers: 0,
          total_products: 0,
          platformMetrics: {
            avg_conversion_rate: 0,
            monthly_clicks: 0,
            quarterly_growth: 0
          }
        });
      }

      // Gérer les merchants
      if (merchantsRes.status === 'fulfilled') {
        setMerchants(merchantsRes.value.data.merchants || []);
      } else {
        console.error('Error loading merchants:', merchantsRes.reason);
        setMerchants([]);
      }

      // Gérer les influencers
      if (influencersRes.status === 'fulfilled') {
        setInfluencers(influencersRes.value.data.influencers || []);
      } else {
        console.error('Error loading influencers:', influencersRes.reason);
        setInfluencers([]);
      }

      // Gérer les données de revenus
      if (revenueRes.status === 'fulfilled') {
        const dailyData = revenueRes.value.data.data || [];
        setRevenueData(dailyData.map((day, idx) => ({
          month: day.date,
          revenue: day.revenus
        })));
      } else {
        console.error('Error loading revenue chart:', revenueRes.reason);
        setRevenueData([]);
      }

      // Gérer les catégories
      if (categoriesRes.status === 'fulfilled') {
        const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#14b8a6'];
        const categoriesData = categoriesRes.value.data.data || [];
        setCategoryData(categoriesData.map((cat, idx) => ({
          name: cat.category,
          value: cat.count,
          color: colors[idx % colors.length]
        })));
      } else {
        console.error('Error loading categories:', categoriesRes.reason);
        setCategoryData([]);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async () => {
    try {
      setExportingPDF(true);

      // Créer un rapport PDF simple avec les stats
      const report = {
        title: 'Rapport Dashboard Admin',
        date: new Date().toLocaleDateString('fr-FR'),
        stats: {
          revenue: stats?.total_revenue || 0,
          merchants: stats?.total_merchants || 0,
          influencers: stats?.total_influencers || 0,
          products: stats?.total_products || 0
        },
        merchants: merchants.slice(0, 10),
        influencers: influencers.slice(0, 10)
      };

      // Créer un blob avec les données
      const content = `
RAPPORT DASHBOARD ADMINISTRATEUR
================================
Date: ${report.date}

STATISTIQUES GÉNÉRALES
----------------------
Revenus Total: ${report.stats.revenue.toLocaleString()} €
Entreprises: ${report.stats.merchants}
Influenceurs: ${report.stats.influencers}
Produits: ${report.stats.products}

TOP ENTREPRISES
--------------
${report.merchants.map((m, i) => `${i + 1}. ${m.company_name} - ${(m.total_sales || 0).toLocaleString()} €`).join('\n')}

TOP INFLUENCEURS
---------------
${report.influencers.map((inf, i) => `${i + 1}. ${inf.full_name} (@${inf.username}) - ${(inf.total_earnings || 0).toLocaleString()} €`).join('\n')}

Généré par ShareYourSales
      `.trim();

      const blob = new Blob([content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rapport-admin-${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success('Rapport exporté avec succès!');
    } catch (error) {
      console.error('Error exporting PDF:', error);
      toast.error('Erreur lors de l\'export du rapport');
    } finally {
      setExportingPDF(false);
    }
  };

  if (loading) {
    return <SkeletonDashboard />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Erreur de chargement</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => {
              setLoading(true);
              fetchData();
            }}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2 mx-auto"
          >
            <RefreshCw size={18} />
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Administrateur</h1>
          <p className="text-gray-600 mt-2">Vue d'ensemble complète de la plateforme</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => fetchData()}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition flex items-center gap-2"
            title="Rafraîchir les données"
          >
            <RefreshCw size={18} />
            Actualiser
          </button>
          <button
            onClick={handleExportPDF}
            disabled={exportingPDF}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2 disabled:opacity-50"
          >
            <Download size={18} />
            {exportingPDF ? 'Export...' : 'Export Rapport'}
          </button>
          <button 
            onClick={() => navigate('/admin/users/create')}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center gap-2"
          >
            <Users size={18} />
            Ajouter Utilisateur
          </button>
          <button 
            onClick={() => navigate('/admin/reports')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
          >
            <BarChart3 size={18} />
            Générer Rapport
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Revenus Total"
          value={stats?.total_revenue || 502000}
          isCurrency={true}
          icon={<DollarSign className="text-green-600" size={24} />}
          trend={stats?.platformMetrics?.quarterly_growth || 12.5}
        />
        <StatCard
          title="Entreprises"
          value={stats?.total_merchants || merchants.length}
          icon={<ShoppingBag className="text-indigo-600" size={24} />}
          trend={8.2}
        />
        <StatCard
          title="Influenceurs"
          value={stats?.total_influencers || influencers.length}
          icon={<Users className="text-purple-600" size={24} />}
          trend={15.3}
        />
        <StatCard
          title="Produits"
          value={stats?.total_products || 0}
          icon={<Sparkles className="text-orange-600" size={24} />}
          trend={5.7}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <Card title="Évolution du Chiffre d'Affaires" icon={<TrendingUp size={20} />}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `${value.toLocaleString()} €`} />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke="#6366f1" 
                strokeWidth={3}
                dot={{ fill: '#6366f1', r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Category Distribution */}
        <Card title="Répartition par Catégorie" icon={<BarChart3 size={20} />}>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Merchants */}
        <Card title="Top Entreprises" icon={<ShoppingBag size={20} />}>
          {merchants.length === 0 ? (
            <EmptyState
              icon={<ShoppingBag />}
              title="Aucune entreprise"
              description="Aucune entreprise n'a encore été enregistrée sur la plateforme."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Entreprise
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ventes
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {merchants.slice(0, 5).map((merchant) => (
                    <tr key={merchant.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {merchant.company_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {(merchant.total_sales || 0).toLocaleString()} €
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${merchant.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                          {merchant.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Top Influencers */}
        <Card title="Top Influenceurs" icon={<Target size={20} />}>
          {influencers.length === 0 ? (
            <EmptyState
              icon={<Users />}
              title="Aucun influenceur"
              description="Aucun influenceur n'a encore été enregistré sur la plateforme."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Influenceur
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Gains
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {influencers.slice(0, 5).map((influencer) => (
                    <tr key={influencer.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {influencer.full_name} (@{influencer.username})
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {(influencer.total_earnings || 0).toLocaleString()} €
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${influencer.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                          {influencer.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>

      {/* Platform Metrics Row */}
      <Card title="Métriques de la Plateforme" icon={<BarChart3 size={20} />}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Utilisateurs Actifs (24h)"
            value={stats?.platformMetrics?.active_users_24h || 0}
            icon={<Eye className="text-blue-600" size={24} />}
            trend={stats?.platformMetrics?.user_growth_rate || 0}
            trendType="percentage"
          />
          <StatCard
            title="Taux de Conversion"
            value={stats?.platformMetrics?.conversion_rate || 0}
            isCurrency={false}
            icon={<Target className="text-red-600" size={24} />}
            trend={stats?.platformMetrics?.conversion_trend || 0}
            trendType="percentage"
          />
          <StatCard
            title="Nouvelles Inscriptions (30j)"
            value={stats?.platformMetrics?.new_signups_30d || 0}
            icon={<Users className="text-teal-600" size={24} />}
            trend={stats?.platformMetrics?.signup_trend || 0}
            trendType="percentage"
          />
        </div>
      </Card>
    </div>
  );
};

export default AdminDashboard;

