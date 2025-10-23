import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import { Search, X, TrendingUp, Package, Users, Target } from 'lucide-react';

const GlobalSearch = () => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState({
    campaigns: [],
    products: [],
    influencers: [],
    merchants: []
  });
  const [loading, setLoading] = useState(false);
  const searchRef = useRef(null);

  useEffect(() => {
    // Écouter Ctrl+K pour ouvrir la recherche
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    // Click outside pour fermer
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  useEffect(() => {
    if (query.length >= 2) {
      performSearch();
    } else {
      setResults({ campaigns: [], products: [], influencers: [], merchants: [] });
    }
  }, [query]);

  const performSearch = async () => {
    setLoading(true);
    try {
      const [campaignsRes, productsRes, influencersRes, merchantsRes] = await Promise.allSettled([
        api.get('/api/campaigns'),
        api.get('/api/products'),
        api.get('/api/influencers'),
        api.get('/api/merchants')
      ]);

      const searchLower = query.toLowerCase();

      // Filtrer campagnes
      const campaigns = campaignsRes.status === 'fulfilled'
        ? (campaignsRes.value.data.data || []).filter(c =>
            c.name?.toLowerCase().includes(searchLower) ||
            c.category?.toLowerCase().includes(searchLower)
          ).slice(0, 3)
        : [];

      // Filtrer produits
      const products = productsRes.status === 'fulfilled'
        ? (productsRes.value.data.products || []).filter(p =>
            p.name?.toLowerCase().includes(searchLower) ||
            p.description?.toLowerCase().includes(searchLower) ||
            p.category?.toLowerCase().includes(searchLower)
          ).slice(0, 3)
        : [];

      // Filtrer influencers
      const influencers = influencersRes.status === 'fulfilled'
        ? (influencersRes.value.data.influencers || []).filter(i =>
            i.name?.toLowerCase().includes(searchLower) ||
            i.email?.toLowerCase().includes(searchLower)
          ).slice(0, 3)
        : [];

      // Filtrer merchants
      const merchants = merchantsRes.status === 'fulfilled'
        ? (merchantsRes.value.data.merchants || []).filter(m =>
            m.company_name?.toLowerCase().includes(searchLower) ||
            m.email?.toLowerCase().includes(searchLower)
          ).slice(0, 3)
        : [];

      setResults({ campaigns, products, influencers, merchants });
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResultClick = (type, id) => {
    setIsOpen(false);
    setQuery('');
    
    switch (type) {
      case 'campaign':
        navigate(`/campaigns`);
        break;
      case 'product':
        navigate(`/products/${id}/edit`);
        break;
      case 'influencer':
        navigate(`/influencers/${id}`);
        break;
      case 'merchant':
        navigate(`/merchants`);
        break;
      default:
        break;
    }
  };

  const totalResults = results.campaigns.length + results.products.length + 
                       results.influencers.length + results.merchants.length;

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition text-sm text-gray-600"
      >
        <Search size={16} />
        <span>Rechercher...</span>
        <kbd className="hidden md:inline-block px-2 py-0.5 text-xs bg-white border rounded">
          Ctrl+K
        </kbd>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-start justify-center pt-20">
      <div ref={searchRef} className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[600px] flex flex-col">
        {/* Search Input */}
        <div className="p-4 border-b flex items-center gap-3">
          <Search size={20} className="text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher campagnes, produits, influenceurs..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 outline-none text-lg"
            autoFocus
          />
          <button
            onClick={() => {
              setIsOpen(false);
              setQuery('');
            }}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading && (
            <div className="text-center py-8 text-gray-500">
              Recherche en cours...
            </div>
          )}

          {!loading && query.length >= 2 && totalResults === 0 && (
            <div className="text-center py-8 text-gray-500">
              Aucun résultat pour "{query}"
            </div>
          )}

          {!loading && query.length < 2 && (
            <div className="text-center py-8 text-gray-400">
              <Search size={48} className="mx-auto mb-3 text-gray-300" />
              <p>Tapez au moins 2 caractères pour rechercher</p>
              <p className="text-sm mt-2">Campagnes • Produits • Influenceurs • Marchands</p>
            </div>
          )}

          {/* Campaigns */}
          {results.campaigns.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-500 mb-2 flex items-center gap-2">
                <Target size={16} />
                Campagnes
              </h3>
              <div className="space-y-2">
                {results.campaigns.map((campaign) => (
                  <button
                    key={campaign.id}
                    onClick={() => handleResultClick('campaign', campaign.id)}
                    className="w-full p-3 hover:bg-gray-50 rounded-lg text-left transition flex items-center gap-3"
                  >
                    <div className="bg-indigo-100 p-2 rounded">
                      <Target size={18} className="text-indigo-600" />
                    </div>
                    <div>
                      <div className="font-medium">{campaign.name}</div>
                      <div className="text-sm text-gray-500">{campaign.category}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Products */}
          {results.products.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-500 mb-2 flex items-center gap-2">
                <Package size={16} />
                Produits
              </h3>
              <div className="space-y-2">
                {results.products.map((product) => (
                  <button
                    key={product.id}
                    onClick={() => handleResultClick('product', product.id)}
                    className="w-full p-3 hover:bg-gray-50 rounded-lg text-left transition flex items-center gap-3"
                  >
                    <div className="bg-green-100 p-2 rounded">
                      <Package size={18} className="text-green-600" />
                    </div>
                    <div>
                      <div className="font-medium">{product.name}</div>
                      <div className="text-sm text-gray-500">{product.price}€</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Influencers */}
          {results.influencers.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-500 mb-2 flex items-center gap-2">
                <TrendingUp size={16} />
                Influenceurs
              </h3>
              <div className="space-y-2">
                {results.influencers.map((influencer) => (
                  <button
                    key={influencer.id}
                    onClick={() => handleResultClick('influencer', influencer.id)}
                    className="w-full p-3 hover:bg-gray-50 rounded-lg text-left transition flex items-center gap-3"
                  >
                    <div className="bg-purple-100 p-2 rounded">
                      <TrendingUp size={18} className="text-purple-600" />
                    </div>
                    <div>
                      <div className="font-medium">{influencer.name}</div>
                      <div className="text-sm text-gray-500">{influencer.email}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Merchants */}
          {results.merchants.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-500 mb-2 flex items-center gap-2">
                <Users size={16} />
                Marchands
              </h3>
              <div className="space-y-2">
                {results.merchants.map((merchant) => (
                  <button
                    key={merchant.id}
                    onClick={() => handleResultClick('merchant', merchant.id)}
                    className="w-full p-3 hover:bg-gray-50 rounded-lg text-left transition flex items-center gap-3"
                  >
                    <div className="bg-blue-100 p-2 rounded">
                      <Users size={18} className="text-blue-600" />
                    </div>
                    <div>
                      <div className="font-medium">{merchant.company_name || merchant.name}</div>
                      <div className="text-sm text-gray-500">{merchant.email}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t bg-gray-50 text-xs text-gray-500 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-0.5 bg-white border rounded">↑↓</kbd>
              Naviguer
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-0.5 bg-white border rounded">Enter</kbd>
              Sélectionner
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-0.5 bg-white border rounded">Esc</kbd>
              Fermer
            </span>
          </div>
          {totalResults > 0 && (
            <span>{totalResults} résultat{totalResults > 1 ? 's' : ''}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default GlobalSearch;
