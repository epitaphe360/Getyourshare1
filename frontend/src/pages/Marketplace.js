import React, { useState } from 'react';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import { Search, Filter } from 'lucide-react';

const Marketplace = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const offers = [
    {
      id: 1,
      title: 'Campagne Tech Products Q2 2024',
      company: 'TechCorp',
      category: 'Technology',
      commission: '15%',
      description: 'Promouvoir nos derniers produits technologiques avec des commissions attractives.',
      requirements: 'Blog ou chaîne YouTube tech',
      status: 'active',
    },
    {
      id: 2,
      title: 'Collection Printemps Mode',
      company: 'Fashion Boutique',
      category: 'Fashion',
      commission: '20%',
      description: 'Nouvelle collection printemps à promouvoir auprès de votre audience mode.',
      requirements: 'Instagram > 5K followers',
      status: 'active',
    },
    {
      id: 3,
      title: 'Équipements Sportifs',
      company: 'Sports Gear',
      category: 'Sports',
      commission: '10€ fixe',
      description: 'Programme d’affiliation pour équipements sportifs haut de gamme.',
      requirements: 'Passion pour le sport',
      status: 'active',
    },
  ];

  const categories = ['all', 'Technology', 'Fashion', 'Sports', 'Health', 'Finance'];

  const filteredOffers = offers.filter(offer => {
    const matchesSearch = offer.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         offer.company.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || offer.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6" data-testid="marketplace">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Marketplace</h1>
        <p className="text-gray-600 mt-2">Découvrez les offres de partenariat disponibles</p>
      </div>

      {/* Filters */}
      <Card>
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher une offre..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  selectedCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category === 'all' ? 'Tous' : category}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Offers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredOffers.map((offer) => (
          <Card key={offer.id}>
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{offer.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{offer.company}</p>
                </div>
                <Badge status="active">{offer.category}</Badge>
              </div>

              <p className="text-gray-700">{offer.description}</p>

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div>
                  <p className="text-sm text-gray-600">Commission</p>
                  <p className="text-lg font-bold text-blue-600">{offer.commission}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Requis</p>
                  <p className="text-sm font-medium text-gray-900">{offer.requirements}</p>
                </div>
              </div>

              <Button className="w-full">
                Postuler à cette offre
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Marketplace;
