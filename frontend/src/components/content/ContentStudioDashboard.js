import React, { useState, useEffect } from 'react';
import { useI18n } from '../../i18n/i18n';
import api from '../../utils/api';
import {
  Wand2, Image, Video, Calendar, QrCode, Droplet,
  Layout, Sparkles, TrendingUp, Copy, Download, Eye
} from 'lucide-react';

/**
 * Content Studio Dashboard
 *
 * Interface complète pour la création de contenu:
 * - Génération d'images IA
 * - Bibliothèque de templates
 * - Éditeur visuel
 * - QR codes stylisés
 * - Watermarking
 * - Planification posts
 * - A/B Testing
 */
const ContentStudioDashboard = ({ user }) => {
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState('templates');
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'templates') {
      fetchTemplates();
    }
  }, [activeTab]);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/content-studio/templates');
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Erreur chargement templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'templates', name: 'Templates', icon: <Layout size={20} /> },
    { id: 'ai-generator', name: 'Générateur IA', icon: <Wand2 size={20} /> },
    { id: 'qr-codes', name: 'QR Codes', icon: <QrCode size={20} /> },
    { id: 'watermark', name: 'Watermark', icon: <Droplet size={20} /> },
    { id: 'scheduler', name: 'Planification', icon: <Calendar size={20} /> },
    { id: 'ab-testing', name: 'A/B Testing', icon: <TrendingUp size={20} /> }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
              <Sparkles size={32} />
              Content Studio
            </h1>
            <p className="text-pink-100">
              Créez du contenu professionnel en quelques clics
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">47</div>
            <div className="text-pink-100 text-sm">Créations ce mois</div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <QuickStat
          icon={<Image className="text-purple-600" />}
          label="Images Générées"
          value="12"
          trend="+3 cette semaine"
        />
        <QuickStat
          icon={<Layout className="text-pink-600" />}
          label="Templates Utilisés"
          value="23"
          trend="8 favoris"
        />
        <QuickStat
          icon={<Calendar className="text-blue-600" />}
          label="Posts Planifiés"
          value="8"
          trend="4 à venir"
        />
        <QuickStat
          icon={<TrendingUp className="text-green-600" />}
          label="Temps Gagné"
          value="18.5h"
          trend="vs création manuelle"
        />
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {/* Tab Headers */}
        <div className="flex border-b border-gray-200 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'text-purple-600 border-b-2 border-purple-600 bg-purple-50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {tab.icon}
              <span>{tab.name}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'templates' && (
            <TemplatesTab templates={templates} loading={loading} />
          )}
          {activeTab === 'ai-generator' && <AIGeneratorTab />}
          {activeTab === 'qr-codes' && <QRCodeTab />}
          {activeTab === 'watermark' && <WatermarkTab />}
          {activeTab === 'scheduler' && <SchedulerTab />}
          {activeTab === 'ab-testing' && <ABTestingTab />}
        </div>
      </div>
    </div>
  );
};

// ========== SUB-COMPONENTS ==========

const QuickStat = ({ icon, label, value, trend }) => (
  <div className="bg-white rounded-lg p-4 border border-gray-200">
    <div className="flex items-center justify-between mb-2">
      {icon}
      <span className="text-2xl font-bold">{value}</span>
    </div>
    <div className="text-sm text-gray-600">{label}</div>
    <div className="text-xs text-gray-500 mt-1">{trend}</div>
  </div>
);

