import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import { DollarSign, Calendar, CheckCircle, AlertCircle, CreditCard, Building, Info } from 'lucide-react';

const PaymentSettings = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('');
  const [paymentDetails, setPaymentDetails] = useState({});
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchPaymentStatus();
  }, []);

  const fetchPaymentStatus = async () => {
    try {
      const response = await api.get('/api/influencer/payment-status');
      setPaymentStatus(response.data);
      
      // Pré-remplir le formulaire si déjà configuré
      if (response.data.payment_method) {
        setPaymentMethod(response.data.payment_method);
      }
    } catch (error) {
      console.error('Error fetching payment status:', error);
      showMessage('error', 'Erreur lors du chargement des informations');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePaymentMethod = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await api.put('/api/influencer/payment-method', {
        method: paymentMethod,
        details: paymentDetails
      });

      showMessage('success', 'Méthode de paiement configurée avec succès !');
      fetchPaymentStatus();
    } catch (error) {
      showMessage('error', error.response?.data?.detail || 'Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const handlePaymentDetailsChange = (field, value) => {
    setPaymentDetails(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuration des Paiements</h1>
        <p className="mt-2 text-gray-600">
          Configurez votre méthode de paiement pour recevoir automatiquement vos commissions
        </p>
      </div>

      {/* Message de notification */}
      {message.text && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          <div className="flex items-center">
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5 mr-2" />
            ) : (
              <AlertCircle className="w-5 h-5 mr-2" />
            )}
            {message.text}
          </div>
        </div>
      )}

      {/* Statut des paiements */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Solde Disponible</p>
              <h3 className="text-3xl font-bold mt-1">
                {paymentStatus?.balance?.toFixed(2) || '0.00'} €
              </h3>
            </div>
            <DollarSign size={40} className="opacity-80" />
          </div>
          {paymentStatus?.balance >= 50 && (
            <div className="mt-4 p-2 bg-white/20 rounded">
              <p className="text-sm">✅ Éligible au paiement automatique</p>
            </div>
          )}
        </Card>

        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">En Attente de Validation</p>
              <h3 className="text-3xl font-bold mt-1">
                {paymentStatus?.pending_validation?.toFixed(2) || '0.00'} €
              </h3>
            </div>
            <AlertCircle size={40} className="opacity-80" />
          </div>
          <div className="mt-4">
            <p className="text-sm text-orange-100">Validation automatique dans 14 jours</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Prochain Paiement</p>
              <h3 className="text-2xl font-bold mt-1">
                {paymentStatus?.next_payout_date ? (
                  new Date(paymentStatus.next_payout_date).toLocaleDateString('fr-FR', {
                    day: 'numeric',
                    month: 'long'
                  })
                ) : (
                  'Non prévu'
                )}
              </h3>
            </div>
            <Calendar size={40} className="opacity-80" />
          </div>
          {!paymentStatus?.payment_method_configured && (
            <div className="mt-4 p-2 bg-white/20 rounded">
              <p className="text-sm">⚠️ Configurez votre paiement</p>
            </div>
          )}
        </Card>
      </div>

      {/* Info sur le système de paiement automatique */}
      <Card>
        <div className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
          <Info className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-2">💰 Paiements Automatiques Activés</p>
            <ul className="space-y-1 ml-4 list-disc">
              <li>Vos ventes sont validées automatiquement après <strong>14 jours</strong> (délai de rétractation)</li>
              <li>Dès que votre solde atteint <strong>50€</strong>, un paiement est programmé</li>
              <li>Les paiements sont traités chaque <strong>vendredi à 10h</strong></li>
              <li>Vous recevez une notification par email à chaque paiement</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Formulaire de configuration */}
      <Card title="Méthode de Paiement" icon={<CreditCard size={20} />}>
        <form onSubmit={handleSavePaymentMethod} className="space-y-6">
          {/* Choix de la méthode */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Choisissez votre méthode de paiement
            </label>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* PayPal */}
              <div
                onClick={() => setPaymentMethod('paypal')}
                className={`relative border-2 rounded-lg p-4 cursor-pointer transition ${
                  paymentMethod === 'paypal'
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <CreditCard className={paymentMethod === 'paypal' ? 'text-purple-600' : 'text-gray-400'} />
                  <div>
                    <h4 className="font-semibold">PayPal</h4>
                    <p className="text-sm text-gray-600">Paiement instantané</p>
                  </div>
                </div>
                {paymentMethod === 'paypal' && (
                  <CheckCircle className="absolute top-4 right-4 text-purple-600" size={20} />
                )}
              </div>

              {/* Virement bancaire */}
              <div
                onClick={() => setPaymentMethod('bank_transfer')}
                className={`relative border-2 rounded-lg p-4 cursor-pointer transition ${
                  paymentMethod === 'bank_transfer'
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Building className={paymentMethod === 'bank_transfer' ? 'text-purple-600' : 'text-gray-400'} />
                  <div>
                    <h4 className="font-semibold">Virement Bancaire</h4>
                    <p className="text-sm text-gray-600">SEPA (1-2 jours)</p>
                  </div>
                </div>
                {paymentMethod === 'bank_transfer' && (
                  <CheckCircle className="absolute top-4 right-4 text-purple-600" size={20} />
                )}
              </div>
            </div>
          </div>

          {/* Formulaire PayPal */}
          {paymentMethod === 'paypal' && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email PayPal *
                </label>
                <input
                  type="email"
                  required
                  value={paymentDetails.email || ''}
                  onChange={(e) => handlePaymentDetailsChange('email', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="votre-email@paypal.com"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Les paiements seront envoyés sur cette adresse email PayPal
                </p>
              </div>
            </div>
          )}

          {/* Formulaire Virement */}
          {paymentMethod === 'bank_transfer' && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  IBAN *
                </label>
                <input
                  type="text"
                  required
                  value={paymentDetails.iban || ''}
                  onChange={(e) => handlePaymentDetailsChange('iban', e.target.value.toUpperCase())}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono"
                  placeholder="FR76 1234 5678 9012 3456 7890 123"
                  maxLength={34}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Code BIC/SWIFT (optionnel)
                </label>
                <input
                  type="text"
                  value={paymentDetails.bic || ''}
                  onChange={(e) => handlePaymentDetailsChange('bic', e.target.value.toUpperCase())}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono"
                  placeholder="BNPAFRPP"
                  maxLength={11}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom du titulaire du compte *
                </label>
                <input
                  type="text"
                  required
                  value={paymentDetails.account_name || ''}
                  onChange={(e) => handlePaymentDetailsChange('account_name', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Jean Dupont"
                />
              </div>

              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-xs text-yellow-800">
                  ⚠️ Les virements bancaires sont traités sous 1-2 jours ouvrés après validation
                </p>
              </div>
            </div>
          )}

          {/* Bouton de sauvegarde */}
          {paymentMethod && (
            <div className="flex justify-end">
              <Button
                type="submit"
                loading={saving}
                disabled={saving}
              >
                {saving ? 'Enregistrement...' : 'Enregistrer la méthode de paiement'}
              </Button>
            </div>
          )}
        </form>
      </Card>

      {/* Historique des paiements */}
      <Card title="Historique des Paiements">
        <p className="text-gray-600">
          Consultez l'historique de vos paiements dans la section{' '}
          <a href="/affiliate-payouts" className="text-purple-600 hover:underline">
            Mes Paiements
          </a>
        </p>
      </Card>
    </div>
  );
};

export default PaymentSettings;
