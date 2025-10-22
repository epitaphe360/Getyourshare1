import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

const AffiliateSettings = () => {
  const [settings, setSettings] = useState({
    min_withdrawal: 50,
    auto_approval: false,
    email_verification: true,
    payment_mode: 'on_demand',
    single_campaign_mode: false,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Saving affiliate settings:', settings);
  };

  return (
    <div className="space-y-6" data-testid="affiliate-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres des Affiliés</h1>
        <p className="text-gray-600 mt-2">Configurez le comportement des affiliés</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card title="Configuration Générale">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Montant minimum de retrait (€)
              </label>
              <input
                type="number"
                value={settings.min_withdrawal}
                onChange={(e) => setSettings({ ...settings, min_withdrawal: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold">Approbation automatique</h3>
                <p className="text-sm text-gray-600">Approuver automatiquement les nouvelles demandes d'affiliation</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.auto_approval}
                  onChange={(e) => setSettings({ ...settings, auto_approval: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold">Vérification email requise</h3>
                <p className="text-sm text-gray-600">Exiger la vérification de l'email pour les nouveaux affiliés</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.email_verification}
                  onChange={(e) => setSettings({ ...settings, email_verification: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mode de paiement
              </label>
              <select
                value={settings.payment_mode}
                onChange={(e) => setSettings({ ...settings, payment_mode: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="on_demand">À la demande</option>
                <option value="automatic">Automatique</option>
              </select>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold">Mode campagne unique</h3>
                <p className="text-sm text-gray-600">Limiter les affiliés à une seule campagne</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.single_campaign_mode}
                  onChange={(e) => setSettings({ ...settings, single_campaign_mode: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex justify-end">
              <Button type="submit">
                Enregistrer les modifications
              </Button>
            </div>
          </div>
        </Card>
      </form>
    </div>
  );
};

export default AffiliateSettings;
