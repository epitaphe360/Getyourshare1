import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { Plus } from 'lucide-react';

const Users = () => {
  const [users] = useState([
    {
      id: 'user_1',
      name: 'Admin Manager',
      email: 'admin@tracknow.io',
      country: 'FR',
      role: 'Manager',
      status: 'active',
      phone: '+33612345678',
    },
    {
      id: 'user_2',
      name: 'Support Team',
      email: 'support@tracknow.io',
      country: 'FR',
      role: 'Manager',
      status: 'active',
      phone: '+33687654321',
    },
  ]);

  const columns = [
    {
      header: 'Nom',
      accessor: 'name',
      render: (row) => (
        <div>
          <div className="font-semibold">{row.name}</div>
          <div className="text-xs text-gray-500">{row.email}</div>
        </div>
      ),
    },
    {
      header: 'Pays',
      accessor: 'country',
    },
    {
      header: 'Rôle',
      accessor: 'role',
    },
    {
      header: 'Téléphone',
      accessor: 'phone',
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <Button size="sm" variant="outline">
          Modifier
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="users-settings">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Utilisateurs</h1>
          <p className="text-gray-600 mt-2">Gérez les utilisateurs managers</p>
        </div>
        <Button>
          <Plus size={20} className="mr-2" />
          Nouvel Utilisateur
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={users} />
      </Card>
    </div>
  );
};

export default Users;
