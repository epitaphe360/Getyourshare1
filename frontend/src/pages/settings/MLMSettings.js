import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';

const MLMSettings = () => {
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [mlmEnabled, setMlmEnabled] = useState(true);
  const [levels, setLevels] = useState([
    { level: 1, percentage: 10, enabled: true },
    { level: 2, percentage: 5, enabled: true },
    { level: 3, percentage: 2.5, enabled: true },
    { level: 4, percentage: 0, enabled: false },
    { level: 5, percentage: 0, enabled: false },
    { level: 6, percentage: 0, enabled: false },
    { level: 7, percentage: 0, enabled: false },
    { level: 8, percentage: 0, enabled: false },
    { level: 9, percentage: 0, enabled: false },
    { level: 10, percentage: 0, enabled: false },
  ]);

  const handleLevelChange = (index, field, value) => {
    const newLevels = [...levels];
    newLevels[index][field] = value;
    setLevels(newLevels);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post('/api/settings/mlm', { mlmEnabled, levels });
      toast.success('Paramètres MLM sauvegardés avec succès');
    } catch (error) {
      console.error('Error saving MLM settings:', error);
      toast.error('Erreur lors de la sauvegarde des paramètres');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="mlm-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres MLM</h1>
        <p className="text-gray-600 mt-2">Configurez le Multi-Level Marketing</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card title="Configuration MLM">
          <div className="space-y-6">
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div>
                <h3 className="font-semibold text-lg">Activer le MLM</h3>
                <p className="text-sm text-gray-600">Permettre le marketing multi-niveaux</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={mlmEnabled}
                  onChange={(e) => setMlmEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {mlmEnabled && (
              <div className="space-y-4">
                <h3 className="font-semibold text-lg">Niveaux de Commission</h3>
                {levels.map((level, index) => (
                  <div key={level.level} className="grid grid-cols-12 gap-4 items-center p-4 bg-gray-50 rounded-lg">
                    <div className="col-span-2">
                      <span className="font-semibold">Niveau {level.level}</span>
                    </div>
                    <div className="col-span-4">
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={level.enabled}
                          onChange={(e) => handleLevelChange(index, 'enabled', e.target.checked)}
                          className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                        />
                        <span className="text-sm">Activé</span>
                      </label>
                    </div>
                    <div className="col-span-6">
                      <div className="flex items-center space-x-2">
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="100"
                          value={level.percentage}
                          onChange={(e) => handleLevelChange(index, 'percentage', parseFloat(e.target.value))}
                          disabled={!level.enabled}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                        />
                        <span className="text-gray-600">%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-end">
              <Button type="submit" disabled={saving}>
                {saving ? 'Sauvegarde...' : 'Enregistrer les modifications'}
              </Button>
            </div>
          </div>
        </Card>
      </form>
    </div>
  );
};

export default MLMSettings;
