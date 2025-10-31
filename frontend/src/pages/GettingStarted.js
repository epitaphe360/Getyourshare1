import React from 'react';
import Card from '../components/common/Card';
import { CheckCircle, ArrowRight } from 'lucide-react';

const GettingStarted = () => {
  const steps = [
    {
      title: 'Étape 1: Configurer votre compte',
      description: 'Complétez les informations de votre entreprise dans les paramètres.',
      completed: true,
    },
    {
      title: 'Étape 2: Créer votre première campagne',
      description: 'Allez dans Campagnes/Offres pour créer une nouvelle campagne.',
      completed: false,
    },
    {
      title: 'Étape 3: Inviter des affiliés',
      description: 'Invitez des affiliés à rejoindre votre programme.',
      completed: false,
    },
    {
      title: 'Étape 4: Configurer les commissions',
      description: 'Définissez vos règles de commission dans les paramètres.',
      completed: false,
    },
  ];

  return (
    <div className="space-y-8" data-testid="getting-started">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Bienvenue sur ShareYourSales!</h1>
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
                  <ArrowRight className="text-gray-400" size={20} />
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Ressources">
            <div className="space-y-3">
              <a href="#" className="block p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-all">
                <h4 className="font-semibold text-blue-900">Documentation</h4>
                <p className="text-sm text-blue-700 mt-1">Guides complets</p>
              </a>
              <a href="#" className="block p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-all">
                <h4 className="font-semibold text-green-900">Vidéos Tutoriels</h4>
                <p className="text-sm text-green-700 mt-1">Apprenez en vidéo</p>
              </a>
              <a href="#" className="block p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-all">
                <h4 className="font-semibold text-purple-900">Support</h4>
                <p className="text-sm text-purple-700 mt-1">Contactez-nous</p>
              </a>
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
