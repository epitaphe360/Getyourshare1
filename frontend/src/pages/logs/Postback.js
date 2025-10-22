import React from 'react';
import Card from '../../components/common/Card';
import { Server } from 'lucide-react';

const Postback = () => {
  return (
    <div className="space-y-6" data-testid="postback-log">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Logs Postback</h1>
        <p className="text-gray-600 mt-2">Suivi des notifications de conversion</p>
      </div>

      <Card>
        <div className="text-center py-12">
          <Server className="mx-auto text-gray-400" size={48} />
          <h3 className="mt-4 text-lg font-semibold text-gray-900">Aucun postback récent</h3>
          <p className="mt-2 text-gray-600">Les postbacks apparaîtront ici</p>
        </div>
      </Card>
    </div>
  );
};

export default Postback;
