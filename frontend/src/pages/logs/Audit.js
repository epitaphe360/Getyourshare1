import React from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import { formatDate } from '../../utils/helpers';

const Audit = () => {
  const mockAuditLogs = [
    {
      id: 'audit_1',
      user: 'Admin Manager',
      action: 'Approved Affiliate',
      entity: 'affiliate_3',
      ip: '192.168.1.100',
      created_at: '2024-03-20T10:30:00Z',
    },
    {
      id: 'audit_2',
      user: 'Admin Manager',
      action: 'Created Campaign',
      entity: 'campaign_5',
      ip: '192.168.1.100',
      created_at: '2024-03-20T09:15:00Z',
    },
    {
      id: 'audit_3',
      user: 'John Advertiser',
      action: 'Updated Settings',
      entity: 'settings',
      ip: '192.168.1.105',
      created_at: '2024-03-19T16:45:00Z',
    },
  ];

  const columns = [
    {
      header: 'Utilisateur',
      accessor: 'user',
    },
    {
      header: 'Action',
      accessor: 'action',
      render: (row) => <Badge status="active">{row.action}</Badge>,
    },
    {
      header: 'Entité',
      accessor: 'entity',
      render: (row) => <span className="font-mono text-sm">{row.entity}</span>,
    },
    {
      header: 'IP',
      accessor: 'ip',
      render: (row) => <span className="font-mono text-sm">{row.ip}</span>,
    },
    {
      header: 'Date',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
  ];

  return (
    <div className="space-y-6" data-testid="audit-log">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Logs d'Audit</h1>
        <p className="text-gray-600 mt-2">Historique des actions utilisateurs</p>
      </div>

      <Card>
        <Table columns={columns} data={mockAuditLogs} />
      </Card>
    </div>
  );
};

export default Audit;
