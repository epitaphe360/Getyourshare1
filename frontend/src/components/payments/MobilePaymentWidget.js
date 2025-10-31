/**
 * Widget de Paiements Mobiles Marocains
 * Interface pour demander un paiement via Cash Plus, Orange Money, etc.
 */

import React, { useState, useEffect } from 'react';
import { useI18n } from '../../i18n/i18n';
import api from '../../services/api';

const MobilePaymentWidget = ({ user, onSuccess, onError }) => {
  const { t } = useI18n();
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState('');

  // Charger les opérateurs disponibles
  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await api.get('/api/mobile-payments-ma/providers');
      setProviders(response.data);
      if (response.data.length > 0) {
        setSelectedProvider(response.data[0]);
      }
    } catch (error) {
      console.error('Erreur chargement opérateurs:', error);
    }
  };

  const validatePhone = (phone) => {
    const pattern = /^(?:\+212|0)[5-7]\d{8}$/;
    return pattern.test(phone);
  };

  const handlePhoneChange = (e) => {
    const value = e.target.value;
    setPhoneNumber(value);

    if (value && !validatePhone(value)) {
      setValidationError(t('error_invalid_phone'));
    } else {
      setValidationError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!phoneNumber || !validatePhone(phoneNumber)) {
      setValidationError(t('error_invalid_phone'));
      return;
    }

    const amountNum = parseFloat(amount);
    if (!amountNum || amountNum < selectedProvider.min_amount) {
      setValidationError(t('error_min_amount', { min: selectedProvider.min_amount }));
      return;
    }

    if (amountNum > selectedProvider.max_amount) {
      setValidationError(t('error_max_amount', { max: selectedProvider.max_amount }));
      return;
    }

    setLoading(true);
    setValidationError('');

    try {
      const response = await api.post('/api/mobile-payments-ma/payout', {
        user_id: user.id,
        amount: amountNum,
        phone_number: phoneNumber,
        provider: selectedProvider.id,
        reference: `PAYOUT-${Date.now()}`,
      });

      if (response.data.status === 'completed') {
        onSuccess && onSuccess(response.data);
        // Reset form
        setPhoneNumber('');
        setAmount('');
      } else {
        onError && onError(response.data.message);
      }
    } catch (error) {
      console.error('Erreur paiement:', error);
      onError && onError(error.response?.data?.detail || t('error_server'));
    } finally {
      setLoading(false);
    }
  };

  if (providers.length === 0) {
    return <div className="text-center py-8">{t('loading')}</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          {t('payment_mobile_title')}
        </h3>
        <p className="text-gray-600">
          {t('payment_choose_provider')}
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Sélection Opérateur */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            {t('payment_choose_provider')}
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {providers.map((provider) => (
              <button
                key={provider.id}
                type="button"
                onClick={() => setSelectedProvider(provider)}
                className={`
                  p-4 border-2 rounded-lg transition-all
                  flex flex-col items-center justify-center gap-2
                  ${
                    selectedProvider?.id === provider.id
                      ? 'border-indigo-600 bg-indigo-50 ring-2 ring-indigo-600'
                      : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
                  }
                `}
              >
                <div className="text-3xl">
                  {provider.id === 'cash_plus' && '💵'}
                  {provider.id === 'wafacash' && '🏦'}
                  {provider.id === 'orange_money' && '🍊'}
                  {provider.id === 'inwi_money' && '📱'}
                  {provider.id === 'maroc_telecom' && '📞'}
                  {provider.id === 'cih_mobile' && '🏛️'}
                </div>
                <span className="text-sm font-medium text-gray-900 text-center">
                  {provider.name}
                </span>
                <span className="text-xs text-gray-500">
                  {t('payment_instant')}
                </span>
              </button>
            ))}
          </div>

          {/* Infos opérateur sélectionné */}
          {selectedProvider && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <p className="text-sm text-blue-900 font-medium">{selectedProvider.name}</p>
                  <p className="text-xs text-blue-700 mt-1">{selectedProvider.description}</p>
                  <p className="text-xs text-blue-600 mt-2">
                    Montant: {selectedProvider.min_amount} - {selectedProvider.max_amount} MAD
                    {selectedProvider.fees > 0 && ` | Frais: ${selectedProvider.fees} MAD`}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Numéro de téléphone */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('payment_phone_number')}
          </label>
          <input
            type="tel"
            value={phoneNumber}
            onChange={handlePhoneChange}
            placeholder="+212612345678 ou 0612345678"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            dir="ltr"
          />
          <p className="text-xs text-gray-500 mt-1">
            Format: +212612345678 ou 0612345678
          </p>
        </div>

        {/* Montant */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('payment_amount')}
          </label>
          <div className="relative">
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              min={selectedProvider?.min_amount || 0}
              max={selectedProvider?.max_amount || 10000}
              step="0.01"
              placeholder="500.00"
              className="w-full px-4 py-3 pr-16 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 font-medium">
              MAD
            </span>
          </div>
          {selectedProvider && (
            <p className="text-xs text-gray-500 mt-1">
              Min: {selectedProvider.min_amount} MAD | Max: {selectedProvider.max_amount} MAD
            </p>
          )}
        </div>

        {/* Erreur de validation */}
        {validationError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex gap-3">
              <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-red-800">{validationError}</p>
            </div>
          </div>
        )}

        {/* Bouton Submit */}
        <button
          type="submit"
          disabled={loading || !selectedProvider || !phoneNumber || !amount}
          className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              {t('payment_processing')}
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {t('payment_request')}
            </>
          )}
        </button>
      </form>

      {/* Note de sécurité */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex gap-3">
          <svg className="w-5 h-5 text-gray-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
          </svg>
          <p className="text-xs text-gray-600">
            {t('language') === 'fr' && 'Paiements sécurisés et instantanés. Vous recevrez l\'argent directement sur votre compte mobile.'}
            {t('language') === 'ar' && 'مدفوعات آمنة وفورية. ستستلم المال مباشرة في حسابك المحمول.'}
            {t('language') === 'darija' && 'الدفع آمن وفوري. غادي توصلك الفلوس دغية فحسابك.'}
            {t('language') === 'en' && 'Secure and instant payments. You will receive money directly to your mobile account.'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default MobilePaymentWidget;
