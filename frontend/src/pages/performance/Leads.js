import React from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import { formatDate } from '../../utils/helpers';

const Leads = () => {
  const mockLeads = [
    {
      id: 'lead_1',
      email: 'john.doe@example.com',
      campaign: 'Summer Sale',
      affiliate: 'Marie Dupont',
      status: 'qualified',
      created_at: '2024-03-20T10:30:00Z',
    },
    {
      id: 'lead_2',
      email: 'jane.smith@example.com',
      campaign: 'Black Friday',
      affiliate: 'Pierre Martin',
      status: 'pending',
      created_at: '2024-03-21T14:15:00Z',
    },
  ];

  const columns = [
    {
      header: 'ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-sm">{row.id}</span>,
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
    <div className="space-y-6" data-testid="leads">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Leads</h1>
        <p className="text-gray-600 mt-2">Statistiques des leads générés</p>
      </div>

      <Card>
        <Table columns={columns} data={mockLeads} />
      </Card>
    </div>
  );
};

export default Leads;
