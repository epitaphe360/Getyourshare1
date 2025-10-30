import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, ShoppingBag, TrendingUp, ArrowRight, Eye, DollarSign, BarChart3 } from 'lucide-react';
import Button from '../components/common/Button';

const Demo = () => {
  const navigate = useNavigate();
  const [selectedRole, setSelectedRole] = useState(null);

  const roles = [
    {
      id: 'visitor',
      title: 'Visiteur / Affilié',
      icon: Users,
      color: 'blue',
      description: 'Découvrez comment gagner de l\'argent en partageant des produits',
      features: [
        'Parcourir le marketplace de produits',
        'Générer vos liens d\'affiliation personnalisés',
        'Suivre vos ventes et commissions en temps réel',
        'Gérer vos paiements et retraits',
      ],
      stats: [
        { label: 'Commission moyenne', value: '15%' },
        { label: 'Produits disponibles', value: '500+' },
        { label: 'Paiement minimum', value: '50€' },
      ],
      dashboardPath: '/demo/affiliate',
    },
    {
      id: 'influencer',
      title: 'Influenceur',
      icon: TrendingUp,
      color: 'purple',
      description: 'Monétisez votre audience avec des outils professionnels',
      features: [
        'Dashboard analytics avancé',
        'Liens de tracking personnalisés',
        'Programme MLM multi-niveaux',
        'Outils marketing intégrés (QR codes, widgets)',
      ],
      stats: [
        { label: 'Tracking en temps réel', value: '100%' },
        { label: 'Niveaux MLM', value: '5' },
        { label: 'Bonus parrainage', value: '5%' },
      ],
      dashboardPath: '/demo/influencer',
    },
    {
      id: 'merchant',
      title: 'Marchand / E-commerce',
      icon: ShoppingBag,
      color: 'green',
      description: 'Développez vos ventes grâce à un réseau d\'affiliés',
      features: [
        'Gérer vos produits et catalogues',
        'Recruter et gérer des affiliés',
        'Analytics détaillés des performances',
        'Système de commission automatisé',
      ],
      stats: [
        { label: 'Affiliés actifs', value: '1000+' },
        { label: 'ROI moyen', value: '300%' },
        { label: 'Commission flexible', value: '5-30%' },
      ],
      dashboardPath: '/demo/merchant',
    },
  ];

  const RoleCard = ({ role }) => {
    const Icon = role.icon;
    const colorClasses = {
      blue: 'from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700',
      purple: 'from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700',
      green: 'from-green-500 to-green-600 hover:from-green-600 hover:to-green-700',
    };

    return (
      <div
        className={`bg-white rounded-xl shadow-lg p-8 transition-all duration-300 hover:shadow-2xl cursor-pointer border-2 ${
          selectedRole === role.id ? 'border-' + role.color + '-500 scale-105' : 'border-transparent'
        }`}
        onClick={() => setSelectedRole(role.id)}
      >
        <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${colorClasses[role.color]} flex items-center justify-center mb-6`}>
          <Icon className="text-white" size={32} />
        </div>

        <h3 className="text-2xl font-bold text-gray-900 mb-3">{role.title}</h3>
        <p className="text-gray-600 mb-6">{role.description}</p>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-3 mb-6">
          {role.stats.map((stat, index) => (
            <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-600">{stat.label}</span>
              <span className={`text-lg font-bold text-${role.color}-600`}>{stat.value}</span>
            </div>
          ))}
        </div>

        {/* Features */}
        <div className="space-y-3 mb-6">
          <h4 className="font-semibold text-gray-900 text-sm uppercase tracking-wide">Fonctionnalités</h4>
          {role.features.map((feature, index) => (
            <div key={index} className="flex items-start gap-2">
              <div className={`w-5 h-5 rounded-full bg-${role.color}-100 flex items-center justify-center flex-shrink-0 mt-0.5`}>
                <div className={`w-2 h-2 rounded-full bg-${role.color}-500`}></div>
              </div>
              <span className="text-sm text-gray-700">{feature}</span>
            </div>
          ))}
        </div>

        {/* CTA Button */}
        <Button
          className={`w-full bg-gradient-to-r ${colorClasses[role.color]} text-white font-semibold`}
          onClick={(e) => {
            e.stopPropagation();
            navigate(role.dashboardPath);
          }}
        >
          Essayer cette vue
          <ArrowRight className="ml-2" size={18} />
        </Button>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Démo Interactive ShareYourSales</h1>
              <p className="text-gray-600 mt-2">Explorez l'application selon votre profil</p>
            </div>
            <Button variant="outline" disabled={loading} onClick={() => navigate('/')}>
              Retour à l'accueil
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Intro Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold mb-4">
            <Eye size={16} />
            Mode Démo - Aucune inscription requise
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Choisissez votre perspective
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez comment ShareYourSales répond aux besoins spécifiques de chaque profil d'utilisateur
          </p>
        </div>

        {/* Role Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {roles.map((role) => (
            <RoleCard key={role.id} role={role} />
          ))}
        </div>

        {/* Benefits Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 mt-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Pourquoi choisir ShareYourSales ?
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <DollarSign className="text-blue-600" size={24} />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Commissions attractives</h4>
              <p className="text-sm text-gray-600">
                Jusqu'à 30% de commission sur chaque vente + bonus de parrainage
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="text-purple-600" size={24} />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Analytics en temps réel</h4>
              <p className="text-sm text-gray-600">
                Suivez vos performances avec des tableaux de bord détaillés
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="text-green-600" size={24} />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Croissance garantie</h4>
              <p className="text-sm text-gray-600">
                Programme MLM sur 5 niveaux pour maximiser vos revenus passifs
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-6">Prêt à commencer pour de vrai ?</p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" disabled={loading} onClick={() => navigate('/register')}>
              Créer un compte gratuit
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/login')}>
              Se connecter
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Demo;
