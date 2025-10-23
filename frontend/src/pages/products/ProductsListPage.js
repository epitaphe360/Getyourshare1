import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Table from '../../components/common/Table';
import Modal from '../../components/common/Modal';
import Badge from '../../components/common/Badge';
import {
  Package, Plus, Edit, Trash2, Search, Eye, TrendingUp,
  DollarSign, Archive
} from 'lucide-react';

const ProductsListPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, product: null });
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    totalValue: 0
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/products');
      const productsData = response.data.products || [];
      setProducts(productsData);
      
      // Calculer statistiques
      const total = productsData.length;
      const active = productsData.filter(p => p.status === 'active').length;
      const totalValue = productsData.reduce((sum, p) => sum + (parseFloat(p.price) || 0), 0);
      
      setStats({ total, active, totalValue });
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (productId) => {
    try {
      await api.delete(`/api/products/${productId}`);
      setDeleteModal({ isOpen: false, product: null });
      await fetchProducts();
    } catch (error) {
      console.error('Error deleting product:', error);
      alert('Erreur lors de la suppression du produit');
    }
  };

  const filteredProducts = products.filter(product =>
    product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const columns = [
    {
      key: 'name',
      label: 'Produit',
      render: (product) => (
        <div className="flex items-center gap-3">
          {product.image_url ? (
            <img 
              src={product.image_url} 
              alt={product.name}
              className="w-12 h-12 rounded object-cover"
            />
          ) : (
            <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
              <Package size={24} className="text-gray-400" />
            </div>
          )}
          <div>
            <div className="font-semibold">{product.name}</div>
            <div className="text-sm text-gray-500">{product.category || 'Non catégorisé'}</div>
          </div>
        </div>
      )
    },
    {
      key: 'description',
      label: 'Description',
      render: (product) => (
        <div className="max-w-md">
          <p className="text-sm text-gray-600 truncate">{product.description}</p>
        </div>
      )
    },
    {
      key: 'price',
      label: 'Prix',
      render: (product) => (
        <div className="font-semibold text-lg">
          {parseFloat(product.price).toFixed(2)} €
        </div>
      )
    },
    {
      key: 'commission_rate',
      label: 'Commission',
      render: (product) => (
        <Badge variant="success">
          {product.commission_rate}%
        </Badge>
      )
    },
    {
      key: 'status',
      label: 'Statut',
      render: (product) => (
        <Badge variant={product.status === 'active' ? 'success' : 'secondary'}>
          {product.status === 'active' ? 'Actif' : 'Inactif'}
        </Badge>
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (product) => (
        <div className="flex gap-2">
          <button
            onClick={() => navigate(`/products/${product.id}/view`)}
            className="p-2 hover:bg-gray-100 rounded transition"
            title="Voir détails"
          >
            <Eye size={18} className="text-gray-600" />
          </button>
          <button
            onClick={() => navigate(`/products/${product.id}/edit`)}
            className="p-2 hover:bg-gray-100 rounded transition"
            title="Modifier"
          >
            <Edit size={18} className="text-blue-600" />
          </button>
          <button
            onClick={() => setDeleteModal({ isOpen: true, product })}
            className="p-2 hover:bg-gray-100 rounded transition"
            title="Supprimer"
          >
            <Trash2 size={18} className="text-red-600" />
          </button>
        </div>
      )
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl">Chargement des produits...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Produits</h1>
          <p className="text-gray-600 mt-1">Gérez votre catalogue de produits</p>
        </div>
        <Button onClick={() => navigate('/products/create')}>
          <Plus size={20} className="mr-2" />
          Ajouter un produit
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Produits</p>
              <p className="text-3xl font-bold mt-2">{stats.total}</p>
            </div>
            <div className="bg-indigo-100 p-4 rounded-lg">
              <Package size={32} className="text-indigo-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Produits Actifs</p>
              <p className="text-3xl font-bold mt-2">{stats.active}</p>
            </div>
            <div className="bg-green-100 p-4 rounded-lg">
              <TrendingUp size={32} className="text-green-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Valeur Catalogue</p>
              <p className="text-3xl font-bold mt-2">{stats.totalValue.toFixed(2)} €</p>
            </div>
            <div className="bg-blue-100 p-4 rounded-lg">
              <DollarSign size={32} className="text-blue-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher par nom, description, catégorie..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </Card>

      {/* Products Table */}
      <Card>
        {filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <Package size={64} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-xl font-semibold mb-2">
              {searchTerm ? 'Aucun produit trouvé' : 'Aucun produit'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchTerm 
                ? 'Essayez de modifier vos critères de recherche'
                : 'Commencez par ajouter votre premier produit'
              }
            </p>
            {!searchTerm && (
              <Button onClick={() => navigate('/products/create')}>
                <Plus size={20} className="mr-2" />
                Créer un produit
              </Button>
            )}
          </div>
        ) : (
          <Table columns={columns} data={filteredProducts} />
        )}
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, product: null })}
        title="Supprimer le produit"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Êtes-vous sûr de vouloir supprimer le produit{' '}
            <span className="font-semibold">{deleteModal.product?.name}</span> ?
          </p>
          <p className="text-sm text-red-600">
            Cette action est irréversible et supprimera également toutes les données associées.
          </p>
          <div className="flex gap-3 justify-end mt-6">
            <Button
              variant="secondary"
              onClick={() => setDeleteModal({ isOpen: false, product: null })}
            >
              Annuler
            </Button>
            <Button
              variant="danger"
              onClick={() => handleDelete(deleteModal.product?.id)}
            >
              <Trash2 size={18} className="mr-2" />
              Supprimer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ProductsListPage;
