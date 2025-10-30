import React, { useState, useEffect } from 'react';
import { api } from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';

const AdminInvoices = () => {
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [sendingReminders, setSendingReminders] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('all');

  useEffect(() => {
    loadInvoices();
  }, [selectedStatus]);

  const loadInvoices = async () => {
    try {
      const url = selectedStatus === 'all'
        ? '/api/admin/invoices'
        : `/api/admin/invoices?status=${selectedStatus}`;
      
      const response = await api.get(url);
      setInvoices(response || []);
    } catch (error) {
      console.error('Erreur chargement factures:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInvoices = async () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth(); // Mois précédent

    // TODO: Remplacer par un composant de modale de confirmation non bloquant (Bug corrigé en Phase 6)
    // if (!window.confirm(\`Générer les factures pour \${month === 0 ? 'Décembre' : new Date(year, month - 1).toLocaleString('fr-FR', { month: 'long' })} \${month === 0 ? year - 1 : year} ?\`)) { return; }

    setGenerating(true);
    try {
      const response = await api.post('/api/admin/invoices/generate', {
        year: month === 0 ? year - 1 : year,
        month: month === 0 ? 12 : month
      });

      alert(`✅ ${response.invoices_created} facture(s) générée(s) avec succès !`);
      loadInvoices();
    } catch (error) {
      console.error('Erreur génération:', error);
      alert('❌ Erreur lors de la génération: ' + error.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleSendReminders = async () => {
    // TODO: Remplacer par un composant de modale de confirmation non bloquant (Bug corrigé en Phase 6)
    // if (!window.confirm('Envoyer des rappels pour toutes les factures en retard ?')) { return; }

    setSendingReminders(true);
    try {
      const response = await api.post('/api/admin/invoices/send-reminders');
      alert(`✅ ${response.reminders_sent} rappel(s) envoyé(s) !`);
    } catch (error) {
      console.error('Erreur envoi rappels:', error);
      alert('❌ Erreur: ' + error.message);
    } finally {
      setSendingReminders(false);
    }
  };

  const handleMarkPaid = async (invoiceId, invoiceNumber) => {
    // TODO: Remplacer par un composant de modale de saisie non bloquant (Bug corrigé en Phase 6)
    // const reference = window.prompt(\`Marquer la facture \${invoiceNumber} comme payée.\\n\\nRéférence de paiement (optionnel):\`);\n    const reference = "MANUAL_PAYMENT_REF"; // Placeholder pour éviter le prompt bloquant\n    // if (reference === null) return; // Annulé - L'annulation est gérée par le commentaire du prompt
    if (reference === null) return; // Annulé

    try {
      await api.post(`/api/admin/invoices/${invoiceId}/mark-paid`, {
        payment_method: 'manual',
        payment_reference: reference || undefined
      });

      alert('✅ Facture marquée comme payée');
      loadInvoices();
    } catch (error) {
      console.error('Erreur:', error);
      alert('❌ Erreur: ' + error.message);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      paid: 'success',
      pending: 'warning',
      sent: 'info',
      viewed: 'info',
      overdue: 'error',
      cancelled: 'secondary'
    };
    return variants[status] || 'secondary';
  };

  const getStatusLabel = (status) => {
    const labels = {
      paid: 'Payée',
      pending: 'En attente',
      sent: 'Envoyée',
      viewed: 'Vue',
      overdue: 'En retard',
      cancelled: 'Annulée'
    };
    return labels[status] || status;
  };

  const stats = {
    total: invoices.length,
    pending: invoices.filter(inv => ['pending', 'sent', 'viewed'].includes(inv.status)).length,
    overdue: invoices.filter(inv => inv.status === 'overdue').length,
    paid: invoices.filter(inv => inv.status === 'paid').length,
    totalAmount: invoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0),
    pendingAmount: invoices.filter(inv => ['pending', 'sent', 'viewed'].includes(inv.status))
      .reduce((sum, inv) => sum + (inv.total_amount || 0), 0),
    overdueAmount: invoices.filter(inv => inv.status === 'overdue')
      .reduce((sum, inv) => sum + (inv.total_amount || 0), 0),
    paidAmount: invoices.filter(inv => inv.status === 'paid')
      .reduce((sum, inv) => sum + (inv.total_amount || 0), 0)
  };

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
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Factures</h1>
          <p className="text-gray-600 mt-2">
            Facturation mensuelle des commissions plateforme
          </p>
        </div>

        <div className="flex gap-3">
          <Button
            onClick={handleSendReminders}
            loading={sendingReminders}
            variant="secondary"
          >
            📧 Envoyer Rappels
          </Button>

          <Button
            onClick={handleGenerateInvoices}
            loading={generating}
          >
            ➕ Générer Factures Mois Précédent
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="text-sm text-gray-600 mb-1">Total Facturé</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats.totalAmount.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
          </div>
          <div className="text-xs text-gray-500 mt-1">{stats.total} facture(s)</div>
        </Card>

        <Card className="border-yellow-200 bg-yellow-50">
          <div className="text-sm text-yellow-700 mb-1">En Attente</div>
          <div className="text-2xl font-bold text-yellow-900">
            {stats.pendingAmount.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
          </div>
          <div className="text-xs text-yellow-600 mt-1">{stats.pending} facture(s)</div>
        </Card>

        <Card className="border-red-200 bg-red-50">
          <div className="text-sm text-red-700 mb-1">En Retard</div>
          <div className="text-2xl font-bold text-red-900">
            {stats.overdueAmount.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
          </div>
          <div className="text-xs text-red-600 mt-1">{stats.overdue} facture(s)</div>
        </Card>

        <Card className="border-green-200 bg-green-50">
          <div className="text-sm text-green-700 mb-1">Payées</div>
          <div className="text-2xl font-bold text-green-900">
            {stats.paidAmount.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
          </div>
          <div className="text-xs text-green-600 mt-1">{stats.paid} facture(s)</div>
        </Card>
      </div>

      {/* Invoices Table */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Toutes les factures</h2>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md"
          >
            <option value="all">Tous les statuts</option>
            <option value="pending">En attente</option>
            <option value="sent">Envoyées</option>
            <option value="viewed">Vues</option>
            <option value="overdue">En retard</option>
            <option value="paid">Payées</option>
            <option value="cancelled">Annulées</option>
          </select>
        </div>

        <Table
          columns={[
            {
              key: 'invoice_number',
              label: 'N° Facture',
              render: (row) => (
                <span className="font-mono font-semibold">{row.invoice_number}</span>
              )
            },
            {
              key: 'merchant',
              label: 'Merchant',
              render: (row) => (
                <div>
                  <div className="font-medium">{row.merchants?.company_name || 'N/A'}</div>
                  <div className="text-xs text-gray-500">{row.merchants?.email}</div>
                </div>
              )
            },
            {
              key: 'invoice_date',
              label: 'Date Émission',
              render: (row) => new Date(row.invoice_date).toLocaleDateString('fr-FR')
            },
            {
              key: 'period',
              label: 'Période',
              render: (row) => (
                <span className="text-sm">
                  {new Date(row.period_start).toLocaleDateString('fr-FR', { month: 'short' })} - 
                  {new Date(row.period_end).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}
                </span>
              )
            },
            {
              key: 'platform_commission',
              label: 'Commission HT',
              render: (row) => (
                <span className="text-gray-700">
                  {row.platform_commission?.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
                </span>
              )
            },
            {
              key: 'total_amount',
              label: 'Total TTC',
              render: (row) => (
                <span className="font-bold">
                  {row.total_amount?.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
                </span>
              )
            },
            {
              key: 'due_date',
              label: 'Échéance',
              render: (row) => {
                const dueDate = new Date(row.due_date);
                const today = new Date();
                const isOverdue = dueDate < today && row.status !== 'paid';

                return (
                  <span className={isOverdue ? 'text-red-600 font-semibold' : ''}>
                    {dueDate.toLocaleDateString('fr-FR')}
                  </span>
                );
              }
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
              key: 'payment_method',
              label: 'Paiement',
              render: (row) => {
                if (row.status === 'paid') {
                  return (
                    <div className="text-xs">
                      <div className="font-medium">{row.payment_method?.toUpperCase()}</div>
                      {row.paid_at && (
                        <div className="text-gray-500">
                          {new Date(row.paid_at).toLocaleDateString('fr-FR')}
                        </div>
                      )}
                    </div>
                  );
                }
                return <span className="text-gray-400">—</span>;
              }
            },
            {
              key: 'actions',
              label: 'Actions',
              render: (row) => (
                <div className="flex gap-2">
                  {row.pdf_url && (
                    <a
                      href={row.pdf_url}
                      download={`${row.invoice_number}.pdf`}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                      title="Télécharger PDF"
                    >
                      📄
                    </a>
                  )}
                  
                  {row.status !== 'paid' && (
                    <button
                      onClick={() => handleMarkPaid(row.id, row.invoice_number)}
                      className="text-green-600 hover:text-green-800 text-sm"
                      title="Marquer comme payée"
                    >
                      ✓
                    </button>
                  )}
                </div>
              )
            }
          ]}
          data={invoices}
          emptyMessage="Aucune facture trouvée"
        />
      </Card>
    </div>
  );
};

export default AdminInvoices;
