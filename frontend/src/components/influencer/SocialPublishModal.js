import React, { useState } from 'react';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Modal from '../common/Modal';
import {
  Instagram, Facebook, X, Loader,
  Image, Video, Type, Sparkles, Check
} from 'lucide-react';

/**
 * Social Media Publish Modal
 * Allows influencers to publish affiliate links to social media platforms
 */
const SocialPublishModal = ({ link, onClose, onSuccess }) => {
  const toast = useToast();

  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [customCaption, setCustomCaption] = useState('');
  const [mediaUrls, setMediaUrls] = useState({ default: '' });
  const [publishing, setPublishing] = useState(false);
  const [useCustomCaption, setUseCustomCaption] = useState(false);

  const platforms = [
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      color: 'from-purple-600 to-pink-600',
      description: 'Feed, Stories, Reels'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: 'from-blue-600 to-blue-700',
      description: 'Page, Groupes'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      icon: () => <span className="text-2xl font-bold">TT</span>,
      color: 'from-black to-gray-800',
      description: 'Vidéos'
    }
  ];

  const togglePlatform = (platformId) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platformId)
        ? prev.filter((p) => p !== platformId)
        : [...prev, platformId]
    );
  };

  const handlePublish = async () => {
    if (selectedPlatforms.length === 0) {
      toast.warning('Veuillez sélectionner au moins une plateforme');
      return;
    }

    setPublishing(true);

    try {
      const payload = {
        platforms: selectedPlatforms
      };

      if (useCustomCaption && customCaption) {
        payload.custom_caption = customCaption;
      }

      // Only add media URLs if they're provided
      const filteredMediaUrls = {};
      Object.keys(mediaUrls).forEach((key) => {
        if (mediaUrls[key]) {
          filteredMediaUrls[key] = mediaUrls[key];
        }
      });

      if (Object.keys(filteredMediaUrls).length > 0) {
        payload.media_urls = filteredMediaUrls;
      }

      const response = await api.post(`/api/affiliate/link/${link.id}/publish`, payload);

      if (response.data.success) {
        const published = response.data.published || [];
        const failed = response.data.failed || [];

        if (published.length > 0 && failed.length === 0) {
          toast.success(`Publié avec succès sur ${published.length} plateformes!`);
        } else if (published.length > 0 && failed.length > 0) {
          toast.warning(
            `Publié sur ${published.length} plateformes, ${failed.length} ont échoué`
          );
        } else {
          toast.error('Échec de la publication sur toutes les plateformes');
        }

        if (published.length > 0) {
          onSuccess && onSuccess();
          onClose();
        }
      }
    } catch (error) {
      console.error('Error publishing:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la publication');
    } finally {
      setPublishing(false);
    }
  };

  const defaultCaption = `🔥 Découvrez ${link.product?.name || 'cette offre'} !

${link.product?.description || ''}

💰 Prix: ${link.product?.discounted_price?.toLocaleString() || 'N/A'} DH
${link.product?.discount_percentage ? `🎁 -${link.product.discount_percentage}% de réduction!\n` : ''}
👉 Commandez maintenant: ${link.full_url}

#ShareYourSales #Maroc #Deal #Shopping #Promotion`;

  return (
    <Modal isOpen={true} onClose={onClose} size="large">
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            📱 Publier sur les Réseaux Sociaux
          </h2>
          <p className="text-gray-600">
            Partagez votre lien d'affiliation automatiquement sur vos plateformes
          </p>
        </div>

        {/* Product Preview */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg flex items-start space-x-4">
          {link.product?.images && link.product.images[0] ? (
            <img
              src={link.product.images[0]}
              alt={link.product.name}
              className="w-20 h-20 object-cover rounded-lg"
            />
          ) : (
            <div className="w-20 h-20 bg-purple-100 rounded-lg flex items-center justify-center">
              <Sparkles className="w-10 h-10 text-purple-400" />
            </div>
          )}
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1">{link.product?.name}</h3>
            <p className="text-sm text-gray-600 mb-2">
              Prix: {link.product?.discounted_price?.toLocaleString()} DH
              {link.product?.discount_percentage && (
                <span className="ml-2 text-red-600">-{link.product.discount_percentage}%</span>
              )}
            </p>
            <code className="text-xs bg-white px-2 py-1 rounded">{link.full_url}</code>
          </div>
        </div>

        {/* Platform Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Sélectionner les plateformes
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {platforms.map((platform) => {
              const Icon = platform.icon;
              const isSelected = selectedPlatforms.includes(platform.id);

              return (
                <button
                  key={platform.id}
                  onClick={() => togglePlatform(platform.id)}
                  className={`relative p-4 border-2 rounded-xl transition-all ${
                    isSelected
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {isSelected && (
                    <div className="absolute top-2 right-2">
                      <div className="bg-purple-500 rounded-full p-1">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  )}
                  <div
                    className={`w-12 h-12 rounded-lg bg-gradient-to-r ${platform.color} flex items-center justify-center text-white mb-3 mx-auto`}
                  >
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-gray-900 mb-1">{platform.name}</div>
                    <div className="text-xs text-gray-600">{platform.description}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Caption Options */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">Caption</label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useCustomCaption}
                onChange={(e) => setUseCustomCaption(e.target.checked)}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-600">Personnaliser</span>
            </label>
          </div>

          {useCustomCaption ? (
            <textarea
              value={customCaption}
              onChange={(e) => setCustomCaption(e.target.value)}
              placeholder="Écrivez votre caption personnalisée..."
              rows="6"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
            />
          ) : (
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-start mb-2">
                <Sparkles className="w-5 h-5 text-purple-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-sm font-medium text-purple-700">
                  Caption générée automatiquement
                </span>
              </div>
              <div className="text-sm text-gray-700 whitespace-pre-line font-mono">
                {defaultCaption}
              </div>
            </div>
          )}
        </div>

        {/* Media URLs (Optional) */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Médias (Optionnel)
          </label>
          <div className="space-y-3">
            <input
              type="url"
              placeholder="URL de l'image ou vidéo (par défaut)"
              value={mediaUrls.default}
              onChange={(e) => setMediaUrls({ ...mediaUrls, default: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <p className="text-xs text-gray-500">
              Si vide, utilisera l'image du produit par défaut
            </p>
          </div>
        </div>

        {/* Info Box */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-blue-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">ℹ️ Information</h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>
                  • La publication sera effectuée sur les comptes que vous avez connectés
                  <br />
                  • Les hashtags et le lien d'affiliation seront ajoutés automatiquement
                  <br />• Vous pourrez suivre les performances dans l'historique
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-3">
          <button
            onClick={handlePublish}
            disabled={publishing || selectedPlatforms.length === 0}
            className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {publishing ? (
              <>
                <Loader className="animate-spin w-5 h-5 mr-2" />
                Publication en cours...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                Publier sur {selectedPlatforms.length} plateforme
                {selectedPlatforms.length > 1 ? 's' : ''}
              </>
            )}
          </button>
          <button
            onClick={onClose}
            disabled={publishing}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition disabled:opacity-50"
          >
            Annuler
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default SocialPublishModal;
