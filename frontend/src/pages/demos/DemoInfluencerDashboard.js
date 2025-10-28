import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, DollarSign, Users, Target, ArrowLeft, Eye, Award } from 'lucide-react';
import Button from '../../components/common/Button';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';

const DemoInfluencerDashboard = () => {
  const navigate = useNavigate();

  // Demo data - static, no real database access
  const demoStats = {
    totalFollowers: 45230,
    totalEarnings: 8456.75,
    activeAffiliates: 127,
    conversionRate: 4.82
  };

  const demoMLMLevels = [
    { level: 1, affiliates: 127, sales: 342, earnings: 4230.50 },
    { level: 2, affiliates: 89, sales: 198, earnings: 2156.25 },
    { level: 3, affiliates: 54, sales: 112, earnings: 1345.00 },
    { level: 4, affiliates: 23, sales: 45, earnings: 525.00 },
    { level: 5, affiliates: 8, sales: 12, earnings: 200.00 },
  ];

  const demoTopAffiliates = [
    { name: 'Marie Dubois', sales: 45, earnings: 1250.50, rate: 4.5 },
    { name: 'Jean Martin', sales: 38, earnings: 1089.00, rate: 4.2 },
    { name: 'Sophie Laurent', sales: 32, earnings: 945.75, rate: 3.8 },
    { name: 'Pierre Lefebvre', sales: 28, earnings: 834.25, rate: 3.5 },
  ];

  const demoRecentActivity = [
    { type: 'new_affiliate', name: 'Lucas Bernard', time: 'Il y a 2h', level: 1 },
    { type: 'sale', name: 'Marie Dubois', amount: 125.50, time: 'Il y a 3h', level: 1 },
    { type: 'sale', name: 'Jean Martin', amount: 89.00, time: 'Il y a 5h', level: 1 },
    { type: 'new_affiliate', name: 'Emma Petit', time: 'Il y a 6h', level: 2 },
    { type: 'sale', name: 'Sophie Laurent', amount: 65.75, time: 'Il y a 8h', level: 1 },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Demo Banner */}
      <div className="bg-purple-600 text-white py-3">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Eye size={20} />
            <span className="font-semibold">Mode Démo - Données fictives</span>
          </div>
          <Button variant="outline" size="sm" className="bg-white text-purple-600 hover:bg-purple-50" onClick={() => navigate('/demo')}>
            <ArrowLeft size={16} className="mr-2" />
            Retour
          </Button>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Influenceur</h1>
          <p className="text-gray-600 mt-2">Gérez votre réseau d'affiliés et suivez vos revenus MLM</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Abonnés Total"
            value={demoStats.totalFollowers.toLocaleString()}
            icon={<Users className="text-blue-600" />}
            trend={{ value: 18.2, isPositive: true }}
          />
          <StatCard
            title="Gains Totaux"
            value={`${demoStats.totalEarnings.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €`}
            icon={<DollarSign className="text-green-600" />}
            trend={{ value: 24.5, isPositive: true }}
          />
          <StatCard
            title="Affiliés Actifs"
            value={demoStats.activeAffiliates}
            icon={<Target className="text-purple-600" />}
            trend={{ value: 15.3, isPositive: true }}
          />
          <StatCard
            title="Taux de Conversion"
            value={`${demoStats.conversionRate}%`}
            icon={<TrendingUp className="text-orange-600" />}
            trend={{ value: 3.7, isPositive: true }}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* MLM Levels Performance */}
          <Card title="Performance par Niveau MLM" className="lg:col-span-2">
            <div className="space-y-4">
              {demoMLMLevels.map((level) => (
                <div key={level.level} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    N{level.level}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-gray-900">Niveau {level.level}</h4>
                      <span className="text-sm text-gray-500">({level.affiliates} affiliés)</span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600">
                      <span>{level.sales} ventes</span>
                      <span>•</span>
                      <span className="text-green-600 font-semibold">{level.earnings.toFixed(2)} €</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <Award className="text-purple-500" size={24} />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Top Affiliates */}
          <Card title="Meilleurs Affiliés (Niveau 1)">
            <div className="space-y-4">
              {demoTopAffiliates.map((affiliate, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-semibold text-gray-900">{affiliate.name}</h4>
                    <div className="flex gap-4 mt-1 text-sm text-gray-600">
                      <span>{affiliate.sales} ventes</span>
                      <span>•</span>
                      <span>{affiliate.rate}% taux</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">{affiliate.earnings.toFixed(2)} €</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Recent Activity */}
          <Card title="Activité Récente">
            <div className="space-y-3">
              {demoRecentActivity.map((activity, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    activity.type === 'new_affiliate' ? 'bg-blue-100' : 'bg-green-100'
                  }`}>
                    {activity.type === 'new_affiliate' ? (
                      <Users className="text-blue-600" size={20} />
                    ) : (
                      <DollarSign className="text-green-600" size={20} />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">
                      {activity.type === 'new_affiliate' ? (
                        <>
                          <span className="font-semibold">{activity.name}</span> a rejoint votre réseau (N{activity.level})
                        </>
                      ) : (
                        <>
                          Vente de <span className="font-semibold">{activity.amount} €</span> par {activity.name}
                        </>
                      )}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="mt-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-8 text-white text-center">
          <h3 className="text-2xl font-bold mb-4">Développez votre réseau d'affiliés</h3>
          <p className="text-purple-100 mb-6 max-w-2xl mx-auto">
            Profitez du système MLM sur 5 niveaux pour maximiser vos revenus passifs et créer un empire d'affiliation
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="bg-white text-purple-600 hover:bg-purple-50" onClick={() => navigate('/register')}>
              Devenir Influenceur
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10" onClick={() => navigate('/pricing')}>
              Voir les tarifs
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoInfluencerDashboard;
