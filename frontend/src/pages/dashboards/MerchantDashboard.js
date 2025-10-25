import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import SkeletonDashboard from '../../components/common/SkeletonLoader';
import EmptyState from '../../components/common/EmptyState';
import {
  DollarSign, ShoppingBag, Users, TrendingUp,
  Package, Eye, Target, Award, Plus, Search, FileText, Settings, RefreshCw
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const MerchantDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [salesData, setSalesData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      const [statsRes, productsRes, salesChartRes, performanceRes] = await Promise.all([
        api.get('/api/analytics/overview'),
        api.get('/api/products'),
        api.get('/api/analytics/merchant/sales-chart'),
        api.get('/api/analytics/merchant/performance')
      ]);

      setStats({
        ...statsRes.data,
        performance: performanceRes.data
      });
      setProducts(productsRes.data.products || []);
      setSalesData(salesChartRes.data.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Erreur lors du chargement des données. Veuillez réessayer.');
    } finally {
      setLoading(false);
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
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Entreprise</h1>
          <p className="text-gray-600 mt-2">
            Bienvenue {user?.first_name} ! Suivez vos performances en temps réel
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => fetchData()}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition flex items-center gap-2"
            title="Rafraîchir les données"
          >
            <RefreshCw size={18} />
          </button>
          <button
            onClick={() => navigate('/campaigns/create')}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center gap-2"
          >
            <Plus size={18} />
            Créer Campagne
          </button>
          <button
            onClick={() => navigate('/influencers/search')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
          >
            <Search size={18} />
            Rechercher Influenceurs
          </button>
          <button
            onClick={() => navigate('/products/create')}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
          >
            <Plus size={18} />
            Ajouter Produit
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Chiffre d'Affaires"
          value={typeof stats?.total_sales === 'number' ? stats.total_sales : 145000}
          isCurrency={true}
          icon={<DollarSign className="text-green-600" size={24} />}
          trend={18.5}
        />
        <StatCard
          title="Produits Actifs"
          value={typeof stats?.products_count === 'number' ? stats.products_count : products.length || 3}
          icon={<Package className="text-indigo-600" size={24} />}
        />
        <StatCard
          title="Affiliés Actifs"
          value={typeof stats?.affiliates_count === 'number' ? stats.affiliates_count : 23}
          icon={<Users className="text-purple-600" size={24} />}
          trend={12.3}
        />
        <StatCard
          title="ROI Marketing"
          value={typeof stats?.roi === 'number' && !isNaN(stats.roi) ? stats.roi : 320.5}
          suffix="%"
          icon={<TrendingUp className="text-orange-600" size={24} />}
          trend={5.2}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Chart */}
        <Card title="Ventes des 7 Derniers Jours" icon={<TrendingUp size={20} />}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={salesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" orientation="left" stroke="#6366f1" />
              <YAxis yAxisId="right" orientation="right" stroke="#10b981" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="ventes" fill="#6366f1" name="Ventes" />
              <Bar yAxisId="right" dataKey="revenus" fill="#10b981" name="Revenus (€)" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Performance Overview */}
        <Card title="Vue d'Ensemble Performance" icon={<Target size={20} />}>
          <div className="space-y-6 py-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Taux de Conversion</span>
                <span className="text-sm font-bold text-indigo-600">
                  {stats?.performance?.conversion_rate || 14.2}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-indigo-600 h-3 rounded-full"
                  style={{ width: `${Math.min(stats?.performance?.conversion_rate || 14.2, 100)}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Taux d'Engagement</span>
                <span className="text-sm font-bold text-purple-600">
                  {stats?.performance?.engagement_rate || 68}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-purple-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.engagement_rate || 68}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Satisfaction Client</span>
                <span className="text-sm font-bold text-green-600">
                  {stats?.performance?.satisfaction_rate || 92}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.satisfaction_rate || 92}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Objectif Mensuel</span>
                <span className="text-sm font-bold text-orange-600">
                  {stats?.performance?.monthly_goal_progress || 78}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-orange-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.monthly_goal_progress || 78}%` }}
                ></div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Products Performance */}
      <Card title="Top Produits Performants" icon={<Award size={20} />}>
        {products.length === 0 ? (
          <EmptyState
            icon={<Package size={48} />}
            title="Aucun produit"
            description="Ajoutez vos premiers produits pour commencer"
            action={{
              label: "Ajouter un Produit",
              onClick: () => navigate('/products/create')
            }}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Produit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Catégorie
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vues
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Clics
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ventes
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Revenus
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.slice(0, 5).map((product) => (
                <tr key={product.id} className="hover:bg-gray-50 cursor-pointer">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{product.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{product.category || 'Non spécifié'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.views || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.clicks || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.sales || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {(product.revenue || 0).toLocaleString()} €
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {products.length > 5 && (
          <div className="mt-4 text-right">
            <button
              onClick={() => navigate('/products')}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-900"
            >
              Voir tous les produits →
            </button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default MerchantDashboard;

