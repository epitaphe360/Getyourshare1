import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import { formatCurrency, formatDate } from '../../utils/helpers';
import { Download } from 'lucide-react';
import Button from '../../components/common/Button';

const Conversions = () => {
  const [conversions, setConversions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConversions();
  }, []);

  const fetchConversions = async () => {
    try {
      const response = await api.get('/api/conversions');
      setConversions(response.data.data);
    } catch (error) {
      console.error('Error fetching conversions:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      header: 'ID Commande',
      accessor: 'order_id',
      render: (row) => <span className="font-mono text-sm">{row.order_id}</span>,
    },
    {
      header: 'Campagne',
      accessor: 'campaign_id',
    },
    {
      header: 'Affilié',
      accessor: 'affiliate_id',
    },
    {
      header: 'Montant',
      accessor: 'amount',
      render: (row) => formatCurrency(row.amount),
    },
    {
      header: 'Commission',
      accessor: 'commission',
      render: (row) => formatCurrency(row.commission),
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Date',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
  ];

  return (
    <div className="space-y-6" data-testid="conversions">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Conversions</h1>
          <p className="text-gray-600 mt-2">Suivez toutes vos conversions</p>
        </div>
        <Button variant="outline">
          <Download size={20} className="mr-2" />
          Exporter
        </Button>
      </div>

      <Card>
        {loading ? (
          <div className="text-center py-8">Chargement...</div>
        ) : (
          <Table columns={columns} data={conversions} />
        )}
      </Card>
    </div>
  );
};

export default Conversions;
