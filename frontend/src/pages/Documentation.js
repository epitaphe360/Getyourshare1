import React, { useState } from 'react';
import Card from '../components/common/Card';
import { Book, Search, ChevronRight, FileText, Video, Code, Settings, Users, TrendingUp } from 'lucide-react';

const Documentation = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const categories = [
    {
      title: 'Démarrage',
      icon: <Book className="text-blue-500" size={24} />,
      articles: [
        { title: 'Guide de démarrage rapide', description: 'Commencez en 5 minutes', duration: '5 min' },
        { title: 'Configuration de votre compte', description: 'Paramétrez votre profil', duration: '10 min' },
        { title: 'Premiers pas avec les campagnes', description: 'Créez votre première campagne', duration: '15 min' },
      ]
    },
    {
      title: 'Pour les Influenceurs',
      icon: <Users className="text-green-500" size={24} />,
      articles: [
        { title: 'Comment rejoindre une campagne', description: 'Trouvez et rejoignez des campagnes', duration: '8 min' },
        { title: 'Générer vos liens de tracking', description: 'Créez vos liens personnalisés', duration: '5 min' },
        { title: 'Suivre vos performances', description: 'Analysez vos statistiques', duration: '10 min' },
        { title: 'Demander un paiement', description: 'Comment retirer vos gains', duration: '7 min' },
      ]
    },
    {
      title: 'Pour les Marchands',
      icon: <TrendingUp className="text-purple-500" size={24} />,
      articles: [
        { title: 'Créer une campagne attractive', description: 'Attirez les meilleurs influenceurs', duration: '12 min' },
        { title: 'Gérer vos affiliés', description: 'Approuvez et gérez vos partenaires', duration: '10 min' },
        { title: 'Configuration des commissions', description: 'Définissez vos règles de rémunération', duration: '8 min' },
        { title: 'Intégration technique', description: 'Connectez votre boutique', duration: '20 min' },
      ]
    },
    {
      title: 'Paramètres & Configuration',
      icon: <Settings className="text-orange-500" size={24} />,
      articles: [
        { title: 'Paramètres de sécurité', description: 'Sécurisez votre compte', duration: '6 min' },
        { title: 'Configuration SMTP', description: 'Configurez vos emails', duration: '15 min' },
        { title: 'Webhooks et intégrations', description: 'Automatisez vos workflows', duration: '25 min' },
      ]
    },
    {
      title: 'API & Développeurs',
      icon: <Code className="text-red-500" size={24} />,
      articles: [
        { title: 'Documentation API', description: 'Référence complète de l\'API', duration: '30 min' },
        { title: 'Authentification', description: 'Gérez les tokens JWT', duration: '10 min' },
        { title: 'Exemples de code', description: 'Intégrations prêtes à l\'emploi', duration: '20 min' },
      ]
    },
  ];

  const popularArticles = [
    { title: 'Comment augmenter vos conversions', views: '12.5K', category: 'Marketing' },
    { title: 'Meilleures pratiques pour les influenceurs', views: '8.3K', category: 'Conseils' },
    { title: 'Optimiser vos campagnes', views: '6.7K', category: 'Stratégie' },
    { title: 'Comprendre les commissions MLM', views: '5.2K', category: 'Finances' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Centre de Documentation</h1>
        <p className="text-blue-100 mb-6">Tout ce dont vous avez besoin pour réussir avec Share Your Sales</p>
        
        {/* Search Bar */}
        <div className="relative max-w-2xl">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Rechercher dans la documentation..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
      </div>

      {/* Popular Articles */}
      <Card title="📈 Articles Populaires">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {popularArticles.map((article, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-all">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">{article.title}</h3>
                  <p className="text-sm text-gray-600">{article.category} • {article.views} vues</p>
                </div>
                <ChevronRight className="text-gray-400" size={20} />
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Documentation Categories */}
      <div className="grid grid-cols-1 gap-6">
        {categories.map((category, index) => (
          <Card key={index} title={
            <div className="flex items-center space-x-3">
              {category.icon}
              <span>{category.title}</span>
            </div>
          }>
            <div className="space-y-3">
              {category.articles.map((article, articleIndex) => (
                <div 
                  key={articleIndex}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-all"
                >
                  <div className="flex items-start space-x-3">
                    <FileText className="text-gray-400 mt-1" size={20} />
                    <div>
                      <h4 className="font-semibold text-gray-900">{article.title}</h4>
                      <p className="text-sm text-gray-600">{article.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-500">{article.duration}</span>
                    <ChevronRight className="text-gray-400" size={20} />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>

      {/* Help Section */}
      <Card>
        <div className="text-center py-8">
          <h3 className="text-xl font-bold text-gray-900 mb-2">Besoin d'aide supplémentaire ?</h3>
          <p className="text-gray-600 mb-6">Notre équipe support est là pour vous aider</p>
          <div className="flex justify-center space-x-4">
            <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all">
              Contacter le Support
            </button>
            <button className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all">
              Voir les Vidéos
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Documentation;
