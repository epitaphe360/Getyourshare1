import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';

const RegistrationSettings = () => {
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    allow_affiliate_registration: true,
    allow_advertiser_registration: true,
    require_invitation: false,
    require_2fa: false,
    country_required: true,
    company_name_required: true,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post('/api/settings/registration', settings);
      toast.success('Paramètres d\'inscription sauvegardés avec succès');
    } catch (error) {
      console.error('Error saving registration settings:', error);
      toast.error('Erreur lors de la sauvegarde des paramètres');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="registration-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres d'Inscription</h1>
        <p className="text-gray-600 mt-2">Configurez le processus d'inscription</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card title="Options d'Inscription">
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold">Autoriser inscription affiliés</h3>
                <p className="text-sm text-gray-600">Permettre aux nouveaux affiliés de s'inscrire</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.allow_affiliate_registration}
                  onChange={(e) => setSettings({ ...settings, allow_affiliate_registration: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold">Autoriser inscription annonceurs</h3>
                <p className="text-sm text-gray-600">Permettre aux nouveaux annonceurs de s'inscrire</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.allow_advertiser_registration}
                  onChange={(e) => setSettings({ ...settings, allow_advertiser_registration: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold">Invitation requise (MLM)</h3>
                <p className="text-sm text-gray-600">Exiger un lien de parrainage MLM pour l'inscription</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.require_invitation}
                  onChange={(e) => setSettings({ ...settings, require_invitation: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold">2FA obligatoire</h3>
                <p className="text-sm text-gray-600">Exiger l'authentification à deux facteurs</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.require_2fa}
                  onChange={(e) => setSettings({ ...settings, require_2fa: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
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

export default RegistrationSettings;
