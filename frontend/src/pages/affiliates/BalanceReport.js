import React from 'react';
import Card from '../../components/common/Card';
import StatCard from '../../components/common/StatCard';
import { DollarSign, TrendingUp, Users } from 'lucide-react';

const BalanceReport = () => {
  return (
    <div className="space-y-6" data-testid="balance-report">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Rapport de Solde</h1>
        <p className="text-gray-600 mt-2">Vue d'ensemble des soldes affiliés</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Solde Total"
          value={45230.50}
          isCurrency={true}
          icon={<DollarSign className="text-blue-600" size={24} />}
        />
        <StatCard
          title="Paiements en Attente"
          value={12450.00}
          isCurrency={true}
          icon={<TrendingUp className="text-yellow-600" size={24} />}
        />
        <StatCard
          title="Affiliés avec Solde"
          value={87}
          icon={<Users className="text-green-600" size={24} />}
        />
      </div>

      <Card title="Détails par Affilié">
        <div className="text-center py-8 text-gray-600">
          Sélectionnez un affilié pour voir les détails
        </div>
      </Card>
    </div>
  );
};

export default BalanceReport;
