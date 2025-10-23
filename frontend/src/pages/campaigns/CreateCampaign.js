import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import FileUpload from '../../components/common/FileUpload';
import { Target, Calendar, DollarSign, Tag, FileText, Package, Users, TrendingUp, Upload } from 'lucide-react';

const CreateCampaign = () => {
  const navigate = useNavigate();
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
  const [uploadedFiles, setUploadedFiles] = useState([]);
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
      // Préparer les données
      const campaignData = {
        ...formData,
        commission_value: parseFloat(formData.commission_value),
        budget: formData.budget ? parseFloat(formData.budget) : null,
        uploaded_files: uploadedFiles
      };

      const response = await api.post('/api/campaigns', campaignData);
      
      if (response.data) {
        alert('Campagne créée avec succès !');
        navigate('/campaigns');
      }
    } catch (err) {
      console.error('Error creating campaign:', err);
      setError(err.response?.data?.detail || 'Erreur lors de la création de la campagne');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBriefingChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      briefing: {
        ...prev.briefing,
        [name]: value
      }
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
    <div className="max-w-5xl mx-auto space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Créer une Campagne</h1>
          <p className="text-gray-600 mt-2">Configurez votre nouvelle campagne d'affiliation</p>
        </div>
        <Button
          onClick={() => navigate('/campaigns')}
          variant="secondary"
        >
          Annuler
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Section 1: Informations de Base */}
        <Card title="📝 Informations de Base" icon={<FileText size={20} />}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom de la campagne *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Ex: Lancement Collection Automne 2025"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Décrivez votre campagne, ses objectifs et ce que vous attendez des influenceurs..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Catégorie *
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>
        </Card>

        {/* Section 2: Commission */}
        <Card title="💰 Configuration de Commission" icon={<DollarSign size={20} />}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Type de commission *
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="commission_type"
                    value="percentage"
                    checked={formData.commission_type === 'percentage'}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  <span>Pourcentage (%)</span>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="commission_type"
                    value="fixed"
                    checked={formData.commission_type === 'fixed'}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  <span>Montant Fixe (€)</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {formData.commission_type === 'percentage' ? 'Taux de commission (%)' : 'Montant fixe (€)'}
              </label>
              <input
                type="number"
                name="commission_value"
                value={formData.commission_value}
                onChange={handleInputChange}
                required
                min="0"
                step={formData.commission_type === 'percentage' ? '0.1' : '0.01'}
                max={formData.commission_type === 'percentage' ? '100' : undefined}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder={formData.commission_type === 'percentage' ? '10' : '15.00'}
              />
              <p className="text-sm text-gray-500 mt-1">
                {formData.commission_type === 'percentage' 
                  ? 'Pourcentage du prix de vente reversé à l\'influenceur'
                  : 'Montant fixe versé par vente réalisée'}
              </p>
            </div>
          </div>
        </Card>

        {/* Section 3: Dates et Budget */}
        <Card title="📅 Dates et Budget" icon={<Calendar size={20} />}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date de début *
              </label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
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
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Budget total (€)
              </label>
              <input
                type="number"
                name="budget"
                value={formData.budget}
                onChange={handleInputChange}
                min="0"
                step="0.01"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Budget alloué à cette campagne (optionnel)"
              />
            </div>
          </div>
        </Card>

        {/* Section 4: Sélection de Produits */}
        <Card title="📦 Produits à Promouvoir" icon={<Package size={20} />}>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Sélectionnez les produits que vous souhaitez inclure dans cette campagne
            </p>
            
            {products.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Package className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>Aucun produit disponible</p>
                <Button
                  type="button"
                  onClick={() => navigate('/products/new')}
                  className="mt-4"
                  variant="secondary"
                >
                  Créer un Produit
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
                {products.map(product => (
                  <label
                    key={product.id}
                    className={`flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition ${
                      formData.product_ids.includes(product.id)
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-indigo-300'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={formData.product_ids.includes(product.id)}
                      onChange={() => handleProductToggle(product.id)}
                      className="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 truncate">
                        {product.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {product.price} € • {product.category}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            )}
            
            {formData.product_ids.length > 0 && (
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
                <p className="text-sm text-indigo-800">
                  ✓ {formData.product_ids.length} produit(s) sélectionné(s)
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Section 5: Briefing Détaillé */}
        <Card title="📋 Briefing Détaillé" icon={<Target size={20} />}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Objectifs de la campagne
              </label>
              <textarea
                name="objectives"
                value={formData.briefing.objectives}
                onChange={handleBriefingChange}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Ex: Générer 1000 ventes, augmenter la notoriété de la marque..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Audience cible
              </label>
              <textarea
                name="target_audience"
                value={formData.briefing.target_audience}
                onChange={handleBriefingChange}
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Ex: Femmes 25-35 ans intéressées par la mode durable..."
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
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Points importants à communiquer..."
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="#votreMarque #campagne2025"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Limitations de la marque
              </label>
              <textarea
                name="brand_limitations"
                value={formData.briefing.brand_limitations}
                onChange={handleBriefingChange}
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Ex: Ne pas associer à la concurrence, éviter certains sujets..."
              />
            </div>
          </div>
        </Card>

        {/* Section 6: Upload de Matériel Promotionnel */}
        <Card title="📎 Matériel Promotionnel" icon={<Upload size={20} />}>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Uploadez des logos, bannières, images produits, kits de presse, etc.
            </p>
            
            <FileUpload
              onUploadComplete={(urls) => {
                setUploadedFiles([...uploadedFiles, ...urls]);
                console.log('Fichiers uploadés:', urls);
              }}
              accept="image/*,.pdf,.zip"
              maxFiles={10}
              maxSize={10 * 1024 * 1024}
            />

            {uploadedFiles.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Fichiers uploadés ({uploadedFiles.length}):
                </p>
                <div className="space-y-2">
                  {uploadedFiles.map((file, idx) => (
                    <div key={idx} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <Upload className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-700">
                          {file.name || file.url || `Fichier ${idx + 1}`}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setUploadedFiles(uploadedFiles.filter((_, i) => i !== idx))}
                        className="text-red-600 hover:text-red-800 text-sm font-medium"
                      >
                        Supprimer
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Boutons d'action */}
        <div className="flex justify-end space-x-4 pt-6">
          <Button
            type="button"
            onClick={() => navigate('/campaigns')}
            variant="secondary"
            disabled={loading}
          >
            Annuler
          </Button>
          <Button
            type="submit"
            disabled={loading || formData.product_ids.length === 0}
          >
            {loading ? 'Création en cours...' : 'Créer la Campagne'}
          </Button>
        </div>

        {formData.product_ids.length === 0 && (
          <p className="text-sm text-amber-600 text-center">
            ⚠️ Veuillez sélectionner au moins un produit pour créer la campagne
          </p>
        )}
      </form>
    </div>
  );
};

export default CreateCampaign;
