import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatDate } from '../../utils/helpers';
import { Check, X } from 'lucide-react';

const AffiliateApplications = () => {
  const [applications] = useState([
    {
      id: 'app_1',
      first_name: 'Sophie',
      last_name: 'Laurent',
      email: 'sophie.laurent@example.com',
      country: 'FR',
      traffic_source: 'Instagram',
      website: 'https://sophiestyle.com',
      status: 'pending',
      created_at: '2024-03-20T16:45:00Z',
    },
    {
      id: 'app_2',
      first_name: 'Thomas',
      last_name: 'Moreau',
      email: 'thomas.moreau@example.com',
      country: 'FR',
      traffic_source: 'Blog',
      website: 'https://thomastech.blog',
      status: 'pending',
      created_at: '2024-03-22T10:30:00Z',
    },
  ]);

  const handleApprove = (id) => {
    console.log('Approve:', id);
  };

  const handleReject = (id) => {
    console.log('Reject:', id);
  };

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
      header: 'Site Web',
      accessor: 'website',
      render: (row) => (
        <a href={row.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm">
          {row.website}
        </a>
      ),
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
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="success" disabled={loading} onClick={() => handleApprove(row.id)}>
            <Check size={16} />
          </Button>
          <Button size="sm" variant="danger" disabled={loading} onClick={() => handleReject(row.id)}>
            <X size={16} />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="affiliate-applications">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Demandes d'Affiliation</h1>
        <p className="text-gray-600 mt-2">Approuvez ou rejetez les demandes</p>
      </div>

      <Card>
        <Table columns={columns} data={applications} />
      </Card>
    </div>
  );
};

export default AffiliateApplications;
