import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import EmptyState from '../../components/common/EmptyState';
import { formatCurrency, formatNumber } from '../../utils/helpers';
import { Plus, Search, MoreVertical, Pause, Play, Archive, Target } from 'lucide-react';

const CampaignsList = () => {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusModal, setStatusModal] = useState({ isOpen: false, campaign: null, newStatus: null });
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await api.get('/api/campaigns');
      // Gestion des deux formats de réponse possibles
      const campaignsData = Array.isArray(response.data) ? response.data : response.data.data || [];
      setCampaigns(campaignsData);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      setCampaigns([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async () => {
    if (!statusModal.campaign || !statusModal.newStatus) return;

    setUpdating(true);
    try {
      await api.put(`/api/campaigns/${statusModal.campaign.id}/status`, {
        status: statusModal.newStatus
      });
      
      // Rafraîchir la liste
      await fetchCampaigns();
      
      // Fermer le modal
      setStatusModal({ isOpen: false, campaign: null, newStatus: null });
    } catch (error) {
      console.error('Error updating campaign status:', error);
      alert('Erreur lors de la mise à jour du statut');
    } finally {
      setUpdating(false);
    }
  };

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'archived': return 'secondary';
      case 'draft': return 'info';
      default: return 'secondary';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'active': return 'Actif';
      case 'paused': return 'En pause';
      case 'archived': return 'Archivé';
      case 'draft': return 'Brouillon';
      default: return status;
    }
  };

  const filteredCampaigns = campaigns.filter(camp =>
    camp.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    camp.advertiser_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    camp.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const columns = [
    {
      header: 'Campagne',
      accessor: 'name',
      render: (row) => (
        <div>
          <div className="font-semibold">{row.name}</div>
          <div className="text-xs text-gray-500">{row.advertiser_name || 'Non défini'}</div>
        </div>
      ),
    },
    {
      header: 'Catégorie',
      accessor: 'category',
      render: (row) => row.category || 'Non défini'
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => (
        <Badge variant={getStatusBadgeVariant(row.status)}>
          {getStatusLabel(row.status)}
        </Badge>
      ),
    },
    {
      header: 'Commission',
      accessor: 'commission',
      render: (row) => (
        <span>
          {row.commission_type === 'percentage' 
            ? `${row.commission_value || 10}%` 
            : formatCurrency(row.commission_value || 0)}
        </span>
      ),
    },
    {
      header: 'Clics',
      accessor: 'clicks',
      render: (row) => formatNumber(row.clicks || 0),
    },
    {
      header: 'Conversions',
      accessor: 'conversions',
      render: (row) => formatNumber(row.conversions || 0),
    },
    {
      header: 'Revenus',
      accessor: 'revenue',
      render: (row) => formatCurrency(row.revenue || 0),
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <div className="flex gap-2">
          {row.status === 'active' && (
            <button
              onClick={() => setStatusModal({ isOpen: true, campaign: row, newStatus: 'paused' })}
              className="p-2 hover:bg-yellow-100 rounded transition text-yellow-600"
              title="Mettre en pause"
            >
              <Pause size={18} />
            </button>
          )}
          {row.status === 'paused' && (
            <button
              onClick={() => setStatusModal({ isOpen: true, campaign: row, newStatus: 'active' })}
              className="p-2 hover:bg-green-100 rounded transition text-green-600"
              title="Activer"
            >
              <Play size={18} />
            </button>
          )}
          {(row.status === 'active' || row.status === 'paused') && (
            <button
              onClick={() => setStatusModal({ isOpen: true, campaign: row, newStatus: 'archived' })}
              className="p-2 hover:bg-gray-100 rounded transition text-gray-600"
              title="Archiver"
            >
              <Archive size={18} />
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="campaigns-list">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campagnes & Offres</h1>
          <p className="text-gray-600 mt-2">Gérez vos campagnes</p>
        </div>
        <Button onClick={() => navigate('/campaigns/create')}>
          <Plus size={20} className="mr-2" />
          Nouvelle Campagne
        </Button>
      </div>

      <Card>
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher une campagne..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="search-input"
            />
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8">Chargement...</div>
        ) : (
          <Table columns={columns} data={filteredCampaigns} />
        )}
      </Card>

      {/* Status Change Confirmation Modal */}
      <Modal
        isOpen={statusModal.isOpen}
        onClose={() => setStatusModal({ isOpen: false, campaign: null, newStatus: null })}
        title="Modifier le statut de la campagne"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Voulez-vous vraiment {' '}
            {statusModal.newStatus === 'active' && <span className="font-semibold text-green-600">activer</span>}
            {statusModal.newStatus === 'paused' && <span className="font-semibold text-yellow-600">mettre en pause</span>}
            {statusModal.newStatus === 'archived' && <span className="font-semibold text-gray-600">archiver</span>}
            {' '} la campagne{' '}
            <span className="font-semibold">{statusModal.campaign?.name}</span> ?
          </p>
          
          {statusModal.newStatus === 'paused' && (
            <p className="text-sm text-gray-500">
              La campagne sera temporairement désactivée. Vous pourrez la réactiver à tout moment.
            </p>
          )}
          
          {statusModal.newStatus === 'archived' && (
            <p className="text-sm text-red-600">
              La campagne sera archivée et ne sera plus visible pour les influenceurs.
            </p>
          )}
          
          <div className="flex gap-3 justify-end mt-6">
            <Button
              variant="secondary"
              onClick={() => setStatusModal({ isOpen: false, campaign: null, newStatus: null })}
              disabled={updating}
            >
              Annuler
            </Button>
            <Button
              onClick={handleStatusChange}
              disabled={updating}
              variant={statusModal.newStatus === 'archived' ? 'danger' : 'primary'}
            >
              {updating ? 'Mise à jour...' : 'Confirmer'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default CampaignsList;
