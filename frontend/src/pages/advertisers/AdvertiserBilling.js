import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatCurrency, formatDate } from '../../utils/helpers';
import { Plus, Download } from 'lucide-react';

const AdvertiserBilling = () => {
  const [invoices] = useState([
    {
      id: 'inv_1',
      advertiser: 'TechCorp',
      invoice_number: 'INV-2024-001',
      amount: 5000.00,
      status: 'paid',
      created_at: '2024-02-01T10:00:00Z',
      due_date: '2024-02-15T23:59:59Z',
    },
    {
      id: 'inv_2',
      advertiser: 'Sports Gear',
      invoice_number: 'INV-2024-002',
      amount: 3500.00,
      status: 'pending',
      created_at: '2024-03-01T10:00:00Z',
      due_date: '2024-03-15T23:59:59Z',
    },
  ]);

  const columns = [
    {
      header: 'N° Facture',
      accessor: 'invoice_number',
    },
    {
      header: 'Annonceur',
      accessor: 'advertiser',
    },
    {
      header: 'Montant',
      accessor: 'amount',
      render: (row) => formatCurrency(row.amount),
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Date de création',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
    {
      header: 'Échéance',
      accessor: 'due_date',
      render: (row) => formatDate(row.due_date),
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <Button size="sm" variant="outline">
          <Download size={16} />
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="advertiser-billing">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Facturation - Annonceurs</h1>
          <p className="text-gray-600 mt-2">Gérez les factures</p>
        </div>
        <Button>
          <Plus size={20} className="mr-2" />
          Nouvelle Facture
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={invoices} />
      </Card>
    </div>
  );
};

export default AdvertiserBilling;
