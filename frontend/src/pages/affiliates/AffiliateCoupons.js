import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatDate } from '../../utils/helpers';
import { Plus } from 'lucide-react';

const AffiliateCoupons = () => {
  const [coupons, setCoupons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCoupons();
  }, []);

  const fetchCoupons = async () => {
    try {
      const response = await api.get('/api/coupons');
      setCoupons(response.data.data);
    } catch (error) {
      console.error('Error fetching coupons:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      header: 'Code',
      accessor: 'code',
      render: (row) => <span className="font-mono font-semibold">{row.code}</span>,
    },
    {
      header: 'Type',
      accessor: 'discount_type',
      render: (row) => row.discount_type === 'percentage' ? 'Pourcentage' : 'Fixe',
    },
    {
      header: 'Valeur',
      accessor: 'discount_value',
      render: (row) => (
        <span>
          {row.discount_type === 'percentage' ? `${row.discount_value}%` : `${row.discount_value}€`}
        </span>
      ),
    },
    {
      header: 'Utilisation',
      accessor: 'usage',
      render: (row) => `${row.usage_count} / ${row.usage_limit}`,
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Expire le',
      accessor: 'expires_at',
      render: (row) => formatDate(row.expires_at),
    },
  ];

  return (
    <div className="space-y-6" data-testid="affiliate-coupons">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Coupons</h1>
          <p className="text-gray-600 mt-2">Créez et gérez les coupons promotionnels</p>
        </div>
        <Button>
          <Plus size={20} className="mr-2" />
          Nouveau Coupon
        </Button>
      </div>

      <Card>
        {loading ? (
          <div className="text-center py-8">Chargement...</div>
        ) : (
          <Table columns={columns} data={coupons} />
        )}
      </Card>
    </div>
  );
};

export default AffiliateCoupons;
