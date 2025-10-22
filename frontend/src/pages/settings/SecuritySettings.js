import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { Lock, Shield, Wifi } from 'lucide-react';

const SecuritySettings = () => {
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [allowedIps, setAllowedIps] = useState(['192.168.1.100', '192.168.1.105']);

  const handlePasswordChange = (e) => {
    e.preventDefault();
    console.log('Changing password');
  };

  return (
    <div className="space-y-6" data-testid="security-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres de Sécurité</h1>
        <p className="text-gray-600 mt-2">Gérez la sécurité de votre compte</p>
      </div>

      {/* Change Password */}
      <Card title="Changer le Mot de Passe">
        <form onSubmit={handlePasswordChange} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe actuel
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nouveau mot de passe
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirmer le mot de passe
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <Button type="submit">
            Changer le mot de passe
          </Button>
        </form>
      </Card>

      {/* Two-Factor Authentication */}
      <Card title="Authentification à Deux Facteurs (2FA)">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Shield className="text-blue-600" size={32} />
            <div>
              <h3 className="font-semibold">2FA {twoFactorEnabled ? 'Activé' : 'Désactivé'}</h3>
              <p className="text-sm text-gray-600">
                Améliorez la sécurité de votre compte avec l'authentification à deux facteurs
              </p>
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={twoFactorEnabled}
              onChange={(e) => setTwoFactorEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </Card>

      {/* Allowed IPs */}
      <Card title="IPs Autorisées">
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Limitez l'accès à votre compte depuis des adresses IP spécifiques
          </p>
          <div className="space-y-2">
            {allowedIps.map((ip, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Wifi className="text-green-600" size={20} />
                  <span className="font-mono">{ip}</span>
                </div>
                <Button size="sm" variant="danger">
                  Supprimer
                </Button>
              </div>
            ))}
          </div>
          <Button variant="outline">
            Ajouter une IP
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default SecuritySettings;
