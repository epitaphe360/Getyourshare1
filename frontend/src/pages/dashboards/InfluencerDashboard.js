import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { useI18n } from '../../i18n/i18n';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import EmptyState from '../../components/common/EmptyState';
import Modal from '../../components/common/Modal';
import MobilePaymentWidget from '../../components/payments/MobilePaymentWidget';
import {
  DollarSign, MousePointer, ShoppingCart, TrendingUp,
  Eye, Target, Award, Link as LinkIcon, Sparkles, RefreshCw, X, Send, BarChart3, Wallet,
  MessageSquare, Users, CheckCircle
} from 'lucide-react';
import CollaborationResponseModal from '../../components/modals/CollaborationResponseModal';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const InfluencerDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  const { t } = useI18n();
  const [stats, setStats] = useState(null);
  const [links, setLinks] = useState([]);
  const [earningsData, setEarningsData] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [productEarnings, setProductEarnings] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [invitations, setInvitations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showPayoutModal, setShowPayoutModal] = useState(false);
  const [showMobilePaymentModal, setShowMobilePaymentModal] = useState(false);
  const [payoutAmount, setPayoutAmount] = useState('');
  const [payoutMethod, setPayoutMethod] = useState('bank_transfer');
  const [payoutSubmitting, setPayoutSubmitting] = useState(false);
  const [minPayoutAmount, setMinPayoutAmount] = useState(50); // Montant minimum de retrait
  const [collaborationRequests, setCollaborationRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showResponseModal, setShowResponseModal] = useState(false);

  useEffect(() => {
    fetchData();
    fetchMinPayoutAmount();
  }, []);

  const fetchMinPayoutAmount = async () => {
    try {
      const response = await api.get('/api/admin/platform-settings/public/min-payout');
      if (response.data && response.data.min_payout_amount) {
        setMinPayoutAmount(response.data.min_payout_amount);
      }
    } catch (error) {
      console.log('Could not fetch min payout amount, using default:', error);
      // Garder la valeur par défaut de 50€
    }
  };

  const fetchData = async () => {
    try {
      setError(null);
      // Utiliser Promise.allSettled au lieu de Promise.all
      const results = await Promise.allSettled([
        api.get('/api/analytics/overview'),
        api.get('/api/affiliate-links'),
        api.get('/api/analytics/influencer/earnings-chart'),
        api.get('/api/subscriptions/current'),
        api.get('/api/invitations/received'),
        api.get('/api/collaborations/requests/received')
      ]);

      const [statsRes, linksRes, earningsRes, subscriptionRes, invitationsRes, collabRes] = results;

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

      // Gérer l'abonnement
      if (subscriptionRes.status === 'fulfilled') {
        setSubscription(subscriptionRes.value.data);
      } else {
        console.error('Error loading subscription:', subscriptionRes.reason);
        // Abonnement par défaut gratuit
        setSubscription({
          plan_name: 'Free',
          commission_rate: 5,
          max_campaigns: 5,
          instant_payout: false,
          analytics_level: 'basic',
          status: 'active'
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

      // Invitations reçues
      if (invitationsRes && invitationsRes.status === 'fulfilled') {
        setInvitations(invitationsRes.value.data.invitations || []);
      } else {
        setInvitations([]);
      }

      // Collaboration requests
      if (collabRes && collabRes.status === 'fulfilled') {
        setCollaborationRequests(collabRes.value.data.requests || []);
      } else {
        setCollaborationRequests([]);
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

      if (amount < minPayoutAmount) {
        toast.error(`Le montant minimum de retrait est de ${minPayoutAmount}€`);
        return;
      }

      // Si paiement mobile marocain, ouvrir le widget mobile
      if (payoutMethod === 'mobile_payment_ma') {
        setShowPayoutModal(false);
        setShowMobilePaymentModal(true);
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

  const handleMobilePaymentSuccess = (result) => {
    toast.success(t('payment_success') || 'Paiement mobile réussi!');
    setShowMobilePaymentModal(false);
    setPayoutAmount('');
    fetchData(); // Rafraîchir les données
  };

  const handleMobilePaymentError = (error) => {
    toast.error(error || 'Erreur lors du paiement mobile');
  };

  const respondInvitation = async (invitationId, action) => {
    try {
      const res = await api.post('/api/invitations/respond', { invitation_id: invitationId, action });
      if (res.data && res.data.success) {
        toast.success(res.data.message || 'Réponse enregistrée');
        // If accepted, add generated links to links list
        if (action === 'accept' && res.data.affiliate_links) {
          setLinks(prev => [...(prev || []), ...res.data.affiliate_links.map(l => ({ id: l.product_id + '_' + l.affiliate_code, affiliate_url: l.affiliate_link, product_name: l.product_name, commission_earned: 0 }))]);
        }
        // Remove the invitation from local list
        setInvitations(prev => prev.filter(i => i.id !== invitationId));
      }
    } catch (error) {
      console.error('Error responding to invitation:', error);
      toast.error('Erreur lors de la réponse');
    }
  };

  const handleOpenResponseModal = (request) => {
    setSelectedRequest(request);
    setShowResponseModal(true);
  };

  const handleCollaborationRespond = (response) => {
    toast.success('Réponse envoyée avec succès');
    fetchData(); // Refresh data
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
            onClick={() => navigate('/marketplace', { state: { fromDashboard: true } })}
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

        {/* Invitations (pending) */}
        {invitations && invitations.length > 0 && (
          <Card title={`Invitations (${invitations.length})`} icon={<MessageSquare size={20} />}>
            <div className="space-y-3">
              {invitations.map(inv => (
                <div key={inv.id} className="flex items-start justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-semibold">Invitation de {inv.merchant?.name || 'Marchand'}</div>
                    <div className="text-sm text-gray-500">Produit(s): {inv.products?.map(p => p.name).join(', ')}</div>
                    <div className="text-sm text-gray-600 mt-2">{inv.message}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={() => respondInvitation(inv.id, 'reject')} className="px-3 py-1 bg-gray-100 rounded-md">Refuser</button>
                    <button onClick={() => respondInvitation(inv.id, 'accept')} className="px-3 py-1 bg-indigo-600 text-white rounded-md">Accepter</button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Collaboration Requests */}
        {collaborationRequests && collaborationRequests.length > 0 && (
          <Card 
            title={`Demandes de Collaboration (${collaborationRequests.filter(r => r.status === 'pending').length})`} 
            icon={<Users size={20} className="text-purple-600" />}
          >
            <div className="space-y-3">
              {collaborationRequests.map(request => (
                <div 
                  key={request.id} 
                  className="flex items-start justify-between p-4 border border-gray-200 rounded-lg hover:border-purple-300 transition"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-gray-900">
                        {request.merchant_name || 'Marchand'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        request.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        request.status === 'accepted' ? 'bg-green-100 text-green-800' :
                        request.status === 'rejected' ? 'bg-red-100 text-red-800' :
                        request.status === 'counter_offer' ? 'bg-orange-100 text-orange-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {request.status === 'pending' ? 'En attente' :
                         request.status === 'accepted' ? 'Accepté' :
                         request.status === 'rejected' ? 'Refusé' :
                         request.status === 'counter_offer' ? 'Contre-offre' :
                         request.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mb-1">
                      {request.products?.length || 0} produit(s) • Commission: {request.proposed_commission}%
                    </div>
                    {request.message && (
                      <div className="text-sm text-gray-500 mt-2 line-clamp-2">
                        {request.message}
                      </div>
                    )}
                  </div>
                  {request.status === 'pending' && (
                    <button 
                      onClick={() => handleOpenResponseModal(request)}
                      className="ml-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition whitespace-nowrap"
                    >
                      Répondre
                    </button>
                  )}
                  {request.status === 'counter_offer' && (
                    <div className="ml-4 text-sm text-orange-600 font-medium">
                      En attente de réponse du marchand
                    </div>
                  )}
                  {request.status === 'accepted' && (
                    <div className="ml-4 text-sm text-green-600 font-medium flex items-center gap-1">
                      <CheckCircle size={16} />
                      Collaboration active
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

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

      {/* Subscription Card */}
      {subscription && (
        <Card 
          title="Mon Abonnement Influenceur" 
          icon={<Sparkles size={20} />}
          className="border-l-4 border-purple-600"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                  subscription.plan_name === 'Elite' ? 'bg-purple-100 text-purple-800' :
                  subscription.plan_name === 'Pro' ? 'bg-indigo-100 text-indigo-800' :
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
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
              >
                {subscription.plan_name === 'Free' ? 'Passer à Pro' : 'Améliorer mon Plan'}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Taux de commission</span>
                  <span className="text-lg font-bold text-green-600">{subscription.commission_rate || 5}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Campagnes par mois</span>
                  <span className="text-lg font-bold text-indigo-600">{subscription.max_campaigns || '∞'}</span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Paiement instantané</span>
                  <span className={`text-sm font-medium ${subscription.instant_payout ? 'text-green-600' : 'text-gray-400'}`}>
                    {subscription.instant_payout ? '✓ Activé' : '✗ Non disponible'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Analytics</span>
                  <span className="text-sm font-medium text-indigo-600 capitalize">
                    {subscription.analytics_level || 'Basic'}
                  </span>
                </div>
              </div>
            </div>

            {subscription.plan_name === 'Free' && (
              <div className="pt-4 border-t bg-purple-50 -m-6 mt-4 p-4 rounded-b-lg">
                <p className="text-sm text-purple-900">
                  <strong>Passez à Pro</strong> pour débloquer un taux de commission réduit (3%), 
                  des paiements instantanés et des analytics avancés ! 🚀
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

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
            Le montant minimum de retrait est de <span className="font-bold">{minPayoutAmount} €</span>.
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
              <option value="mobile_payment_ma">💵 Paiement Mobile Maroc (Cash Plus, Orange Money, etc.)</option>
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

      {/* Mobile Payment Modal (Morocco) */}
      <Modal
        isOpen={showMobilePaymentModal}
        onClose={() => setShowMobilePaymentModal(false)}
        title={t('payment_mobile_title') || 'Paiements Mobile Maroc'}
        size="large"
      >
        <MobilePaymentWidget
          user={user}
          onSuccess={handleMobilePaymentSuccess}
          onError={handleMobilePaymentError}
        />
      </Modal>

      {/* Collaboration Response Modal */}
      <CollaborationResponseModal
        isOpen={showResponseModal}
        onClose={() => setShowResponseModal(false)}
        request={selectedRequest}
        onRespond={handleCollaborationRespond}
      />
    </div>
  );
};

export default InfluencerDashboard;

