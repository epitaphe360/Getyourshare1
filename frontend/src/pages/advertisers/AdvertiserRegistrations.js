import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatDate } from '../../utils/helpers';
import { Check, X } from 'lucide-react';

const AdvertiserRegistrations = () => {
  const [registrations] = useState([
    {
      id: 'reg_1',
      company_name: 'Fashion Boutique',
      email: 'hello@fashionboutique.com',
      country: 'FR',
      status: 'pending',
      created_at: '2024-03-10T14:20:00Z',
    },
    {
      id: 'reg_2',
      company_name: 'Tech Solutions',
      email: 'info@techsolutions.com',
      country: 'US',
      status: 'pending',
      created_at: '2024-03-12T09:30:00Z',
    },
  ]);
  
  const [loading, setLoading] = useState(false);

  const handleApprove = (id) => {
    console.log('Approve:', id);
    // API call to approve
  };

  const handleReject = (id) => {
    console.log('Reject:', id);
    // API call to reject
  };

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
      header: 'Date de demande',
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
    <div className="space-y-6" data-testid="advertiser-registrations">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Demandes d'Inscription - Annonceurs</h1>
        <p className="text-gray-600 mt-2">Approuvez ou rejetez les demandes</p>
      </div>

      <Card>
        <Table columns={columns} data={registrations} />
      </Card>
    </div>
  );
};

export default AdvertiserRegistrations;
