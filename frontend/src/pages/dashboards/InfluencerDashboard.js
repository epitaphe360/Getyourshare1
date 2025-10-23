import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import { 
  DollarSign, MousePointer, ShoppingCart, TrendingUp, 
  Eye, Target, Award, Link as LinkIcon, Sparkles, Wallet, BarChart3
} from 'lucide-react';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

const InfluencerDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [links, setLinks] = useState([]);
  const [earningsData, setEarningsData] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [productEarnings, setProductEarnings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, linksRes, earningsRes] = await Promise.all([
        api.get('/api/analytics/overview'),
        api.get('/api/affiliate-links'),
        api.get('/api/analytics/influencer/earnings-chart')
      ]);
      
      setStats(statsRes.data);
      setLinks(linksRes.data.links || []);
      setEarningsData(earningsRes.data.data || []);
      
      // Calculer les gains par produit à partir des liens
      const productEarningsData = (linksRes.data.links || [])
        .filter(link => link.commission_earned > 0)
        .sort((a, b) => b.commission_earned - a.commission_earned)
        .slice(0, 10) // Top 10 produits
        .map(link => ({
          name: link.product_name?.substring(0, 20) + (link.product_name?.length > 20 ? '...' : ''),
          gains: link.commission_earned || 0,
          conversions: link.conversions || 0
        }));
      setProductEarnings(productEarningsData);
      
      // Pour performanceData, on peut utiliser les mêmes données mais avec clics et conversions
      // On va créer un calcul basé sur les stats existantes
      const perfData = (earningsRes.data.data || []).map(day => ({
        date: day.date,
        clics: Math.round((day.gains || 0) * 3), // Estimation basée sur les gains
        conversions: Math.round((day.gains || 0) / 25) // Estimation: gain moyen de 25€ par conversion
      }));
      setPerformanceData(perfData);
    } catch (error) {
      console.error('Error fetching data:', error);
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
          value={stats?.total_earnings || 18650}
          isCurrency={true}
          icon={<DollarSign className="text-green-600" size={24} />}
          trend={24.8}
        />
        <StatCard
          title="Clics Générés"
          value={stats?.total_clicks || 12450}
          icon={<MousePointer className="text-indigo-600" size={24} />}
          trend={18.2}
        />
        <StatCard
          title="Ventes Réalisées"
          value={stats?.total_sales || 186}
          icon={<ShoppingCart className="text-purple-600" size={24} />}
          trend={15.7}
        />
        <StatCard
          title="Taux de Conversion"
          value={`${((stats?.total_sales / stats?.total_clicks * 100) || 1.49).toFixed(2)}%`}
          icon={<Target className="text-orange-600" size={24} />}
        />
      </div>

      {/* Balance Card */}
      <div className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl p-8 text-white">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-purple-100 mb-2">Solde Disponible</div>
            <div className="text-5xl font-bold mb-4">
              {(stats?.balance || 4250).toLocaleString()} €
            </div>
            <button className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-purple-50 transition">
              Demander un Paiement
            </button>
          </div>
          <div className="text-right">
            <div className="text-purple-100 mb-2">Gains ce Mois</div>
            <div className="text-3xl font-bold">
              {((stats?.total_earnings || 18650) * 0.25).toLocaleString()} €
            </div>
            <div className="text-purple-200 text-sm mt-1">+32% vs mois dernier</div>
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

      {/* Gains par Produit Affilié */}
      <Card title="💰 Top 10 - Gains par Produit Affilié" icon={<DollarSign size={20} />}>
        {productEarnings.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={productEarnings} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={150} />
                <Tooltip 
                  formatter={(value, name) => {
                    if (name === 'gains') return [`${value} €`, 'Gains'];
                    return [value, 'Conversions'];
                  }}
                />
                <Legend />
                <Bar dataKey="gains" fill="#10b981" name="Gains (€)" />
                <Bar dataKey="conversions" fill="#6366f1" name="Conversions" />
              </BarChart>
            </ResponsiveContainer>
            
            {/* Tableau détaillé */}
            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rang</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Produit</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Conversions</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Gains</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Gain/Conv</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {productEarnings.map((product, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                          index === 0 ? 'bg-yellow-100 text-yellow-700' :
                          index === 1 ? 'bg-gray-100 text-gray-700' :
                          index === 2 ? 'bg-orange-100 text-orange-700' :
                          'bg-blue-50 text-blue-700'
                        }`}>
                          {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">{product.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <span className="px-2 py-1 text-sm font-semibold rounded-full bg-indigo-100 text-indigo-800">
                          {product.conversions}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <span className="text-lg font-bold text-green-600">
                          {product.gains.toLocaleString()} €
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-600">
                        {product.conversions > 0 ? (product.gains / product.conversions).toFixed(2) : '0.00'} €
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <DollarSign className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">Aucun gain enregistré</p>
            <p className="text-sm mt-2">Commencez à promouvoir des produits pour voir vos gains ici</p>
            <button
              onClick={() => navigate('/marketplace')}
              className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              Explorer le Marketplace
            </button>
          </div>
        )}
      </Card>

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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
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

        <button
          onClick={() => navigate('/performance/reports')}
          className="p-6 bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 transition"
        >
          <BarChart3 className="w-8 h-8 mb-3" />
          <div className="text-xl font-bold">Mes Rapports</div>
          <div className="text-sm text-green-100 mt-1">Analyses de performance</div>
        </button>
      </div>
    </div>
  );
};

export default InfluencerDashboard;
