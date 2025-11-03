import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import './MarketplaceAnimations.css';
import {
  Star, MapPin, Clock, Tag, Share2, Heart,
  Sparkles, ChevronLeft, ChevronRight,
  Check, X, Calendar, Users, Award, Phone,
  Mail, Globe, AlertCircle, ThumbsUp, ThumbsDown, Briefcase
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
  const [userProfile, setUserProfile] = useState(null);
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

  // Vérifier si l'utilisateur revient après connexion pour ouvrir la modale d'affiliation
  useEffect(() => {
    if (user && product) {
      const shouldOpenAffiliate = localStorage.getItem('openAffiliateModal');
      if (shouldOpenAffiliate === 'true') {
        localStorage.removeItem('openAffiliateModal');
        // Ouvrir la modale automatiquement
        setShowAffiliateModal(true);
        setAffiliateData({
          selectedProduct: product.name,
          message: ''
        });
      }
    }
  }, [user, product]);

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

  const fetchUserProfile = async () => {
    if (!user) return;
    
    try {
      let endpoint = '';
      if (user.role === 'influencer') {
        endpoint = '/api/influencers/profile';
      } else if (user.role === 'commercial') {
        endpoint = '/api/commercials/profile';
      }
      
      if (endpoint) {
        const response = await api.get(endpoint);
        if (response.data.success) {
          setUserProfile(response.data.profile || response.data.commercial);
        }
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const handleRequestAffiliation = async () => {
    // Vérifier si l'utilisateur est connecté
    if (!user) {
      toast.info('Veuillez vous connecter pour demander une affiliation');
      // Sauvegarder l'URL actuelle pour rediriger après connexion
      localStorage.setItem('redirectAfterLogin', window.location.pathname);
      // Sauvegarder l'intention d'ouvrir la modale d'affiliation
      localStorage.setItem('openAffiliateModal', 'true');
      navigate('/login');
      return;
    }

    // Vérifier le rôle
    if (user.role !== 'influencer' && user.role !== 'commercial') {
      toast.warning('Vous devez être un influenceur ou commercial pour demander une affiliation');
      return;
    }

    // Charger le profil de l'utilisateur
    await fetchUserProfile();

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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="relative mb-6">
            <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-b-4 border-cyan-600 mx-auto"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <Sparkles className="text-cyan-600 animate-pulse" size={32} />
            </div>
          </div>
          <p className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
            Chargement du produit...
          </p>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 flex flex-col items-center justify-center p-8">
        <div className="bg-white rounded-2xl shadow-2xl p-12 text-center max-w-lg hover-lift">
          <div className="mb-6">
            <AlertCircle className="w-24 h-24 text-gray-300 mx-auto mb-4 animate-pulse" />
          </div>
          <h2 className="text-3xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-4">
            Produit non trouvé
          </h2>
          <p className="text-gray-600 mb-8 text-lg">
            Ce produit n'existe pas ou a été supprimé
          </p>
          <button
            onClick={() => navigate('/marketplace')}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 text-white rounded-xl font-bold hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center gap-2 mx-auto"
          >
            <ChevronLeft size={20} />
            Retour au Marketplace
          </button>
        </div>
      </div>
    );
  }

  const images = getImages();
  const highlights = getHighlights();
  const faq = getFAQ();
  const hasDiscount = product.discount_percentage && product.discount_percentage > 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Back Button - Ultra-moderne */}
        <button
          onClick={() => navigate('/marketplace')}
          className="group flex items-center gap-2 px-6 py-3 bg-white rounded-xl font-bold text-gray-700 hover:text-cyan-600 transition-all duration-300 shadow-md hover:shadow-xl transform hover:scale-105 mb-8"
        >
          <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
          Retour au Marketplace
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Images & Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Image Gallery - Ultra-moderne */}
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden hover-lift">
              {images.length > 0 ? (
                <div className="relative group">
                  <img
                    src={images[currentImageIndex]}
                    alt={product.name}
                    className="w-full h-[500px] object-cover"
                    onError={(e) => {
                      // Fallback selon le type (product ou service)
                      e.target.onerror = null;
                      if (product?.type === 'service') {
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="600"%3E%3Crect fill="%233b82f6" width="800" height="600"/%3E%3Ctext fill="%23ffffff" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EService%3C/text%3E%3C/svg%3E';
                      } else {
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="600"%3E%3Crect fill="%230891b2" width="800" height="600"/%3E%3Ctext fill="%23ffffff" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EProduit%3C/text%3E%3C/svg%3E';
                      }
                    }}
                  />
                  {hasDiscount && (
                    <div className="absolute top-6 right-6 bg-gradient-to-r from-red-500 to-pink-500 text-white px-6 py-3 rounded-2xl font-black text-xl shadow-2xl animate-pulse z-10">
                      -{product.discount_percentage}%
                    </div>
                  )}
                  {images.length > 1 && (
                    <>
                      <button
                        onClick={() => setCurrentImageIndex((currentImageIndex - 1 + images.length) % images.length)}
                        className="absolute left-6 top-1/2 transform -translate-y-1/2 bg-white/95 backdrop-blur-sm p-4 rounded-xl hover:bg-white shadow-xl opacity-0 group-hover:opacity-100 transition-all duration-300 hover:scale-110"
                      >
                        <ChevronLeft className="w-7 h-7 text-gray-800" />
                      </button>
                      <button
                        onClick={() => setCurrentImageIndex((currentImageIndex + 1) % images.length)}
                        className="absolute right-6 top-1/2 transform -translate-y-1/2 bg-white/95 backdrop-blur-sm p-4 rounded-xl hover:bg-white shadow-xl opacity-0 group-hover:opacity-100 transition-all duration-300 hover:scale-110"
                      >
                        <ChevronRight className="w-7 h-7 text-gray-800" />
                      </button>
                      <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-3 bg-black/30 backdrop-blur-md px-4 py-3 rounded-full">
                        {images.map((_, index) => (
                          <button
                            key={index}
                            onClick={() => setCurrentImageIndex(index)}
                            className={`transition-all duration-300 rounded-full ${
                              index === currentImageIndex 
                                ? 'w-10 h-3 bg-white' 
                                : 'w-3 h-3 bg-white/50 hover:bg-white/75'
                            }`}
                          />
                        ))}
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="w-full h-[500px] bg-gradient-to-br from-blue-100 via-cyan-100 to-teal-100 flex items-center justify-center">
                  <div className="text-center">
                    <Sparkles className="w-32 h-32 text-cyan-400 mx-auto mb-6 animate-pulse" />
                    <p className="text-gray-600 font-bold text-xl">Image du produit</p>
                  </div>
                </div>
              )}
            </div>

          {/* Product Title & Description - Ultra-moderne */}
          <div className="bg-white rounded-2xl shadow-xl p-8 hover-lift">
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <h1 className="text-4xl font-black bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent mb-3 leading-tight">
                  {product.name}
                </h1>
                <p className="text-gray-600 text-lg font-semibold flex items-center gap-2">
                  <Award className="w-5 h-5 text-cyan-600" />
                  {product.merchant?.name || 'Marchand Certifié'}
                </p>
              </div>
              <div className="flex space-x-3">
                <button className="p-4 bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl hover:shadow-xl transition-all duration-300 group hover:scale-110">
                  <Heart className="w-6 h-6 text-pink-500 group-hover:fill-pink-500 transition-all" />
                </button>
                <button className="p-4 bg-gradient-to-br from-blue-50 to-cyan-100 rounded-xl hover:shadow-xl transition-all duration-300 group hover:scale-110">
                  <Share2 className="w-6 h-6 text-cyan-600 group-hover:rotate-12 transition-all" />
                </button>
              </div>
            </div>

            {/* Rating */}
            {product.rating_average > 0 && (
              <div className="flex items-center mb-6 bg-gradient-to-r from-yellow-50 to-orange-50 px-4 py-3 rounded-xl">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-6 h-6 ${
                        i < Math.floor(product.rating_average)
                          ? 'text-yellow-400 fill-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="ml-3 text-gray-800 font-bold text-lg">
                  {product.rating_average.toFixed(1)}
                </span>
                <span className="ml-2 text-gray-600 font-medium">
                  ({product.rating_count} avis)
                </span>
              </div>
            )}

            {/* Location for services */}
            {product.is_service && product.location && (
              <div className="flex items-center gap-3 text-gray-700 mb-6 bg-gradient-to-r from-blue-50 to-cyan-50 px-4 py-3 rounded-xl">
                <MapPin className="w-6 h-6 text-cyan-600" />
                <span className="font-semibold">
                  {product.location.address}, {product.location.city}
                </span>
              </div>
            )}

            {/* Description */}
            <div className="prose max-w-none">
              <p className="text-gray-700 leading-relaxed text-lg">{product.description}</p>
            </div>
          </div>

          {/* Highlights - Ultra-moderne */}
          {highlights.length > 0 && (
            <div className="bg-white rounded-2xl shadow-xl p-8 hover-lift">
              <h2 className="text-3xl font-black bg-gradient-to-r from-green-500 to-emerald-600 bg-clip-text text-transparent mb-6 flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-emerald-100 rounded-xl flex items-center justify-center">
                  ✨
                </div>
                Points Forts
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {highlights.map((highlight, index) => (
                  <div key={index} className="flex items-start gap-3 bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-xl hover:shadow-lg transition-all duration-300">
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-gray-800 font-medium leading-relaxed">{highlight}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* What's Included */}
          {product.included && product.included.length > 0 && (
            <div className="bg-white rounded-2xl shadow-xl p-8 hover-lift">
              <h2 className="text-3xl font-black bg-gradient-to-r from-purple-500 to-pink-600 bg-clip-text text-transparent mb-6 flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 rounded-xl flex items-center justify-center">
                  📦
                </div>
                Ce qui est inclus
              </h2>
              <ul className="space-y-3">
                {product.included.map((item, index) => (
                  <li key={index} className="flex items-start gap-3 bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-xl hover:shadow-lg transition-all duration-300">
                    <Award className="w-6 h-6 text-purple-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-800 font-medium leading-relaxed">{item}</span>
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

        {/* Right Column - Purchase Card Ultra-moderne */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl shadow-2xl p-8 sticky top-6 hover-lift border-2 border-blue-100">
            {/* Price - Ultra-moderne */}
            <div className="mb-8">
              {hasDiscount ? (
                <>
                  <div className="flex items-baseline space-x-3 mb-3">
                    <span className="text-5xl font-black bg-gradient-to-r from-red-500 to-pink-600 bg-clip-text text-transparent">
                      {product.discounted_price?.toLocaleString()}
                    </span>
                    <span className="text-2xl font-bold text-gray-900">DH</span>
                  </div>
                  <div className="flex items-baseline space-x-2 mb-4">
                    <span className="text-xl text-gray-400 line-through">
                      {product.original_price?.toLocaleString()} DH
                    </span>
                  </div>
                  <div className="inline-block bg-gradient-to-r from-red-500 to-pink-500 text-white px-4 py-2 rounded-xl text-sm font-black shadow-lg animate-pulse mb-3">
                    🔥 -{product.discount_percentage}% DE RÉDUCTION
                  </div>
                  <div className="text-base font-bold bg-gradient-to-r from-green-500 to-emerald-600 bg-clip-text text-transparent">
                    💰 Économisez{' '}
                    {(product.original_price - product.discounted_price).toLocaleString()} DH
                  </div>
                </>
              ) : (
                <div className="flex items-baseline space-x-3">
                  <span className="text-5xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                    {product.discounted_price?.toLocaleString() ||
                      product.original_price?.toLocaleString()}
                  </span>
                  <span className="text-2xl font-bold text-gray-900">DH</span>
                </div>
              )}
            </div>

            {/* Expiry */}
            {product.expiry_date && (
              <div className="flex items-center gap-3 text-orange-700 mb-6 p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-xl border-2 border-orange-200">
                <div className="w-10 h-10 bg-orange-500 rounded-xl flex items-center justify-center">
                  <Clock className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-orange-600 uppercase">Expire le</div>
                  <div className="text-sm font-bold">
                    {new Date(product.expiry_date).toLocaleDateString('fr-FR')}
                  </div>
                </div>
              </div>
            )}

            {/* Stock */}
            {product.stock_quantity !== null && (
              <div className="mb-6">
                {product.stock_quantity > 0 ? (
                  <div className="flex items-center gap-2 bg-gradient-to-r from-green-50 to-emerald-50 px-4 py-3 rounded-xl border-2 border-green-200">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-green-700 font-bold text-sm">
                      ✓ En stock ({product.stock_quantity} disponibles)
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 bg-gradient-to-r from-red-50 to-pink-50 px-4 py-3 rounded-xl border-2 border-red-200">
                    <X className="w-5 h-5 text-red-500" />
                    <span className="text-red-700 font-bold text-sm">Rupture de stock</span>
                  </div>
                )}
              </div>
            )}

            {/* Sold Count */}
            {product.sold_count > 0 && (
              <div className="flex items-center gap-3 text-gray-700 mb-6 bg-gradient-to-r from-blue-50 to-cyan-50 px-4 py-3 rounded-xl">
                <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-blue-600 uppercase">Popularité</div>
                  <div className="text-sm font-bold">{product.sold_count} personnes ont acheté</div>
                </div>
              </div>
            )}

            {/* Request Affiliation Button - Principal */}
            <button
              onClick={handleRequestAffiliation}
              className="w-full bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 text-white py-5 rounded-xl font-black text-lg hover:from-green-600 hover:via-emerald-600 hover:to-teal-600 transition-all duration-300 flex items-center justify-center shadow-2xl mb-6 transform hover:scale-105 animate-gradient"
            >
              <Sparkles className="inline-block w-7 h-7 mr-2 animate-pulse" />
              {user ? 'Devenir Affilié' : 'Connexion Affilié'}
            </button>

            {/* Commission Info - Ultra-moderne */}
            <div className="p-6 bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 rounded-2xl border-2 border-green-200 shadow-inner mb-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-bold text-green-800 uppercase tracking-wide">
                  💰 Commission
                </span>
                <span className="text-4xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  {product.commission_rate || 15}%
                </span>
              </div>
              <p className="text-xs text-green-700 font-semibold leading-relaxed">
                Gagnez des revenus passifs en partageant ce produit avec votre audience
              </p>
            </div>

            {/* Merchant Info - Ultra-moderne */}
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
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            {/* Header - Dynamique selon le rôle */}
            <div className={`sticky top-0 ${user?.role === 'influencer' ? 'bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-600' : 'bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600'} text-white p-6 rounded-t-2xl`}>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold flex items-center">
                    <Sparkles className="w-6 h-6 mr-2" />
                    {user?.role === 'influencer' ? 'Devenir Partenaire Influenceur' : 'Devenir Partenaire Commercial'}
                  </h2>
                  <p className="text-white/90 text-sm mt-1">
                    {user?.role === 'influencer' 
                      ? 'Monétisez votre audience en promouvant des produits de qualité'
                      : 'Développez votre réseau et gagnez des commissions'}
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
              {/* Profil automatiquement détecté */}
              {userProfile && (
                <div className={`mb-6 p-6 rounded-2xl border-2 ${user?.role === 'influencer' ? 'bg-gradient-to-br from-pink-50 to-purple-50 border-pink-200' : 'bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200'}`}>
                  <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Votre Profil
                  </h3>
                  
                  {user?.role === 'influencer' ? (
                    // Profil Influenceur
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                        <div className="text-2xl font-black bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                          {userProfile.followers_count ? (userProfile.followers_count / 1000).toFixed(1) : 0}K
                        </div>
                        <div className="text-xs text-gray-600 font-semibold mt-1">Followers</div>
                      </div>
                      <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                        <div className="text-2xl font-black bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                          {userProfile.engagement_rate || 0}%
                        </div>
                        <div className="text-xs text-gray-600 font-semibold mt-1">Engagement</div>
                      </div>
                      <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                        <div className="text-2xl font-black bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">
                          {userProfile.campaigns_completed || 0}
                        </div>
                        <div className="text-xs text-gray-600 font-semibold mt-1">Campagnes</div>
                      </div>
                      <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                        <div className="text-2xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                          {userProfile.rating || 4.5}⭐
                        </div>
                        <div className="text-xs text-gray-600 font-semibold mt-1">Note</div>
                      </div>
                    </div>
                  ) : (
                    // Profil Commercial
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                        <div className="text-2xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                          {userProfile.total_sales || 0}
                        </div>
                        <div className="text-xs text-gray-600 font-semibold mt-1">Ventes</div>
                      </div>
                      <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                        <div className="text-2xl font-black bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent">
                          {userProfile.commission_earned || 0}
                        </div>
                        <div className="text-xs text-gray-600 font-semibold mt-1">DH Gagnés</div>
                      </div>
                      <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                        <div className="text-2xl font-black bg-gradient-to-r from-teal-600 to-green-600 bg-clip-text text-transparent">
                          {userProfile.territory || 'National'}
                        </div>
                        <div className="text-xs text-gray-600 font-semibold mt-1">Territoire</div>
                      </div>
                      <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                        <div className="text-2xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                          {userProfile.rating || 4.5}⭐
                        </div>
                        <div className="text-xs text-gray-600 font-semibold mt-1">Note</div>
                      </div>
                    </div>
                  )}
                  
                  {/* Informations supplémentaires */}
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="flex items-center gap-2 text-sm">
                        <MapPin className="w-4 h-4 text-gray-500" />
                        <span className="font-semibold">{userProfile.city || 'Maroc'}</span>
                      </div>
                      {user?.role === 'influencer' && userProfile.niche && (
                        <div className="flex items-center gap-2 text-sm">
                          <Tag className="w-4 h-4 text-gray-500" />
                          <span className="font-semibold">{userProfile.niche}</span>
                        </div>
                      )}
                      {user?.role === 'commercial' && userProfile.department && (
                        <div className="flex items-center gap-2 text-sm">
                          <Briefcase className="w-4 h-4 text-gray-500" />
                          <span className="font-semibold">{userProfile.department}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* How it works */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
                <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Comment ça fonctionne ?
                </h3>
                <p className="text-blue-800 text-sm leading-relaxed">
                  Votre profil a été automatiquement récupéré. Le marchand verra vos statistiques et pourra approuver votre demande. 
                  Un lien de tracking unique sera créé pour vous.
                </p>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmitAffiliateRequest} className="space-y-6">
                {/* Product Selection */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-2">
                    Produit sélectionné <span className="text-red-500">*</span>
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
                </div>

                {/* Message to Merchant */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-2">
                    Message de motivation <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={affiliateData.message}
                    onChange={(e) => setAffiliateData({ ...affiliateData, message: e.target.value })}
                    rows="5"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 transition resize-none"
                    placeholder={user?.role === 'influencer' 
                      ? "Expliquez comment vous allez promouvoir ce produit auprès de votre audience...\nExemple: Stories Instagram, vidéos TikTok, posts sponsorisés..."
                      : "Expliquez votre stratégie commerciale pour ce produit...\nExemple: Réseau de clients, zone géographique, expérience secteur..."}
                    required
                  />
                  <div className="flex items-start mt-2 text-xs text-gray-500">
                    <AlertCircle className="w-4 h-4 mr-1 mt-0.5 flex-shrink-0" />
                    <p>
                      {user?.role === 'influencer' 
                        ? 'Décrivez votre stratégie de contenu et plateformes que vous utiliserez'
                        : 'Présentez votre expérience et votre réseau commercial'}
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
                        className="w-20 h-20 object-cover rounded-lg shadow-md"
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
                              {product.price} DH
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
                        💰 Commission de {product?.commission_rate || 15}%
                      </h4>
                      <p className="text-sm text-yellow-800">
                        {user?.role === 'influencer' 
                          ? `Pour chaque vente générée via votre lien d'affiliation, vous recevez ${product?.commission_rate || 15}% du montant.`
                          : `Commission de ${product?.commission_rate || 15}% sur chaque vente réalisée dans votre zone.`}
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
    </div>
  );
};

export default ProductDetail;
