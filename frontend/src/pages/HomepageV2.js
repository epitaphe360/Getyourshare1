import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp, Users, ShoppingBag, Sparkles, DollarSign,
  Target, Share2, BarChart3, Zap, CheckCircle, Shield,
  Clock, Globe, Award, ArrowRight, Star, Quote,
  Instagram, Facebook, Youtube, MessageSquare, HelpCircle
} from 'lucide-react';

/**
 * Homepage V2 - Enhanced Landing Page
 * Showcases all platform advantages and features
 */
const HomepageV2 = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: TrendingUp,
      title: 'Commissions Attractives',
      description: 'Gagnez jusqu\'à 25% de commission sur chaque vente générée',
      color: 'from-green-500 to-emerald-600'
    },
    {
      icon: Share2,
      title: 'Publication Automatique',
      description: 'Partagez vos liens sur Instagram, Facebook, TikTok en un clic',
      color: 'from-purple-500 to-pink-600'
    },
    {
      icon: BarChart3,
      title: 'Analytics en Temps Réel',
      description: 'Suivez vos performances avec des statistiques détaillées',
      color: 'from-blue-500 to-cyan-600'
    },
    {
      icon: ShoppingBag,
      title: 'Marketplace Groupon-Style',
      description: 'Des milliers de produits et deals exclusifs à promouvoir',
      color: 'from-orange-500 to-red-600'
    },
    {
      icon: Zap,
      title: 'Liens Instantanés',
      description: 'Générez vos liens d\'affiliation en quelques secondes',
      color: 'from-yellow-500 to-orange-600'
    },
    {
      icon: Shield,
      title: 'Paiements Sécurisés',
      description: 'Recevez vos commissions de manière fiable et transparente',
      color: 'from-indigo-500 to-purple-600'
    }
  ];

  const stats = [
    { value: '2,500+', label: 'Influenceurs Actifs', icon: Users },
    { value: '1,200+', label: 'Marchands Partenaires', icon: ShoppingBag },
    { value: '15M DH', label: 'Commissions Versées', icon: DollarSign },
    { value: '4.8/5', label: 'Satisfaction Client', icon: Star }
  ];

  const testimonials = [
    {
      name: 'Fatima Zahra',
      role: 'Influenceuse Mode',
      image: 'https://i.pravatar.cc/150?img=5',
      quote: 'ShareYourSales a transformé ma présence sur les réseaux sociaux en véritable source de revenus. La publication automatique me fait gagner un temps précieux!',
      rating: 5
    },
    {
      name: 'Ahmed Benali',
      role: 'E-commerce',
      image: 'https://i.pravatar.cc/150?img=12',
      quote: 'En tant que marchand, j\'ai vu mes ventes exploser grâce aux influenceurs. Le ROI est impressionnant et le système est très transparent.',
      rating: 5
    },
    {
      name: 'Sara Alami',
      role: 'Influenceuse Beauté',
      image: 'https://i.pravatar.cc/150?img=9',
      quote: 'J\'adore le marketplace style Groupon! Les deals sont incroyables et mes followers sont toujours ravis. Je recommande à 100%!',
      rating: 5
    }
  ];

  const howItWorks = [
    {
      step: '1',
      title: 'Inscrivez-vous',
      description: 'Créez votre compte en 2 minutes - Gratuit pour toujours',
      icon: Users
    },
    {
      step: '2',
      title: 'Choisissez vos Produits',
      description: 'Parcourez le marketplace et sélectionnez les produits qui matchent votre audience',
      icon: ShoppingBag
    },
    {
      step: '3',
      title: 'Partagez & Gagnez',
      description: 'Publiez sur vos réseaux sociaux et gagnez des commissions sur chaque vente',
      icon: DollarSign
    }
  ];

  const faq = [
    {
      question: 'Comment fonctionnent les commissions?',
      answer: 'Vous gagnez un pourcentage sur chaque vente générée via votre lien unique. Les commissions varient de 5% à 25% selon les produits.'
    },
    {
      question: 'Quand suis-je payé?',
      answer: 'Les paiements sont effectués le 15 de chaque mois pour les commissions du mois précédent, directement sur votre compte bancaire.'
    },
    {
      question: 'Puis-je promouvoir sur plusieurs plateformes?',
      answer: 'Absolument! Vous pouvez publier sur Instagram, Facebook, TikTok, YouTube et tous vos réseaux sociaux simultanément.'
    },
    {
      question: 'Y a-t-il des frais d\'inscription?',
      answer: 'Non, l\'inscription est 100% gratuite pour les influenceurs. Vous ne payez que si vous gagnez (pourcentage sur commissions).'
    }
  ];

  const pricingPlans = [
    {
      name: 'Influenceur',
      price: 'Gratuit',
      description: 'Pour les créateurs de contenu',
      features: [
        'Liens d\'affiliation illimités',
        'Publication multi-plateformes',
        'Analytics en temps réel',
        'Support par email',
        'Paiements mensuels'
      ],
      cta: 'Devenir Influenceur',
      highlighted: true,
      role: 'influencer'
    },
    {
      name: 'Marchand',
      price: '5%',
      description: 'Commission sur ventes',
      features: [
        'Catalogue produits illimité',
        'Accès à 2,500+ influenceurs',
        'Dashboard complet',
        'Support prioritaire',
        'Paiement à la performance'
      ],
      cta: 'Devenir Marchand',
      highlighted: false,
      role: 'merchant'
    }
  ];

  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-purple-600 via-pink-600 to-orange-500 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-72 h-72 bg-white opacity-10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white opacity-10 rounded-full blur-3xl"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 py-24 md:py-32">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full mb-8">
              <Sparkles className="w-5 h-5" />
              <span className="text-sm font-medium">Plateforme #1 d'Affiliation au Maroc</span>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              Transformez Votre Influence
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-orange-200">
                en Revenus
              </span>
            </h1>

            <p className="text-xl md:text-2xl mb-10 text-purple-100">
              Connectez influenceurs et marchands pour créer des partenariats gagnant-gagnant.
              Commissions attractives, publication automatique, paiements garantis.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
              <button
                onClick={() => navigate('/register?role=influencer')}
                className="w-full sm:w-auto px-8 py-4 bg-white text-purple-600 rounded-lg font-bold text-lg hover:bg-purple-50 transition shadow-xl"
              >
                Devenir Influenceur
                <ArrowRight className="inline-block ml-2 w-5 h-5" />
              </button>
              <button
                onClick={() => navigate('/register?role=merchant')}
                className="w-full sm:w-auto px-8 py-4 bg-transparent border-2 border-white text-white rounded-lg font-bold text-lg hover:bg-white/10 transition"
              >
                Devenir Marchand
              </button>
            </div>

            <div className="mt-12 flex items-center justify-center space-x-8 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5" />
                <span>Gratuit pour Influenceurs</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5" />
                <span>Paiement Sécurisé</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5" />
                <span>Support 7j/7</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="bg-white py-12 border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={index} className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Icon className="w-8 h-8 text-purple-600" />
                  </div>
                  <div className="text-4xl font-bold text-gray-900 mb-1">{stat.value}</div>
                  <div className="text-sm text-gray-600">{stat.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Pourquoi Choisir ShareYourSales?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              La plateforme la plus complète pour l'affiliation au Maroc
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-xl transition-shadow">
                  <div className={`w-14 h-14 rounded-lg bg-gradient-to-r ${feature.color} flex items-center justify-center mb-4`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Comment Ça Marche?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Commencez à gagner en 3 étapes simples
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {howItWorks.map((item, index) => {
              const Icon = item.icon;
              return (
                <div key={index} className="text-center relative">
                  {index < howItWorks.length - 1 && (
                    <div className="hidden md:block absolute top-16 left-1/2 w-full h-0.5 bg-gradient-to-r from-purple-200 to-pink-200"></div>
                  )}
                  <div className="relative inline-flex items-center justify-center w-32 h-32 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full mb-6 shadow-xl">
                    <div className="absolute inset-2 bg-white rounded-full flex items-center justify-center">
                      <Icon className="w-12 h-12 text-purple-600" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-10 h-10 bg-yellow-400 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                      {item.step}
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">{item.title}</h3>
                  <p className="text-gray-600">{item.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Ce Que Disent Nos Utilisateurs
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Plus de 2,500 influenceurs et marchands nous font confiance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-xl transition-shadow">
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <Quote className="w-10 h-10 text-purple-200 mb-4" />
                <p className="text-gray-700 mb-6 italic">"{testimonial.quote}"</p>
                <div className="flex items-center space-x-3">
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full"
                  />
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.name}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Tarifs Simples et Transparents
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Choisissez le plan qui vous correspond
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <div
                key={index}
                className={`rounded-xl p-8 ${
                  plan.highlighted
                    ? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white shadow-2xl transform scale-105'
                    : 'bg-gray-50 text-gray-900'
                }`}
              >
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className={`mb-6 ${plan.highlighted ? 'text-purple-100' : 'text-gray-600'}`}>
                  {plan.description}
                </p>
                <div className="mb-6">
                  <span className="text-5xl font-bold">{plan.price}</span>
                  {plan.price !== 'Gratuit' && <span className="text-xl ml-2">par vente</span>}
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center space-x-2">
                      <CheckCircle className={`w-5 h-5 ${plan.highlighted ? 'text-white' : 'text-green-500'}`} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => navigate(`/register?role=${plan.role}`)}
                  className={`w-full py-3 rounded-lg font-semibold transition ${
                    plan.highlighted
                      ? 'bg-white text-purple-600 hover:bg-purple-50'
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Questions Fréquentes
            </h2>
            <p className="text-xl text-gray-600">
              Tout ce que vous devez savoir sur ShareYourSales
            </p>
          </div>

          <div className="space-y-4">
            {faq.map((item, index) => (
              <details key={index} className="bg-white rounded-lg shadow-sm">
                <summary className="flex items-center justify-between p-6 cursor-pointer font-semibold text-gray-900">
                  <span className="flex items-center">
                    <HelpCircle className="w-5 h-5 mr-3 text-purple-600" />
                    {item.question}
                  </span>
                  <ArrowRight className="w-5 h-5 text-gray-400" />
                </summary>
                <div className="px-6 pb-6 text-gray-600">
                  {item.answer}
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-pink-600 text-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Prêt à Commencer?
          </h2>
          <p className="text-xl mb-10 text-purple-100">
            Rejoignez plus de 2,500 influenceurs qui gagnent déjà avec ShareYourSales
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button
              onClick={() => navigate('/register')}
              className="w-full sm:w-auto px-10 py-4 bg-white text-purple-600 rounded-lg font-bold text-lg hover:bg-purple-50 transition shadow-xl"
            >
              Inscription Gratuite
              <ArrowRight className="inline-block ml-2 w-5 h-5" />
            </button>
            <button
              onClick={() => navigate('/marketplace')}
              className="w-full sm:w-auto px-10 py-4 bg-transparent border-2 border-white text-white rounded-lg font-bold text-lg hover:bg-white/10 transition"
            >
              Voir le Marketplace
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomepageV2;
