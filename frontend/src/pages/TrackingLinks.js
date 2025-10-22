import React, { useState } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Table from '../components/common/Table';
import Modal from '../components/common/Modal';
import { Plus, Copy, Link as LinkIcon, ExternalLink } from 'lucide-react';

const TrackingLinks = () => {
  const [links, setLinks] = useState([
    {
      id: 'link_1',
      name: 'Campagne Été 2024',
      campaign: 'Summer Sale 2024',
      affiliate: 'Marie Dupont',
      full_link: 'https://tracknow.io/track/abc123def456',
      short_link: 'https://trk.io/abc123',
      clicks: 1250,
      conversions: 45,
      created_at: '2024-03-01T10:00:00Z',
    },
    {
      id: 'link_2',
      name: 'Promo Black Friday',
      campaign: 'Black Friday Deals',
      affiliate: 'Pierre Martin',
      full_link: 'https://tracknow.io/track/xyz789ghi012',
      short_link: 'https://trk.io/xyz789',
      clicks: 3420,
      conversions: 128,
      created_at: '2024-02-15T14:30:00Z',
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newLink, setNewLink] = useState({
    name: '',
    campaign_id: '',
    affiliate_id: '',
    destination_url: '',
  });

  const handleCopy = (link) => {
    navigator.clipboard.writeText(link);
    alert('Lien copié dans le presse-papier!');
  };

  const handleGenerate = () => {
    const randomId = Math.random().toString(36).substring(7);
    const newTracking = {
      id: `link_${links.length + 1}`,
      name: newLink.name,
      campaign: 'Selected Campaign',
      affiliate: 'Selected Affiliate',
      full_link: `https://tracknow.io/track/${randomId}${randomId}`,
      short_link: `https://trk.io/${randomId}`,
      clicks: 0,
      conversions: 0,
      created_at: new Date().toISOString(),
    };
    setLinks([newTracking, ...links]);
    setIsModalOpen(false);
    setNewLink({ name: '', campaign_id: '', affiliate_id: '', destination_url: '' });
  };

  const columns = [
    {
      header: 'Nom',
      accessor: 'name',
      render: (row) => (
        <div>
          <div className="font-semibold">{row.name}</div>
          <div className="text-xs text-gray-500">{row.campaign}</div>
        </div>
      ),
    },
    {
      header: 'Affilié',
      accessor: 'affiliate',
    },
    {
      header: 'Lien Court',
      accessor: 'short_link',
      render: (row) => (
        <div className="flex items-center space-x-2">
          <a href={row.short_link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm font-mono">
            {row.short_link}
          </a>
          <button onClick={() => handleCopy(row.short_link)} className="text-gray-400 hover:text-gray-600">
            <Copy size={16} />
          </button>
        </div>
      ),
    },
    {
      header: 'Clics',
      accessor: 'clicks',
    },
    {
      header: 'Conversions',
      accessor: 'conversions',
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="outline" onClick={() => handleCopy(row.full_link)}>
            <Copy size={16} />
          </Button>
          <Button size="sm" variant="outline">
            <ExternalLink size={16} />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="tracking-links">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Liens de Tracking</h1>
          <p className="text-gray-600 mt-2">Générez et gérez vos liens de suivi</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus size={20} className="mr-2" />
          Générer un Lien
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Liens Actifs</p>
              <p className="text-3xl font-bold text-blue-600">{links.length}</p>
            </div>
            <LinkIcon className="text-blue-600" size={32} />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Clics</p>
              <p className="text-3xl font-bold text-green-600">{links.reduce((sum, l) => sum + l.clicks, 0)}</p>
            </div>
            <ExternalLink className="text-green-600" size={32} />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Conversions</p>
              <p className="text-3xl font-bold text-purple-600">{links.reduce((sum, l) => sum + l.conversions, 0)}</p>
            </div>
            <LinkIcon className="text-purple-600" size={32} />
          </div>
        </Card>
      </div>

      {/* Links Table */}
      <Card>
        <Table columns={columns} data={links} />
      </Card>

      {/* Generate Link Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Générer un Lien de Tracking"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom du lien
            </label>
            <input
              type="text"
              value={newLink.name}
              onChange={(e) => setNewLink({ ...newLink, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: Campagne Printemps 2024"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Campagne
            </label>
            <select
              value={newLink.campaign_id}
              onChange={(e) => setNewLink({ ...newLink, campaign_id: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sélectionnez une campagne</option>
              <option value="camp_1">Summer Sale 2024</option>
              <option value="camp_2">Black Friday Deals</option>
              <option value="camp_3">Spring Fashion</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Affilié
            </label>
            <select
              value={newLink.affiliate_id}
              onChange={(e) => setNewLink({ ...newLink, affiliate_id: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sélectionnez un affilié</option>
              <option value="aff_1">Marie Dupont</option>
              <option value="aff_2">Pierre Martin</option>
              <option value="aff_4">Lucas Bernard</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              URL de destination
            </label>
            <input
              type="url"
              value={newLink.destination_url}
              onChange={(e) => setNewLink({ ...newLink, destination_url: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://example.com/product"
            />
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> Le lien de tracking sera généré automatiquement et contiendra tous les paramètres nécessaires pour le suivi.
            </p>
          </div>

          <div className="flex justify-end space-x-2">
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleGenerate}>
              Générer le Lien
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TrackingLinks;
