import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import api from '../../utils/api';

const MLMSettings = () => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
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

  useEffect(() => {
    loadMLMSettings();
  }, []);

  const loadMLMSettings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/settings/mlm');
      if (response.data) {
        setMlmEnabled(response.data.mlm_enabled ?? true);
        if (response.data.levels && response.data.levels.length > 0) {
          setLevels(response.data.levels);
        }
      }
    } catch (error) {
      console.error('Erreur chargement MLM settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLevelChange = (index, field, value) => {
    const newLevels = [...levels];
    newLevels[index][field] = value;
    setLevels(newLevels);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      await api.put('/api/settings/mlm', { mlm_enabled: mlmEnabled, levels });
      setMessage({ type: 'success', text: '✅ Paramètres MLM enregistrés avec succès !' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      console.error('Erreur sauvegarde MLM settings:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || '❌ Erreur lors de l\'enregistrement' 
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="mlm-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres MLM</h1>
        <p className="text-gray-600 mt-2">Configurez le Multi-Level Marketing</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

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
                {saving ? 'Enregistrement...' : 'Enregistrer les modifications'}
              </Button>
            </div>
          </div>
        </Card>
      </form>
    </div>
  );
};

export default MLMSettings;
