import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import EmptyState from '../../components/common/EmptyState';
import Modal from '../../components/common/Modal';
import {
  DollarSign, MousePointer, ShoppingCart, TrendingUp,
  Eye, Target, Award, Link as LinkIcon, Sparkles, RefreshCw, X, Send, BarChart3, Wallet
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
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
  const [productEarnings, setProductEarnings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showPayoutModal, setShowPayoutModal] = useState(false);
  const [payoutAmount, setPayoutAmount] = useState('');
  const [payoutMethod, setPayoutMethod] = useState('bank_transfer');
  const [payoutSubmitting, setPayoutSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
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
        // Calculer les gains par produit à partir des liens (Logique de HEAD)
        const productEarningsData = (linksRes.value.data.links || [])
          .filter(link => link.commission_earned > 0)
          .sort((a, b) => b.commission_earned - a.commission_earned)
          .slice(0, 10) // Top 10 produits
          .map(link => ({
            name: link.product_name?.substring(0, 20) + (link.product_name?.length > 20 ? '...' : ''),
            gains: link.commission_earned || 0,
            conversions: link.conversions || 0
          }));
        setProductEarnings(productEarningsData);
      } else {
        console.error('Error loading links:', linksRes.reason);
        setLinks([]);
        setProductEarnings([]);
      }

      // Gérer les données de gains
      if (earningsRes.status === 'fulfilled') {
        const earningsDataResult = earningsRes.value.data.data || [];
        setEarningsData(earningsDataResult);

        // Créer les données de performance basées sur les gains réels
        const perfData = earningsDataResult.map(day => ({
          date: day.date,
          clics: Math.round((day.gains || 0) * 3), // Estimation basée sur les gains
          conversions: Math.round((day.gains || 0) / 25) // Estimation: gain moyen de 25€ par conversion
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

  const handleRequestPayout = async () => {
    try {
      setPayoutSubmitting(true);

      const amount = parseFloat(payoutAmount);
      const currentBalance = stats?.balance || 0;

      // Validations
      if (isNaN(amount) || amount <= 0) {
        toast.error('Veuillez entrer un montant valide');
        return;
      }

      if (amount > currentBalance) {
        toast.error(`Montant demandé (${amount}€) supérieur au solde disponible (${currentBalance}€)`);
        return;
      }

      if (amount < 50) {
        toast.error('Le montant minimum de retrait est de 50€');
        return;
      }

      // Créer la demande de payout
      const response = await api.post('/api/payouts/request', {
        amount,
        payment_method: payoutMethod,
        currency: 'EUR'
      });

      if (response.data) {
        toast.success(`Demande de paiement de ${amount}€ envoyée avec succès! Elle sera traitée sous 2-3 jours ouvrés.`);
        setShowPayoutModal(false);
        setPayoutAmount('');
        fetchData(); // Rafraîchir les données
      }
    } catch (error) {
      console.error('Error requesting payout:', error);
      toast.error('Erreur lors de la demande de paiement. Veuillez réessayer.');
    } finally {
      setPayoutSubmitting(false);
    }
  };

  const handleCopyLink = (link) => {
    try {
      navigator.clipboard.writeText(link);
      toast.success('Lien copié dans le presse-papier!');
    } catch (error) {
      console.error('Error copying link:', error);
      toast.error('Erreur lors de la copie du lien');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
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
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Influenceur</h1>
          <p className="text-gray-600 mt-2">
            Bienvenue {user?.first_name} ! Voici vos performances 🚀
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
              onClick={() => setShowPayoutModal(true)}
              className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-purple-50 transition flex items-center gap-2"
            >
              <Send size={18} />
              Demander un Paiement
            </button>
          </div>
          <div className="text-right">
            <div className="text-purple-100 mb-2">Gains ce Mois</div>
            <div className="text-3xl font-bold">
              {((stats?.total_earnings || 0) * 0.25).toLocaleString()} €
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
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Performance Chart */}
        <Card title="Performance (Clics vs Conversions)" icon={<Target size={20} />}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" stroke="#6366f1" />
              <YAxis yAxisId="right" orientation="right" stroke="#f59e0b" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="clics" stroke="#6366f1" activeDot={{ r: 8 }} />
              <Line yAxisId="right" type="monotone" dataKey="conversions" stroke="#f59e0b" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Product Earnings and Links */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Product Earnings */}
        <Card title="Top Produits (Gains)" icon={<Wallet size={20} />}>
          {productEarnings.length === 0 ? (
            <EmptyState
              icon={<Sparkles />}
              title="Aucun gain enregistré"
              description="Commencez à partager vos liens d'affiliation pour générer des gains."
            />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={productEarnings}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={100} />
                <Tooltip formatter={(value) => `${value.toLocaleString()} €`} />
                <Legend />
                <Bar dataKey="gains" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        {/* Affiliate Links Table */}
        <Card title="Mes Liens d'Affiliation" icon={<LinkIcon size={20} />}>
          {links.length === 0 ? (
            <EmptyState
              icon={<LinkIcon />}
              title="Aucun lien d'affiliation"
              description="Créez votre premier lien depuis la Marketplace pour commencer à gagner des commissions."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Produit
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Gains (€)
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Clics
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {links.slice(0, 5).map((link) => (
                    <tr key={link.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {link.product_name || 'Produit Inconnu'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {(link.commission_earned || 0).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {link.clicks || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => handleCopyLink(link.affiliate_url)}
                          className="text-indigo-600 hover:text-indigo-900 font-medium"
                        >
                          Copier Lien
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className="mt-4 text-right">
            <button
              onClick={() => navigate('/affiliate-links')}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-900"
            >
              Voir tous les liens →
            </button>
          </div>
        </Card>
      </div>

      {/* Payout Modal */}
      <Modal 
        isOpen={showPayoutModal} 
        onClose={() => setShowPayoutModal(false)}
        title="Demander un Paiement"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Votre solde actuel est de <span className="font-bold">{(stats?.balance || 0).toLocaleString()} €</span>.
            Le montant minimum de retrait est de 50 €.
          </p>
          <div>
            <label htmlFor="payoutAmount" className="block text-sm font-medium text-gray-700">
              Montant à Retirer (€)
            </label>
            <input
              type="number"
              id="payoutAmount"
              value={payoutAmount}
              onChange={(e) => setPayoutAmount(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              placeholder="Ex: 1000"
              min="50"
              step="0.01"
            />
          </div>
          <div>
            <label htmlFor="payoutMethod" className="block text-sm font-medium text-gray-700">
              Méthode de Paiement
            </label>
            <select
              id="payoutMethod"
              value={payoutMethod}
              onChange={(e) => setPayoutMethod(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            >
              <option value="bank_transfer">Virement Bancaire (SEPA)</option>
              <option value="paypal">PayPal</option>
            </select>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={() => setShowPayoutModal(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Annuler
            </button>
            <button
              onClick={handleRequestPayout}
              disabled={payoutSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50 flex items-center"
            >
              {payoutSubmitting ? 'Envoi...' : 'Confirmer la Demande'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default InfluencerDashboard;

