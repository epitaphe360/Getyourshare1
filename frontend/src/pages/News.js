import React from 'react';
import Card from '../components/common/Card';
import { Newspaper, Calendar } from 'lucide-react';

const News = () => {
  const newsItems = [
    {
      id: 1,
      title: 'Nouvelle fonctionnalité MLM disponible',
      date: '2024-03-20',
      content: 'Configurez jusqu’à 10 niveaux de commissions MLM pour votre programme d’affiliation.',
      type: 'feature',
    },
    {
      id: 2,
      title: 'Mise à jour de sécurité',
      date: '2024-03-15',
      content: 'Amélioration de la sécurité avec authentification à deux facteurs.',
      type: 'update',
    },
    {
      id: 3,
      title: 'Nouveau tableau de bord',
      date: '2024-03-10',
      content: 'Découvrez notre nouveau tableau de bord avec des statistiques avancées.',
      type: 'feature',
    },
  ];

  return (
    <div className="space-y-6" data-testid="news">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">News & Newsletter</h1>
        <p className="text-gray-600 mt-2">Dernières actualités de la plateforme</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {newsItems.map((news) => (
            <Card key={news.id}>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <Newspaper className="text-blue-600" size={24} />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900">{news.title}</h3>
                  <div className="flex items-center space-x-2 mt-2 text-sm text-gray-600">
                    <Calendar size={16} />
                    <span>{new Date(news.date).toLocaleDateString('fr-FR')}</span>
                  </div>
                  <p className="mt-3 text-gray-700">{news.content}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div>
          <Card title="S'abonner à la Newsletter">
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Recevez les dernières actualités et mises à jour directement dans votre boîte mail.
              </p>
              <input
                type="email"
                placeholder="votre@email.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all">
                S'abonner
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default News;
