import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
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
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [salesData, setSalesData] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      // Utiliser Promise.allSettled au lieu de Promise.all
      const results = await Promise.allSettled([
        api.get('/api/analytics/overview'),
        api.get('/api/products'),
        api.get('/api/analytics/merchant/sales-chart'),
        api.get('/api/analytics/merchant/performance'),
        api.get('/api/subscriptions/current')
      ]);

      const [statsRes, productsRes, salesChartRes, performanceRes, subscriptionRes] = results;

      // Gérer les statistiques
      if (statsRes.status === 'fulfilled' && performanceRes.status === 'fulfilled') {
        setStats({
          ...statsRes.value.data,
          performance: performanceRes.value.data
        });
      } else {
        console.error('Error loading stats:', statsRes.reason || performanceRes.reason);
        toast.error('Erreur lors du chargement des statistiques');
        setStats({
          total_sales: 0,
          products_count: 0,
          affiliates_count: 0,
          roi: 0,
          performance: {
            conversion_rate: 0,
            engagement_rate: 0,
            satisfaction_rate: 0,
            monthly_goal_progress: 0
          }
        });
      }

      // Gérer l'abonnement
      if (subscriptionRes.status === 'fulfilled') {
        setSubscription(subscriptionRes.value.data);
      } else {
        console.error('Error loading subscription:', subscriptionRes.reason);
        // Abonnement par défaut gratuit
        setSubscription({
          plan_name: 'Freemium',
          max_products: 5,
          max_campaigns: 1,
          max_affiliates: 10,
          commission_fee: 0,
          status: 'active'
        });
      }

      // Gérer les produits
      if (productsRes.status === 'fulfilled') {
        setProducts(productsRes.value.data.products || []);
      } else {
        console.error('Error loading products:', productsRes.reason);
        setProducts([]);
      }

      // Gérer les données de ventes
      if (salesChartRes.status === 'fulfilled') {
        setSalesData(salesChartRes.value.data.data || []);
      } else {
        console.error('Error loading sales chart:', salesChartRes.reason);
        setSalesData([]);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Erreur lors du chargement des données');
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
          value={typeof stats?.total_sales === 'number' ? stats.total_sales : 0}
          isCurrency={true}
          icon={<DollarSign className="text-green-600" size={24} />}
          trend={stats?.sales_growth || 0}
        />
        <StatCard
          title="Produits Actifs"
          value={typeof stats?.products_count === 'number' ? stats.products_count : products.length || 0}
          icon={<Package className="text-indigo-600" size={24} />}
        />
        <StatCard
          title="Affiliés Actifs"
          value={typeof stats?.affiliates_count === 'number' ? stats.affiliates_count : 0}
          icon={<Users className="text-purple-600" size={24} />}
          trend={stats?.affiliates_growth || 0}
        />
        <StatCard
          title="ROI Marketing"
          value={typeof stats?.roi === 'number' && !isNaN(stats.roi) ? stats.roi : 0}
          suffix="%"
          icon={<TrendingUp className="text-orange-600" size={24} />}
          trend={stats?.roi_growth || 0}
        />
      </div>

      {/* Subscription Card */}
      {subscription && (
        <Card 
          title="Mon Abonnement" 
          icon={<Settings size={20} />}
          className="border-l-4 border-indigo-600"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                  subscription.plan_name === 'Enterprise' ? 'bg-purple-100 text-purple-800' :
                  subscription.plan_name === 'Premium' ? 'bg-indigo-100 text-indigo-800' :
                  subscription.plan_name === 'Standard' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {subscription.plan_name}
                </span>
                <p className="text-sm text-gray-500 mt-1">
                  Statut: <span className={`font-medium ${subscription.status === 'active' ? 'text-green-600' : 'text-red-600'}`}>
                    {subscription.status === 'active' ? 'Actif' : 'Inactif'}
                  </span>
                </p>
              </div>
              <button
                onClick={() => navigate('/pricing')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
              >
                Améliorer mon Plan
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats?.products_count || 0} / {subscription.max_products || '∞'}
                </div>
                <div className="text-sm text-gray-500 mt-1">Produits</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      ((stats?.products_count || 0) / (subscription.max_products || 1)) > 0.8 ? 'bg-red-500' : 'bg-indigo-600'
                    }`}
                    style={{ width: `${Math.min(((stats?.products_count || 0) / (subscription.max_products || 1)) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats?.campaigns_count || 0} / {subscription.max_campaigns || '∞'}
                </div>
                <div className="text-sm text-gray-500 mt-1">Campagnes</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      ((stats?.campaigns_count || 0) / (subscription.max_campaigns || 1)) > 0.8 ? 'bg-red-500' : 'bg-indigo-600'
                    }`}
                    style={{ width: `${Math.min(((stats?.campaigns_count || 0) / (subscription.max_campaigns || 1)) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats?.affiliates_count || 0} / {subscription.max_affiliates || '∞'}
                </div>
                <div className="text-sm text-gray-500 mt-1">Affiliés</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      ((stats?.affiliates_count || 0) / (subscription.max_affiliates || 1)) > 0.8 ? 'bg-red-500' : 'bg-indigo-600'
                    }`}
                    style={{ width: `${Math.min(((stats?.affiliates_count || 0) / (subscription.max_affiliates || 1)) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {subscription.commission_fee > 0 && (
              <div className="pt-4 border-t">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Frais de commission:</span> {subscription.commission_fee}%
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

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
                  {stats?.performance?.conversion_rate || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-indigo-600 h-3 rounded-full"
                  style={{ width: `${Math.min(stats?.performance?.conversion_rate || 0, 100)}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Taux d'Engagement</span>
                <span className="text-sm font-bold text-purple-600">
                  {stats?.performance?.engagement_rate || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-purple-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.engagement_rate || 0}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Satisfaction Client</span>
                <span className="text-sm font-bold text-green-600">
                  {stats?.performance?.satisfaction_rate || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.satisfaction_rate || 0}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Objectif Mensuel</span>
                <span className="text-sm font-bold text-orange-600">
                  {stats?.performance?.monthly_goal_progress || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-orange-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.monthly_goal_progress || 0}%` }}
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

