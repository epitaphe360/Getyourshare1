import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp, Users, ShoppingBag, Sparkles, DollarSign,
  Target, Share2, BarChart3, Zap, CheckCircle, Shield,
  Clock, Globe, Award, ArrowRight, Star, Quote,
  Link as LinkIcon, Settings, MousePointer, MessageSquare,
  Percent, Eye, RefreshCw, Lock, Smartphone, Briefcase
} from 'lucide-react';

/**
 * Homepage ShareYourSales - Version Complète
 * "Chaque partage devient une vente"
 * Plateforme d'affiliation B2B qui connecte entreprises, commerciaux et influenceurs
 */
const HomepageV2 = () => {
  const navigate = useNavigate();

  // Fonctionnalités principales de la plateforme
  const mainFeatures = [
    {
      icon: LinkIcon,
      title: 'Liens Traçables & Sécurisés',
      description: 'Générez des liens uniques et personnalisés pour suivre chaque clic et recommandation en temps réel',
      color: 'from-blue-500 to-cyan-600',
      badge: 'Tracking'
    },
    {
      icon: BarChart3,
      title: 'Dashboard Temps Réel',
      description: 'Tableau de bord intuitif avec vue instantanée des clics, ventes et commissions générées',
      color: 'from-purple-500 to-pink-600',
      badge: 'Analytics'
    },
    {
      icon: DollarSign,
      title: 'Commissions Automatiques',
      description: 'Rémunérations versées automatiquement une fois les ventes validées, sans intervention manuelle',
      color: 'from-green-500 to-emerald-600',
      badge: 'Paiements'
    },
    {
      icon: Eye,
      title: 'Rapports de Performance',
      description: 'Analyses détaillées par produit, influenceur ou canal avec exports personnalisables',
      color: 'from-orange-500 to-red-600',
      badge: 'Reporting'
    },
    {
      icon: Target,
      title: 'Outils d\'Optimisation',
      description: 'Optimisez vos stratégies avec des outils puissants d\'analyse et de recommandation',
      color: 'from-indigo-500 to-purple-600',
      badge: 'Intelligence'
    },
    {
      icon: Lock,
      title: 'Sécurité & Conformité',
      description: 'Protection RGPD, vérifications légales (RC, IF, CNIE) et conformité fiscale garanties',
      color: 'from-red-500 to-pink-600',
      badge: 'Sécurité'
    }
  ];

  // Les 4 plans d'abonnement
  const pricingPlans = [
    {
      name: 'Small Business',
      price: '199',
      currency: 'MAD',
      period: '/mois',
      description: 'Idéal pour PME débutant',
      features: [
        '2 membres d\'équipe',
        '1 domaine autorisé',
        'Dashboard complet',
        'Liens illimités',
        'Support email',
        'Analytics de base'
      ],
      cta: 'Commencer',
      highlighted: false,
      role: 'company',
      badge: 'PME'
    },
    {
      name: 'Medium Business',
      price: '499',
      currency: 'MAD',
      period: '/mois',
      description: 'Pour entreprises multi-équipes',
      features: [
        '10 membres d\'équipe',
        '2 domaines autorisés',
        'Dashboard avancé',
        'Liens illimités',
        'Support prioritaire 24h',
        'Analytics avancés',
        'Rapports personnalisés'
      ],
      cta: 'Choisir Medium',
      highlighted: true,
      role: 'company',
      badge: 'Populaire'
    },
    {
      name: 'Large Business',
      price: '799',
      currency: 'MAD',
      period: '/mois',
      description: 'Gestion étendue et premium',
      features: [
        '30 membres d\'équipe',
        'Domaines ILLIMITÉS',
        'Dashboard premium',
        'Support VIP 24/7 (2h)',
        'API access',
        'White-label',
        'Gestionnaire dédié'
      ],
      cta: 'Choisir Large',
      highlighted: false,
      role: 'company',
      badge: 'Premium'
    },
    {
      name: 'Marketplace',
      price: '99',
      currency: 'MAD',
      period: '/mois',
      description: 'Pour commerciaux indépendants',
      features: [
        'Accès marketplace complet',
        'Sélection libre produits',
        'Dashboard individuel',
        'Commissions jusqu\'à 30%',
        'Support email',
        'Formation vidéo'
      ],
      cta: 'Devenir Partenaire',
      highlighted: false,
      role: 'influencer',
      badge: 'Indépendant'
    }
  ];

  const stats = [
    { value: '3,500+', label: 'Commerciaux & Influenceurs', icon: Users },
    { value: '450+', label: 'Entreprises Partenaires', icon: Briefcase },
    { value: '2.5M DH', label: 'Commissions Versées', icon: DollarSign },
    { value: '99.8%', label: 'Satisfaction Client', icon: Star }
  ];

  const marketplaceTabs = [
    {
      icon: ShoppingBag,
      title: 'Produits',
      count: '256+',
      description: 'Produits physiques avec commissions jusqu\'à 25%'
    },
    {
      icon: Briefcase,
      title: 'Services',
      count: '43+',
      description: 'Services B2B avec commissions attractives'
    },
    {
      icon: Users,
      title: 'Commerciaux',
      count: '78+',
      description: 'Professionnels qualifiés pour vos ventes'
    },
    {
      icon: Sparkles,
      title: 'Influenceurs',
      count: '124+',
      description: 'Créateurs de contenu actifs'
    }
  ];

  const testimonials = [
    {
      name: 'Karim El Amrani',
      role: 'Directeur Commercial - TechStyle',
      image: 'https://i.pravatar.cc/150?img=12',
      quote: 'ShareYourSales a révolutionné notre façon de gérer nos commerciaux. Le système de distribution automatique des leads est génial!',
      rating: 5,
      stats: '127 ventes ce mois'
    },
    {
      name: 'Sarah Benjelloun',
      role: 'Influenceuse Beauté - 125K followers',
      image: 'https://i.pravatar.cc/150?img=9',
      quote: 'Enfin une plateforme qui valorise vraiment notre travail. Les commissions sont transparentes et les paiements toujours à l\'heure!',
      rating: 5,
      stats: '3,890 DH de commissions'
    },
    {
      name: 'Mohamed Tazi',
      role: 'CEO - Boutique Exemple SARL',
      image: 'https://i.pravatar.cc/150?img=33',
      quote: 'Le ROI est impressionnant. Nous avons augmenté nos ventes de 45% en 3 mois grâce au réseau d\'influenceurs de la plateforme.',
      rating: 5,
      stats: '+45% de ventes'
    }
  ];

  const howItWorks = [
    {
      step: '1',
      title: 'Générez un lien personnalisé',
      description: 'L\'entreprise ou le partenaire crée un lien unique directement depuis la plateforme',
      icon: LinkIcon
    },
    {
      step: '2',
      title: 'Partagez-le partout',
      description: 'Diffusez sur les réseaux sociaux, par email ou tout autre canal de votre choix',
      icon: Share2
    },
    {
      step: '3',
      title: 'Suivez en temps réel',
      description: 'Visualisez instantanément les clics et les ventes générées via votre dashboard',
      icon: Eye
    },
    {
      step: '4',
      title: 'Encaissez vos commissions',
      description: 'Les commissions sont versées automatiquement après validation des ventes',
      icon: DollarSign
    }
  ];

  const benefits = [
    {
      title: 'Pour les Entreprises',
      icon: Briefcase,
      points: [
        'Publiez offres et produits avec taux de commission',
        'Suivi complet des ventes et performances',
        'Gestion centralisée de vos équipes',
        'Accès à un réseau qualifié',
        'ROI garanti et traçable'
      ],
      color: 'from-blue-600 to-cyan-600'
    },
    {
      title: 'Pour Commerciaux & Influenceurs',
      icon: Users,
      points: [
        'Choisissez les offres qui vous correspondent',
        'Générez des ventes et percevez des commissions',
        'Flexibilité totale et opportunités illimitées',
        'Dashboard personnel de suivi',
        'Paiements directs et transparents'
      ],
      color: 'from-purple-600 to-pink-600'
    }
  ];

  return (
    <div className="w-full">
      {/* Header Sticky avec Navigation Complète */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center space-x-8">
              <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
                <img 
                  src="/logo.png" 
                  alt="Logo" 
                  className="h-16 w-auto object-contain"
                  onError={(e) => {
                    e.target.src = '/logo.png';
                  }}
                />
              </div>
            </div>
            
            {/* Navigation Menu */}
            <nav className="hidden lg:flex items-center space-x-6">
              <a href="/#fonctionnalites" className="text-gray-700 hover:text-blue-600 font-medium transition">
                Fonctionnalités
              </a>
              <a href="/about" className="text-gray-700 hover:text-blue-600 font-medium transition">
                À Propos
              </a>
              <a href="/marketplace" className="text-gray-700 hover:text-blue-600 font-medium transition">
                Marketplace
              </a>
              <a href="/pricing" className="text-gray-700 hover:text-blue-600 font-medium transition">
                Tarifs
              </a>
              <a href="/contact" className="text-gray-700 hover:text-blue-600 font-medium transition">
                Contact
              </a>
            </nav>
            
            {/* Boutons Connexion/Inscription */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/login')}
                className="px-6 py-2 text-gray-700 hover:text-blue-600 font-semibold transition flex items-center space-x-2"
              >
                <Lock className="w-4 h-4" />
                <span>Se Connecter</span>
              </button>
              <button
                onClick={() => navigate('/register')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition shadow-md"
              >
                S'inscrire
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section - Proposition de Valeur */}
      <section className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white overflow-hidden min-h-[600px] pt-16">
        <div className="absolute inset-0 bg-black opacity-5"></div>
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-96 h-96 bg-white opacity-10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white opacity-10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 py-24 md:py-32">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm px-6 py-3 rounded-full mb-8 animate-bounce">
              <Sparkles className="w-5 h-5" />
              <span className="text-sm font-semibold">Plateforme #1 d'Affiliation B2B au Maroc</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
              Chaque Partage
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-orange-200 to-pink-200">
                Devient une Vente
              </span>
            </h1>

            <p className="text-xl md:text-2xl mb-4 text-blue-100 leading-relaxed">
              Digitalisez la vente par recommandation en connectant<br />
              <strong>Entreprises</strong>, <strong>Commerciaux</strong> et <strong>Influenceurs</strong>
            </p>

            <p className="text-lg mb-10 text-purple-100">
              ✓ Transparence totale  •  ✓ Automatisation complète  •  ✓ Traçabilité garantie
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
              <button
                onClick={() => navigate('/login')}
                className="w-full sm:w-auto px-10 py-5 bg-white/10 backdrop-blur-sm border-2 border-white text-white rounded-xl font-bold text-lg hover:bg-white/20 transition transform hover:scale-105 flex items-center justify-center space-x-2"
              >
                <Lock className="w-5 h-5" />
                <span>Se Connecter</span>
              </button>
              <button
                onClick={() => navigate('/register?role=company')}
                className="w-full sm:w-auto px-10 py-5 bg-white text-purple-600 rounded-xl font-bold text-lg hover:bg-purple-50 transition shadow-2xl transform hover:scale-105"
              >
                Je suis une Entreprise
                <ArrowRight className="inline-block ml-2 w-5 h-5" />
              </button>
              <button
                onClick={() => navigate('/register?role=influencer')}
                className="w-full sm:w-auto px-10 py-5 bg-transparent border-3 border-white text-white rounded-xl font-bold text-lg hover:bg-white/10 transition transform hover:scale-105"
              >
                Je suis Commercial/Influenceur
              </button>
            </div>

            <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-300" />
                <span>Inscription Gratuite</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-300" />
                <span>Sans Engagement</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-300" />
                <span>5% de Commission Plateforme</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-300" />
                <span>Support 7j/7</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="bg-white py-16 border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={index} className="text-center transform hover:scale-105 transition">
                  <div className="flex items-center justify-center mb-3">
                    <Icon className="w-10 h-10 text-blue-600" />
                  </div>
                  <div className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">{stat.value}</div>
                  <div className="text-sm text-gray-600">{stat.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Comment ça marche */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 bg-blue-100 text-blue-600 px-4 py-2 rounded-full mb-4">
              <Zap className="w-4 h-4" />
              <span className="text-sm font-semibold">Simple et Efficace</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Comment Ça Marche?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              4 étapes simples pour transformer vos partages en revenus
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {howItWorks.map((item, index) => {
              const Icon = item.icon;
              return (
                <div key={index} className="relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition transform hover:-translate-y-2">
                  <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
                    <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-xl">
                      {item.step}
                    </div>
                  </div>
                  <div className="mt-6">
                    <div className="flex justify-center mb-4">
                      <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center">
                        <Icon className="w-8 h-8 text-blue-600" />
                      </div>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-3 text-center">{item.title}</h3>
                    <p className="text-gray-600 text-center">{item.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Fonctionnalités Principales */}
      <section id="fonctionnalites" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 bg-purple-100 text-purple-600 px-4 py-2 rounded-full mb-4">
              <Target className="w-4 h-4" />
              <span className="text-sm font-semibold">Fonctionnalités Puissantes</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              6 Fonctionnalités Clés de Performance
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Tout ce dont vous avez besoin pour réussir dans l'affiliation B2B
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {mainFeatures.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="group bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-sm hover:shadow-2xl transition-all border border-gray-100 hover:border-transparent transform hover:-translate-y-1">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-16 h-16 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <span className="bg-blue-100 text-blue-600 text-xs font-semibold px-3 py-1 rounded-full">
                      {feature.badge}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Marketplace 4 Onglets */}
      <section className="py-20 bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 bg-orange-100 text-orange-600 px-4 py-2 rounded-full mb-4">
              <ShoppingBag className="w-4 h-4" />
              <span className="text-sm font-semibold">Marketplace Complète</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              La Marketplace qui Connecte Tout
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Accès exclusif aux membres abonnés pour un écosystème de qualité
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {marketplaceTabs.map((tab, index) => {
              const Icon = tab.icon;
              return (
                <div key={index} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition transform hover:-translate-y-2">
                  <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl mb-6 mx-auto">
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2 text-center">{tab.title}</h3>
                  <div className="text-3xl font-bold text-blue-600 mb-3 text-center">{tab.count}</div>
                  <p className="text-gray-600 text-center text-sm">{tab.description}</p>
                </div>
              );
            })}
          </div>

          <div className="text-center mt-12">
            <button
              onClick={() => navigate('/marketplace')}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition shadow-xl transform hover:scale-105"
            >
              Explorer la Marketplace
              <ArrowRight className="inline-block ml-2 w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Avantages Par Type d'Utilisateur */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <div key={index} className={`relative bg-gradient-to-br ${benefit.color} rounded-3xl p-10 text-white shadow-2xl transform hover:scale-105 transition`}>
                  <div className="absolute top-6 right-6 w-20 h-20 bg-white/10 rounded-full blur-2xl"></div>
                  <div className="relative">
                    <div className="flex items-center space-x-4 mb-6">
                      <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-3xl font-bold">{benefit.title}</h3>
                    </div>
                    <div className="space-y-4">
                      {benefit.points.map((point, idx) => (
                        <div key={idx} className="flex items-start space-x-3">
                          <CheckCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                          <span className="text-lg">{point}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Témoignages */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 bg-green-100 text-green-600 px-4 py-2 rounded-full mb-4">
              <Award className="w-4 h-4" />
              <span className="text-sm font-semibold">Témoignages Clients</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Ils Nous Font Confiance
            </h2>
            <p className="text-xl text-gray-600">
              Des milliers d'utilisateurs satisfaits partagent leur expérience
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition">
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <Quote className="w-10 h-10 text-blue-200 mb-4" />
                <p className="text-gray-700 mb-6 italic leading-relaxed">"{testimonial.quote}"</p>
                <div className="flex items-center space-x-4 pt-4 border-t border-gray-100">
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="w-14 h-14 rounded-full border-2 border-blue-200"
                  />
                  <div className="flex-1">
                    <div className="font-bold text-gray-900">{testimonial.name}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                    <div className="text-xs text-blue-600 font-semibold mt-1">{testimonial.stats}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tarifs - 4 Plans */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-4">
              <DollarSign className="w-4 h-4" />
              <span className="text-sm font-semibold">Tarification Transparente</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Choisissez Votre Plan
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Seulement 5% de commission sur les ventes. Aucun frais caché.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {pricingPlans.map((plan, index) => (
              <div
                key={index}
                className={`relative rounded-3xl p-8 transition transform hover:scale-105 ${
                  plan.highlighted
                    ? 'bg-gradient-to-br from-blue-600 to-purple-600 shadow-2xl ring-4 ring-white/20'
                    : 'bg-gray-800 hover:bg-gray-750'
                }`}
              >
                {plan.badge && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className={`px-4 py-1 rounded-full text-xs font-bold shadow-lg ${
                      plan.highlighted ? 'bg-yellow-400 text-gray-900' : 'bg-blue-500 text-white'
                    }`}>
                      {plan.badge}
                    </span>
                  </div>
                )}

                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <p className={`text-sm mb-4 ${plan.highlighted ? 'text-blue-100' : 'text-gray-400'}`}>
                    {plan.description}
                  </p>
                  <div className="mb-2">
                    <span className="text-5xl font-bold">{plan.price}</span>
                    <span className="text-lg ml-1">{plan.currency}</span>
                  </div>
                  <div className={`text-sm ${plan.highlighted ? 'text-blue-100' : 'text-gray-400'}`}>
                    {plan.period}
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start space-x-2 text-sm">
                      <CheckCircle className={`w-5 h-5 flex-shrink-0 ${plan.highlighted ? 'text-white' : 'text-green-400'}`} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => navigate(`/register?role=${plan.role}`)}
                  className={`w-full py-3 rounded-xl font-bold transition ${
                    plan.highlighted
                      ? 'bg-white text-purple-600 hover:bg-gray-100'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>

          <div className="text-center mt-12 text-gray-300">
            <p className="text-lg">
              💡 <strong>Offre Pilote Gratuite</strong> : Testez avec 1 produit, 1 lien et 10 clics
            </p>
          </div>
        </div>
      </section>

      {/* Sécurité & Conformité */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <div className="inline-flex items-center space-x-2 bg-red-100 text-red-600 px-4 py-2 rounded-full mb-4">
              <Shield className="w-4 h-4" />
              <span className="text-sm font-semibold">Sécurité & Conformité</span>
            </div>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Votre Sécurité, Notre Priorité
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-8 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl">
              <Lock className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">Vérification Légale</h3>
              <p className="text-gray-600">Documents RC, IF, CNIE vérifiés avant activation</p>
            </div>
            <div className="text-center p-8 bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl">
              <Shield className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">Conformité RGPD</h3>
              <p className="text-gray-600">Protection totale de vos données personnelles</p>
            </div>
            <div className="text-center p-8 bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl">
              <CheckCircle className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">Conformité Fiscale</h3>
              <p className="text-gray-600">Structure conforme aux réglementations marocaines</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <Sparkles className="w-16 h-16 mx-auto mb-6" />
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Prêt à Transformer Vos Partages en Revenus?
          </h2>
          <p className="text-xl mb-10 text-blue-100">
            Rejoignez des milliers d'entreprises et de partenaires qui réussissent avec ShareYourSales
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button
              onClick={() => navigate('/register')}
              className="w-full sm:w-auto px-10 py-5 bg-white text-purple-600 rounded-xl font-bold text-lg hover:bg-purple-50 transition shadow-2xl transform hover:scale-105"
            >
              Commencer Gratuitement
              <ArrowRight className="inline-block ml-2 w-5 h-5" />
            </button>
            <button
              onClick={() => navigate('/contact')}
              className="w-full sm:w-auto px-10 py-5 bg-transparent border-3 border-white text-white rounded-xl font-bold text-lg hover:bg-white/10 transition transform hover:scale-105"
            >
              Parler à un Expert
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <img 
                  src="/logo.png" 
                  alt="ShareYourSales Logo" 
                  className="h-8 w-auto object-contain"
                  onError={(e) => {
                    e.target.src = '/logo.png';
                  }}
                />
                <span className="text-xl font-bold text-white">ShareYourSales</span>
              </div>
              <p className="text-sm mb-4">
                La plateforme d'affiliation B2B qui connecte entreprises, commerciaux et influenceurs.
              </p>
              <p className="text-xs text-gray-500">
                "Chaque partage devient une vente"
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Produit</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="/pricing" className="hover:text-white transition">Tarifs</a></li>
                <li><a href="/marketplace" className="hover:text-white transition">Marketplace</a></li>
                <li><a href="#" className="hover:text-white transition">Fonctionnalités</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Entreprise</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">À Propos</a></li>
                <li><a href="/contact" className="hover:text-white transition">Contact</a></li>
                <li><a href="#" className="hover:text-white transition">Carrières</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Légal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">Confidentialité</a></li>
                <li><a href="#" className="hover:text-white transition">CGV</a></li>
                <li><a href="#" className="hover:text-white transition">Mentions Légales</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>© 2025 ShareYourSales. Tous droits réservés. Made with ❤️ in Morocco 🇲🇦</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomepageV2;
