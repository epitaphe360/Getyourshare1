import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import Card from '../components/common/Card';
import {
  Search, Filter, Star, TrendingUp, Package,
  Users, ShoppingBag, Sparkles, Eye, Target,
  Heart, ExternalLink, Tag, Clock, MapPin
} from 'lucide-react';

/**
 * Marketplace Page V2 - Groupon Style
 * Utilise les nouveaux endpoints /api/marketplace/*
 */
const MarketplaceV2 = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [dealsOfDay, setDealsOfDay] = useState([]);
  const [loading, setLoading] = useState(true);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minDiscount, setMinDiscount] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchCategories();
    fetchFeaturedProducts();
    fetchDealsOfDay();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [selectedCategory, sortBy, page, minPrice, maxPrice, minDiscount]);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/api/marketplace/categories');
      if (response.data.success) {
        setCategories(response.data.categories || []);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchFeaturedProducts = async () => {
    try {
      const response = await api.get('/api/marketplace/featured');
      if (response.data.success) {
        setFeaturedProducts(response.data.products || []);
      }
    } catch (error) {
      console.error('Error fetching featured products:', error);
    }
  };

  const fetchDealsOfDay = async () => {
    try {
      const response = await api.get('/api/marketplace/deals-of-day');
      if (response.data.success) {
        setDealsOfDay(response.data.deals || []);
      }
    } catch (error) {
      console.error('Error fetching deals:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: 12,
        sort: sortBy,
        ...(searchTerm && { search: searchTerm }),
        ...(selectedCategory && { category: selectedCategory }),
        ...(minPrice && { min_price: minPrice }),
        ...(maxPrice && { max_price: maxPrice }),
        ...(minDiscount && { min_discount: minDiscount })
      };

      const response = await api.get('/api/marketplace/products', { params });
      if (response.data.success) {
        setProducts(response.data.products || []);
        setTotalPages(response.data.total_pages || 1);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
      toast.error('Erreur lors du chargement des produits');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchProducts();
  };

  const handleRequestAffiliation = async (productId) => {
    if (user?.role !== 'influencer') {
      toast.warning('Vous devez être un influenceur pour demander une affiliation');
      return;
    }

    try {
      const response = await api.post(`/api/marketplace/products/${productId}/request-affiliate`, {
        message: 'Je souhaite promouvoir ce produit sur mes réseaux sociaux.'
      });

      if (response.data.success) {
        toast.success('Demande d\'affiliation envoyée avec succès!');
      }
    } catch (error) {
      console.error('Error requesting affiliation:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la demande');
    }
  };

  const handleViewDetails = (productId) => {
    navigate(`/marketplace/product/${productId}`);
  };

  // Fonction utilitaire pour gérer les images (JSONB array)
  const getProductImage = (product) => {
    if (!product.images) return null;

    if (Array.isArray(product.images) && product.images.length > 0) {
      return product.images[0];
    }

    if (typeof product.images === 'string') {
      try {
        const parsed = JSON.parse(product.images);
        return Array.isArray(parsed) && parsed.length > 0 ? parsed[0] : null;
      } catch {
        return null;
      }
    }

    return null;
  };

  const ProductCard = ({ product, featured = false }) => {
    const imageUrl = getProductImage(product);
    const hasDiscount = product.discount_percentage && product.discount_percentage > 0;

    return (
      <div
        className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 group cursor-pointer ${
          featured ? 'ring-2 ring-purple-500' : ''
        }`}
        onClick={() => handleViewDetails(product.id)}
      >
        {/* Product Image */}
        <div className="relative h-56 bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center overflow-hidden">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={product.name}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          ) : (
            <Package className="w-24 h-24 text-purple-300" />
          )}

          {/* Discount Badge */}
          {hasDiscount && (
            <div className="absolute top-3 left-3">
              <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg">
                -{product.discount_percentage}%
              </span>
            </div>
          )}

          {/* Featured Badge */}
          {featured && (
            <div className="absolute top-3 right-3">
              <span className="bg-purple-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">
                ⭐ VEDETTE
              </span>
            </div>
          )}

          {/* Deal of Day Badge */}
          {product.is_deal_of_day && (
            <div className="absolute top-3 right-3">
              <span className="bg-orange-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg animate-pulse">
                🔥 DEAL DU JOUR
              </span>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="p-5">
          <div className="mb-3">
            <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-2">
              {product.name}
            </h3>
            <p className="text-sm text-gray-500">{product.merchant?.name || 'Marchand'}</p>
          </div>

          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {product.description}
          </p>

          {/* Location for services */}
          {product.is_service && product.location && (
            <div className="flex items-center text-sm text-gray-500 mb-3">
              <MapPin className="w-4 h-4 mr-1" />
              {product.location.city || 'Maroc'}
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Eye className="w-4 h-4 text-gray-400 mr-1" />
              </div>
              <div className="text-xs text-gray-600">{product.views_count || 0}</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Star className="w-4 h-4 text-yellow-400 mr-1" />
              </div>
              <div className="text-xs text-gray-600">
                {product.rating_average ? product.rating_average.toFixed(1) : 'N/A'}
              </div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <ShoppingBag className="w-4 h-4 text-gray-400 mr-1" />
              </div>
              <div className="text-xs text-gray-600">{product.sold_count || 0}</div>
            </div>
          </div>

          {/* Price & Discount */}
          <div className="mb-4">
            {hasDiscount ? (
              <div>
                <div className="flex items-baseline space-x-2">
                  <div className="text-2xl font-bold text-red-600">
                    {product.discounted_price?.toLocaleString()} DH
                  </div>
                  <div className="text-lg text-gray-400 line-through">
                    {product.original_price?.toLocaleString()} DH
                  </div>
                </div>
                <div className="text-xs text-green-600 mt-1">
                  Économisez {(product.original_price - product.discounted_price).toLocaleString()} DH
                </div>
              </div>
            ) : (
              <div className="text-2xl font-bold text-gray-900">
                {product.discounted_price?.toLocaleString() || product.original_price?.toLocaleString()} DH
              </div>
            )}
          </div>

          {/* Expiry Date */}
          {product.expiry_date && (
            <div className="flex items-center text-sm text-orange-600 mb-3">
              <Clock className="w-4 h-4 mr-1" />
              Expire le {new Date(product.expiry_date).toLocaleDateString('fr-FR')}
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleViewDetails(product.id);
              }}
              className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition"
            >
              Voir Détails
            </button>

            {user?.role === 'influencer' && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRequestAffiliation(product.id);
                }}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
                title="Demander l'affiliation"
              >
                <Sparkles className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (loading && page === 1) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement du marketplace...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center space-x-3 mb-4">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 w-16 h-16 rounded-2xl flex items-center justify-center">
            <ShoppingBag className="text-white" size={32} />
          </div>
        </div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
          Marketplace ShareYourSales
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Découvrez des offres exclusives style Groupon - Deals, Services, Produits
        </p>
      </div>

      {/* Deals of the Day */}
      {dealsOfDay.length > 0 && (
        <div>
          <div className="flex items-center mb-4">
            <Tag className="w-6 h-6 text-orange-500 mr-2" />
            <h2 className="text-2xl font-bold text-gray-900">🔥 Deals du Jour</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {dealsOfDay.slice(0, 4).map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      )}

      {/* Featured Products */}
      {featuredProducts.length > 0 && (
        <div>
          <div className="flex items-center mb-4">
            <Star className="w-6 h-6 text-purple-500 mr-2" />
            <h2 className="text-2xl font-bold text-gray-900">⭐ Produits Vedettes</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {featuredProducts.slice(0, 3).map((product) => (
              <ProductCard key={product.id} product={product} featured />
            ))}
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <Card>
        <div className="space-y-4">
          {/* Search Bar */}
          <form onSubmit={handleSearch}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher un produit, service, deal..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </form>

          {/* Category Filters */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                selectedCategory === ''
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Tous
            </button>
            {categories.slice(0, 8).map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  selectedCategory === category.id
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.icon && <span className="mr-2">{category.icon}</span>}
                {category.name}
              </button>
            ))}
          </div>

          {/* Price and Discount Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              type="number"
              placeholder="Prix min (DH)"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <input
              type="number"
              placeholder="Prix max (DH)"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <input
              type="number"
              placeholder="Réduction min (%)"
              value={minDiscount}
              onChange={(e) => setMinDiscount(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="created_at">Plus Récents</option>
              <option value="discount">Meilleur Rabais</option>
              <option value="price">Prix Croissant</option>
              <option value="rating">Mieux Notés</option>
              <option value="sold_count">Plus Vendus</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Products Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Tous les Produits</h2>
          <div className="text-sm text-gray-600">
            Page {page} sur {totalPages}
          </div>
        </div>

        {products.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun produit trouvé</h3>
            <p className="text-gray-600">Essayez de modifier vos filtres de recherche</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center mt-8 space-x-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-300"
                >
                  Précédent
                </button>
                <div className="flex items-center px-4">
                  Page {page} / {totalPages}
                </div>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-300"
                >
                  Suivant
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* CTA Banner */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white text-center">
        <h3 className="text-2xl font-bold mb-2">Vous êtes un commerçant ?</h3>
        <p className="text-purple-100 mb-4">
          Ajoutez vos produits et offres au marketplace - Deals, réductions, services
        </p>
        <button
          onClick={() => navigate('/register')}
          className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-purple-50 transition"
        >
          Rejoindre en tant que Marchand
        </button>
      </div>
    </div>
  );
};

export default MarketplaceV2;
