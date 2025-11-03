import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './BillingHistory.css';

function BillingHistory() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/invoices/history', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.data.success) {
        setInvoices(response.data.invoices);
      }
    } catch (err) {
      console.error('Erreur lors de la récupération des factures:', err);
      setError(err.response?.data?.detail || 'Erreur lors du chargement des factures');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      paid: { label: 'Payée', class: 'status-paid' },
      open: { label: 'En attente', class: 'status-open' },
      void: { label: 'Annulée', class: 'status-void' },
      uncollectible: { label: 'Impayée', class: 'status-uncollectible' },
      draft: { label: 'Brouillon', class: 'status-draft' }
    };

    const config = statusConfig[status] || { label: status, class: 'status-default' };
    return <span className={`status-badge ${config.class}`}>{config.label}</span>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatAmount = (amount, currency) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  const handleDownloadPDF = (invoice) => {
    if (invoice.invoice_pdf) {
      window.open(invoice.invoice_pdf, '_blank');
    }
  };

  const handleViewInvoice = (invoice) => {
    if (invoice.hosted_invoice_url) {
      window.open(invoice.hosted_invoice_url, '_blank');
    }
  };

  const handleInvoiceClick = (invoice) => {
    setSelectedInvoice(invoice);
  };

  const closeModal = () => {
    setSelectedInvoice(null);
  };

  if (loading) {
    return (
      <div className="billing-history">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Chargement de l'historique de facturation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="billing-history">
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h3>Erreur</h3>
          <p>{error}</p>
          <button onClick={fetchInvoices} className="retry-button">
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="billing-history">
      <div className="billing-header">
        <h1>Historique de facturation</h1>
        <p className="billing-subtitle">
          Retrouvez toutes vos factures et paiements
        </p>
      </div>

      {invoices.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h3>Aucune facture disponible</h3>
          <p>Vos factures apparaîtront ici après votre premier paiement</p>
        </div>
      ) : (
        <div className="invoices-container">
          <div className="invoices-summary">
            <div className="summary-card">
              <div className="summary-icon">📊</div>
              <div className="summary-content">
                <span className="summary-label">Total factures</span>
                <span className="summary-value">{invoices.length}</span>
              </div>
            </div>
            <div className="summary-card">
              <div className="summary-icon">✅</div>
              <div className="summary-content">
                <span className="summary-label">Factures payées</span>
                <span className="summary-value">
                  {invoices.filter(inv => inv.status === 'paid').length}
                </span>
              </div>
            </div>
            <div className="summary-card">
              <div className="summary-icon">💰</div>
              <div className="summary-content">
                <span className="summary-label">Montant total</span>
                <span className="summary-value">
                  {formatAmount(
                    invoices.reduce((sum, inv) => sum + inv.amount_paid, 0),
                    invoices[0]?.currency || 'EUR'
                  )}
                </span>
              </div>
            </div>
          </div>

          <div className="invoices-table-container">
            <table className="invoices-table">
              <thead>
                <tr>
                  <th>N° Facture</th>
                  <th>Date</th>
                  <th>Période</th>
                  <th>Montant</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.id} onClick={() => handleInvoiceClick(invoice)}>
                    <td className="invoice-number">
                      {invoice.invoice_number || invoice.id.substring(0, 8)}
                    </td>
                    <td>{formatDate(invoice.created)}</td>
                    <td className="invoice-period">
                      {invoice.period_start && invoice.period_end ? (
                        <>
                          {formatDate(invoice.period_start)}
                          {' - '}
                          {formatDate(invoice.period_end)}
                        </>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="invoice-amount">
                      {formatAmount(invoice.amount_paid, invoice.currency)}
                    </td>
                    <td>{getStatusBadge(invoice.status)}</td>
                    <td className="invoice-actions">
                      {invoice.invoice_pdf && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDownloadPDF(invoice);
                          }}
                          className="action-button download-button"
                          title="Télécharger PDF"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <polyline points="7 10 12 15 17 10" />
                            <line x1="12" y1="15" x2="12" y2="3" />
                          </svg>
                        </button>
                      )}
                      {invoice.hosted_invoice_url && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewInvoice(invoice);
                          }}
                          className="action-button view-button"
                          title="Voir la facture"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                            <circle cx="12" cy="12" r="3" />
                          </svg>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {selectedInvoice && (
        <div className="invoice-modal-overlay" onClick={closeModal}>
          <div className="invoice-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>×</button>
            
            <div className="modal-header">
              <h2>Détails de la facture</h2>
              <span className="modal-invoice-number">
                {selectedInvoice.invoice_number || selectedInvoice.id.substring(0, 8)}
              </span>
            </div>

            <div className="modal-body">
              <div className="modal-row">
                <span className="modal-label">Statut:</span>
                {getStatusBadge(selectedInvoice.status)}
              </div>
              <div className="modal-row">
                <span className="modal-label">Date de création:</span>
                <span>{formatDate(selectedInvoice.created)}</span>
              </div>
              {selectedInvoice.paid_at && (
                <div className="modal-row">
                  <span className="modal-label">Date de paiement:</span>
                  <span>{formatDate(selectedInvoice.paid_at)}</span>
                </div>
              )}
              <div className="modal-row">
                <span className="modal-label">Période:</span>
                <span>
                  {formatDate(selectedInvoice.period_start)} - {formatDate(selectedInvoice.period_end)}
                </span>
              </div>
              <div className="modal-row highlight">
                <span className="modal-label">Montant payé:</span>
                <span className="modal-amount">
                  {formatAmount(selectedInvoice.amount_paid, selectedInvoice.currency)}
                </span>
              </div>
              {selectedInvoice.description && (
                <div className="modal-row full-width">
                  <span className="modal-label">Description:</span>
                  <span>{selectedInvoice.description}</span>
                </div>
              )}
            </div>

            <div className="modal-footer">
              {selectedInvoice.invoice_pdf && (
                <button
                  onClick={() => handleDownloadPDF(selectedInvoice)}
                  className="modal-button primary"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  Télécharger PDF
                </button>
              )}
              {selectedInvoice.hosted_invoice_url && (
                <button
                  onClick={() => handleViewInvoice(selectedInvoice)}
                  className="modal-button secondary"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                  Voir en ligne
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BillingHistory;
