import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, DollarSign, MousePointer, ShoppingBag, ArrowLeft, Eye } from 'lucide-react';
import Button from '../../components/common/Button';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';

const DemoAffiliateDashboard = () => {
  const navigate = useNavigate();

  // Demo data - static, no real database access
  const demoStats = {
    totalClicks: 1247,
    totalSales: 43,
    totalEarnings: 2156.50,
    conversionRate: 3.45
  };

  const demoRecentSales = [
    { id: 1, product: 'MacBook Pro 16"', merchant: 'Tech Store', commission: 120.00, date: '2025-10-27', status: 'Validée' },
    { id: 2, product: 'iPhone 15 Pro', merchant: 'Mobile Hub', commission: 85.00, date: '2025-10-26', status: 'Validée' },
    { id: 3, product: 'AirPods Pro', merchant: 'Audio World', commission: 25.50, date: '2025-10-25', status: 'En attente' },
    { id: 4, product: 'iPad Air', merchant: 'Tech Store', commission: 65.00, date: '2025-10-24', status: 'Validée' },
    { id: 5, product: 'Apple Watch Series 9', merchant: 'Wearable Tech', commission: 42.00, date: '2025-10-23', status: 'Validée' },
  ];

  const demoTopProducts = [
    { name: 'MacBook Pro 16"', clicks: 234, sales: 12, commission: 15 },
    { name: 'iPhone 15 Pro', clicks: 189, sales: 9, commission: 12 },
    { name: 'iPad Air', clicks: 156, sales: 7, commission: 10 },
    { name: 'AirPods Pro', clicks: 143, sales: 6, commission: 8 },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Demo Banner */}
      <div className="bg-blue-600 text-white py-3">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Eye size={20} />
            <span className="font-semibold">Mode Démo - Données fictives</span>
          </div>
          <Button variant="outline" size="sm" className="bg-white text-blue-600 hover:bg-blue-50" onClick={() => navigate('/demo')}>
            <ArrowLeft size={16} className="mr-2" />
            Retour
          </Button>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Affilié</h1>
          <p className="text-gray-600 mt-2">Vue d'ensemble de vos performances</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Clics"
            value={demoStats.totalClicks.toLocaleString()}
            icon={<MousePointer className="text-blue-600" />}
            trend={{ value: 12.5, isPositive: true }}
          />
          <StatCard
            title="Ventes"
            value={demoStats.totalSales}
            icon={<ShoppingBag className="text-green-600" />}
            trend={{ value: 8.3, isPositive: true }}
          />
          <StatCard
            title="Gains Totaux"
            value={`${demoStats.totalEarnings.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €`}
            icon={<DollarSign className="text-purple-600" />}
            trend={{ value: 15.7, isPositive: true }}
          />
          <StatCard
            title="Taux de Conversion"
            value={`${demoStats.conversionRate}%`}
            icon={<TrendingUp className="text-orange-600" />}
            trend={{ value: 2.1, isPositive: true }}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Sales */}
          <Card title="Ventes Récentes" className="lg:col-span-2">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Produit</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Marchand</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Commission</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Date</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {demoRecentSales.map((sale) => (
                    <tr key={sale.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 text-sm text-gray-900">{sale.product}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{sale.merchant}</td>
                      <td className="py-3 px-4 text-sm font-semibold text-green-600">
                        {sale.commission.toFixed(2)} €
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{sale.date}</td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          sale.status === 'Validée' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {sale.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Top Products */}
          <Card title="Produits les Plus Performants" className="lg:col-span-2">
            <div className="space-y-4">
              {demoTopProducts.map((product, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{product.name}</h4>
                    <div className="flex gap-4 mt-1 text-sm text-gray-600">
                      <span>{product.clicks} clics</span>
                      <span>•</span>
                      <span>{product.sales} ventes</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">{product.commission}%</div>
                    <div className="text-xs text-gray-500">Commission</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="mt-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white text-center">
          <h3 className="text-2xl font-bold mb-4">Prêt à commencer pour de vrai ?</h3>
          <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
            Créez votre compte gratuit et commencez à gagner de l'argent en partageant des produits dès aujourd'hui
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50" onClick={() => navigate('/register')}>
              Créer un compte gratuit
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

export default DemoAffiliateDashboard;
