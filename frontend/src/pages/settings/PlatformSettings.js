import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import { Settings, DollarSign, Clock, Shield, AlertCircle } from 'lucide-react';

const PlatformSettings = () => {
  const toast = useToast();
  const { user } = useAuth();
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({
    min_payout_amount: 50,
    payout_frequency: 'weekly',
    payout_day: 'friday',
    validation_delay_days: 14,
    platform_commission_rate: 5,
    auto_payout_enabled: true,
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await api.get('/api/admin/platform-settings');
      if (response.data.settings) {
        setSettings(response.data.settings);
      }
    } catch (error) {
      console.error('Error fetching platform settings:', error);
      // Garder les valeurs par défaut si erreur
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (settings.min_payout_amount < 10) {
      toast.error('Le montant minimum doit être au moins 10€');
      return;
    }
    
    if (settings.min_payout_amount > 1000) {
      toast.error('Le montant minimum ne peut pas dépasser 1000€');
      return;
    }

    if (settings.platform_commission_rate < 0 || settings.platform_commission_rate > 50) {
      toast.error('Le taux de commission doit être entre 0% et 50%');
      return;
    }

    setSaving(true);
    try {
      await api.post('/api/admin/platform-settings', settings);
      toast.success('Paramètres de plateforme sauvegardés avec succès');
    } catch (error) {
      console.error('Error saving platform settings:', error);
      toast.error('Erreur lors de la sauvegarde des paramètres');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  // Vérifier que l'utilisateur est admin
  if (user?.role !== 'admin') {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="mx-auto mb-4 text-red-600" size={64} />
          <h2 className="text-2xl font-bold text-red-600 mb-4">Accès refusé</h2>
          <p className="text-gray-600">
            Cette page est réservée aux administrateurs de la plateforme.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="platform-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres de la Plateforme</h1>
        <p className="text-gray-600 mt-2">
          Configuration globale de la plateforme (réservé aux administrateurs)
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Paramètres de Paiement */}
        <Card title="💰 Paramètres de Paiement" icon={<DollarSign size={20} />}>
          <div className="space-y-6">
            {/* MONTANT MINIMUM - PARAMÈTRE CRITIQUE */}
            <div className="p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
              <div className="flex items-start">
                <Shield className="text-yellow-600 mr-3 flex-shrink-0 mt-1" size={20} />
                <div>
                  <h3 className="font-semibold text-yellow-900 mb-1">
                    ⚠️ Paramètre Global Critique
                  </h3>
                  <p className="text-sm text-yellow-800">
                    Ce montant s'applique à <strong>tous les influenceurs</strong> de la plateforme. 
                    Les marchands ne peuvent PAS modifier cette valeur individuellement.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <DollarSign className="inline mr-1" size={16} />
                Montant minimum de retrait pour tous les influenceurs (€) *
              </label>
              <input
                type="number"
                min="10"
                max="1000"
                step="5"
                value={settings.min_payout_amount}
                onChange={(e) => setSettings({ ...settings, min_payout_amount: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
              <p className="mt-2 text-sm text-gray-600">
                💡 Valeur recommandée: <strong>50€</strong> (équilibre entre liquidité et coûts de transaction)
              </p>
              <p className="mt-1 text-xs text-gray-500">
                • Trop bas (10€): Coûts de transaction élevés, beaucoup de demandes
              </p>
              <p className="mt-1 text-xs text-gray-500">
                • Trop haut (500€): Influenceurs attendent trop longtemps pour être payés
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Taux de commission de la plateforme (%)
              </label>
              <input
                type="number"
                min="0"
                max="50"
                step="0.5"
                value={settings.platform_commission_rate}
                onChange={(e) => setSettings({ ...settings, platform_commission_rate: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <p className="mt-2 text-sm text-gray-600">
                Commission prélevée par la plateforme sur chaque vente
              </p>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold">Paiements automatiques activés</h3>
                <p className="text-sm text-gray-600">
                  Traiter automatiquement les paiements dès que le seuil est atteint
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.auto_payout_enabled}
                  onChange={(e) => setSettings({ ...settings, auto_payout_enabled: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>
        </Card>

        {/* Paramètres de Fréquence */}
        <Card title="⏰ Fréquence des Paiements" icon={<Clock size={20} />} className="mt-6">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fréquence de traitement
              </label>
              <select
                value={settings.payout_frequency}
                onChange={(e) => setSettings({ ...settings, payout_frequency: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="daily">Quotidien (tous les jours)</option>
                <option value="weekly">Hebdomadaire (recommandé)</option>
                <option value="biweekly">Bi-mensuel (2 fois par mois)</option>
                <option value="monthly">Mensuel</option>
              </select>
            </div>

            {settings.payout_frequency === 'weekly' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Jour de la semaine
                </label>
                <select
                  value={settings.payout_day}
                  onChange={(e) => setSettings({ ...settings, payout_day: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="monday">Lundi</option>
                  <option value="tuesday">Mardi</option>
                  <option value="wednesday">Mercredi</option>
                  <option value="thursday">Jeudi</option>
                  <option value="friday">Vendredi (recommandé)</option>
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Délai de validation des ventes (jours)
              </label>
              <input
                type="number"
                min="0"
                max="90"
                value={settings.validation_delay_days}
                onChange={(e) => setSettings({ ...settings, validation_delay_days: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <p className="mt-2 text-sm text-gray-600">
                Délai avant qu'une vente soit validée et éligible au paiement (délai de rétractation)
              </p>
              <p className="mt-1 text-xs text-gray-500">
                💡 Recommandé: 14 jours (délai légal de rétractation en France)
              </p>
            </div>
          </div>
        </Card>

        {/* Résumé de la configuration */}
        <Card title="📊 Résumé de la Configuration" className="mt-6">
          <div className="p-4 bg-indigo-50 rounded-lg space-y-2">
            <p className="text-sm">
              <strong>Montant minimum:</strong> {settings.min_payout_amount}€ 
              (les influenceurs doivent atteindre ce montant pour être payés)
            </p>
            <p className="text-sm">
              <strong>Fréquence:</strong> {
                settings.payout_frequency === 'weekly' ? 'Hebdomadaire' :
                settings.payout_frequency === 'daily' ? 'Quotidien' :
                settings.payout_frequency === 'biweekly' ? 'Bi-mensuel' :
                'Mensuel'
              }
              {settings.payout_frequency === 'weekly' && ` (le ${
                settings.payout_day === 'friday' ? 'vendredi' :
                settings.payout_day === 'monday' ? 'lundi' :
                settings.payout_day === 'tuesday' ? 'mardi' :
                settings.payout_day === 'wednesday' ? 'mercredi' :
                'jeudi'
              })`}
            </p>
            <p className="text-sm">
              <strong>Délai de validation:</strong> {settings.validation_delay_days} jours
            </p>
            <p className="text-sm">
              <strong>Commission plateforme:</strong> {settings.platform_commission_rate}%
            </p>
            <p className="text-sm">
              <strong>Paiements automatiques:</strong> {settings.auto_payout_enabled ? '✅ Activés' : '❌ Désactivés'}
            </p>
          </div>
        </Card>

        <div className="flex justify-end mt-6">
          <Button type="submit" disabled={saving}>
            {saving ? 'Sauvegarde...' : 'Enregistrer les modifications'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default PlatformSettings;
