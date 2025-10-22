import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatCurrency, formatDate } from '../../utils/helpers';
import { Check, X } from 'lucide-react';

const AffiliatePayouts = () => {
  const [payouts, setPayouts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPayouts();
  }, []);

  const fetchPayouts = async () => {
    try {
      const response = await api.get('/api/payouts');
      setPayouts(response.data.data);
    } catch (error) {
      console.error('Error fetching payouts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await api.put(`/api/payouts/${id}/status`, { status: 'approved' });
      fetchPayouts();
    } catch (error) {
      console.error('Error approving payout:', error);
    }
  };

  const handleReject = async (id) => {
    try {
      await api.put(`/api/payouts/${id}/status`, { status: 'rejected' });
      fetchPayouts();
    } catch (error) {
      console.error('Error rejecting payout:', error);
    }
  };

  const columns = [
    {
      header: 'Affilié',
      accessor: 'affiliate_name',
    },
    {
      header: 'Montant',
      accessor: 'amount',
      render: (row) => formatCurrency(row.amount),
    },
    {
      header: 'Méthode',
      accessor: 'method',
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Demandé le',
      accessor: 'requested_at',
      render: (row) => formatDate(row.requested_at),
    },
    {
      header: 'Traité le',
      accessor: 'processed_at',
      render: (row) => row.processed_at ? formatDate(row.processed_at) : '-',
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        row.status === 'pending' ? (
          <div className="flex space-x-2">
            <Button size="sm" variant="success" onClick={() => handleApprove(row.id)}>
              <Check size={16} />
            </Button>
            <Button size="sm" variant="danger" onClick={() => handleReject(row.id)}>
              <X size={16} />
            </Button>
          </div>
        ) : null
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="affiliate-payouts">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paiements Affiliés</h1>
        <p className="text-gray-600 mt-2">Gérez les demandes de paiement</p>
      </div>

      <Card>
        {loading ? (
          <div className="text-center py-8">Chargement...</div>
        ) : (
          <Table columns={columns} data={payouts} />
        )}
      </Card>
    </div>
  );
};

export default AffiliatePayouts;
