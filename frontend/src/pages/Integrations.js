import React, { useState } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import { Plus, Settings, Check } from 'lucide-react';

const Integrations = () => {
  const [integrations] = useState([
    {
      id: 1,
      name: 'Stripe',
      description: 'Processeur de paiement pour les transactions',
      category: 'Payment',
      status: 'active',
      icon: '💳',
    },
    {
      id: 2,
      name: 'PayPal',
      description: 'Alternative de paiement pour les affiliés',
      category: 'Payment',
      status: 'active',
      icon: '💰',
    },
    {
      id: 3,
      name: 'Webhooks',
      description: 'Notifications temps réel des événements',
      category: 'API',
      status: 'active',
      icon: '🔔',
    },
    {
      id: 4,
      name: 'Google Analytics',
      description: 'Suivi et analyse du trafic',
      category: 'Analytics',
      status: 'inactive',
      icon: '📊',
    },
    {
      id: 5,
      name: 'Zapier',
      description: 'Automatisation et intégrations tierces',
      category: 'Automation',
      status: 'inactive',
      icon: '⚡',
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState(null);

  const handleConfigure = (integration) => {
    setSelectedIntegration(integration);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6" data-testid="integrations">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Intégrations</h1>
          <p className="text-gray-600 mt-2">Connectez vos services tiers</p>
        </div>
        <Button>
          <Plus size={20} className="mr-2" />
          Ajouter une Intégration
        </Button>
      </div>

      {/* Categories */}
      <div className="flex space-x-4 overflow-x-auto pb-2">
        {['Toutes', 'Payment', 'Analytics', 'API', 'Automation'].map((cat) => (
          <button
            key={cat}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 whitespace-nowrap"
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Integrations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.map((integration) => (
          <Card key={integration.id}>
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-4xl">{integration.icon}</div>
                  <div>
                    <h3 className="font-semibold text-lg">{integration.name}</h3>
                    <Badge status={integration.status}>{integration.status}</Badge>
                  </div>
                </div>
                {integration.status === 'active' && (
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <Check className="text-green-600" size={20} />
                  </div>
                )}
              </div>

              <p className="text-sm text-gray-600">{integration.description}</p>

              <div className="pt-4 border-t border-gray-200">
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full"
                  onClick={() => handleConfigure(integration)}
                >
                  <Settings size={16} className="mr-2" />
                  Configurer
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Configuration Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={`Configuration - ${selectedIntegration?.name}`}
        size="md"
      >
        {selectedIntegration && (
          <div className="space-y-4">
            <div className="text-center py-4">
              <div className="text-6xl mb-4">{selectedIntegration.icon}</div>
              <h3 className="text-xl font-semibold">{selectedIntegration.name}</h3>
              <p className="text-gray-600 mt-2">{selectedIntegration.description}</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Entrez votre clé API"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Secret
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Entrez votre secret API"
                />
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium">Activer l'intégration</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked={selectedIntegration.status === 'active'} />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Annuler
              </Button>
              <Button onClick={() => setIsModalOpen(false)}>
                Enregistrer
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Integrations;
