import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { Building, Mail, MapPin, CreditCard } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

const CompanySettings = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await api.get('/api/settings');
      setSettings(response.data.company);
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put('/api/settings/company', settings);
      toast.success('Paramètres de l\'entreprise sauvegardés avec succès');
      await fetchSettings(); // Refresh settings
    } catch (error) {
      console.error('Error saving company settings:', error);
      toast.error('Erreur lors de la sauvegarde des paramètres');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Chargement...</div>;

  return (
    <div className="space-y-6" data-testid="company-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres de l'Entreprise</h1>
        <p className="text-gray-600 mt-2">Informations générales de votre entreprise</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card title="Informations de l'Entreprise">
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom de l'entreprise
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={settings?.name || ''}
                    onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email de contact
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="email"
                    value={settings?.email || ''}
                    onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Adresse
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 text-gray-400" size={20} />
                  <textarea
                    value={settings?.address || ''}
                    onChange={(e) => setSettings({ ...settings, address: e.target.value })}
                    rows={3}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Numéro de TVA
                </label>
                <div className="relative">
                  <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={settings?.tax_id || ''}
                    onChange={(e) => setSettings({ ...settings, tax_id: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Devise
                </label>
                <select
                  value={settings?.currency || 'EUR'}
                  onChange={(e) => setSettings({ ...settings, currency: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="EUR">Euro (€)</option>
                  <option value="USD">Dollar ($)</option>
                  <option value="GBP">Livre (£)</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={saving}>
                {saving ? 'Sauvegarde...' : 'Enregistrer les modifications'}
              </Button>
            </div>
          </div>
        </Card>
      </form>
    </div>
  );
};

export default CompanySettings;
