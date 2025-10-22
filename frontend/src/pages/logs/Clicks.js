import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { formatDate } from '../../utils/helpers';

const Clicks = () => {
  const [clicks, setClicks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClicks();
  }, []);

  const fetchClicks = async () => {
    try {
      const response = await api.get('/api/clicks');
      setClicks(response.data.data);
    } catch (error) {
      console.error('Error fetching clicks:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      header: 'ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-sm">{row.id}</span>,
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
      header: 'IP',
      accessor: 'ip',
      render: (row) => <span className="font-mono text-sm">{row.ip}</span>,
    },
    {
      header: 'Pays',
      accessor: 'country',
    },
    {
      header: 'Appareil',
      accessor: 'device',
    },
    {
      header: 'Navigateur',
      accessor: 'browser',
    },
    {
      header: 'Date',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
  ];

  return (
    <div className="space-y-6" data-testid="clicks-log">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Logs de Clics</h1>
        <p className="text-gray-600 mt-2">Détails de tous les clics</p>
      </div>

      <Card>
        {loading ? (
          <div className="text-center py-8">Chargement...</div>
        ) : (
          <Table columns={columns} data={clicks} />
        )}
      </Card>
    </div>
  );
};

export default Clicks;
