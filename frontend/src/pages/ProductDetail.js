import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import {
  Star, MapPin, Clock, Tag, Share2, Heart,
  Sparkles, ChevronLeft, ChevronRight,
  Check, X, Calendar, Users, Award, Phone,
  Mail, Globe, AlertCircle, ThumbsUp, ThumbsDown
} from 'lucide-react';

/**
 * Product Detail Page - Groupon Style
 * Full product details with images, highlights, conditions, FAQ, reviews
 */
const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();

  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [showAffiliateModal, setShowAffiliateModal] = useState(false);
  const [affiliateData, setAffiliateData] = useState({
    selectedProduct: '',
    message: ''
  });
  const [reviewData, setReviewData] = useState({
    rating: 5,
    title: '',
    comment: ''
  });

  useEffect(() => {
    if (productId) {
      fetchProductDetails();
      fetchProductReviews();
    }
  }, [productId]);

  const fetchProductDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/marketplace/products/${productId}`);
      if (response.data.success) {
        setProduct(response.data.product);
      }
    } catch (error) {
      console.error('Error fetching product:', error);
      toast.error('Erreur lors du chargement du produit');
    } finally {
      setLoading(false);
    }
  };

  const fetchProductReviews = async () => {
    try {
      const response = await api.get(`/api/marketplace/products/${productId}/reviews`);
      if (response.data.success) {
        setReviews(response.data.reviews || []);
      }
    } catch (error) {
      console.error('Error fetching reviews:', error);
    }
  };

  const handleRequestAffiliation = async () => {
    // Vérifier si l'utilisateur est connecté
    if (!user) {
      toast.info('Veuillez vous connecter pour demander une affiliation');
      // Sauvegarder l'URL actuelle pour rediriger après connexion
      localStorage.setItem('redirectAfterLogin', window.location.pathname);
      navigate('/login');
      return;
    }

    // Vérifier le rôle
    if (user.role !== 'influencer' && user.role !== 'commercial') {
      toast.warning('Vous devez être un influenceur ou commercial pour demander une affiliation');
      return;
    }

    // Ouvrir la modale
    setShowAffiliateModal(true);
    setAffiliateData({
      selectedProduct: product.name,
      message: ''
    });
  };

  const handleSubmitAffiliateRequest = async (e) => {
    e.preventDefault();

    if (!affiliateData.message.trim()) {
      toast.warning('Veuillez rédiger un message de présentation');
      return;
    }

    try {
      const response = await api.post(`/api/marketplace/products/${productId}/request-affiliate`, {
        message: affiliateData.message
      });

      if (response.data.success) {
        toast.success('Demande d\'affiliation envoyée avec succès!');
        if (response.data.affiliate_link) {
          toast.info(`Votre lien: ${response.data.affiliate_link}`);
        }
        setShowAffiliateModal(false);
        setAffiliateData({ selectedProduct: '', message: '' });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la demande');
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!user) {
      toast.warning('Vous devez être connecté pour laisser un avis');
      return;
    }

    try {
      const response = await api.post(`/api/marketplace/products/${productId}/review`, reviewData);
      if (response.data.success) {
        toast.success('Votre avis a été soumis et sera vérifié par nos modérateurs');
        setShowReviewForm(false);
        setReviewData({ rating: 5, title: '', comment: '' });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'envoi de l\'avis');
    }
  };

  const getImages = () => {
    // Utiliser l'image principale du produit (image_url) comme dans le marketplace
    const mainImage = product?.image_url || 
                     (product?.type === 'service' 
                       ? `https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=600&fit=crop&q=80`
                       : `https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop&q=80`);
    
    // Si images existe, l'utiliser en complément
    if (product?.images) {
      if (Array.isArray(product.images)) {
        return [mainImage, ...product.images];
      }
      if (typeof product.images === 'string') {
        try {
          const parsed = JSON.parse(product.images);
          if (Array.isArray(parsed)) {
            return [mainImage, ...parsed];
          }
        } catch {
          // Ignore parsing error
        }
      }
    }
    
    // Par défaut, retourner seulement l'image principale
    return [mainImage];
  };

  const getHighlights = () => {
    if (!product?.highlights) return [];
    if (Array.isArray(product.highlights)) return product.highlights;
    if (typeof product.highlights === 'string') {
      try {
        return JSON.parse(product.highlights);
      } catch {
        return [];
      }
    }
    return [];
  };

  const getFAQ = () => {
    if (!product?.faq) return [];
    if (Array.isArray(product.faq)) return product.faq;
    if (typeof product.faq === 'string') {
      try {
        return JSON.parse(product.faq);
      } catch {
        return [];
      }
    }
    return [];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <AlertCircle className="w-16 h-16 text-gray-300 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Produit non trouvé</h2>
        <button
          onClick={() => navigate('/marketplace')}
          className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Retour au Marketplace
        </button>
      </div>
    );
  }

  const images = getImages();
  const highlights = getHighlights();
  const faq = getFAQ();
  const hasDiscount = product.discount_percentage && product.discount_percentage > 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Back Button */}
      <button
        onClick={() => navigate('/marketplace')}
        className="flex items-center text-purple-600 hover:text-purple-700 mb-6"
      >
        <ChevronLeft className="w-5 h-5 mr-1" />
        Retour au Marketplace
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Images & Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Image Gallery */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            {images.length > 0 ? (
              <div className="relative">
                <img
                  src={images[currentImageIndex]}
                  alt={product.name}
                  className="w-full h-96 object-cover"
                  onError={(e) => {
                    // Fallback selon le type (product ou service)
                    e.target.onerror = null;
                    if (product?.type === 'service') {
                      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="600"%3E%3Crect fill="%233b82f6" width="800" height="600"/%3E%3Ctext fill="%23ffffff" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EService%3C/text%3E%3C/svg%3E';
                    } else {
                      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="600"%3E%3Crect fill="%2310b981" width="800" height="600"/%3E%3Ctext fill="%23ffffff" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EProduit%3C/text%3E%3C/svg%3E';
                    }
                  }}
                />
                {images.length > 1 && (
                  <>
                    <button
                      onClick={() => setCurrentImageIndex((currentImageIndex - 1 + images.length) % images.length)}
                      className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white/80 p-2 rounded-full hover:bg-white"
                    >
                      <ChevronLeft className="w-6 h-6" />
                    </button>
                    <button
                      onClick={() => setCurrentImageIndex((currentImageIndex + 1) % images.length)}
                      className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white/80 p-2 rounded-full hover:bg-white"
                    >
                      <ChevronRight className="w-6 h-6" />
                    </button>
                    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
                      {images.map((_, index) => (
                        <button
                          key={index}
                          onClick={() => setCurrentImageIndex(index)}
                          className={`w-2 h-2 rounded-full ${
                            index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                          }`}
                        />
                      ))}
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="w-full h-96 bg-gradient-to-br from-green-100 to-blue-100 flex items-center justify-center">
                <div className="text-center">
                  <Sparkles className="w-24 h-24 text-green-400 mx-auto mb-4" />
                  <p className="text-gray-600 font-medium">Image du produit</p>
                </div>
              </div>
            )}
          </div>

          {/* Product Title & Description */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>
                <p className="text-gray-600">{product.merchant?.name || 'Marchand'}</p>
              </div>
              <div className="flex space-x-2">
                <button className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200">
                  <Heart className="w-6 h-6 text-gray-600" />
                </button>
                <button className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200">
                  <Share2 className="w-6 h-6 text-gray-600" />
                </button>
              </div>
            </div>

            {/* Rating */}
            {product.rating_average > 0 && (
              <div className="flex items-center mb-4">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-5 h-5 ${
                        i < Math.floor(product.rating_average)
                          ? 'text-yellow-400 fill-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="ml-2 text-gray-600">
                  {product.rating_average.toFixed(1)} ({product.rating_count} avis)
                </span>
              </div>
            )}

            {/* Location for services */}
            {product.is_service && product.location && (
              <div className="flex items-center text-gray-600 mb-4">
                <MapPin className="w-5 h-5 mr-2" />
                <span>
                  {product.location.address}, {product.location.city}
                </span>
              </div>
            )}

            {/* Description */}
            <div className="prose max-w-none">
              <p className="text-gray-700 leading-relaxed">{product.description}</p>
            </div>
          </div>

          {/* Highlights */}
          {highlights.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">✨ Points Forts</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {highlights.map((highlight, index) => (
                  <div key={index} className="flex items-start">
                    <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{highlight}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* What's Included */}
          {product.included && product.included.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">📦 Ce qui est inclus</h2>
              <ul className="space-y-2">
                {product.included.map((item, index) => (
                  <li key={index} className="flex items-start">
                    <Award className="w-5 h-5 text-purple-500 mr-2 mt-0.5" />
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* How it Works */}
          {product.how_it_works && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">🔄 Comment ça marche</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-line">{product.how_it_works}</p>
              </div>
            </div>
          )}

          {/* Conditions */}
          {product.conditions && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">📋 Conditions</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-line">{product.conditions}</p>
              </div>
            </div>
          )}

          {/* FAQ */}
          {faq.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">❓ Questions Fréquentes</h2>
              <div className="space-y-4">
                {faq.map((item, index) => (
                  <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                    <h3 className="font-semibold text-gray-900 mb-2">{item.question}</h3>
                    <p className="text-gray-700">{item.answer}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reviews */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">⭐ Avis Clients</h2>
              {user && (
                <button
                  onClick={() => setShowReviewForm(!showReviewForm)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Laisser un avis
                </button>
              )}
            </div>

            {/* Review Form */}
            {showReviewForm && (
              <form onSubmit={handleSubmitReview} className="mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Note
                  </label>
                  <div className="flex space-x-2">
                    {[1, 2, 3, 4, 5].map((rating) => (
                      <button
                        key={rating}
                        type="button"
                        onClick={() => setReviewData({ ...reviewData, rating })}
                        className="focus:outline-none"
                      >
                        <Star
                          className={`w-8 h-8 ${
                            rating <= reviewData.rating
                              ? 'text-yellow-400 fill-yellow-400'
                              : 'text-gray-300'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Titre (optionnel)
                  </label>
                  <input
                    type="text"
                    value={reviewData.title}
                    onChange={(e) => setReviewData({ ...reviewData, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Résumez votre expérience"
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Commentaire
                  </label>
                  <textarea
                    value={reviewData.comment}
                    onChange={(e) => setReviewData({ ...reviewData, comment: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    rows="4"
                    placeholder="Partagez votre avis..."
                    required
                  />
                </div>

                <div className="flex space-x-2">
                  <button
                    type="submit"
                    className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  >
                    Publier
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowReviewForm(false)}
                    className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            )}

            {/* Reviews List */}
            {reviews.length === 0 ? (
              <p className="text-gray-600 text-center py-8">
                Soyez le premier à laisser un avis!
              </p>
            ) : (
              <div className="space-y-4">
                {reviews.map((review) => (
                  <div key={review.id} className="border-b border-gray-200 pb-4 last:border-b-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <div className="flex items-center mb-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-4 h-4 ${
                                i < review.rating
                                  ? 'text-yellow-400 fill-yellow-400'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        {review.title && (
                          <h4 className="font-semibold text-gray-900">{review.title}</h4>
                        )}
                        <p className="text-sm text-gray-500">
                          Par {review.user?.first_name || 'Anonyme'} le{' '}
                          {new Date(review.created_at).toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                      {review.is_verified_purchase && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          ✓ Achat vérifié
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700">{review.comment}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Purchase Card */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-lg p-6 sticky top-6">
            {/* Price */}
            <div className="mb-6">
              {hasDiscount ? (
                <>
                  <div className="flex items-baseline space-x-2 mb-2">
                    <span className="text-4xl font-bold text-red-600">
                      {product.discounted_price?.toLocaleString()} DH
                    </span>
                    <span className="text-xl text-gray-400 line-through">
                      {product.original_price?.toLocaleString()} DH
                    </span>
                  </div>
                  <div className="inline-block bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-bold">
                    -{product.discount_percentage}% de réduction
                  </div>
                  <div className="text-sm text-green-600 mt-2">
                    Économisez{' '}
                    {(product.original_price - product.discounted_price).toLocaleString()} DH
                  </div>
                </>
              ) : (
                <div className="text-4xl font-bold text-gray-900">
                  {product.discounted_price?.toLocaleString() ||
                    product.original_price?.toLocaleString()}{' '}
                  DH
                </div>
              )}
            </div>

            {/* Expiry */}
            {product.expiry_date && (
              <div className="flex items-center text-orange-600 mb-4 p-3 bg-orange-50 rounded-lg">
                <Clock className="w-5 h-5 mr-2" />
                <span className="text-sm">
                  Expire le {new Date(product.expiry_date).toLocaleDateString('fr-FR')}
                </span>
              </div>
            )}

            {/* Stock */}
            {product.stock_quantity !== null && (
              <div className="mb-4">
                {product.stock_quantity > 0 ? (
                  <span className="text-green-600 text-sm">
                    ✓ En stock ({product.stock_quantity} disponibles)
                  </span>
                ) : (
                  <span className="text-red-600 text-sm">✗ Rupture de stock</span>
                )}
              </div>
            )}

            {/* Sold Count */}
            {product.sold_count > 0 && (
              <div className="flex items-center text-gray-600 mb-4">
                <Users className="w-5 h-5 mr-2" />
                <span className="text-sm">{product.sold_count} personnes ont acheté</span>
              </div>
            )}

            {/* Request Affiliation Button - Principal et toujours visible */}
            <button
              onClick={handleRequestAffiliation}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-4 rounded-lg font-bold text-lg hover:from-green-600 hover:to-emerald-700 transition flex items-center justify-center shadow-lg mb-3"
            >
              <Sparkles className="inline-block w-6 h-6 mr-2" />
              {user ? 'Demander un Lien d\'Affiliation' : 'Se connecter pour devenir Affilié'}
            </button>

            {/* Commission Info */}
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-green-800">
                  Commission d'affiliation
                </span>
                <span className="text-2xl font-bold text-green-600">
                  {product.commission_rate || 15}%
                </span>
              </div>
              <p className="text-xs text-green-700">
                💰 Gagnez des commissions en promouvant ce produit auprès de votre audience
              </p>
            </div>

            {/* Merchant Info */}
            {product.merchant && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="font-semibold text-gray-900 mb-3">Vendu par</h3>
                <div className="space-y-2">
                  <p className="font-medium text-gray-900">{product.merchant.name}</p>
                  {product.merchant.phone && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Phone className="w-4 h-4 mr-2" />
                      {product.merchant.phone}
                    </div>
                  )}
                  {product.merchant.email && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Mail className="w-4 h-4 mr-2" />
                      {product.merchant.email}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Affiliate Request Modal */}
      {showAffiliateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            {/* Header */}
            <div className="sticky top-0 bg-gradient-to-r from-green-500 to-emerald-600 text-white p-6 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold flex items-center">
                    <Sparkles className="w-6 h-6 mr-2" />
                    Demander un Lien d'Affiliation
                  </h2>
                  <p className="text-green-50 text-sm mt-1">
                    Rejoignez notre programme d'affiliation et commencez à gagner des commissions
                  </p>
                </div>
                <button
                  onClick={() => setShowAffiliateModal(false)}
                  className="text-white hover:bg-white/20 rounded-full p-2 transition"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* How it works */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
                <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Comment ça fonctionne ?
                </h3>
                <p className="text-blue-800 text-sm leading-relaxed">
                  Sélectionnez un produit et présentez-vous au marchand. Si votre demande est approuvée, 
                  un lien de tracking sera automatiquement créé pour vous.
                </p>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmitAffiliateRequest} className="space-y-6">
                {/* Product Selection */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-2">
                    Sélectionnez un produit <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={affiliateData.selectedProduct}
                      readOnly
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg bg-gray-50 text-gray-700 font-medium cursor-not-allowed"
                      placeholder="Choisir un produit..."
                    />
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <Check className="w-5 h-5 text-green-600" />
                    </div>
                  </div>
                  {!product && (
                    <p className="text-sm text-gray-500 mt-2">
                      Aucun produit disponible. Visitez le Marketplace pour découvrir les produits.
                    </p>
                  )}
                </div>

                {/* Message to Merchant */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-2">
                    Message au marchand <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={affiliateData.message}
                    onChange={(e) => setAffiliateData({ ...affiliateData, message: e.target.value })}
                    rows="6"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 transition resize-none"
                    placeholder="Présentez-vous et expliquez pourquoi vous souhaitez promouvoir ce produit...&#10;Incluez vos réseaux sociaux, nombre de followers, niche, etc."
                    required
                  />
                  <div className="flex items-start mt-2 text-xs text-gray-500">
                    <AlertCircle className="w-4 h-4 mr-1 mt-0.5 flex-shrink-0" />
                    <p>
                      Incluez vos réseaux sociaux, nombre de followers, niche, etc.
                    </p>
                  </div>
                </div>

                {/* Product Info Card */}
                {product && (
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-4">
                    <div className="flex items-start space-x-4">
                      <img
                        src={product.image_url || '/logo.jpg'}
                        alt={product.name}
                        className="w-20 h-20 object-cover rounded-lg"
                        onError={(e) => {
                          e.target.src = '/logo.png';
                        }}
                      />
                      <div className="flex-1">
                        <h4 className="font-bold text-gray-900 mb-1">{product.name}</h4>
                        <p className="text-sm text-gray-600 mb-2">{product.description?.substring(0, 100)}...</p>
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center">
                            <Award className="w-4 h-4 text-green-600 mr-1" />
                            <span className="text-sm font-semibold text-green-700">
                              {product.commission_rate || 15}% commission
                            </span>
                          </div>
                          {product.price && (
                            <span className="text-sm font-bold text-gray-900">
                              {product.price.toFixed(2)} MAD
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Commission Info */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <Award className="w-6 h-6 text-yellow-600" />
                    </div>
                    <div className="ml-3">
                      <h4 className="font-semibold text-yellow-900 mb-1">
                        Gagnez {product?.commission_rate || 15}% de commission
                      </h4>
                      <p className="text-sm text-yellow-800">
                        Pour chaque vente générée via votre lien d'affiliation, vous recevez une commission de {product?.commission_rate || 15}%.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAffiliateModal(false)}
                    className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-bold hover:from-green-600 hover:to-emerald-700 transition flex items-center justify-center shadow-lg"
                  >
                    <Sparkles className="w-5 h-5 mr-2" />
                    Envoyer la Demande
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;
