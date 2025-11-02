import React, { useState, useEffect } from 'react';
import { useToast } from '../../context/ToastContext';
import { api } from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';

const MerchantInvoices = () => {
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState([]);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [paying, setPaying] = useState(false);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      const response = await api.get('/api/merchant/invoices');
      setInvoices(response || []);
    } catch (error) {
      console.error('Erreur chargement factures:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePayInvoice = async (invoiceId) => {
    setPaying(true);
    try {
      const response = await api.post(`/api/merchant/invoices/${invoiceId}/pay`);
      
      if (response.payment_url) {
        toast.info('Redirection vers la page de paiement...');
        // Rediriger vers page de paiement
        window.location.href = response.payment_url;
      } else {
        toast.success('Paiement initié avec succès');
        loadInvoices();
      }
    } catch (error) {
      console.error('Erreur paiement:', error);
      toast.error('Erreur lors du paiement: ' + error.message);
    } finally {
      setPaying(false);
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

  const totalPending = invoices
    .filter(inv => ['pending', 'sent', 'viewed'].includes(inv.status))
    .reduce((sum, inv) => sum + (inv.total_amount || 0), 0);

  const totalOverdue = invoices
    .filter(inv => inv.status === 'overdue')
    .reduce((sum, inv) => sum + (inv.total_amount || 0), 0);

  const totalPaid = invoices
    .filter(inv => inv.status === 'paid')
    .reduce((sum, inv) => sum + (inv.total_amount || 0), 0);

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
        <h1 className="text-3xl font-bold text-gray-900">Mes Factures</h1>
        <p className="text-gray-600 mt-2">
          Consultez et payez vos factures de commissions plateforme
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-yellow-200 bg-yellow-50">
          <div className="text-sm text-yellow-700 mb-1">À Payer</div>
          <div className="text-2xl font-bold text-yellow-900">
            {totalPending.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
          </div>
          <div className="text-xs text-yellow-600 mt-1">
            {invoices.filter(inv => ['pending', 'sent', 'viewed'].includes(inv.status)).length} facture(s)
          </div>
        </Card>

        <Card className="border-red-200 bg-red-50">
          <div className="text-sm text-red-700 mb-1">En Retard</div>
          <div className="text-2xl font-bold text-red-900">
            {totalOverdue.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
          </div>
          <div className="text-xs text-red-600 mt-1">
            {invoices.filter(inv => inv.status === 'overdue').length} facture(s)
          </div>
        </Card>

        <Card className="border-green-200 bg-green-50">
          <div className="text-sm text-green-700 mb-1">Payées</div>
          <div className="text-2xl font-bold text-green-900">
            {totalPaid.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
          </div>
          <div className="text-xs text-green-600 mt-1">
            {invoices.filter(inv => inv.status === 'paid').length} facture(s)
          </div>
        </Card>
      </div>

      {/* Invoices Table */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Toutes les factures</h2>

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
              key: 'invoice_date',
              label: 'Date',
              render: (row) => new Date(row.invoice_date).toLocaleDateString('fr-FR')
            },
            {
              key: 'period',
              label: 'Période',
              render: (row) => (
                <span className="text-sm">
                  {new Date(row.period_start).toLocaleDateString('fr-FR')} - {new Date(row.period_end).toLocaleDateString('fr-FR')}
                </span>
              )
            },
            {
              key: 'total_sales_amount',
              label: 'Ventes Totales',
              render: (row) => (
                <span className="text-gray-600">
                  {row.total_sales_amount?.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} MAD
                </span>
              )
            },
            {
              key: 'total_amount',
              label: 'Montant TTC',
              render: (row) => (
                <span className="font-bold text-lg">
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
              key: 'actions',
              label: 'Actions',
              render: (row) => (
                <div className="flex gap-2">
                  {row.pdf_url && (
                    <a
                      href={row.pdf_url}
                      download={`${row.invoice_number}.pdf`}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      📄 PDF
                    </a>
                  )}
                  
                  {row.status !== 'paid' && (
                    <Button
                      size="sm"
                      onClick={() => handlePayInvoice(row.id)}
                      loading={paying}
                      className="ml-2"
                    >
                      Payer
                    </Button>
                  )}
                </div>
              )
            }
          ]}
          data={invoices}
          emptyMessage="Aucune facture pour le moment"
        />
      </Card>

      {/* Help Section */}
      <Card className="bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-3">💡 Comment ça marche ?</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>
            <strong>1. Génération automatique :</strong> Chaque mois, nous générons une facture 
            récapitulative de vos commissions dues (5% de vos ventes).
          </p>
          <p>
            <strong>2. Échéance :</strong> Vous avez 30 jours pour payer à compter de la date d'émission.
          </p>
          <p>
            <strong>3. Paiement :</strong> Cliquez sur "Payer" pour régler via votre solution de paiement 
            configurée (CMI, PayZen, SG Maroc).
          </p>
          <p>
            <strong>4. TVA :</strong> Le montant TTC inclut la TVA marocaine à 20%.
          </p>
        </div>
      </Card>
    </div>
  );
};

export default MerchantInvoices;
