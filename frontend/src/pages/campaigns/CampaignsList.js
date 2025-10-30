import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../context/ToastContext';
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
  const toast = useToast();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionModal, setActionModal] = useState({ isOpen: false, campaign: null, action: null });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await api.get('/api/campaigns');
      setCampaigns(response.data.data || []);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (campaignId, newStatus) => {
    try {
      await api.put(`/api/campaigns/${campaignId}/status`, { status: newStatus });
      await fetchCampaigns();
      setActionModal({ isOpen: false, campaign: null, action: null });
      toast.success(`Campagne ${newStatus === 'active' ? 'activée' : newStatus === 'paused' ? 'mise en pause' : 'archivée'}`);
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error('Erreur lors de la mise à jour du statut');
    }
  };

  const filteredCampaigns = campaigns.filter(campaign =>
    campaign.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    campaign.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const columns = [
    {
      key: 'name',
      label: 'Campagne',
      render: (campaign) => (
        <div>
          <div className="font-medium text-gray-900">{campaign.name}</div>
          <div className="text-sm text-gray-500">{campaign.description}</div>
        </div>
      )
    },
    {
      key: 'category',
      label: 'Catégorie',
      accessor: 'category',
      render: (row) => row.category || 'Non défini'
    },
    {
      key: 'budget',
      label: 'Budget',
      render: (campaign) => formatCurrency(campaign.budget)
    },
    {
      key: 'commission_rate',
      label: 'Commission',
      render: (campaign) => `${campaign.commission_rate}%`
    },
    {
      key: 'influencers',
      label: 'Influenceurs',
      render: (campaign) => formatNumber(campaign.influencers_count || 0)
    },
    {
      key: 'status',
      label: 'Statut',
      render: (campaign) => (
        <Badge status={campaign.status}>
          {campaign.status === 'active' ? 'Active' :
           campaign.status === 'paused' ? 'Pausée' :
           campaign.status === 'ended' ? 'Terminée' : 'Brouillon'}
        </Badge>
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (campaign) => (
        <div className="flex gap-2">
          {campaign.status === 'active' && (
            <button
              onClick={() => setActionModal({ isOpen: true, campaign, action: 'pause' })}
              className="text-yellow-600 hover:text-yellow-700"
              title="Mettre en pause"
            >
              <Pause size={18} />
            </button>
          )}
          {campaign.status === 'paused' && (
            <button
              onClick={() => setActionModal({ isOpen: true, campaign, action: 'activate' })}
              className="text-green-600 hover:text-green-700"
              title="Activer"
            >
              <Play size={18} />
            </button>
          )}
          <button
            onClick={() => setActionModal({ isOpen: true, campaign, action: 'archive' })}
            className="text-gray-600 hover:text-gray-700"
            title="Archiver"
          >
            <Archive size={18} />
          </button>
        </div>
      )
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campagnes</h1>
          <p className="text-gray-600 mt-2">Gérez vos campagnes marketing</p>
        </div>
        <Button disabled={loading} onClick={() => navigate('/campaigns/create')} data-testid="create-campaign-btn">
          <Plus size={20} className="mr-2" />
          Nouvelle Campagne
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher une campagne..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              data-testid="search-input"
            />
          </div>
        </div>
      </Card>

      {/* Campaigns Table */}
      <Card>
        {loading ? (
          <div className="text-center py-8">Chargement...</div>
        ) : filteredCampaigns.length === 0 ? (
          <EmptyState
            icon={Target}
            title={searchTerm ? "Aucune campagne trouvée" : "Aucune campagne pour le moment"}
            description={searchTerm ? "Essayez avec d'autres mots-clés" : "Créez votre première campagne pour commencer à travailler avec des influenceurs"}
            actionLabel={!searchTerm ? "Créer une campagne" : null}
            onAction={() => navigate('/campaigns/create')}
          />
        ) : (
          <Table columns={columns} data={filteredCampaigns} />
        )}
      </Card>

      {/* Action Confirmation Modal */}
      <Modal
        isOpen={actionModal.isOpen}
        onClose={() => setActionModal({ isOpen: false, campaign: null, action: null })}
        title="Confirmer l'action"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            {actionModal.action === 'pause' && 'Voulez-vous mettre en pause cette campagne ?'}
            {actionModal.action === 'activate' && 'Voulez-vous activer cette campagne ?'}
            {actionModal.action === 'archive' && 'Voulez-vous archiver cette campagne ?'}
          </p>
          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => setActionModal({ isOpen: false, campaign: null, action: null })}
            >
              Annuler
            </Button>
            <Button
              onClick={() => handleUpdateStatus(
                actionModal.campaign?.id,
                actionModal.action === 'pause' ? 'paused' :
                actionModal.action === 'activate' ? 'active' : 'archived'
              )}
            >
              Confirmer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default CampaignsList;
