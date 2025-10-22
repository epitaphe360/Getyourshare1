import React from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import { formatDate } from '../../utils/helpers';

const Webhooks = () => {
  const mockWebhooks = [
    {
      id: 'webhook_1',
      event: 'conversion.created',
      url: 'https://api.example.com/webhook',
      status: 'success',
      response_code: 200,
      created_at: '2024-03-20T10:30:00Z',
    },
    {
      id: 'webhook_2',
      event: 'affiliate.approved',
      url: 'https://api.example.com/webhook',
      status: 'success',
      response_code: 200,
      created_at: '2024-03-20T09:15:00Z',
    },
  ];

  const columns = [
    {
      header: 'ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-sm">{row.id}</span>,
    },
    {
      header: 'Événement',
      accessor: 'event',
      render: (row) => <span className="font-mono text-sm">{row.event}</span>,
    },
    {
      header: 'URL',
      accessor: 'url',
      render: (row) => <span className="text-sm truncate max-w-xs block">{row.url}</span>,
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Code',
      accessor: 'response_code',
      render: (row) => <span className="font-mono">{row.response_code}</span>,
    },
    {
      header: 'Date',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
  ];

  return (
    <div className="space-y-6" data-testid="webhooks-log">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Logs Webhooks</h1>
        <p className="text-gray-600 mt-2">Historique des webhooks envoyés</p>
      </div>

      <Card>
        <Table columns={columns} data={mockWebhooks} />
      </Card>
    </div>
  );
};

export default Webhooks;
