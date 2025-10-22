import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TrendingUp, Users, Target, Shield, Zap, BarChart3, 
  Globe, DollarSign, Check, ArrowRight, Menu, X,
  MousePointer, Link as LinkIcon, Settings, Award
} from 'lucide-react';
import Button from '../components/common/Button';

const LandingPage = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const features = [
    {
      icon: <TrendingUp className="text-blue-600" size={32} />,
      title: "Suivi en Temps Réel",
      description: "Dashboard pour surveiller les performances de vos affiliés et influenceurs en temps réel avec des KPIs détaillés."
    },
    {
      icon: <Settings className="text-green-600" size={32} />,
      title: "Personnalisation & Marque Blanche",
      description: "Ajoutez votre logo, modifiez les couleurs du thème, configurez SSL et personnalisez complètement vos emails."
    },
    {
      icon: <Target className="text-purple-600" size={32} />,
      title: "Suivi des Coupons",
      description: "Suivez les coupons hors ligne pour récompenser vos affiliés avec une gestion complète des codes promotionnels."
    },
    {
      icon: <Users className="text-orange-600" size={32} />,
      title: "Marketing Multi-Niveaux (MLM)",
      description: "Outil pour développer vos réseaux d'affiliés jusqu'à 10 niveaux et générer des revenus sur leurs ventes."
    },
    {
      icon: <DollarSign className="text-yellow-600" size={32} />,
      title: "Règles de Commission Avancées",
      description: "Personnalisez les commissions par produit, catégorie ou affilié avec des taux de commission personnalisés."
    },
    {
      icon: <Shield className="text-red-600" size={32} />,
      title: "Détection Avancée de Fraude",
      description: "Fonctionnalité anti-fraude pour protéger vos revenus avec des algorithmes de détection intelligents."
    },
    {
      icon: <Zap className="text-indigo-600" size={32} />,
      title: "API Robuste",
      description: "Intégration API pour récupérer des données, télécharger les ventes et mettre à jour les statuts de commission."
    },
    {
      icon: <LinkIcon className="text-pink-600" size={32} />,
      title: "Liens de Tracking",
      description: "Générez des liens de suivi uniques et courts pour suivre précisément chaque clic et conversion."
    },
    {
      icon: <BarChart3 className="text-teal-600" size={32} />,
      title: "Rapports & Analytics",
      description: "Rapports détaillés avec graphiques, statistiques et possibilité d'export pour analyser vos performances."
    },
    {
      icon: <Globe className="text-cyan-600" size={32} />,
      title: "Marketplace Intégré",
      description: "Connectez entreprises et affiliés via un marketplace dédié avec filtres par secteur d'activité."
    },
    {
      icon: <MousePointer className="text-blue-500" size={32} />,
      title: "Gestion Complète des Affiliés",
      description: "Plateforme tout-en-un pour la gestion du programme, suivi des ventes, coupons et commissions par niveau."
    },
    {
      icon: <Award className="text-amber-600" size={32} />,
      title: "Gamification & Challenges",
      description: "Classements, récompenses et défis pour booster l'engagement et la motivation de vos affiliés."
    }
  ];

  const benefits = [
    "Monétisation simplifiée - Gagnez des commissions directement",
    "Transparence totale avec rapports de performance précis",
    "Optimisation en temps réel avec insights détaillés",
    "ROI garanti en traçant l'impact de chaque influenceur",
    "Automatisation complète de la gestion des relations"
  ];

  const pricing = [
    {
      name: "Starter",
      price: "49€",
      period: "par mois",
      features: [
        "Jusqu'à 100 affiliés",
        "Suivi en temps réel",
        "Rapports basiques",
        "Support email",
        "API accès"
      ]
    },
    {
      name: "Professional",
      price: "149€",
      period: "par mois",
      features: [
        "Affiliés illimités",
        "MLM jusqu'à 10 niveaux",
        "White Label complet",
        "Support prioritaire",
        "Webhooks & Intégrations",
        "Détection de fraude"
      ],
      popular: true
    },
    {
      name: "Enterprise",
      price: "Sur devis",
      period: "",
      features: [
        "Tout Professional +",
        "Serveur dédié",
        "Onboarding personnalisé",
        "Support 24/7",
        "Consultant dédié",
        "SLA garanti"
      ]
    }
  ];

  const stats = [
    { value: "15,000+", label: "Affiliés Actifs" },
    { value: "500+", label: "Entreprises" },
    { value: "5M€", label: "Commissions Versées" },
    { value: "99.9%", label: "Uptime" }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-sm border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <TrendingUp className="text-white" size={24} />
              </div>
              <span className="text-2xl font-bold text-gray-900">Tracknow</span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition-colors">Fonctionnalités</a>
              <a href="#pricing" className="text-gray-700 hover:text-blue-600 transition-colors">Tarifs</a>
              <a href="#about" className="text-gray-700 hover:text-blue-600 transition-colors">À Propos</a>
              <Button variant="outline" onClick={() => navigate('/login')}>
                Se Connecter
              </Button>
              <Button onClick={() => navigate('/login')}>
                Commencer Gratuitement
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-4 py-4 space-y-4">
              <a href="#features" className="block text-gray-700 hover:text-blue-600">Fonctionnalités</a>
              <a href="#pricing" className="block text-gray-700 hover:text-blue-600">Tarifs</a>
              <a href="#about" className="block text-gray-700 hover:text-blue-600">À Propos</a>
              <Button variant="outline" className="w-full" onClick={() => navigate('/login')}>
                Se Connecter
              </Button>
              <Button className="w-full" onClick={() => navigate('/login')}>
                Commencer Gratuitement
              </Button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 mb-6">
              La Plateforme de Gestion
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                {" "}d'Affiliation{" "}
              </span>
              Ultime
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Maximisez vos revenus grâce à notre solution complète de tracking, gestion d'affiliés et marketing multi-niveaux. 
              Transformez vos interactions en opportunités de croissance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" onClick={() => navigate('/login')} className="text-lg px-8 py-4">
                Démarrer Maintenant
                <ArrowRight className="ml-2" size={20} />
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-4">
                Voir la Démo
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Fonctionnalités Puissantes</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Tout ce dont vous avez besoin pour gérer votre programme d'affiliation avec succès
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-all hover:-translate-y-1">
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 bg-gradient-to-br from-blue-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">Pourquoi Choisir Tracknow?</h2>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <Check className="flex-shrink-0 mt-1" size={24} />
                    <p className="text-lg">{benefit}</p>
                  </div>
                ))}
              </div>
              <Button size="lg" variant="secondary" className="mt-8" onClick={() => navigate('/login')}>
                Commencer Gratuitement
              </Button>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-8 rounded-2xl">
              <div className="space-y-6">
                <div>
                  <div className="text-5xl font-bold mb-2">2.73%</div>
                  <p className="text-blue-100">Taux de conversion moyen</p>
                </div>
                <div>
                  <div className="text-5xl font-bold mb-2">152€</div>
                  <p className="text-blue-100">Valeur moyenne par commande</p>
                </div>
                <div>
                  <div className="text-5xl font-bold mb-2">10x</div>
                  <p className="text-blue-100">ROI amélioré avec MLM</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Tarifs Simples et Transparents</h2>
            <p className="text-xl text-gray-600">Choisissez le plan qui correspond à vos besoins</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricing.map((plan, index) => (
              <div key={index} className={`bg-white rounded-2xl shadow-lg p-8 ${
                plan.popular ? 'ring-2 ring-blue-600 relative' : ''
              }`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Plus Populaire
                    </span>
                  </div>
                )}
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="text-4xl font-bold text-blue-600 mb-1">{plan.price}</div>
                  <div className="text-gray-600">{plan.period}</div>
                </div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start space-x-3">
                      <Check className="text-green-600 flex-shrink-0 mt-1" size={20} />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  className="w-full" 
                  variant={plan.popular ? 'primary' : 'outline'}
                  onClick={() => navigate('/login')}
                >
                  Commencer
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">
            Prêt à Transformer Votre Programme d'Affiliation?
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Rejoignez des centaines d'entreprises qui font confiance à Tracknow pour gérer leurs affiliés
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="text-lg px-8 py-4" onClick={() => navigate('/login')}>
              Essai Gratuit 14 Jours
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 py-4 text-white border-white hover:bg-white hover:text-blue-600">
                Parler à un Expert
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                  <TrendingUp className="text-white" size={24} />
                </div>
                <span className="text-xl font-bold text-white">Tracknow</span>
              </div>
              <p className="text-sm">
                La plateforme de gestion d'affiliation la plus puissante du marché.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Produit</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-white">Fonctionnalités</a></li>
                <li><a href="#pricing" className="hover:text-white">Tarifs</a></li>
                <li><a href="#" className="hover:text-white">Intégrations</a></li>
                <li><a href="#" className="hover:text-white">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Ressources</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Documentation</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Support</a></li>
                <li><a href="#" className="hover:text-white">Status</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Légal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Confidentialité</a></li>
                <li><a href="#" className="hover:text-white">Conditions</a></li>
                <li><a href="#" className="hover:text-white">Cookies</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>© 2024 Tracknow. Tous droits réservés.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
