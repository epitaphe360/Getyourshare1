import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import { Plus, Edit, Trash2 } from 'lucide-react';

const TrafficSources = () => {
  const [sources, setSources] = useState([
    { id: 1, name: 'Facebook', status: 'active' },
    { id: 2, name: 'Google', status: 'active' },
    { id: 3, name: 'Instagram', status: 'active' },
    { id: 4, name: 'Blog', status: 'active' },
    { id: 5, name: 'Email', status: 'active' },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newSource, setNewSource] = useState('');

  const handleAdd = () => {
    if (newSource.trim()) {
      setSources([...sources, { id: sources.length + 1, name: newSource, status: 'active' }]);
      setNewSource('');
      setIsModalOpen(false);
    }
  };

  const columns = [
    {
      header: 'Nom',
      accessor: 'name',
      render: (row) => <span className="font-semibold">{row.name}</span>,
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => (
        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
          {row.status}
        </span>
      ),
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="outline">
            <Edit size={16} />
          </Button>
          <Button size="sm" variant="danger">
            <Trash2 size={16} />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="traffic-sources">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sources de Trafic</h1>
          <p className="text-gray-600 mt-2">Gérez les sources de trafic disponibles</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus size={20} className="mr-2" />
          Nouvelle Source
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={sources} />
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Ajouter une Source de Trafic"
        size="sm"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom de la source
            </label>
            <input
              type="text"
              value={newSource}
              onChange={(e) => setNewSource(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: TikTok, YouTube, etc."
            />
          </div>
          <div className="flex justify-end space-x-2">
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleAdd}>
              Ajouter
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TrafficSources;
