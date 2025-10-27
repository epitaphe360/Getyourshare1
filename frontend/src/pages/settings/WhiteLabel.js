import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { Upload, Palette, Mail, Shield } from 'lucide-react';
import api from '../../utils/api';

const WhiteLabel = () => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [settings, setSettings] = useState({
    logo_url: '',
    primary_color: '#3b82f6',
    secondary_color: '#1e40af',
    accent_color: '#10b981',
    company_name: 'Share Your Sales Platform',
    custom_domain: 'track.votredomaine.com',
    ssl_enabled: true,
    custom_email_domain: 'noreply@votredomaine.com',
  });

  const [previewColors, setPreviewColors] = useState({
    primary: '#3b82f6',
    secondary: '#1e40af',
    accent: '#10b981',
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/settings/whitelabel');
      setSettings({
        logo_url: response.data.logo_url || '',
        primary_color: response.data.primary_color || '#3b82f6',
        secondary_color: response.data.secondary_color || '#1e40af',
        accent_color: response.data.accent_color || '#10b981',
        company_name: response.data.company_name || 'Share Your Sales Platform',
        custom_domain: response.data.custom_domain || 'track.votredomaine.com',
        ssl_enabled: response.data.ssl_enabled ?? true,
        custom_email_domain: response.data.custom_email_domain || 'noreply@votredomaine.com',
      });
      setPreviewColors({
        primary: response.data.primary_color || '#3b82f6',
        secondary: response.data.secondary_color || '#1e40af',
        accent: response.data.accent_color || '#10b981',
      });
    } catch (error) {
      console.error('Erreur chargement white label:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSettings({ ...settings, logo_url: reader.result });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      await api.put('/api/settings/whitelabel', settings);
      setMessage({ type: 'success', text: '✅ Paramètres White Label enregistrés avec succès !' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      console.error('Erreur sauvegarde white label:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || '❌ Erreur lors de l\'enregistrement' 
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="white-label-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Configuration White Label</h1>
        <p className="text-gray-600 mt-2">Personnalisez l'apparence de votre plateforme</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 
          'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Logo */}
        <Card title="Logo & Branding">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Logo de la plateforme
              </label>
              <div className="flex items-center space-x-4">
                {settings.logo_url ? (
                  <img src={settings.logo_url} alt="Logo" className="h-20 w-20 object-contain border border-gray-300 rounded-lg" />
                ) : (
                  <div className="h-20 w-20 bg-gray-100 rounded-lg flex items-center justify-center">
                    <Upload className="text-gray-400" size={32} />
                  </div>
                )}
                <div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleLogoUpload}
                    className="hidden"
                    id="logo-upload"
                  />
                  <label htmlFor="logo-upload">
                    <Button type="button" as="span" variant="outline">
                      <Upload size={16} className="mr-2" />
                      Télécharger un Logo
                    </Button>
                  </label>
                  <p className="text-xs text-gray-500 mt-2">PNG, JPG jusqu'à 2MB</p>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom de la plateforme
              </label>
              <input
                type="text"
                value={settings.company_name}
                onChange={(e) => setSettings({ ...settings, company_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </Card>

        {/* Colors */}
        <Card title="Couleurs du Thème" className="mt-6">
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Couleur Principale
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    value={settings.primary_color}
                    onChange={(e) => {
                      setSettings({ ...settings, primary_color: e.target.value });
                      setPreviewColors({ ...previewColors, primary: e.target.value });
                    }}
                    className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={settings.primary_color}
                    onChange={(e) => setSettings({ ...settings, primary_color: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Couleur Secondaire
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    value={settings.secondary_color}
                    onChange={(e) => {
                      setSettings({ ...settings, secondary_color: e.target.value });
                      setPreviewColors({ ...previewColors, secondary: e.target.value });
                    }}
                    className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={settings.secondary_color}
                    onChange={(e) => setSettings({ ...settings, secondary_color: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Couleur Accent
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    value={settings.accent_color}
                    onChange={(e) => {
                      setSettings({ ...settings, accent_color: e.target.value });
                      setPreviewColors({ ...previewColors, accent: e.target.value });
                    }}
                    className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={settings.accent_color}
                    onChange={(e) => setSettings({ ...settings, accent_color: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Preview */}
            <div className="p-6 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-4">Aperçu des Couleurs</h4>
              <div className="flex space-x-4">
                <div className="flex-1 p-4 rounded-lg text-white text-center font-semibold" style={{ backgroundColor: previewColors.primary }}>
                  Principale
                </div>
                <div className="flex-1 p-4 rounded-lg text-white text-center font-semibold" style={{ backgroundColor: previewColors.secondary }}>
                  Secondaire
                </div>
                <div className="flex-1 p-4 rounded-lg text-white text-center font-semibold" style={{ backgroundColor: previewColors.accent }}>
                  Accent
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Domain & SSL */}
        <Card title="Domaine Personnalisé & SSL" className="mt-6">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Domaine personnalisé
              </label>
              <input
                type="text"
                value={settings.custom_domain}
                onChange={(e) => setSettings({ ...settings, custom_domain: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="track.votredomaine.com"
              />
              <p className="text-xs text-gray-500 mt-2">
                Configurez un CNAME pointant vers notre serveur
              </p>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Shield className="text-green-600" size={24} />
                <div>
                  <h4 className="font-semibold">SSL/HTTPS Automatique</h4>
                  <p className="text-sm text-gray-600">Certificat SSL gratuit avec Let's Encrypt</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.ssl_enabled}
                  onChange={(e) => setSettings({ ...settings, ssl_enabled: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-green-600"></div>
              </label>
            </div>
          </div>
        </Card>

        {/* Email Customization */}
        <Card title="Personnalisation des Emails" className="mt-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Domaine email personnalisé
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  value={settings.custom_email_domain}
                  onChange={(e) => setSettings({ ...settings, custom_email_domain: e.target.value })}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="noreply@votredomaine.com"
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Tous les emails seront envoyés depuis cette adresse
              </p>
            </div>
          </div>
        </Card>

        <div className="flex justify-end mt-6">
          <Button type="submit" size="lg" disabled={saving}>
            {saving ? 'Enregistrement...' : 'Enregistrer la Configuration'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default WhiteLabel;
