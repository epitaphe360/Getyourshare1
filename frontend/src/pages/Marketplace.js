import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import Card from '../components/common/Card';
import { 
  Search, Filter, Star, TrendingUp, Package, 
  Users, ShoppingBag, Sparkles, Eye, Target,
  Heart, ExternalLink
} from 'lucide-react';

const MarketplaceNew = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('popular');

  useEffect(() => {
    fetchProducts();
  }, [selectedCategory]);

  const fetchProducts = async () => {
    try {
      const params = selectedCategory !== 'all' ? { category: selectedCategory } : {};
      const response = await api.get('/api/products', { params });
      // Gestion des deux formats de réponse possibles
      const productsData = Array.isArray(response.data) ? response.data : response.data.products || [];
      setProducts(productsData);
    } catch (error) {
      console.error('Error fetching products:', error);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { id: 'all', name: 'Tous', icon: '🌟' },
    { id: 'Mode', name: 'Mode', icon: '👕' },
    { id: 'Beauté', name: 'Beauté', icon: '💄' },
    { id: 'Technologie', name: 'Tech', icon: '📱' },
    { id: 'Sport', name: 'Sport', icon: '⚽' },
    { id: 'Alimentation', name: 'Food', icon: '🍔' },
    { id: 'Maison', name: 'Maison', icon: '🏠' }
  ];

  const handleGenerateLink = async (productId) => {
    console.log('Generate link called for product:', productId);
    console.log('User role:', user?.role);
    
    if (user?.role !== 'influencer') {
      alert('Vous devez être un influenceur pour générer des liens');
      return;
    }

    try {
      console.log('Sending API request...');
      const response = await api.post('/api/affiliate-links/generate', { product_id: productId });
      console.log('API Response:', response.data);
      
      if (response.data.link) {
        const linkUrl = response.data.link.short_url || response.data.link.full_url;
        alert(`✅ Lien généré avec succès !\n\n${linkUrl}`);
        
        // Copy to clipboard (with error handling)
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(linkUrl);
          }
        } catch (err) {
          console.log('Could not copy to clipboard:', err);
        }
        
        // Redirect to tracking links page
        setTimeout(() => {
          navigate('/tracking-links');
        }, 1500);
      }
    } catch (error) {
      console.error('Error generating link:', error);
      console.error('Error details:', error.response?.data);
      alert(`❌ Erreur lors de la génération du lien:\n${error.response?.data?.detail || error.message}`);
    }
  };

  // Filter and sort products
  let filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.description?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  // Sort products
  if (sortBy === 'popular') {
    filteredProducts.sort((a, b) => (b.total_views || 0) - (a.total_views || 0));
  } else if (sortBy === 'commission') {
    filteredProducts.sort((a, b) => (b.commission_rate || 0) - (a.commission_rate || 0));
  } else if (sortBy === 'sales') {
    filteredProducts.sort((a, b) => (b.total_sales || 0) - (a.total_sales || 0));
  }

  if (loading) {
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
          Découvrez des milliers de produits à promouvoir et gagnez des commissions attractives
        </p>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="bg-purple-100 p-3 rounded-lg">
              <Package className="text-purple-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{products.length}</div>
              <div className="text-sm text-gray-600">Produits Disponibles</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="bg-green-100 p-3 rounded-lg">
              <TrendingUp className="text-green-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">15-25%</div>
              <div className="text-sm text-gray-600">Commission Moyenne</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-100 p-3 rounded-lg">
              <Users className="text-indigo-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">2.5K+</div>
              <div className="text-sm text-gray-600">Affiliés Actifs</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="bg-orange-100 p-3 rounded-lg">
              <Star className="text-orange-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">4.8/5</div>
              <div className="text-sm text-gray-600">Satisfaction Moyenne</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <div className="space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher un produit, une marque..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          {/* Category Filters */}
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  selectedCategory === category.id
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span className="mr-2">{category.icon}</span>
                {category.name}
              </button>
            ))}
          </div>

          {/* Sort Options */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              <span className="font-semibold">{filteredProducts.length}</span> produits trouvés
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="text-gray-400" size={16} />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="popular">Plus Populaires</option>
                <option value="commission">Meilleure Commission</option>
                <option value="sales">Meilleures Ventes</option>
              </select>
            </div>
          </div>
        </div>
      </Card>

      {/* Products Grid */}
      {filteredProducts.length === 0 ? (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun produit trouvé</h3>
          <p className="text-gray-600">Essayez de modifier vos filtres de recherche</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 group"
            >
              {/* Product Image */}
              <div className="relative h-48 bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center overflow-hidden">
                {product.images && product.images.length > 0 ? (
                  <img
                    src={product.images[0]}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                  />
                ) : (
                  <Package className="w-24 h-24 text-purple-300" />
                )}
                <div className="absolute top-3 right-3">
                  <button className="bg-white p-2 rounded-full shadow-lg hover:bg-pink-50 transition">
                    <Heart className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
                <div className="absolute top-3 left-3">
                  <span className="bg-white px-3 py-1 rounded-full text-sm font-semibold text-purple-600">
                    {product.category}
                  </span>
                </div>
              </div>

              {/* Product Info */}
              <div className="p-5">
                <div className="mb-3">
                  <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-2">
                    {product.name}
                  </h3>
                  <p className="text-sm text-gray-500">{product.merchant_name}</p>
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {product.description}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2 mb-4">
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                      <Eye className="w-4 h-4 text-gray-400 mr-1" />
                    </div>
                    <div className="text-xs text-gray-600">{product.total_views || 0}</div>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                      <Target className="w-4 h-4 text-gray-400 mr-1" />
                    </div>
                    <div className="text-xs text-gray-600">{product.total_clicks || 0}</div>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                      <ShoppingBag className="w-4 h-4 text-gray-400 mr-1" />
                    </div>
                    <div className="text-xs text-gray-600">{product.total_sales || 0}</div>
                  </div>
                </div>

                {/* Price & Commission */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className="text-2xl font-bold text-gray-900">
                      {product.price?.toLocaleString()} {product.currency || '€'}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-600">Commission</div>
                    <div className="text-lg font-bold text-green-600">
                      {product.commission_rate}%
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex space-x-2">
                  {user?.role === 'influencer' ? (
                    <button
                      onClick={() => handleGenerateLink(product.id)}
                      className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition"
                    >
                      <Sparkles className="inline-block w-4 h-4 mr-2" />
                      Générer Lien
                    </button>
                  ) : (
                    <button
                      className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg font-semibold hover:bg-gray-200 transition"
                    >
                      Voir Détails
                    </button>
                  )}
                  <button className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition">
                    <ExternalLink className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* CTA Banner */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white text-center">
        <h3 className="text-2xl font-bold mb-2">Vous êtes une entreprise ?</h3>
        <p className="text-purple-100 mb-4">
          Ajoutez vos produits au marketplace et trouvez des influenceurs pour les promouvoir
        </p>
        <button
          onClick={() => navigate('/register')}
          className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-purple-50 transition"
        >
          Rejoindre en tant qu'Entreprise
        </button>
      </div>
    </div>
  );
};

export default MarketplaceNew;
