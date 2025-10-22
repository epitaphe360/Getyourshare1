import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

const Permissions = () => {
  const [permissions, setPermissions] = useState({
    visible_screens: {
      performance: true,
      clicks: true,
      impressions: false,
      conversions: true,
      leads: true,
      references: true,
      campaigns: true,
      lost_orders: false,
    },
    visible_fields: {
      conversion_amount: true,
      short_link: true,
      conversion_order_id: true,
    },
    authorized_actions: {
      api_access: true,
      view_personal_info: true,
    },
  });

  const handleToggle = (category, key) => {
    setPermissions({
      ...permissions,
      [category]: {
        ...permissions[category],
        [key]: !permissions[category][key],
      },
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Saving permissions:', permissions);
  };

  return (
    <div className="space-y-6" data-testid="permissions">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Permissions par Défaut</h1>
        <p className="text-gray-600 mt-2">Définissez les permissions par défaut des affiliés</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
          <Card title="Écrans Visibles">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(permissions.visible_screens).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="capitalize">{key.replace('_', ' ')}</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={() => handleToggle('visible_screens', key)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Champs Visibles">
            <div className="space-y-4">
              {Object.entries(permissions.visible_fields).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={() => handleToggle('visible_fields', key)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Actions Autorisées">
            <div className="space-y-4">
              {Object.entries(permissions.authorized_actions).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={() => handleToggle('authorized_actions', key)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </Card>

          <div className="flex justify-end">
            <Button type="submit">
              Enregistrer les modifications
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default Permissions;
