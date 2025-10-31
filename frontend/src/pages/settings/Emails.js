import React, { useState } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { Mail, Eye } from 'lucide-react';

const Emails = () => {
  const emailTemplates = [
    { id: 1, name: 'Bienvenue Affilié', subject: 'Bienvenue sur ShareYourSales!', status: 'active' },
    { id: 2, name: 'Approbation Affilié', subject: 'Votre compte a été approuvé', status: 'active' },
    { id: 3, name: 'Nouvelle Conversion', subject: 'Nouvelle conversion enregistrée', status: 'active' },
    { id: 4, name: 'Paiement Traité', subject: 'Votre paiement a été traité', status: 'active' },
    { id: 5, name: 'Réinitialisation Mot de Passe', subject: 'Réinitialisation de votre mot de passe', status: 'active' },
  ];

  return (
    <div className="space-y-6" data-testid="email-templates">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Templates d'Emails</h1>
        <p className="text-gray-600 mt-2">Gérez les modèles d'emails envoyés aux affiliés</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {emailTemplates.map((template) => (
          <Card key={template.id}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Mail className="text-blue-600" size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{template.name}</h3>
                  <p className="text-sm text-gray-600">{template.subject}</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button size="sm" variant="outline">
                  <Eye size={16} className="mr-2" />
                  Aperçu
                </Button>
                <Button size="sm">
                  Modifier
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Emails;
