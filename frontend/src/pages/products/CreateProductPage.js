import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { ArrowLeft, Save, Upload, X, Image as ImageIcon } from 'lucide-react';

const CreateProductPage = () => {
  const navigate = useNavigate();
  const { productId } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const isEdit = !!productId;

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: '',
    commission_rate: '10',
    status: 'active',
    image_url: '',
    stock: '',
    sku: '',
    tags: ''
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isEdit) {
      fetchProduct();
    }
  }, [productId]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/products/${productId}`);
      const product = response.data;
      
      setFormData({
        name: product.name || '',
        description: product.description || '',
        price: product.price || '',
        category: product.category || '',
        commission_rate: product.commission_rate || '10',
        status: product.status || 'active',
        image_url: product.image_url || '',
        stock: product.stock || '',
        sku: product.sku || '',
        tags: product.tags ? product.tags.join(', ') : ''
      });
      
      if (product.image_url) {
        setImagePreview(product.image_url);
      }
    } catch (error) {
      console.error('Error fetching product:', error);
      alert('Erreur lors du chargement du produit');
      navigate('/products');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setErrors(prev => ({ ...prev, image: 'Image trop volumineuse (max 5MB)' }));
        return;
      }

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
        // In a real app, upload to storage and get URL
        // For now, we'll use the base64
        setFormData(prev => ({ ...prev, image_url: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImagePreview(null);
    setFormData(prev => ({ ...prev, image_url: '' }));
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Le nom est requis';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'La description est requise';
    }

    if (!formData.price || parseFloat(formData.price) <= 0) {
      newErrors.price = 'Le prix doit être supérieur à 0';
    }

    if (!formData.category.trim()) {
      newErrors.category = 'La catégorie est requise';
    }

    if (!formData.commission_rate || parseFloat(formData.commission_rate) < 0 || parseFloat(formData.commission_rate) > 100) {
      newErrors.commission_rate = 'La commission doit être entre 0 et 100%';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setSubmitting(true);
    try {
      // Prepare data
      const productData = {
        ...formData,
        price: parseFloat(formData.price),
        commission_rate: parseFloat(formData.commission_rate),
        stock: formData.stock ? parseInt(formData.stock) : null,
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(t => t) : [],
        merchant_id: user.id
      };

      if (isEdit) {
        await api.put(`/api/products/${productId}`, productData);
      } else {
        await api.post('/api/products', productData);
      }

      navigate('/products');
    } catch (error) {
      console.error('Error saving product:', error);
      alert(`Erreur lors de ${isEdit ? 'la modification' : 'la création'} du produit`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/products')}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft size={24} />
        </button>
        <div>
          <h1 className="text-3xl font-bold">
            {isEdit ? 'Modifier le produit' : 'Créer un produit'}
          </h1>
          <p className="text-gray-600 mt-1">
            {isEdit ? 'Modifiez les informations du produit' : 'Ajoutez un nouveau produit à votre catalogue'}
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <Card>
          <div className="space-y-6">
            {/* Image Upload */}
            <div>
              <label className="block text-sm font-medium mb-2">Image du produit</label>
              {imagePreview ? (
                <div className="relative inline-block">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-48 h-48 object-cover rounded-lg border"
                  />
                  <button
                    type="button"
                    onClick={removeImage}
                    className="absolute -top-2 -right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600 transition"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <label className="w-48 h-48 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-indigo-500 transition">
                  <ImageIcon size={48} className="text-gray-400 mb-2" />
                  <span className="text-sm text-gray-600">Cliquer pour uploader</span>
                  <span className="text-xs text-gray-400 mt-1">PNG, JPG (max 5MB)</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                  />
                </label>
              )}
              {errors.image && <p className="text-red-500 text-sm mt-1">{errors.image}</p>}
            </div>

            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-2">
                Nom du produit *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  errors.name ? 'border-red-500' : ''
                }`}
                placeholder="Ex: iPhone 15 Pro Max"
              />
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium mb-2">
                Description *
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  errors.description ? 'border-red-500' : ''
                }`}
                placeholder="Décrivez votre produit en détail..."
              />
              {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
            </div>

            {/* Price and Commission */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="price" className="block text-sm font-medium mb-2">
                  Prix (€) *
                </label>
                <input
                  type="number"
                  id="price"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  step="0.01"
                  min="0"
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    errors.price ? 'border-red-500' : ''
                  }`}
                  placeholder="99.99"
                />
                {errors.price && <p className="text-red-500 text-sm mt-1">{errors.price}</p>}
              </div>

              <div>
                <label htmlFor="commission_rate" className="block text-sm font-medium mb-2">
                  Commission (%) *
                </label>
                <input
                  type="number"
                  id="commission_rate"
                  name="commission_rate"
                  value={formData.commission_rate}
                  onChange={handleChange}
                  step="0.1"
                  min="0"
                  max="100"
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    errors.commission_rate ? 'border-red-500' : ''
                  }`}
                  placeholder="10"
                />
                {errors.commission_rate && <p className="text-red-500 text-sm mt-1">{errors.commission_rate}</p>}
              </div>
            </div>

            {/* Category and Status */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="category" className="block text-sm font-medium mb-2">
                  Catégorie *
                </label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    errors.category ? 'border-red-500' : ''
                  }`}
                >
                  <option value="">Sélectionner une catégorie</option>
                  <option value="Tech">Tech</option>
                  <option value="Mode">Mode</option>
                  <option value="Beauté">Beauté</option>
                  <option value="Sport">Sport</option>
                  <option value="Maison">Maison</option>
                  <option value="Alimentation">Alimentation</option>
                  <option value="Voyage">Voyage</option>
                  <option value="Autre">Autre</option>
                </select>
                {errors.category && <p className="text-red-500 text-sm mt-1">{errors.category}</p>}
              </div>

              <div>
                <label htmlFor="status" className="block text-sm font-medium mb-2">
                  Statut
                </label>
                <select
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="active">Actif</option>
                  <option value="inactive">Inactif</option>
                  <option value="out_of_stock">Rupture de stock</option>
                </select>
              </div>
            </div>

            {/* SKU and Stock */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="sku" className="block text-sm font-medium mb-2">
                  SKU (référence)
                </label>
                <input
                  type="text"
                  id="sku"
                  name="sku"
                  value={formData.sku}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="PROD-001"
                />
              </div>

              <div>
                <label htmlFor="stock" className="block text-sm font-medium mb-2">
                  Stock disponible
                </label>
                <input
                  type="number"
                  id="stock"
                  name="stock"
                  value={formData.stock}
                  onChange={handleChange}
                  min="0"
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="100"
                />
              </div>
            </div>

            {/* Tags */}
            <div>
              <label htmlFor="tags" className="block text-sm font-medium mb-2">
                Tags (séparés par des virgules)
              </label>
              <input
                type="text"
                id="tags"
                name="tags"
                value={formData.tags}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="nouveau, promo, populaire"
              />
              <p className="text-sm text-gray-500 mt-1">
                Les tags aident à organiser et rechercher vos produits
              </p>
            </div>
          </div>
        </Card>

        {/* Actions */}
        <div className="flex gap-4 justify-end mt-6">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/products')}
          >
            Annuler
          </Button>
          <Button type="submit" disabled={submitting}>
            <Save size={20} className="mr-2" />
            {submitting ? 'Enregistrement...' : isEdit ? 'Mettre à jour' : 'Créer le produit'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CreateProductPage;
