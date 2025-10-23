import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import { formatDate, formatCurrency } from '../../utils/helpers';
import api from '../../utils/api';

const Leads = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await api.get('/api/leads');
      setLeads(response.data.data || []);
    } catch (error) {
      console.error('Error fetching leads:', error);
      setLeads([]);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      header: 'ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-sm">{row.id.substring(0, 8)}...</span>,
    },
    {
      header: 'Email',
      accessor: 'email',
    },
    {
      header: 'Campagne',
      accessor: 'campaign',
    },
    {
      header: 'Affilié',
      accessor: 'affiliate',
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl">Chargement des leads...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="leads">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Leads</h1>
        <p className="text-gray-600 mt-2">
          Statistiques des leads générés ({leads.length} lead{leads.length !== 1 ? 's' : ''})
        </p>
      </div>

      <Card>
        {leads.length > 0 ? (
          <Table columns={columns} data={leads} />
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Aucun lead en attente</p>
            <p className="text-gray-400 text-sm mt-2">Les ventes en statut "pending" apparaîtront ici</p>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Leads;
