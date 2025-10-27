import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { CheckCircle, ArrowRight } from 'lucide-react';

const GettingStarted = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Étapes adaptées selon le rôle
  const getStepsForRole = (role) => {
    // Étapes pour INFLUENCER
    if (role?.toLowerCase() === 'influencer') {
      return [
        {
          title: 'Étape 1: Complétez votre profil',
          description: 'Ajoutez vos informations personnelles et vos réseaux sociaux.',
          completed: true,
          action: 'Mon profil',
          link: '/settings/personal',
        },
        {
          title: 'Étape 2: Explorez le Marketplace',
          description: 'Découvrez les campagnes disponibles et trouvez celles qui vous correspondent.',
          completed: false,
          action: 'Voir le Marketplace',
          link: '/marketplace',
        },
        {
          title: 'Étape 3: Générez vos liens',
          description: 'Créez vos liens de tracking personnalisés pour promouvoir les produits.',
          completed: false,
          action: 'Mes liens',
          link: '/tracking-links',
        },
        {
          title: 'Étape 4: Suivez vos performances',
          description: 'Consultez vos statistiques et vos gains en temps réel.',
          completed: false,
          action: 'Voir mes stats',
          link: '/performance/reports',
        },
      ];
    }

    // Étapes pour MERCHANT
    if (role?.toLowerCase() === 'merchant') {
      return [
        {
          title: 'Étape 1: Configurer votre entreprise',
          description: 'Complétez les informations de votre entreprise dans les paramètres.',
          completed: true,
          action: 'Configurer',
          link: '/settings/company',
        },
        {
          title: 'Étape 2: Créer votre première campagne',
          description: 'Créez une campagne pour attirer des influenceurs.',
          completed: false,
          action: 'Créer une campagne',
          link: '/campaigns',
        },
        {
          title: 'Étape 3: Gérer vos affiliés',
          description: 'Acceptez les demandes et gérez vos affiliés.',
          completed: false,
          action: 'Voir les affiliés',
          link: '/affiliates',
        },
        {
          title: 'Étape 4: Configurer les commissions',
          description: 'Définissez vos règles de commission.',
          completed: false,
          action: 'Configurer',
          link: '/settings/affiliates',
        },
      ];
    }

    // Étapes pour ADMIN (par défaut)
    return [
      {
        title: 'Étape 1: Configuration de la plateforme',
        description: 'Configurez les paramètres généraux de la plateforme.',
        completed: true,
        action: 'Configurer',
        link: '/settings/company',
      },
      {
        title: 'Étape 2: Gérer les campagnes',
        description: 'Supervisez toutes les campagnes de la plateforme.',
        completed: false,
        action: 'Voir les campagnes',
        link: '/campaigns',
      },
      {
        title: 'Étape 3: Gérer les utilisateurs',
        description: 'Administrez les marchands, influenceurs et leurs permissions.',
        completed: false,
        action: 'Voir les utilisateurs',
        link: '/settings/users',
      },
      {
        title: 'Étape 4: Surveiller les performances',
        description: 'Consultez les rapports globaux de la plateforme.',
        completed: false,
        action: 'Voir les rapports',
        link: '/performance/reports',
      },
    ];
  };

  const steps = getStepsForRole(user?.role);

  return (
    <div className="space-y-8" data-testid="getting-started">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Bienvenue sur Share Your Sales!</h1>
        <p className="text-gray-600 mt-2">Suivez ces étapes pour commencer</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card title="Guide de Démarrage">
            <div className="space-y-4">
              {steps.map((step, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all"
                >
                  <div className="flex-shrink-0">
                    {step.completed ? (
                      <CheckCircle className="text-green-500" size={24} />
                    ) : (
                      <div className="w-6 h-6 border-2 border-gray-300 rounded-full" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{step.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                  </div>
                  <Button 
                    size="sm" 
                    variant={step.completed ? "secondary" : "primary"}
                    onClick={() => navigate(step.link)}
                  >
                    {step.action} <ArrowRight className="ml-1" size={16} />
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Ressources">
            <div className="space-y-3">
              <div 
                onClick={() => navigate('/documentation')}
                className="block p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-all cursor-pointer"
              >
                <h4 className="font-semibold text-blue-900">Documentation</h4>
                <p className="text-sm text-blue-700 mt-1">Guides complets</p>
              </div>
              <div 
                onClick={() => navigate('/video-tutorials')}
                className="block p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-all cursor-pointer"
              >
                <h4 className="font-semibold text-green-900">Vidéos Tutoriels</h4>
                <p className="text-sm text-green-700 mt-1">Apprenez en vidéo</p>
              </div>
              <div 
                onClick={() => navigate('/support')}
                className="block p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-all cursor-pointer"
              >
                <h4 className="font-semibold text-purple-900">Support</h4>
                <p className="text-sm text-purple-700 mt-1">Contactez-nous</p>
              </div>
            </div>
          </Card>

          <Card title="Statistiques Rapides">
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Complétion du profil</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '60%' }} />
                </div>
                <p className="text-xs text-gray-500 mt-1">60%</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default GettingStarted;
