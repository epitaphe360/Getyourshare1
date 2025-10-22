import React from 'react';
import { useAuth } from '../context/AuthContext';
import AdminDashboard from './dashboards/AdminDashboard';
import MerchantDashboard from './dashboards/MerchantDashboard';
import InfluencerDashboard from './dashboards/InfluencerDashboard';

const Dashboard = () => {
  const { user } = useAuth();

  // Route vers le bon dashboard selon le rôle
  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  // Redirection selon le rôle
  if (user.role === 'admin') {
    return <AdminDashboard />;
  } else if (user.role === 'merchant') {
    return <MerchantDashboard />;
  } else if (user.role === 'influencer') {
    return <InfluencerDashboard />;
  }

  // Fallback
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Bienvenue sur ShareYourSales</h2>
        <p className="text-gray-600">Votre dashboard sera disponible prochainement.</p>
      </div>
    </div>
  );
};

export default Dashboard;
