import React, { useState } from 'react';
import { useI18n } from '../../i18n/i18n';
import api from '../../utils/api';
import { Music, Upload, Check, X, AlertCircle, Loader } from 'lucide-react';

/**
 * Composant de synchronisation TikTok Shop
 *
 * Permet de synchroniser des produits vers TikTok Shop
 * et de suivre leur statut
 */
const TikTokProductSync = ({ product, onSyncSuccess, onSyncError }) => {
  const { t } = useI18n();
  const [syncing, setSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null); // null, 'success', 'error', 'pending'
  const [tiktokProductId, setTiktokProductId] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSync = async () => {
    try {
      setSyncing(true);
      setErrorMessage('');

      // Préparer les données du produit
      const syncData = {
        product_id: product.id,
        title: product.name,
        description: product.description,
        category_id: product.category_id,
        price: product.price,
        currency: product.currency || 'MAD',
        stock: product.stock || 0,
        images: product.images || [],
        video_url: product.video_url,
        brand: product.brand,
        attributes: product.attributes
      };

      // Appeler l'API de synchronisation
      const response = await api.post('/api/tiktok-shop/sync-product', syncData);

      if (response.data.success) {
        setTiktokProductId(response.data.tiktok_product_id);
        setSyncStatus(response.data.status === 'APPROVED' ? 'success' : 'pending');

        if (onSyncSuccess) {
          onSyncSuccess(response.data);
        }
      } else {
        throw new Error('Sync failed');
      }
    } catch (error) {
      console.error('Erreur sync TikTok:', error);
      setErrorMessage(error.response?.data?.detail || 'Erreur lors de la synchronisation');
      setSyncStatus('error');

      if (onSyncError) {
        onSyncError(error);
      }
    } finally {
      setSyncing(false);
    }
  };

  const getStatusBadge = () => {
    switch (syncStatus) {
      case 'success':
        return (
          <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
            <Check size={16} />
            <span>En ligne sur TikTok</span>
          </div>
        );
      case 'pending':
        return (
          <div className="flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
            <AlertCircle size={16} />
            <span>En attente d'approbation</span>
          </div>
        );
      case 'error':
        return (
          <div className="flex items-center gap-2 px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm">
            <X size={16} />
            <span>Erreur de synchronisation</span>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Header TikTok */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center">
            <Music className="text-white" size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">TikTok Shop</h3>
            <p className="text-sm text-gray-500">Synchroniser ce produit</p>
          </div>
        </div>

        {getStatusBadge()}
      </div>

      {/* Product preview */}
      <div className="bg-gray-50 rounded-lg p-3 mb-4">
        <div className="flex gap-3">
          {product.images && product.images[0] && (
            <img
              src={product.images[0]}
              alt={product.name}
              className="w-16 h-16 object-cover rounded"
            />
          )}
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900 truncate">{product.name}</p>
            <p className="text-sm text-gray-600">
              {product.price} {product.currency || 'MAD'}
            </p>
            <p className="text-xs text-gray-500">
              Stock: {product.stock || 0} unités
            </p>
          </div>
        </div>
      </div>

      {/* Error message */}
      {errorMessage && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{errorMessage}</p>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-2">
        <button
          onClick={handleSync}
          disabled={syncing || syncStatus === 'success'}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
            syncing || syncStatus === 'success'
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-black text-white hover:bg-gray-800'
          }`}
        >
          {syncing ? (
            <>
              <Loader className="animate-spin" size={18} />
              <span>Synchronisation...</span>
            </>
          ) : syncStatus === 'success' ? (
            <>
              <Check size={18} />
              <span>Synchronisé</span>
            </>
          ) : (
            <>
              <Upload size={18} />
              <span>Synchroniser</span>
            </>
          )}
        </button>

        {tiktokProductId && (
          <button
            onClick={() => window.open(`https://shop.tiktok.com/product/${tiktokProductId}`, '_blank')}
            className="px-4 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition"
          >
            Voir sur TikTok
          </button>
        )}
      </div>

      {/* Info */}
      {syncStatus === 'pending' && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            📋 Votre produit est en cours de modération par TikTok. Cela prend généralement 24-48 heures.
          </p>
        </div>
      )}

      {syncStatus === 'success' && (
        <div className="mt-4 space-y-2">
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800 font-medium mb-2">
              ✅ Produit en ligne sur TikTok Shop!
            </p>
            <p className="text-xs text-green-700">
              Vous pouvez maintenant créer des vidéos TikTok pour promouvoir ce produit.
            </p>
          </div>

          <button
            onClick={() => {/* TODO: Ouvrir le générateur de script */}}
            className="w-full px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg font-medium hover:from-pink-600 hover:to-purple-700 transition"
          >
            🎬 Générer un script vidéo TikTok
          </button>
        </div>
      )}
    </div>
  );
};

export default TikTokProductSync;
