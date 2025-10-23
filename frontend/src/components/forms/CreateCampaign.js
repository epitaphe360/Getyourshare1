import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import { Target, Calendar, DollarSign, Tag, FileText, Package, Users, TrendingUp } from 'lucide-react';

const CreateCampaign = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'Mode',
    commission_type: 'percentage',
    commission_value: 10,
    start_date: '',
    end_date: '',
    budget: '',
    status: 'active',
    product_ids: [],
    briefing: {
      objectives: '',
      target_audience: '',
      key_messages: '',
      deadlines: '',
      visual_references: '',
      brand_limitations: '',
      hashtags: ''
    }
  });
  
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const categories = ['Mode', 'Beauté', 'Technologie', 'Sport', 'Alimentation', 'Maison', 'Autre'];

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/api/products');
      const productsData = Array.isArray(response.data) ? response.data : response.data.products || [];
      setProducts(productsData);
    } catch (err) {
      console.error('Error fetching products:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const campaignData = {
        ...formData,
        commission_value: parseFloat(formData.commission_value),
        budget: formData.budget ? parseFloat(formData.budget) : null
      };

      const response = await api.post('/api/campaigns', campaignData);
      
      if (onSuccess) onSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la création de la campagne');
      console.error('Error creating campaign:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleBriefingChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      briefing: { ...prev.briefing, [name]: value }
    }));
  };

  const handleProductToggle = (productId) => {
    setFormData(prev => ({
      ...prev,
      product_ids: prev.product_ids.includes(productId)
        ? prev.product_ids.filter(id => id !== productId)
        : [...prev.product_ids, productId]
    }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Target className="w-6 h-6 text-blue-600" />
            Créer une nouvelle campagne
          </h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Informations de base */}
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Informations de base
              </h3>
              
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom de la campagne *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Lancement Collection Été 2025"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Description détaillée de la campagne..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Catégorie *
                    </label>
                    <select
                      name="category"
                      value={formData.category}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {categories.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Statut
                    </label>
                    <select
                      name="status"
                      value={formData.status}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="active">Active</option>
                      <option value="paused">En pause</option>
                      <option value="ended">Terminée</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Commission */}
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Configuration des commissions
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Type de commission *
                  </label>
                  <select
                    name="commission_type"
                    value={formData.commission_type}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="percentage">Pourcentage (%)</option>
                    <option value="fixed">Montant fixe (€)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Valeur de commission *
                  </label>
                  <input
                    type="number"
                    name="commission_value"
                    value={formData.commission_value}
                    onChange={handleChange}
                    required
                    step="0.1"
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={formData.commission_type === 'percentage' ? '10' : '5.00'}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {formData.commission_type === 'percentage' ? 'Pourcentage du prix de vente' : 'Montant en euros par vente'}
                  </p>
                </div>
              </div>
            </div>

            {/* Dates et Budget */}
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Période et budget
              </h3>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date de début
                  </label>
                  <input
                    type="date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date de fin
                  </label>
                  <input
                    type="date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Budget (€)
                  </label>
                  <input
                    type="number"
                    name="budget"
                    value={formData.budget}
                    onChange={handleChange}
                    step="0.01"
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="5000.00"
                  />
                </div>
              </div>
            </div>

            {/* Sélection de produits */}
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Package className="w-5 h-5" />
                Produits de la campagne ({formData.product_ids.length} sélectionné{formData.product_ids.length > 1 ? 's' : ''})
              </h3>
              
              <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto border rounded-lg p-3">
                {products.length === 0 ? (
                  <p className="text-gray-500 col-span-2">Aucun produit disponible</p>
                ) : (
                  products.map(product => (
                    <label key={product.id} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.product_ids.includes(product.id)}
                        onChange={() => handleProductToggle(product.id)}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm">{product.name} - {product.price}€</span>
                    </label>
                  ))
                )}
              </div>
            </div>

            {/* Briefing détaillé */}
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Users className="w-5 h-5" />
                Briefing pour les influenceurs
              </h3>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Objectifs de la campagne
                  </label>
                  <textarea
                    name="objectives"
                    value={formData.briefing.objectives}
                    onChange={handleBriefingChange}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Augmenter les ventes de 30%, atteindre 10 000 nouveaux clients..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Audience cible
                  </label>
                  <input
                    type="text"
                    name="target_audience"
                    value={formData.briefing.target_audience}
                    onChange={handleBriefingChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Femmes 25-40 ans, intéressées par la mode durable..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Messages clés
                  </label>
                  <textarea
                    name="key_messages"
                    value={formData.briefing.key_messages}
                    onChange={handleBriefingChange}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Points importants à mettre en avant..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hashtags recommandés
                  </label>
                  <input
                    type="text"
                    name="hashtags"
                    value={formData.briefing.hashtags}
                    onChange={handleBriefingChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: #Mode2025 #StyleDurable #TechStyle"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Limitations de branding
                  </label>
                  <textarea
                    name="brand_limitations"
                    value={formData.briefing.brand_limitations}
                    onChange={handleBriefingChange}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Restrictions, guidelines à respecter..."
                  />
                </div>
              </div>
            </div>

            {/* Boutons */}
            <div className="flex gap-3 pt-4">
              <Button type="submit" disabled={loading}>
                {loading ? 'Création...' : '✨ Créer la campagne'}
              </Button>
              {onCancel && (
                <Button type="button" variant="secondary" onClick={onCancel}>
                  Annuler
                </Button>
              )}
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
};

export default CreateCampaign;
