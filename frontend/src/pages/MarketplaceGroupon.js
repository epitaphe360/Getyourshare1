import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../services/api';
import Layout from '../components/layout/Layout';
import CollaborationRequestModal from '../components/modals/CollaborationRequestModal';
import './MarketplaceAnimations.css';
import {
  Search, MapPin, Star, TrendingUp, Users, 
  ShoppingBag, Briefcase, Instagram, ChevronRight
} from 'lucide-react';

const MarketplaceGroupon = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const toast = useToast();
  const [currentTab, setCurrentTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [services, setServices] = useState([]);
  const [commercials, setCommercials] = useState([]);
  const [influencers, setInfluencers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCollabModal, setShowCollabModal] = useState(false);
  const [selectedInfluencer, setSelectedInfluencer] = useState(null);
  const [merchantProducts, setMerchantProducts] = useState([]);

  // Détecter si on vient du dashboard ou de la home
  const fromDashboard = location.state?.fromDashboard || false;

  const tabs = [
    { id: 0, name: 'Produits', icon: ShoppingBag, color: 'bg-green-500' },
    { id: 1, name: 'Services', icon: Briefcase, color: 'bg-blue-500' },
    { id: 2, name: 'Commerciaux', icon: Users, color: 'bg-purple-500' },
    { id: 3, name: 'Influenceurs', icon: Instagram, color: 'bg-pink-500' }
  ];

  useEffect(() => {
    loadTabData();
  }, [currentTab]);

  useEffect(() => {
    // Charger les produits du marchand si connecté en tant que merchant
    if (user && user.role === 'merchant') {
      loadMerchantProducts();
    }
  }, [user]);

  const loadMerchantProducts = async () => {
    try {
      const res = await api.get('/api/products');
      setMerchantProducts(res.data.products || []);
    } catch (error) {
      console.error('Error loading merchant products:', error);
    }
  };

  const handleCollaborateClick = (influencer) => {
    // Vérifier si l'utilisateur est connecté
    if (!user) {
      toast.error('Veuillez vous connecter pour envoyer une demande de collaboration');
      navigate('/login', { state: { from: location } });
      return;
    }

    // Vérifier que c'est un marchand
    if (user.role !== 'merchant') {
      toast.error('Seuls les marchands peuvent envoyer des demandes de collaboration');
      return;
    }

    // Vérifier que le marchand a des produits
    if (!merchantProducts || merchantProducts.length === 0) {
      toast.error('Vous devez avoir au moins un produit pour envoyer une demande de collaboration');
      navigate('/products/create');
      return;
    }

    // Ouvrir le modal
    setSelectedInfluencer(influencer);
    setShowCollabModal(true);
  };

  const loadTabData = async () => {
    setLoading(true);
    try {
      if (currentTab === 0) {
        const res = await api.get('/api/marketplace/products?type=product&limit=20');
        setProducts(res.data.products || []);
      } else if (currentTab === 1) {
        const res = await api.get('/api/marketplace/products?type=service&limit=20');
        setServices(res.data.products || []);
      } else if (currentTab === 2) {
        const res = await api.get('/api/commercials/directory?limit=20');
        setCommercials(res.data.commercials || []);
      } else if (currentTab === 3) {
        const res = await api.get('/api/influencers/directory?limit=20');
        setInfluencers(res.data.influencers || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (item, type) => {
    // Permettre l'accès aux détails sans connexion
    // La connexion sera demandée seulement lors de la demande d'affiliation
    
    // Rediriger selon le type
    if (type === 'product' || type === 'service') {
      navigate(`/marketplace/product/${item.id}`);
    } else if (type === 'commercial') {
      navigate(`/commercial/${item.id}`);
    } else if (type === 'influencer') {
      navigate(`/influencer/${item.id}`);
    }
  };

  // Contenu principal du marketplace
  const marketplaceContent = (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Hero Section - Ultra Moderne & Dynamique */}
      <div className="relative bg-gradient-to-br from-blue-600 via-cyan-500 to-teal-500 text-white overflow-hidden">
        {/* Motif de fond ultra-animé */}
        <div className="absolute inset-0">
          {/* Particules flottantes */}
          <div className="absolute w-3 h-3 bg-white/60 rounded-full top-[10%] left-[15%] animate-float"></div>
          <div className="absolute w-2 h-2 bg-white/40 rounded-full top-[70%] left-[85%] animate-float-delayed"></div>
          <div className="absolute w-4 h-4 bg-white/50 rounded-full top-[85%] left-[20%] animate-float-slow"></div>
          <div className="absolute w-2 h-2 bg-white/60 rounded-full top-[25%] left-[75%] animate-float"></div>
          <div className="absolute w-3 h-3 bg-white/30 rounded-full top-[45%] left-[40%] animate-float-delayed"></div>
          <div className="absolute w-2 h-2 bg-white/50 rounded-full top-[60%] left-[60%] animate-float-slow"></div>
          
          {/* Cercles de gradient animés avec blob effect */}
          <div className="absolute w-[600px] h-[600px] bg-gradient-to-br from-cyan-400/30 to-blue-600/30 rounded-full blur-3xl -top-64 -left-64 animate-blob"></div>
          <div className="absolute w-[500px] h-[500px] bg-gradient-to-br from-teal-400/30 to-cyan-600/30 rounded-full blur-3xl -bottom-48 -right-48 animate-blob animation-delay-2000"></div>
          <div className="absolute w-[400px] h-[400px] bg-gradient-to-br from-blue-400/20 to-teal-600/20 rounded-full blur-2xl top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 animate-blob animation-delay-4000"></div>
          
          {/* Cercles tournants */}
          <div className="absolute top-10 right-10 w-20 h-20 border-2 border-white/20 rounded-full animate-rotate-slow"></div>
          <div className="absolute bottom-20 left-20 w-32 h-32 border-2 border-white/10 rounded-full animate-rotate-slow"></div>
          
          {/* Vagues animées */}
          <div className="absolute inset-0 opacity-10">
            <svg className="absolute bottom-0 w-full h-56 animate-wave" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320">
              <path fill="white" fillOpacity="0.4" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
            </svg>
          </div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 py-16 sm:py-20">
          <div className="text-center">
            <div className="inline-block mb-4 px-5 py-2.5 bg-white/25 backdrop-blur-md rounded-full animate-pulse-glow border border-white/30">
              <span className="text-sm font-bold">🚀 Nouvelle Marketplace - 100% Maroc</span>
            </div>
            <h1 className="text-5xl sm:text-7xl font-black mb-6 leading-tight">
              Gagnez de l'argent en <br />
              <span className="inline-block bg-gradient-to-r from-yellow-300 via-orange-300 to-yellow-400 bg-clip-text text-transparent animate-gradient">
                partageant ce que vous aimez
              </span>
            </h1>
            <p className="text-xl sm:text-2xl mb-4 font-semibold opacity-95 max-w-3xl mx-auto">
              Des milliers de produits et services à promouvoir
            </p>
            <p className="text-lg mb-10 opacity-90 max-w-2xl mx-auto">
              Inscrivez-vous gratuitement et commencez à générer des revenus aujourd'hui 💸
            </p>
            
            {/* Statistiques avec animation */}
            <div className="flex flex-wrap justify-center gap-8 mb-10">
              <div className="text-center hover-lift bg-white/10 backdrop-blur-sm px-6 py-4 rounded-2xl border border-white/20">
                <div className="text-5xl font-black bg-gradient-to-br from-yellow-300 to-orange-400 bg-clip-text text-transparent">500+</div>
                <div className="text-sm font-semibold opacity-90 mt-1">Produits</div>
              </div>
              <div className="text-center hover-lift bg-white/10 backdrop-blur-sm px-6 py-4 rounded-2xl border border-white/20">
                <div className="text-5xl font-black bg-gradient-to-br from-green-300 to-emerald-400 bg-clip-text text-transparent">15%</div>
                <div className="text-sm font-semibold opacity-90 mt-1">Commission Moyenne</div>
              </div>
              <div className="text-center hover-lift bg-white/10 backdrop-blur-sm px-6 py-4 rounded-2xl border border-white/20">
                <div className="text-5xl font-black bg-gradient-to-br from-pink-300 to-rose-400 bg-clip-text text-transparent">1000+</div>
                <div className="text-sm font-semibold opacity-90 mt-1">Influenceurs Actifs</div>
              </div>
            </div>
            
            {/* Barre de recherche ultra-moderne */}
            <div className="flex flex-col sm:flex-row gap-3 max-w-3xl mx-auto">
              <div className="flex-1 relative group">
                <Search className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-cyan-600 transition-all duration-300" size={24} />
                <input
                  type="text"
                  placeholder="Rechercher des produits, services, marques..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-14 pr-5 py-5 rounded-2xl text-gray-900 text-lg font-medium focus:outline-none focus:ring-4 focus:ring-cyan-300 shadow-2xl hover-lift"
                />
              </div>
              <button className="px-10 py-5 bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500 text-white rounded-2xl font-bold hover:shadow-2xl hover:scale-105 transition-all duration-300 animate-gradient">
                🔍 Rechercher
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs - Design Moderne & Dynamique */}
      <div className="bg-white/90 backdrop-blur-xl border-b sticky top-0 z-20 shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-2 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setCurrentTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 font-bold transition-all duration-300 whitespace-nowrap ${
                    currentTab === tab.id
                      ? 'border-b-4 border-cyan-600 text-cyan-600 bg-gradient-to-br from-blue-50 to-cyan-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={22} className={currentTab === tab.id ? 'animate-pulse' : ''} />
                  {tab.name}
                  {currentTab === tab.id && (
                    <span className="ml-1 px-2.5 py-1 bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-xs rounded-full font-bold shadow-md">
                      Actif
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-10">
        {loading ? (
          <div className="flex flex-col justify-center items-center h-64 space-y-4">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-600"></div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <ShoppingBag className="text-purple-600" size={28} />
              </div>
            </div>
            <p className="text-gray-600 font-medium">Chargement des offres...</p>
          </div>
        ) : (
          <>
            {/* Tab 0: Produits */}
            {currentTab === 0 && (
              <>
                <div className="mb-10">
                  <h2 className="text-4xl font-black bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent mb-3 animate-gradient">
                    Produits en Vedette ✨
                  </h2>
                  <p className="text-gray-600 text-lg font-medium">Découvrez les meilleures offres avec commission attractive</p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {products.map((product) => (
                  <div
                    key={product.id}
                    className="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-500 cursor-pointer group hover-lift border border-gray-100"
                    onClick={() => handleViewDetails(product, 'product')}
                  >
                    <div className="relative h-52 overflow-hidden bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50">
                      <img
                        src={product.image_url || `https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop&q=80`}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-125 group-hover:rotate-3 transition-all duration-700"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%230891b2" width="400" height="300"/%3E%3Ctext fill="%23ffffff" font-family="Arial" font-size="24" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EProduit%3C/text%3E%3C/svg%3E';
                        }}
                      />
                      {product.discount && (
                        <div className="absolute top-3 right-3 bg-gradient-to-r from-red-500 to-pink-500 text-white px-3 py-1.5 rounded-xl font-bold text-sm z-10 shadow-xl animate-pulse">
                          -{product.discount}%
                        </div>
                      )}
                      <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-sm px-3 py-1.5 rounded-xl flex items-center gap-2 z-10 shadow-lg">
                        <Star size={16} className="fill-yellow-400 text-yellow-400" />
                        <span className="text-sm font-bold text-gray-800">
                          {product.rating || 4.5}
                        </span>
                      </div>
                      <div className="absolute bottom-3 left-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-3 py-1.5 rounded-xl flex items-center gap-1.5 z-10 text-xs font-semibold shadow-lg">
                        <MapPin size={12} />
                        {product.city || 'Maroc'}
                      </div>
                    </div>
                    <div className="p-5">
                      <h3 className="font-bold text-lg mb-2 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-blue-600 group-hover:to-cyan-600 group-hover:bg-clip-text transition-all duration-300 line-clamp-2 min-h-[56px]">
                        {product.name}
                      </h3>
                      <p className="text-gray-600 text-sm mb-4 line-clamp-2 min-h-[40px]">
                        {product.description}
                      </p>
                      
                      {/* Prix et Commission */}
                      <div className="mb-4">
                        <div className="flex items-baseline gap-2 mb-3">
                          <span className="text-3xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                            {product.price}
                          </span>
                          <span className="text-gray-600 font-bold">DH</span>
                        </div>
                        <div className="bg-gradient-to-r from-blue-50 via-cyan-50 to-teal-50 px-4 py-3 rounded-xl border-2 border-blue-100 shadow-inner">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 animate-pulse"></div>
                              <span className="text-xs font-bold text-blue-700 uppercase tracking-wide">Commission</span>
                            </div>
                            <span className="text-2xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                              {product.commission_rate || 15}%
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <button className="w-full py-3.5 bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 text-white rounded-xl font-bold hover:from-blue-700 hover:via-cyan-700 hover:to-teal-700 transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-2xl transform hover:scale-105 animate-gradient">
                        <span>Voir détails</span>
                        <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              </>
            )}

            {/* Tab 1: Services */}
            {currentTab === 1 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {services.map((service) => (
                  <div
                    key={service.id}
                    className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-lg transition-all cursor-pointer group"
                    onClick={() => handleViewDetails(service, 'product')}
                  >
                    <div className="relative h-48 overflow-hidden bg-gradient-to-br from-blue-100 to-blue-200">
                      <img
                        src={service.image_url || `https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=300&fit=crop&q=80`}
                        alt={service.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%233b82f6" width="400" height="300"/%3E%3Ctext fill="%23ffffff" font-family="Arial" font-size="24" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EService%3C/text%3E%3C/svg%3E';
                        }}
                      />
                    </div>
                    <div className="p-5">
                      <h3 className="font-bold text-lg mb-2 group-hover:text-blue-600 transition">
                        {service.name}
                      </h3>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {service.description}
                      </p>
                      
                      {/* Prix et Commission d'Affiliation */}
                      <div className="space-y-2 mb-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">Prix public</span>
                          <span className="text-lg font-bold text-gray-900">
                            {service.price} DH
                          </span>
                        </div>
                        <div className="flex items-center justify-between bg-blue-50 px-3 py-2 rounded-lg">
                          <span className="text-sm font-semibold text-blue-700">Commission d'affiliation</span>
                          <span className="text-xl font-bold text-blue-600">
                            {service.commission_rate || 20}%
                          </span>
                        </div>
                      </div>
                      
                      <button className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center justify-center gap-2">
                        Voir les détails <ChevronRight size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Tab 2: Commerciaux */}
            {currentTab === 2 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {commercials.map((commercial) => (
                  <div
                    key={commercial.id}
                    className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-all cursor-pointer group"
                    onClick={() => handleViewDetails(commercial, 'commercial')}
                  >
                    {/* Header avec gradient */}
                    <div className="h-24 bg-gradient-to-r from-purple-500 to-purple-700 relative">
                      <div className="absolute -bottom-12 left-6">
                        <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-purple-200 rounded-full flex items-center justify-center text-purple-700 font-bold text-3xl border-4 border-white shadow-lg">
                          {commercial.profile?.first_name?.[0]}{commercial.profile?.last_name?.[0]}
                        </div>
                      </div>
                      <div className="absolute top-3 right-3 bg-white/90 px-3 py-1 rounded-full text-purple-700 font-semibold text-sm">
                        Commercial Pro
                      </div>
                    </div>

                    {/* Contenu */}
                    <div className="pt-16 px-6 pb-6">
                      <h3 className="font-bold text-xl mb-1 group-hover:text-purple-600 transition">
                        {commercial.profile?.first_name} {commercial.profile?.last_name}
                      </h3>
                      <p className="text-gray-600 text-sm mb-4">{commercial.profile?.department || 'Commercial Expert'}</p>
                      
                      {/* Stats */}
                      <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="bg-purple-50 rounded-lg p-3 text-center">
                          <div className="text-2xl font-bold text-purple-600">
                            {commercial.profile?.total_sales || 0}
                          </div>
                          <div className="text-xs text-gray-600">Ventes</div>
                        </div>
                        <div className="bg-green-50 rounded-lg p-3 text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {commercial.profile?.commission_earned || 0} DH
                          </div>
                          <div className="text-xs text-gray-600">Commissions</div>
                        </div>
                      </div>

                      {/* Infos */}
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center gap-2 text-sm text-gray-700">
                          <MapPin size={16} className="text-purple-500" />
                          <span className="font-medium">{commercial.profile?.city || 'Maroc'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-700">
                          <Briefcase size={16} className="text-purple-500" />
                          <span>{commercial.profile?.territory || 'Secteur National'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-700">
                          <Star size={16} className="text-yellow-400 fill-current" />
                          <span className="font-semibold">{commercial.profile?.rating || 4.5}</span>
                          <span className="text-gray-500">({commercial.profile?.reviews || 0} avis)</span>
                        </div>
                      </div>

                      {/* Spécialités */}
                      {commercial.profile?.specialties && (
                        <div className="mb-4">
                          <div className="flex flex-wrap gap-1">
                            {commercial.profile.specialties.slice(0, 3).map((specialty, idx) => (
                              <span key={idx} className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs">
                                {specialty}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <button className="w-full py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-purple-800 transition flex items-center justify-center gap-2 shadow-md">
                        <Users size={18} />
                        Contacter le Commercial
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Tab 3: Influenceurs */}
            {currentTab === 3 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {influencers.map((influencer) => (
                  <div
                    key={influencer.id}
                    className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-all cursor-pointer group"
                    onClick={() => handleViewDetails(influencer, 'influencer')}
                  >
                    {/* Header avec gradient */}
                    <div className="h-32 bg-gradient-to-br from-pink-400 via-pink-500 to-purple-600 relative">
                      <div className="absolute -bottom-14 left-6">
                        <div className="w-28 h-28 bg-gradient-to-br from-pink-100 to-purple-200 rounded-full flex items-center justify-center text-pink-700 font-bold text-4xl border-4 border-white shadow-xl">
                          {influencer.profile?.first_name?.[0]}{influencer.profile?.last_name?.[0]}
                        </div>
                      </div>
                      
                      {/* Badge vérifié */}
                      <div className="absolute top-3 right-3 bg-white/95 px-3 py-1 rounded-full flex items-center gap-1 shadow-md">
                        <Star size={14} className="text-pink-500 fill-current" />
                        <span className="text-pink-700 font-semibold text-sm">Vérifié</span>
                      </div>
                      
                      {/* Badge trending */}
                      {influencer.profile?.trending && (
                        <div className="absolute top-12 right-3 bg-orange-500 text-white px-2 py-1 rounded-full flex items-center gap-1 text-xs font-semibold">
                          <TrendingUp size={12} />
                          Trending
                        </div>
                      )}
                    </div>

                    {/* Contenu */}
                    <div className="pt-20 px-6 pb-6">
                      <h3 className="font-bold text-xl mb-1 group-hover:text-pink-600 transition">
                        {influencer.profile?.first_name} {influencer.profile?.last_name}
                      </h3>
                      <p className="text-gray-600 text-sm mb-1">{influencer.profile?.niche || 'Content Creator'}</p>
                      <p className="text-gray-500 text-xs mb-4">@{influencer.username || 'username'}</p>
                      
                      {/* Stats principales */}
                      <div className="grid grid-cols-3 gap-2 mb-4">
                        <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-3 text-center">
                          <div className="text-lg font-bold text-pink-600">
                            {(influencer.profile?.followers_count / 1000).toFixed(0)}K
                          </div>
                          <div className="text-xs text-gray-600">Followers</div>
                        </div>
                        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 text-center">
                          <div className="text-lg font-bold text-purple-600">
                            {influencer.profile?.engagement_rate || 0}%
                          </div>
                          <div className="text-xs text-gray-600">Engagement</div>
                        </div>
                        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 text-center">
                          <div className="text-lg font-bold text-green-600">
                            {influencer.profile?.campaigns_completed || 0}
                          </div>
                          <div className="text-xs text-gray-600">Campagnes</div>
                        </div>
                      </div>

                      {/* Réseaux sociaux */}
                      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                        <div className="text-xs text-gray-500 mb-2 font-semibold">Plateformes actives</div>
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-1 bg-white px-2 py-1 rounded shadow-sm">
                            <Instagram size={14} className="text-pink-500" />
                            <span className="text-xs font-semibold">
                              {(influencer.profile?.followers_count / 1000).toFixed(0)}K
                            </span>
                          </div>
                          {influencer.profile?.tiktok_followers && (
                            <div className="flex items-center gap-1 bg-white px-2 py-1 rounded shadow-sm">
                              <span className="text-xs">📱</span>
                              <span className="text-xs font-semibold">
                                {(influencer.profile.tiktok_followers / 1000).toFixed(0)}K
                              </span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Catégories */}
                      {influencer.profile?.categories && (
                        <div className="mb-4">
                          <div className="flex flex-wrap gap-1">
                            {influencer.profile.categories.slice(0, 3).map((cat, idx) => (
                              <span key={idx} className="bg-pink-100 text-pink-700 px-2 py-1 rounded-full text-xs font-medium">
                                {cat}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Commission d'Affiliation */}
                      <div className="mb-4 p-4 bg-gradient-to-r from-green-50 via-emerald-50 to-teal-50 rounded-xl border-2 border-green-200 shadow-inner">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-green-800 uppercase tracking-wide">
                            💰 Commission
                          </span>
                          <span className="text-3xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                            {influencer.profile?.commission_rate || '5-15'}%
                          </span>
                        </div>
                        <p className="text-xs text-green-700 font-medium">
                          Touchez un pourcentage sur les ventes générées
                        </p>
                      </div>

                      {/* Rating */}
                      <div className="flex items-center gap-2 mb-4 text-sm">
                        <div className="flex items-center gap-1">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              size={14}
                              className={star <= (influencer.profile?.rating || 4.5) ? 'text-yellow-400 fill-current' : 'text-gray-300'}
                            />
                          ))}
                        </div>
                        <span className="font-semibold">{influencer.profile?.rating || 4.5}</span>
                        <span className="text-gray-500">({influencer.profile?.reviews || 0} avis)</span>
                      </div>

                      <button 
                        onClick={() => handleCollaborateClick(influencer)}
                        className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg font-semibold hover:from-pink-600 hover:to-purple-700 transition flex items-center justify-center gap-2 shadow-md"
                      >
                        <Instagram size={18} />
                        Collaborer Maintenant
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Empty State */}
            {((currentTab === 0 && products.length === 0) ||
              (currentTab === 1 && services.length === 0) ||
              (currentTab === 2 && commercials.length === 0) ||
              (currentTab === 3 && influencers.length === 0)) && !loading && (
              <div className="text-center py-16">
                <div className="text-gray-400 mb-4">
                  <Search size={64} className="mx-auto" />
                </div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Aucun résultat trouvé
                </h3>
                <p className="text-gray-500">
                  Essayez de modifier vos critères de recherche
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );

  // Si on vient du dashboard, afficher avec le Layout (menu)
  if (fromDashboard) {
    return (
      <Layout>
        {marketplaceContent}
        <CollaborationRequestModal
          isOpen={showCollabModal}
          onClose={() => setShowCollabModal(false)}
          products={merchantProducts}
          influencerId={selectedInfluencer?.id}
          influencerName={selectedInfluencer?.name || `${selectedInfluencer?.first_name} ${selectedInfluencer?.last_name}`}
        />
      </Layout>
    );
  }

  // Sinon, afficher sans menu (depuis la home)
  return (
    <>
      {marketplaceContent}
      <CollaborationRequestModal
        isOpen={showCollabModal}
        onClose={() => setShowCollabModal(false)}
        products={merchantProducts}
        influencerId={selectedInfluencer?.id}
        influencerName={selectedInfluencer?.name || `${selectedInfluencer?.first_name} ${selectedInfluencer?.last_name}`}
      />
    </>
  );
};

export default MarketplaceGroupon;
