import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatCurrency, formatNumber } from '../../utils/helpers';
import { Plus, Search } from 'lucide-react';

const CampaignsList = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await api.get('/api/campaigns');
      setCampaigns(response.data.data);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCampaigns = campaigns.filter(camp =>
    camp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    camp.advertiser_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const columns = [
    {
      header: 'Campagne',
      accessor: 'name',
      render: (row) => (
        <div>
          <div className="font-semibold">{row.name}</div>
          <div className="text-xs text-gray-500">{row.advertiser_name}</div>
        </div>
      ),
    },
    {
      header: 'Catégorie',
      accessor: 'category',
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Commission',
      accessor: 'commission',
      render: (row) => (
        <span>
          {row.commission_type === 'percentage' ? `${row.commission_value}%` : formatCurrency(row.commission_value)}
        </span>
      ),
    },
    {
      header: 'Clics',
      accessor: 'clicks',
      render: (row) => formatNumber(row.clicks),
    },
    {
      header: 'Conversions',
      accessor: 'conversions',
      render: (row) => formatNumber(row.conversions),
    },
    {
      header: 'Revenus',
      accessor: 'revenue',
      render: (row) => formatCurrency(row.revenue),
    },
  ];

  return (
    <div className="space-y-6" data-testid="campaigns-list">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campagnes & Offres</h1>
          <p className="text-gray-600 mt-2">Gérez vos campagnes</p>
        </div>
        <Button>
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
    </div>
  );
};

export default CampaignsList;
