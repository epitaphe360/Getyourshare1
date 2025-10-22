import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { Download, FileText, Calendar } from 'lucide-react';

const Reports = () => {
  const [reportType, setReportType] = useState('conversions');
  const [dateRange, setDateRange] = useState('30days');

  const reportTypes = [
    { value: 'conversions', label: 'Conversions' },
    { value: 'clicks', label: 'Clics' },
    { value: 'affiliates', label: 'Affiliés' },
    { value: 'campaigns', label: 'Campagnes' },
    { value: 'revenue', label: 'Revenus' },
  ];

  const dateRanges = [
    { value: '7days', label: '7 derniers jours' },
    { value: '30days', label: '30 derniers jours' },
    { value: '90days', label: '90 derniers jours' },
    { value: 'custom', label: 'Période personnalisée' },
  ];

  return (
    <div className="space-y-6" data-testid="reports">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Rapports</h1>
        <p className="text-gray-600 mt-2">Générez des rapports personnalisés</p>
      </div>

      <Card title="Configuration du Rapport">
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de Rapport
              </label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {reportTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Période
              </label>
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {dateRanges.map((range) => (
                  <option key={range.value} value={range.value}>
                    {range.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex space-x-4">
            <Button>
              <FileText size={20} className="mr-2" />
              Générer le Rapport
            </Button>
            <Button variant="outline">
              <Download size={20} className="mr-2" />
              Exporter CSV
            </Button>
          </div>
        </div>
      </Card>

      <Card title="Rapports Récents">
        <div className="space-y-3">
          {['Rapport de conversions - Mars 2024', 'Rapport des affiliés - Février 2024', 'Rapport de revenus - Janvier 2024'].map((report, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all">
              <div className="flex items-center space-x-3">
                <FileText className="text-blue-600" size={24} />
                <div>
                  <p className="font-semibold">{report}</p>
                  <p className="text-sm text-gray-600">Généré le {new Date().toLocaleDateString('fr-FR')}</p>
                </div>
              </div>
              <Button size="sm" variant="outline">
                <Download size={16} />
              </Button>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default Reports;
