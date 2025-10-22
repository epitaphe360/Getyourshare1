import React from 'react';
import Card from '../../components/common/Card';
import StatCard from '../../components/common/StatCard';
import { DollarSign, Users, TrendingUp } from 'lucide-react';

const MLMCommissions = () => {
  const levels = [
    { level: 1, percentage: 10, affiliates: 45, earned: 4500 },
    { level: 2, percentage: 5, affiliates: 123, earned: 3450 },
    { level: 3, percentage: 2.5, affiliates: 89, earned: 1230 },
  ];

  return (
    <div className="space-y-6" data-testid="mlm-commissions">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Commissions MLM</h1>
        <p className="text-gray-600 mt-2">Rapports Multi-Level Marketing</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Commissions MLM"
          value={9180}
          isCurrency={true}
          icon={<DollarSign className="text-blue-600" size={24} />}
        />
        <StatCard
          title="Affiliés Actifs MLM"
          value={257}
          icon={<Users className="text-green-600" size={24} />}
        />
        <StatCard
          title="Taux Moyen"
          value="5.8%"
          icon={<TrendingUp className="text-purple-600" size={24} />}
        />
      </div>

      <Card title="Commissions par Niveau">
        <div className="space-y-4">
          {levels.map((level) => (
            <div key={level.level} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold text-lg">Niveau {level.level}</h3>
                  <p className="text-sm text-gray-600">{level.percentage}% de commission</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-blue-600">{level.earned}€</p>
                  <p className="text-sm text-gray-600">{level.affiliates} affiliés</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default MLMCommissions;
