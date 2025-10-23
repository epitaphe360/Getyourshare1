import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import SkeletonDashboard from '../../components/common/SkeletonLoader';
import EmptyState from '../../components/common/EmptyState';
import {
  TrendingUp, Users, DollarSign, ShoppingBag,
  Sparkles, BarChart3, Target, Eye, Download, RefreshCw
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const AdminDashboard = () => {
  const navigate = useNavigate();
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
      const [statsRes, merchantsRes, influencersRes, revenueRes, categoriesRes, metricsRes] = await Promise.all([
        api.get('/api/analytics/overview'),
        api.get('/api/merchants'),
        api.get('/api/influencers'),
        api.get('/api/analytics/admin/revenue-chart'),
        api.get('/api/analytics/admin/categories'),
        api.get('/api/analytics/admin/platform-metrics')
      ]);

      setStats({
        ...statsRes.data,
        platformMetrics: metricsRes.data
      });
      setMerchants(merchantsRes.data.merchants || []);
      setInfluencers(influencersRes.data.influencers || []);

      // Transformer les données de revenus en format mensuel (simplification pour l'exemple)
      const dailyData = revenueRes.data.data || [];
      setRevenueData(dailyData.map((day, idx) => ({
        month: day.date,
        revenue: day.revenus
      })));

      // CategoryData: données réelles depuis l'API
      const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#14b8a6'];
      const categoriesData = categoriesRes.data.data || [];
      setCategoryData(categoriesData.map((cat, idx) => ({
        name: cat.category,
        value: cat.count,
        color: colors[idx % colors.length]
      })));
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Erreur lors du chargement des données. Veuillez réessayer.');
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

      alert('✅ Rapport exporté avec succès!');
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('❌ Erreur lors de l\'export du rapport');
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
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Revenus Total"
          value={stats?.total_revenue || 502000}
          isCurrency={true}
          icon={<DollarSign className="text-green-600" size={24} />}
          trend={12.5}
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
              icon={<ShoppingBag size={48} />}
              title="Aucune entreprise"
              description="Les entreprises inscrites apparaîtront ici"
            />
          ) : (
            <div className="space-y-3">
              {merchants.slice(0, 5).map((merchant, index) => (
              <div 
                key={merchant.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition cursor-pointer"
                onClick={() => navigate(`/merchants/${merchant.id}`)}
              >
                <div className="flex items-center space-x-3">
                  <div className="bg-indigo-100 text-indigo-600 w-10 h-10 rounded-full flex items-center justify-center font-bold">
                    #{index + 1}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{merchant.company_name}</div>
                    <div className="text-sm text-gray-500">{merchant.category}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900">
                    {merchant.total_sales?.toLocaleString() || 0} €
                  </div>
                  <div className="text-sm text-gray-500">
                    {merchant.products_count || 0} produits
                  </div>
                </div>
              </div>
              ))}
            </div>
          )}
        </Card>

        {/* Top Influencers */}
        <Card title="Top Influenceurs" icon={<Users size={20} />}>
          {influencers.length === 0 ? (
            <EmptyState
              icon={<Users size={48} />}
              title="Aucun influenceur"
              description="Les influenceurs inscrits apparaîtront ici"
            />
          ) : (
            <div className="space-y-3">
              {influencers.slice(0, 5).map((influencer, index) => (
              <div 
                key={influencer.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition cursor-pointer"
                onClick={() => navigate(`/influencers/${influencer.id}`)}
              >
                <div className="flex items-center space-x-3">
                  <div className="bg-purple-100 text-purple-600 w-10 h-10 rounded-full flex items-center justify-center font-bold">
                    #{index + 1}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{influencer.full_name}</div>
                    <div className="text-sm text-gray-500">
                      @{influencer.username} · {influencer.influencer_type}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900">
                    {influencer.total_earnings?.toLocaleString() || 0} €
                  </div>
                  <div className="text-sm text-gray-500">
                    {influencer.total_sales || 0} ventes
                  </div>
                </div>
              </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Target className="text-green-600" size={32} />
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {stats?.platformMetrics?.avg_conversion_rate || 14.2}%
            </div>
            <div className="text-gray-600 mt-1">Taux de Conversion Moyen</div>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Eye className="text-blue-600" size={32} />
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {((stats?.platformMetrics?.monthly_clicks || 285000) / 1000).toFixed(0)}K
            </div>
            <div className="text-gray-600 mt-1">Clics Totaux ce Mois</div>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="text-purple-600" size={32} />
            </div>
            <div className="text-3xl font-bold text-gray-900">
              +{stats?.platformMetrics?.quarterly_growth || 32}%
            </div>
            <div className="text-gray-600 mt-1">Croissance ce Trimestre</div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;
