import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import StatCard from '../components/common/StatCard';
import Card from '../components/common/Card';
import { TrendingUp, Users, DollarSign, Target, UserCheck, MousePointer } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await api.get('/api/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock chart data
  const revenueData = [
    { month: 'Jan', revenue: 45000 },
    { month: 'Fév', revenue: 52000 },
    { month: 'Mar', revenue: 48000 },
    { month: 'Avr', revenue: 61000 },
    { month: 'Mai', revenue: 55000 },
    { month: 'Juin', revenue: 67000 },
  ];

  const conversionsData = [
    { day: 'Lun', conversions: 45 },
    { day: 'Mar', conversions: 52 },
    { day: 'Mer', conversions: 38 },
    { day: 'Jeu', conversions: 65 },
    { day: 'Ven', conversions: 58 },
    { day: 'Sam', conversions: 42 },
    { day: 'Dim', conversions: 35 },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8" data-testid="dashboard">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord</h1>
        <p className="text-gray-600 mt-2">Vue d'ensemble de vos performances</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Revenus Totaux"
          value={stats?.total_revenue || 0}
          isCurrency={true}
          icon={<DollarSign className="text-blue-600" size={24} />}
          trend={12.5}
        />
        <StatCard
          title="Conversions"
          value={stats?.total_conversions || 0}
          icon={<Target className="text-green-600" size={24} />}
          trend={8.2}
        />
        <StatCard
          title="Clics Totaux"
          value={stats?.total_clicks || 0}
          icon={<MousePointer className="text-purple-600" size={24} />}
          trend={-3.1}
        />
        <StatCard
          title="Affiliés Actifs"
          value={stats?.active_affiliates || 0}
          icon={<UserCheck className="text-orange-600" size={24} />}
          trend={5.7}
        />
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Taux de Conversion">
          <div className="text-center">
            <p className="text-4xl font-bold text-blue-600">{stats?.conversion_rate?.toFixed(2)}%</p>
            <p className="text-sm text-gray-600 mt-2">Moyenne sur 30 jours</p>
          </div>
        </Card>
        <Card title="Valeur Moyenne">
          <div className="text-center">
            <p className="text-4xl font-bold text-green-600">{stats?.average_order_value?.toFixed(2)}€</p>
            <p className="text-sm text-gray-600 mt-2">Par commande</p>
          </div>
        </Card>
        <Card title="Campagnes Actives">
          <div className="text-center">
            <p className="text-4xl font-bold text-purple-600">{stats?.active_campaigns || 0}</p>
            <p className="text-sm text-gray-600 mt-2">En cours</p>
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Revenus Mensuels">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="Revenus (€)" />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Conversions Hebdomadaires">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={conversionsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="conversions" fill="#10b981" name="Conversions" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
