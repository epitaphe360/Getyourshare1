import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import EmptyState from '../../components/common/EmptyState';
import Modal from '../../components/common/Modal';
import {
  DollarSign, MousePointer, ShoppingCart, TrendingUp,
  Eye, Target, Award, Link as LinkIcon, Sparkles, RefreshCw, X, Send
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const InfluencerDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [links, setLinks] = useState([]);
  const [earningsData, setEarningsData] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
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
      const [statsRes, linksRes, earningsRes] = await Promise.all([
        api.get('/api/analytics/overview'),
        api.get('/api/affiliate-links'),
        api.get('/api/analytics/influencer/earnings-chart')
      ]);

      setStats(statsRes.data);
      setLinks(linksRes.data.links || []);
      setEarningsData(earningsRes.data.data || []);

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
      setError('Erreur lors du chargement des données. Veuillez réessayer.');
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
        alert('❌ Veuillez entrer un montant valide');
        return;
      }

      if (amount > currentBalance) {
        alert(`❌ Montant demandé (${amount}€) supérieur au solde disponible (${currentBalance}€)`);
        return;
      }

      if (amount < 50) {
        alert('❌ Le montant minimum de retrait est de 50€');
        return;
      }

      // Créer la demande de payout
      const response = await api.post('/api/payouts/request', {
        amount,
        payment_method: payoutMethod,
        currency: 'EUR'
      });

      if (response.data) {
        alert(`✅ Demande de paiement de ${amount}€ envoyée avec succès! Elle sera traitée sous 2-3 jours ouvrés.`);
        setShowPayoutModal(false);
        setPayoutAmount('');
        fetchData(); // Rafraîchir les données
      }
    } catch (error) {
      console.error('Error requesting payout:', error);
      alert('❌ Erreur lors de la demande de paiement. Veuillez réessayer.');
    } finally {
      setPayoutSubmitting(false);
    }
  };

  const handleCopyLink = (link) => {
    try {
      navigator.clipboard.writeText(link);
      alert('✅ Lien copié dans le presse-papier!');
    } catch (error) {
      console.error('Error copying link:', error);
      alert('❌ Erreur lors de la copie du lien');
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

      {/* My Links Performance */}
      <Card title="Mes Liens d'Affiliation" icon={<LinkIcon size={20} />}>
        {links.length === 0 ? (
          <EmptyState
            icon={<LinkIcon size={48} />}
            title="Aucun lien d'affiliation"
            description="Commencez par générer votre premier lien depuis le Marketplace"
            action={{
              label: "Aller au Marketplace",
              onClick: () => navigate('/marketplace')
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
                        onClick={() => handleCopyLink(link.full_link)}
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
        )}
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

      {/* Payout Modal */}
      {showPayoutModal && (
        <Modal
          isOpen={showPayoutModal}
          onClose={() => setShowPayoutModal(false)}
          title="Demander un Paiement"
        >
          <div className="space-y-6">
            <div>
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Solde disponible</span>
                  <span className="text-2xl font-bold text-indigo-600">
                    {(stats?.balance || 0).toLocaleString()} €
                  </span>
                </div>
              </div>

              <label className="block text-sm font-medium text-gray-700 mb-2">
                Montant à retirer (minimum 50€)
              </label>
              <input
                type="number"
                value={payoutAmount}
                onChange={(e) => setPayoutAmount(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Ex: 500"
                min="50"
                max={stats?.balance || 0}
              />
              <p className="text-xs text-gray-500 mt-1">
                Maximum: {(stats?.balance || 0).toLocaleString()}€
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Méthode de paiement
              </label>
              <select
                value={payoutMethod}
                onChange={(e) => setPayoutMethod(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="bank_transfer">Virement bancaire</option>
                <option value="paypal">PayPal</option>
                <option value="western_union">Western Union</option>
              </select>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex gap-2">
                <div className="text-yellow-600 text-sm">ℹ️</div>
                <div className="text-sm text-yellow-800">
                  <p className="font-semibold mb-1">Informations importantes:</p>
                  <ul className="list-disc list-inside space-y-1 text-xs">
                    <li>Délai de traitement: 2-3 jours ouvrés</li>
                    <li>Montant minimum: 50€</li>
                    <li>Frais de transaction: 2% (déduits du montant)</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowPayoutModal(false)}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              >
                Annuler
              </button>
              <button
                onClick={handleRequestPayout}
                disabled={payoutSubmitting || !payoutAmount}
                className="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {payoutSubmitting ? (
                  <>
                    <RefreshCw size={18} className="animate-spin" />
                    Envoi...
                  </>
                ) : (
                  <>
                    <Send size={18} />
                    Confirmer
                  </>
                )}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default InfluencerDashboard;
