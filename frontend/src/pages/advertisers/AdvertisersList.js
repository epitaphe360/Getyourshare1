import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatCurrency, formatDate } from '../../utils/helpers';
import { Plus, Search } from 'lucide-react';

const AdvertisersList = () => {
  const [advertisers, setAdvertisers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAdvertisers();
  }, []);

  const fetchAdvertisers = async () => {
    try {
      const response = await api.get('/api/advertisers');
      // Handle different response structures
      const data = response.data?.data || response.data || [];
      setAdvertisers(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching advertisers:', error);
      setAdvertisers([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const filteredAdvertisers = (advertisers || []).filter(adv =>
    adv?.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    adv?.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const columns = [
    {
      header: 'Entreprise',
      accessor: 'company_name',
      render: (row) => (
        <div>
          <div className="font-semibold">{row.company_name}</div>
          <div className="text-xs text-gray-500">{row.email}</div>
        </div>
      ),
    },
    {
      header: 'Pays',
      accessor: 'country',
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Campagnes',
      accessor: 'campaigns_count',
    },
    {
      header: 'Solde',
      accessor: 'balance',
      render: (row) => formatCurrency(row.balance),
    },
    {
      header: 'Total Dépensé',
      accessor: 'total_spent',
      render: (row) => formatCurrency(row.total_spent),
    },
    {
      header: 'Créé le',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
  ];

  return (
    <div className="space-y-6" data-testid="advertisers-list">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Annonceurs</h1>
          <p className="text-gray-600 mt-2">Gérez vos annonceurs</p>
        </div>
        <Button>
          <Plus size={20} className="mr-2" />
          Nouvel Annonceur
        </Button>
      </div>

      <Card>
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher un annonceur..."
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
          <Table columns={columns} data={filteredAdvertisers} />
        )}
      </Card>
    </div>
  );
};

export default AdvertisersList;
