import React, { useState } from 'react';
import Card from '../components/common/Card';
import { Video, Play, Clock, Eye, ThumbsUp, Filter } from 'lucide-react';

const VideoTutorials = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'Tous les vidéos', count: 24 },
    { id: 'getting-started', label: 'Démarrage', count: 5 },
    { id: 'influencer', label: 'Pour Influenceurs', count: 8 },
    { id: 'merchant', label: 'Pour Marchands', count: 7 },
    { id: 'advanced', label: 'Avancé', count: 4 },
  ];

  const videos = [
    {
      id: 1,
      title: 'Démarrage Rapide - Premiers Pas',
      description: 'Découvrez comment configurer votre compte et commencer en 5 minutes',
      thumbnail: '🚀',
      duration: '5:23',
      views: '12.5K',
      likes: '856',
      category: 'getting-started',
      level: 'Débutant'
    },
    {
      id: 2,
      title: 'Comment générer vos liens de tracking',
      description: 'Créez vos liens personnalisés et commencez à promouvoir',
      thumbnail: '🔗',
      duration: '8:45',
      views: '9.2K',
      likes: '632',
      category: 'influencer',
      level: 'Débutant'
    },
    {
      id: 3,
      title: 'Créer une campagne attractive',
      description: 'Attirez les meilleurs influenceurs avec une campagne optimisée',
      thumbnail: '🎯',
      duration: '12:30',
      views: '7.8K',
      likes: '543',
      category: 'merchant',
      level: 'Intermédiaire'
    },
    {
      id: 4,
      title: 'Analyser vos performances en détail',
      description: 'Comprenez vos statistiques et optimisez vos résultats',
      thumbnail: '📊',
      duration: '15:20',
      views: '6.4K',
      likes: '478',
      category: 'influencer',
      level: 'Intermédiaire'
    },
    {
      id: 5,
      title: 'Configuration des Webhooks',
      description: 'Automatisez vos workflows avec les webhooks',
      thumbnail: '⚙️',
      duration: '18:45',
      views: '4.2K',
      likes: '312',
      category: 'advanced',
      level: 'Avancé'
    },
    {
      id: 6,
      title: 'Stratégies de Marketing d\'Influence',
      description: 'Les meilleures pratiques pour réussir en marketing d\'affiliation',
      thumbnail: '💡',
      duration: '22:15',
      views: '8.9K',
      likes: '721',
      category: 'influencer',
      level: 'Intermédiaire'
    },
    {
      id: 7,
      title: 'Gérer les paiements et commissions',
      description: 'Configurez et gérez efficacement vos paiements',
      thumbnail: '💰',
      duration: '10:30',
      views: '5.6K',
      likes: '434',
      category: 'merchant',
      level: 'Débutant'
    },
    {
      id: 8,
      title: 'Intégration API Complète',
      description: 'Intégrez Share Your Sales à votre système existant',
      thumbnail: '🔧',
      duration: '25:00',
      views: '3.1K',
      likes: '245',
      category: 'advanced',
      level: 'Avancé'
    },
  ];

  const filteredVideos = selectedCategory === 'all' 
    ? videos 
    : videos.filter(v => v.category === selectedCategory);

  const playlists = [
    { title: 'Formation Complète Influenceur', videos: 12, duration: '2h 30min', color: 'bg-blue-500' },
    { title: 'Guide Complet Marchand', videos: 10, duration: '2h 15min', color: 'bg-green-500' },
    { title: 'Masterclass Marketing', videos: 8, duration: '3h 00min', color: 'bg-purple-500' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-8 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <Video size={40} />
          <h1 className="text-3xl font-bold">Vidéos Tutoriels</h1>
        </div>
        <p className="text-purple-100">Apprenez en vidéo avec nos tutoriels pas à pas</p>
      </div>

      {/* Playlists */}
      <Card title="🎬 Playlists Populaires">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {playlists.map((playlist, index) => (
            <div key={index} className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg hover:shadow-lg cursor-pointer transition-all">
              <div className={`w-full h-32 ${playlist.color} rounded-lg flex items-center justify-center mb-4`}>
                <Play className="text-white" size={40} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{playlist.title}</h3>
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>{playlist.videos} vidéos</span>
                <span>{playlist.duration}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Category Filter */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Filter size={20} className="text-gray-600" />
          <span className="font-semibold text-gray-900">Filtrer par catégorie:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                selectedCategory === cat.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cat.label} ({cat.count})
            </button>
          ))}
        </div>
      </Card>

      {/* Video Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredVideos.map((video) => (
          <Card key={video.id} className="hover:shadow-lg transition-all cursor-pointer">
            <div className="space-y-4">
              {/* Thumbnail */}
              <div className="relative w-full h-40 bg-gradient-to-br from-purple-400 to-pink-400 rounded-lg flex items-center justify-center text-6xl">
                {video.thumbnail}
                <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 rounded-lg flex items-center justify-center transition-all">
                  <Play className="text-white opacity-0 hover:opacity-100 transition-all" size={48} />
                </div>
                <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                  {video.duration}
                </div>
              </div>

              {/* Info */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-purple-600 bg-purple-100 px-2 py-1 rounded">
                    {video.level}
                  </span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{video.title}</h3>
                <p className="text-sm text-gray-600 mb-3">{video.description}</p>
                
                {/* Stats */}
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-3">
                    <span className="flex items-center space-x-1">
                      <Eye size={14} />
                      <span>{video.views}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <ThumbsUp size={14} />
                      <span>{video.likes}</span>
                    </span>
                  </div>
                  <Clock size={14} />
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* CTA Section */}
      <Card>
        <div className="text-center py-8">
          <h3 className="text-xl font-bold text-gray-900 mb-2">Vous ne trouvez pas ce que vous cherchez ?</h3>
          <p className="text-gray-600 mb-6">Suggérez-nous un sujet pour une prochaine vidéo</p>
          <button className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all">
            Suggérer une Vidéo
          </button>
        </div>
      </Card>
    </div>
  );
};

export default VideoTutorials;
