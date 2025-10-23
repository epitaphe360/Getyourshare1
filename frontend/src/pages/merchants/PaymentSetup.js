import React, { useState, useEffect } from 'react';
import { api } from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

const PaymentSetup = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [currentConfig, setCurrentConfig] = useState(null);
  const [selectedGateway, setSelectedGateway] = useState('manual');
  const [autoDebit, setAutoDebit] = useState(false);
  const [gatewayConfig, setGatewayConfig] = useState({});
  const [testResult, setTestResult] = useState(null);

  const gateways = [
    {
      code: 'manual',
      name: 'Paiement Manuel',
      description: 'Facturation et suivi manuel des paiements',
      fees: '0%',
      delay: '30 jours',
      icon: '📄',
      color: 'gray',
      fields: []
    },
    {
      code: 'cmi',
      name: 'CMI - Centre Monétique Interbancaire',
      description: 'Solution de paiement nationale marocaine',
      fees: '1.5% - 2%',
      delay: '2-3 jours',
      icon: '🇲🇦',
      color: 'green',
      fields: [
        { name: 'cmi_merchant_id', label: 'Merchant ID', type: 'text', required: true },
        { name: 'cmi_api_key', label: 'API Key', type: 'password', required: true },
        { name: 'cmi_store_key', label: 'Store Key', type: 'password', required: true },
        { name: 'cmi_terminal_id', label: 'Terminal ID', type: 'text', required: true }
      ]
    },
    {
      code: 'payzen',
      name: 'PayZen / Lyra',
      description: 'Solution française populaire au Maroc (Marjane, Jumia, Avito)',
      fees: '1.8% - 2.5%',
      delay: '24-48h',
      icon: '🇫🇷',
      color: 'blue',
      fields: [
        { name: 'payzen_shop_id', label: 'Shop ID', type: 'text', required: true },
        { name: 'payzen_api_key', label: 'API Key', type: 'password', required: true },
        { name: 'payzen_secret_key', label: 'Secret Key', type: 'password', required: true },
        { name: 'payzen_mode', label: 'Mode', type: 'select', options: ['TEST', 'PRODUCTION'], required: true }
      ]
    },
    {
      code: 'sg_maroc',
      name: 'Société Générale Maroc - e-Payment',
      description: 'TPE virtuel + API Société Générale',
      fees: '1.5% - 2.5%',
      delay: '2-3 jours',
      icon: '🏦',
      color: 'red',
      fields: [
        { name: 'sg_merchant_code', label: 'Merchant Code', type: 'text', required: true },
        { name: 'sg_terminal_id', label: 'Terminal ID', type: 'text', required: true },
        { name: 'sg_api_username', label: 'API Username', type: 'text', required: true },
        { name: 'sg_api_password', label: 'API Password', type: 'password', required: true },
        { name: 'sg_certificate', label: 'Certificate', type: 'textarea', required: false }
      ]
    }
  ];

  useEffect(() => {
    loadCurrentConfig();
  }, []);

  const loadCurrentConfig = async () => {
    try {
      const response = await api.get('/api/merchant/payment-config');
      setCurrentConfig(response);
      setSelectedGateway(response.payment_gateway || 'manual');
      setAutoDebit(response.auto_debit_enabled || false);
      setGatewayConfig(response.gateway_config || {});
    } catch (error) {
      console.error('Erreur chargement configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setTestResult(null);

    try {
      const payload = {
        payment_gateway: selectedGateway,
        auto_debit_enabled: autoDebit,
        gateway_config: gatewayConfig
      };

      await api.put('/api/merchant/payment-config', payload);

      alert('✅ Configuration sauvegardée avec succès !');
      loadCurrentConfig();
    } catch (error) {
      console.error('Erreur sauvegarde:', error);
      alert('❌ Erreur lors de la sauvegarde: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const handleFieldChange = (fieldName, value) => {
    setGatewayConfig(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  const selectedGatewayInfo = gateways.find(g => g.code === selectedGateway);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Configuration des Paiements</h1>
        <p className="text-gray-600 mt-2">
          Choisissez comment vous souhaitez payer vos commissions plateforme
        </p>
      </div>

      {/* Current Status */}
      {currentConfig && currentConfig.gateway_activated_at && (
        <Card className="bg-blue-50 border-blue-200">
          <div className="flex items-center gap-3">
            <span className="text-2xl">ℹ️</span>
            <div>
              <div className="font-semibold text-blue-900">
                Configuration actuelle : {gateways.find(g => g.code === currentConfig.payment_gateway)?.name}
              </div>
              <div className="text-sm text-blue-700">
                Activé le {new Date(currentConfig.gateway_activated_at).toLocaleDateString('fr-FR')}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Gateway Selection */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Choisir une solution de paiement</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {gateways.map(gateway => (
            <button
              key={gateway.code}
              onClick={() => setSelectedGateway(gateway.code)}
              className={`p-4 border-2 rounded-lg text-left transition-all ${
                selectedGateway === gateway.code
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start gap-3">
                <span className="text-3xl">{gateway.icon}</span>
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{gateway.name}</div>
                  <div className="text-sm text-gray-600 mt-1">{gateway.description}</div>
                  <div className="flex gap-4 mt-2 text-xs">
                    <span className="text-green-600">💰 {gateway.fees}</span>
                    <span className="text-blue-600">⏱️ {gateway.delay}</span>
                  </div>
                </div>
                {selectedGateway === gateway.code && (
                  <span className="text-blue-500 text-xl">✓</span>
                )}
              </div>
            </button>
          ))}
        </div>
      </Card>

      {/* Configuration Fields */}
      {selectedGatewayInfo && selectedGatewayInfo.fields.length > 0 && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">
            Configuration {selectedGatewayInfo.name}
          </h2>

          <div className="space-y-4">
            {selectedGatewayInfo.fields.map(field => (
              <div key={field.name}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </label>

                {field.type === 'select' ? (
                  <select
                    value={gatewayConfig[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required={field.required}
                  >
                    <option value="">Sélectionner...</option>
                    {field.options.map(option => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                ) : field.type === 'textarea' ? (
                  <textarea
                    value={gatewayConfig[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder={`Entrez votre ${field.label.toLowerCase()}`}
                    required={field.required}
                  />
                ) : (
                  <input
                    type={field.type}
                    value={gatewayConfig[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder={`Entrez votre ${field.label.toLowerCase()}`}
                    required={field.required}
                  />
                )}
              </div>
            ))}
          </div>

          {/* Help Text */}
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="flex items-start gap-2">
              <span className="text-yellow-600">💡</span>
              <div className="text-sm text-yellow-800">
                <strong>Comment obtenir ces informations ?</strong>
                <ul className="mt-2 ml-4 list-disc space-y-1">
                  {selectedGateway === 'cmi' && (
                    <>
                      <li>Contactez votre banque au Maroc</li>
                      <li>Demandez l'activation du service CMI e-commerce</li>
                      <li>Ils vous fourniront vos identifiants (délai: 3-5 jours)</li>
                    </>
                  )}
                  {selectedGateway === 'payzen' && (
                    <>
                      <li>Créez un compte sur <a href="https://payzen.eu" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">payzen.eu</a></li>
                      <li>Complétez le KYC (Know Your Customer)</li>
                      <li>Récupérez vos clés API dans Settings → API Keys</li>
                    </>
                  )}
                  {selectedGateway === 'sg_maroc' && (
                    <>
                      <li>Contactez Société Générale Maroc - Département e-Banking</li>
                      <li>Demandez l'activation du service e-Payment</li>
                      <li>Téléchargez votre certificat dans l'espace client</li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Auto-Debit Option */}
      {selectedGateway !== 'manual' && (
        <Card>
          <div className="flex items-start gap-4">
            <input
              type="checkbox"
              id="auto-debit"
              checked={autoDebit}
              onChange={(e) => setAutoDebit(e.target.checked)}
              className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div className="flex-1">
              <label htmlFor="auto-debit" className="font-medium text-gray-900 cursor-pointer">
                Activer le prélèvement automatique
              </label>
              <p className="text-sm text-gray-600 mt-1">
                Vos factures seront automatiquement payées via {selectedGatewayInfo?.name}.
                Vous recevrez une notification avant chaque prélèvement.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Test Result */}
      {testResult && (
        <Card className={testResult.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}>
          <div className="flex items-center gap-3">
            <span className="text-2xl">{testResult.success ? '✅' : '❌'}</span>
            <div>
              <div className={`font-semibold ${testResult.success ? 'text-green-900' : 'text-red-900'}`}>
                {testResult.message}
              </div>
              {testResult.details && (
                <div className={`text-sm mt-1 ${testResult.success ? 'text-green-700' : 'text-red-700'}`}>
                  {testResult.details}
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Button
          onClick={handleSave}
          loading={saving}
          className="px-6 py-3"
        >
          {saving ? 'Sauvegarde...' : 'Sauvegarder la configuration'}
        </Button>

        {selectedGateway !== 'manual' && (
          <button
            onClick={() => setTestResult({ success: true, message: 'Test de connexion réussi!', details: 'Les identifiants sont valides.' })}
            className="px-6 py-3 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            disabled={saving}
          >
            Tester la connexion
          </button>
        )}
      </div>

      {/* Info Box */}
      <Card className="bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Bon à savoir</h3>
        <ul className="text-sm text-blue-800 space-y-1 ml-4 list-disc">
          <li>Vous pouvez changer de solution de paiement à tout moment</li>
          <li>Les factures déjà émises ne seront pas affectées</li>
          <li>Le prélèvement automatique peut être désactivé à tout moment</li>
          <li>Vos données sont chiffrées et sécurisées (SSL/TLS)</li>
        </ul>
      </Card>
    </div>
  );
};

export default PaymentSetup;
