import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, DollarSign, Users, ShoppingBag, ArrowLeft, Eye, Package } from 'lucide-react';
import Button from '../../components/common/Button';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';

const DemoMerchantDashboard = () => {
  const navigate = useNavigate();

  // Demo data - static, no real database access
  const demoStats = {
    totalRevenue: 54230.75,
    totalOrders: 342,
    activeAffiliates: 1247,
    roi: 324
  };

  const demoTopAffiliates = [
    { name: 'Sophie Influencer', sales: 89, revenue: 12450.50, commission: 1867.58 },
    { name: 'Marc Digital', sales: 67, revenue: 9890.00, commission: 1483.50 },
    { name: 'Laura Marketing', sales: 54, revenue: 7650.25, commission: 1147.54 },
    { name: 'Pierre Creator', sales: 45, revenue: 6234.75, commission: 935.21 },
  ];

  const demoTopProducts = [
    { name: 'MacBook Pro 16"', sales: 89, revenue: 178000, affiliates: 45 },
    { name: 'iPhone 15 Pro', sales: 134, revenue: 134000, affiliates: 67 },
    { name: 'iPad Air', sales: 67, revenue: 40200, affiliates: 34 },
    { name: 'AirPods Pro', sales: 156, revenue: 31200, affiliates: 78 },
  ];

  const demoRecentOrders = [
    { id: 'ORD-1234', affiliate: 'Sophie Influencer', product: 'MacBook Pro 16"', amount: 2499.00, commission: 374.85, date: '2025-10-27', status: 'Livrée' },
    { id: 'ORD-1233', affiliate: 'Marc Digital', product: 'iPhone 15 Pro', amount: 1299.00, commission: 194.85, date: '2025-10-27', status: 'En cours' },
    { id: 'ORD-1232', affiliate: 'Laura Marketing', product: 'iPad Air', amount: 699.00, commission: 104.85, date: '2025-10-26', status: 'Livrée' },
    { id: 'ORD-1231', affiliate: 'Pierre Creator', product: 'AirPods Pro', amount: 279.00, commission: 41.85, date: '2025-10-26', status: 'Livrée' },
    { id: 'ORD-1230', affiliate: 'Sophie Influencer', product: 'Apple Watch', amount: 449.00, commission: 67.35, date: '2025-10-25', status: 'En cours' },
  ];

  const demoAffiliateActivity = [
    { affiliate: 'Emma Laurent', action: 'Nouvelle inscription', time: 'Il y a 1h' },
    { affiliate: 'Thomas Dubois', action: 'Demande de paiement', amount: 450.00, time: 'Il y a 2h' },
    { affiliate: 'Chloé Martin', action: 'Nouveau lien créé', product: 'iPhone 15 Pro', time: 'Il y a 3h' },
    { affiliate: 'Lucas Petit', action: 'Nouvelle inscription', time: 'Il y a 4h' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Demo Banner */}
      <div className="bg-green-600 text-white py-3">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Eye size={20} />
            <span className="font-semibold">Mode Démo - Données fictives</span>
          </div>
          <Button variant="outline" size="sm" className="bg-white text-green-600 hover:bg-green-50" disabled={loading} onClick={() => navigate('/demo')}>
            <ArrowLeft size={16} className="mr-2" />
            Retour
          </Button>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Marchand</h1>
          <p className="text-gray-600 mt-2">Gérez vos affiliés et suivez vos ventes</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Chiffre d'Affaires"
            value={`${demoStats.totalRevenue.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €`}
            icon={<DollarSign className="text-green-600" />}
            trend={{ value: 28.4, isPositive: true }}
          />
          <StatCard
            title="Commandes"
            value={demoStats.totalOrders}
            icon={<ShoppingBag className="text-blue-600" />}
            trend={{ value: 15.2, isPositive: true }}
          />
          <StatCard
            title="Affiliés Actifs"
            value={demoStats.activeAffiliates}
            icon={<Users className="text-purple-600" />}
            trend={{ value: 42.8, isPositive: true }}
          />
          <StatCard
            title="ROI"
            value={`${demoStats.roi}%`}
            icon={<TrendingUp className="text-orange-600" />}
            trend={{ value: 12.5, isPositive: true }}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Affiliates */}
          <Card title="Meilleurs Affiliés">
            <div className="space-y-4">
              {demoTopAffiliates.map((affiliate, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{affiliate.name}</h4>
                    <div className="flex gap-4 mt-1 text-sm text-gray-600">
                      <span>{affiliate.sales} ventes</span>
                      <span>•</span>
                      <span>{affiliate.revenue.toFixed(2)} € CA</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">{affiliate.commission.toFixed(2)} €</div>
                    <div className="text-xs text-gray-500">Commission</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Top Products */}
          <Card title="Produits les Plus Vendus">
            <div className="space-y-4">
              {demoTopProducts.map((product, index) => (
                <div key={index} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                    <Package className="text-white" size={24} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{product.name}</h4>
                    <div className="flex gap-4 mt-1 text-sm text-gray-600">
                      <span>{product.sales} ventes</span>
                      <span>•</span>
                      <span>{product.affiliates} affiliés</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900">{product.revenue.toLocaleString()} €</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Recent Orders */}
          <Card title="Commandes Récentes" className="lg:col-span-2">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">ID</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Affilié</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Produit</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Montant</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Commission</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Date</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {demoRecentOrders.map((order) => (
                    <tr key={order.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 text-sm font-mono text-gray-600">{order.id}</td>
                      <td className="py-3 px-4 text-sm text-gray-900">{order.affiliate}</td>
                      <td className="py-3 px-4 text-sm text-gray-900">{order.product}</td>
                      <td className="py-3 px-4 text-sm font-semibold text-gray-900">{order.amount.toFixed(2)} €</td>
                      <td className="py-3 px-4 text-sm font-semibold text-green-600">{order.commission.toFixed(2)} €</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{order.date}</td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          order.status === 'Livrée' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-blue-100 text-blue-700'
                        }`}>
                          {order.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Affiliate Activity */}
          <Card title="Activité des Affiliés" className="lg:col-span-2">
            <div className="space-y-3">
              {demoAffiliateActivity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <Users className="text-blue-600" size={20} />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{activity.affiliate}</p>
                      <p className="text-xs text-gray-600">
                        {activity.action}
                        {activity.amount && ` - ${activity.amount.toFixed(2)} €`}
                        {activity.product && ` - ${activity.product}`}
                      </p>
                    </div>
                  </div>
                  <span className="text-xs text-gray-500">{activity.time}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="mt-8 bg-gradient-to-r from-green-600 to-teal-600 rounded-xl p-8 text-white text-center">
          <h3 className="text-2xl font-bold mb-4">Développez vos ventes avec un réseau d'affiliés</h3>
          <p className="text-green-100 mb-6 max-w-2xl mx-auto">
            Rejoignez les centaines de marchands qui utilisent ShareYourSales pour générer un ROI de 300%+ grâce au marketing d'affiliation
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="bg-white text-green-600 hover:bg-green-50" disabled={loading} onClick={() => navigate('/register')}>
              Commencer gratuitement
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10" disabled={loading} onClick={() => navigate('/pricing')}>
              Voir les tarifs
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoMerchantDashboard;
