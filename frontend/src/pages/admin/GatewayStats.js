import React, { useState, useEffect } from 'react';
import { api } from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';

const GatewayStats = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [selectedGateway, setSelectedGateway] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Charger statistiques gateways
      const statsResponse = await api.get('/api/admin/gateways/stats');
      setStats(statsResponse || []);

      // Charger transactions récentes
      const transactionsResponse = await api.get('/api/admin/transactions');
      setTransactions(transactionsResponse || []);
    } catch (error) {
      console.error('Erreur chargement données:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGatewayIcon = (gateway) => {
    const icons = {
      cmi: '🇲🇦',
      payzen: '🇫🇷',
      sg_maroc: '🏦'
    };
    return icons[gateway] || '💳';
  };

  const getGatewayName = (gateway) => {
    const names = {
      cmi: 'CMI',
      payzen: 'PayZen',
      sg_maroc: 'SG Maroc'
    };
    return names[gateway] || gateway;
  };

  const getStatusBadge = (status) => {
    const variants = {
      completed: 'success',
      pending: 'warning',
      processing: 'info',
      failed: 'error',
      refunded: 'secondary'
    };
    return variants[status] || 'secondary';
  };

  const getStatusLabel = (status) => {
    const labels = {
      completed: 'Complété',
      pending: 'En attente',
      processing: 'En cours',
      failed: 'Échoué',
      refunded: 'Remboursé'
    };
    return labels[status] || status;
  };

  const filteredTransactions = transactions.filter(t => {
    if (selectedGateway !== 'all' && t.gateway !== selectedGateway) return false;
    if (selectedStatus !== 'all' && t.status !== selectedStatus) return false;
    return true;
  });

  const totalProcessed = stats.reduce((sum, s) => sum + (s.total_amount_processed || 0), 0);
  const totalFees = stats.reduce((sum, s) => sum + (s.total_fees_paid || 0), 0);
  const totalTransactions = stats.reduce((sum, s) => sum + (s.total_transactions || 0), 0);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Statistiques des Gateways</h1>
        <p className="text-gray-600 mt-2">
          Suivi des transactions par solution de paiement
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="text-sm text-gray-600 mb-1">Total Traité</div>
          <div className="text-2xl font-bold text-gray-900">
            {totalProcessed.toLocaleString('fr-MA')} MAD
          </div>
          <div className="text-xs text-gray-500 mt-1">Tous gateways confondus</div>
        </Card>

        <Card>
          <div className="text-sm text-gray-600 mb-1">Total Frais</div>
          <div className="text-2xl font-bold text-red-600">
            {totalFees.toLocaleString('fr-MA')} MAD
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {totalProcessed > 0 ? ((totalFees / totalProcessed) * 100).toFixed(2) : 0}% du total
          </div>
        </Card>

        <Card>
          <div className="text-sm text-gray-600 mb-1">Transactions</div>
          <div className="text-2xl font-bold text-gray-900">
            {totalTransactions}
          </div>
          <div className="text-xs text-gray-500 mt-1">Total traité</div>
        </Card>

        <Card>
          <div className="text-sm text-gray-600 mb-1">Taux Succès Moyen</div>
          <div className="text-2xl font-bold text-green-600">
            {stats.length > 0
              ? (stats.reduce((sum, s) => sum + (s.success_rate || 0), 0) / stats.length).toFixed(1)
              : 0}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Tous gateways</div>
        </Card>
      </div>

      {/* Gateway Stats */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Performances par Gateway</h2>

        <div className="space-y-4">
          {stats.map(gateway => {
            const successRate = gateway.success_rate || 0;
            const avgTime = gateway.avg_completion_time_seconds || 0;

            return (
              <div key={gateway.gateway} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{getGatewayIcon(gateway.gateway)}</span>
                    <div>
                      <div className="font-semibold text-gray-900">
                        {getGatewayName(gateway.gateway)}
                      </div>
                      <div className="text-sm text-gray-500">
                        Dernière transaction: {gateway.last_transaction_date
                          ? new Date(gateway.last_transaction_date).toLocaleDateString('fr-FR')
                          : 'N/A'}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">
                      {(gateway.total_amount_processed || 0).toLocaleString('fr-MA')} MAD
                    </div>
                    <div className="text-sm text-red-600">
                      Frais: {(gateway.total_fees_paid || 0).toLocaleString('fr-MA')} MAD
                    </div>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-4 gap-4 mt-3 pt-3 border-t border-gray-100">
                  <div>
                    <div className="text-xs text-gray-500">Transactions</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {gateway.total_transactions || 0}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-gray-500">Succès</div>
                    <div className="text-lg font-semibold text-green-600">
                      {gateway.successful_transactions || 0}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-gray-500">Taux Succès</div>
                    <div className={`text-lg font-semibold ${
                      successRate >= 95 ? 'text-green-600' :
                      successRate >= 90 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {successRate.toFixed(1)}%
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-gray-500">Temps Moyen</div>
                    <div className="text-lg font-semibold text-blue-600">
                      {avgTime.toFixed(1)}s
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Taux de succès</span>
                    <span>{successRate.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        successRate >= 95 ? 'bg-green-500' :
                        successRate >= 90 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(successRate, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}

          {stats.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Aucune transaction enregistrée
            </div>
          )}
        </div>
      </Card>

      {/* Transactions List */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Transactions Récentes</h2>

          <div className="flex gap-3">
            <select
              value={selectedGateway}
              onChange={(e) => setSelectedGateway(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">Tous les gateways</option>
              <option value="cmi">CMI</option>
              <option value="payzen">PayZen</option>
              <option value="sg_maroc">SG Maroc</option>
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">Tous les statuts</option>
              <option value="completed">Complété</option>
              <option value="pending">En attente</option>
              <option value="processing">En cours</option>
              <option value="failed">Échoué</option>
              <option value="refunded">Remboursé</option>
            </select>
          </div>
        </div>

        <Table
          columns={[
            {
              key: 'gateway',
              label: 'Gateway',
              render: (row) => (
                <div className="flex items-center gap-2">
                  <span className="text-xl">{getGatewayIcon(row.gateway)}</span>
                  <span className="font-medium">{getGatewayName(row.gateway)}</span>
                </div>
              )
            },
            {
              key: 'transaction_id',
              label: 'ID Transaction',
              render: (row) => (
                <span className="font-mono text-sm">{row.transaction_id?.slice(0, 12)}...</span>
              )
            },
            {
              key: 'merchant',
              label: 'Merchant',
              render: (row) => row.merchant?.company_name || 'N/A'
            },
            {
              key: 'amount',
              label: 'Montant',
              render: (row) => (
                <span className="font-semibold">
                  {row.amount?.toFixed(2)} {row.currency || 'MAD'}
                </span>
              )
            },
            {
              key: 'fees',
              label: 'Frais',
              render: (row) => (
                <span className="text-red-600">
                  {row.fees?.toFixed(2)} MAD
                </span>
              )
            },
            {
              key: 'status',
              label: 'Statut',
              render: (row) => (
                <Badge variant={getStatusBadge(row.status)}>
                  {getStatusLabel(row.status)}
                </Badge>
              )
            },
            {
              key: 'created_at',
              label: 'Date',
              render: (row) => new Date(row.created_at).toLocaleString('fr-FR')
            }
          ]}
          data={filteredTransactions}
          emptyMessage="Aucune transaction trouvée"
        />
      </Card>
    </div>
  );
};

export default GatewayStats;
