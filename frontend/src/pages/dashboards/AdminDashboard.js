import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import SkeletonDashboard from '../../components/common/SkeletonLoader';
import { 
  TrendingUp, Users, DollarSign, ShoppingBag, 
  Sparkles, BarChart3, Target, Eye, Settings, FileText, Bell
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

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
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
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <SkeletonDashboard />;
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
          <button 
            onClick={() => window.print()}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
          >
            <TrendingUp size={18} />
            Export PDF
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
        </Card>

        {/* Top Influencers */}
        <Card title="Top Influenceurs" icon={<Users size={20} />}>
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

      {/* Quick Actions for Admin */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <button
          onClick={() => navigate('/admin/users')}
          className="p-6 bg-gradient-to-br from-indigo-500 to-indigo-600 text-white rounded-xl hover:from-indigo-600 hover:to-indigo-700 transition"
        >
          <Users className="w-8 h-8 mb-3" />
          <div className="text-xl font-bold">Gestion Utilisateurs</div>
          <div className="text-sm text-indigo-100 mt-1">Admins, Marchands, Influenceurs</div>
        </button>

        <button
          onClick={() => navigate('/admin/gateway-stats')}
          className="p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 transition"
        >
          <DollarSign className="w-8 h-8 mb-3" />
          <div className="text-xl font-bold">Paiements Gateway</div>
          <div className="text-sm text-purple-100 mt-1">CMI, PayZen, SG Maroc</div>
        </button>

        <button
          onClick={() => navigate('/settings/company')}
          className="p-6 bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 transition"
        >
          <Settings className="w-8 h-8 mb-3" />
          <div className="text-xl font-bold">Configuration</div>
          <div className="text-sm text-green-100 mt-1">Paramètres plateforme</div>
        </button>

        <button
          onClick={() => navigate('/admin/invoices')}
          className="p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl hover:from-orange-600 hover:to-orange-700 transition"
        >
          <FileText className="w-8 h-8 mb-3" />
          <div className="text-xl font-bold">Facturation</div>
          <div className="text-sm text-orange-100 mt-1">Gérer les factures</div>
        </button>
      </div>
    </div>
  );
};

export default AdminDashboard;
