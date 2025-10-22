import React from 'react';
import Card from '../../components/common/Card';
import { AlertTriangle } from 'lucide-react';

const LostOrders = () => {
  return (
    <div className="space-y-6" data-testid="lost-orders">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Commandes Perdues</h1>
        <p className="text-gray-600 mt-2">Suivez les commandes non attribuées</p>
      </div>

      <Card>
        <div className="text-center py-12">
          <AlertTriangle className="mx-auto text-yellow-500" size={48} />
          <h3 className="mt-4 text-lg font-semibold text-gray-900">Aucune commande perdue</h3>
          <p className="mt-2 text-gray-600">Toutes les commandes ont été correctement attribuées</p>
        </div>
      </Card>
    </div>
  );
};

export default LostOrders;