const TemplatesTab = ({ templates, loading }) => {
  if (loading) {
    return <div className="text-center py-12">Chargement des templates...</div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Templates Prêts à l'Emploi</h2>
        <div className="flex gap-2">
          <select className="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">Toutes les catégories</option>
            <option value="product_showcase">Mise en avant produit</option>
            <option value="promotion">Promotion</option>
            <option value="review">Review</option>
            <option value="tutorial">Tutorial</option>
          </select>
          <select className="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">Toutes les plateformes</option>
            <option value="instagram">Instagram</option>
            <option value="tiktok">TikTok</option>
            <option value="facebook">Facebook</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <div
            key={template.id}
            className="bg-gray-50 rounded-lg overflow-hidden border border-gray-200 hover:shadow-lg transition cursor-pointer"
          >
            <div className="aspect-square bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center">
              <Layout size={64} className="text-purple-600" />
            </div>
            <div className="p-4">
              <h3 className="font-semibold mb-1">{template.name}</h3>
              <p className="text-sm text-gray-600 mb-3">{template.description}</p>
              <div className="flex items-center justify-between">
                <div className="flex gap-1">
                  {template.platforms?.slice(0, 3).map((platform) => (
                    <span
                      key={platform}
                      className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded"
                    >
                      {platform}
                    </span>
                  ))}
                </div>
                <button className="px-3 py-1 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700">
                  Utiliser
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const AIGeneratorTab = () => {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('realistic');
  const [generating, setGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      const response = await api.post('/api/content-studio/generate-image', {
        prompt,
        style,
        size: '1024x1024',
        quality: 'standard'
      });

      setGeneratedImage(response.data.image_url);
    } catch (error) {
      console.error('Erreur génération:', error);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-xl font-bold mb-6">Générateur d'Images IA</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Décrivez l'image que vous voulez créer
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ex: Un écouteur Bluetooth moderne sur fond rose avec des effets lumineux..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            rows={4}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Style
          </label>
          <div className="grid grid-cols-4 gap-2">
            {['realistic', 'artistic', 'cartoon', 'minimalist'].map((s) => (
              <button
                key={s}
                onClick={() => setStyle(s)}
                className={`px-4 py-2 rounded-lg border-2 transition ${
                  style === s
                    ? 'border-purple-600 bg-purple-50 text-purple-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={!prompt || generating}
          className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {generating ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
              <span>Génération en cours...</span>
            </>
          ) : (
            <>
              <Wand2 size={20} />
              <span>Générer l'Image</span>
            </>
          )}
        </button>

        {generatedImage && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <img
              src={generatedImage}
              alt="Generated"
              className="w-full rounded-lg shadow-lg"
            />
            <div className="flex gap-2 mt-4">
              <button className="flex-1 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2">
                <Download size={18} />
                Télécharger
              </button>
              <button className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center justify-center gap-2">
                <Eye size={18} />
                Utiliser dans un Post
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const QRCodeTab = () => (
  <div className="max-w-2xl mx-auto text-center">
    <QrCode size={64} className="mx-auto text-purple-600 mb-4" />
    <h2 className="text-2xl font-bold mb-2">QR Codes Stylisés</h2>
    <p className="text-gray-600 mb-6">
      Générez des QR codes design pour vos liens d'affiliation
    </p>
    <button className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700">
      Créer un QR Code
    </button>
  </div>
);

const WatermarkTab = () => (
  <div className="max-w-2xl mx-auto text-center">
    <Droplet size={64} className="mx-auto text-pink-600 mb-4" />
    <h2 className="text-2xl font-bold mb-2">Watermark Automatique</h2>
    <p className="text-gray-600 mb-6">
      Ajoutez votre signature et lien d'affiliation à vos créations
    </p>
    <button className="px-6 py-3 bg-pink-600 text-white rounded-lg font-semibold hover:bg-pink-700">
      Ajouter un Watermark
    </button>
  </div>
);

const SchedulerTab = () => (
  <div className="max-w-2xl mx-auto text-center">
    <Calendar size={64} className="mx-auto text-blue-600 mb-4" />
    <h2 className="text-2xl font-bold mb-2">Planification Multi-Réseaux</h2>
    <p className="text-gray-600 mb-6">
      Planifiez vos posts sur Instagram, TikTok, Facebook et plus
    </p>
    <button className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700">
      Planifier un Post
    </button>
  </div>
);

const ABTestingTab = () => (
  <div className="max-w-2xl mx-auto text-center">
    <TrendingUp size={64} className="mx-auto text-green-600 mb-4" />
    <h2 className="text-2xl font-bold mb-2">A/B Testing</h2>
    <p className="text-gray-600 mb-6">
      Testez 2 versions de vos créatives et découvrez laquelle performe le mieux
    </p>
    <button className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700">
      Créer un A/B Test
    </button>
  </div>
);

export default ContentStudioDashboard;
