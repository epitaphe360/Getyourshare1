import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import InvitationModal from '../../components/modals/InvitationModal';
import { formatCurrency, formatNumber, formatDate } from '../../utils/helpers';
import { Plus, Search } from 'lucide-react';

const AffiliatesList = () => {
  const [affiliates, setAffiliates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showInviteModal, setShowInviteModal] = useState(false);

  useEffect(() => {
    fetchAffiliates();
  }, []);

  const fetchAffiliates = async () => {
    try {
      const response = await api.get('/api/affiliates');
      setAffiliates(response.data.data || []);
    } catch (error) {
      console.error('Error fetching affiliates:', error);
      setAffiliates([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredAffiliates = affiliates.filter(aff => {
    const search = searchTerm.toLowerCase();
    return (
      (aff.first_name?.toLowerCase().includes(search) || false) ||
      (aff.last_name?.toLowerCase().includes(search) || false) ||
      (aff.email?.toLowerCase().includes(search) || false)
    );
  });

  const columns = [
    {
      header: 'Affilié',
      accessor: 'name',
      render: (row) => (
        <div>
          <div className="font-semibold">{row.first_name} {row.last_name}</div>
          <div className="text-xs text-gray-500">{row.email}</div>
        </div>
      ),
    },
    {
      header: 'Pays',
      accessor: 'country',
    },
    {
      header: 'Source',
      accessor: 'traffic_source',
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
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
      header: 'Solde',
      accessor: 'balance',
      render: (row) => formatCurrency(row.balance),
    },
    {
      header: 'Total Gagné',
      accessor: 'total_earned',
      render: (row) => formatCurrency(row.total_earned),
    },
  ];

  return (
    <div className="space-y-6" data-testid="affiliates-list">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Affiliés</h1>
          <p className="text-gray-600 mt-2">Gérez vos affiliés</p>
        </div>
        <Button onClick={() => setShowInviteModal(true)}>
          <Plus size={20} className="mr-2" />
          Nouvel Affilié
        </Button>
      </div>

      {showInviteModal && (
        <InvitationModal
          onClose={() => setShowInviteModal(false)}
          onSent={() => {
            setShowInviteModal(false);
            fetchAffiliates();
            // Optionally show toast from parent if available
          }}
        />
      )}

      <Card>
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher un affilié..."
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
          <Table columns={columns} data={filteredAffiliates} />
        )}
      </Card>
    </div>
  );
};

export default AffiliatesList;
