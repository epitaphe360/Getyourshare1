import React from 'react';
import { TrendingUp, Target, Users, Globe, Award, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const About = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-white/20 backdrop-blur-lg rounded-full flex items-center justify-center">
              <TrendingUp className="w-12 h-12" />
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-4">À Propos de ShareYourSales</h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            La première plateforme d'affiliation B2B au Maroc, connectant entreprises et partenaires commerciaux
          </p>
        </div>
      </div>

      {/* Mission Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <Target className="w-10 h-10 text-blue-600" />
              <h2 className="text-3xl font-bold text-gray-900">Notre Mission</h2>
            </div>
            <p className="text-lg text-gray-700 mb-4">
              Révolutionner la distribution B2B au Maroc en créant un écosystème où chaque entreprise peut 
              développer son réseau de vente grâce à une armée de partenaires motivés.
            </p>
            <p className="text-gray-600">
              Nous croyons que la vente collaborative est l'avenir du commerce. ShareYourSales supprime 
              les barrières entre les entreprises et les commerciaux indépendants, créant des opportunités 
              de croissance pour tous.
            </p>
          </div>
          <div className="bg-white p-8 rounded-2xl shadow-lg">
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 mb-1">Pour les Entreprises</h3>
                  <p className="text-sm text-gray-600">
                    Accédez à un réseau de commerciaux talentueux sans coûts fixes. Payez uniquement au résultat.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Zap className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 mb-1">Pour les Partenaires</h3>
                  <p className="text-sm text-gray-600">
                    Monétisez votre réseau en promouvant des produits de qualité. Gagnez des commissions attractives.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Values Section */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Nos Valeurs</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Les principes qui guident chacune de nos décisions et interactions
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-xl shadow-lg border-t-4 border-blue-600">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Award className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Transparence</h3>
              <p className="text-gray-600">
                Des règles claires, des commissions transparentes, un système de tracking fiable. 
                Pas de mauvaises surprises.
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border-t-4 border-purple-600">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Collaboration</h3>
              <p className="text-gray-600">
                Nous croyons en la force du collectif. Ensemble, entreprises et partenaires 
                vont plus loin.
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border-t-4 border-green-600">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Innovation</h3>
              <p className="text-gray-600">
                Technologie de pointe, intégrations multiples, analytics en temps réel. 
                Toujours à la pointe.
              </p>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-2">ShareYourSales en Chiffres</h2>
            <p className="text-blue-100">Notre impact depuis le lancement</p>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">500+</div>
              <div className="text-blue-100">Entreprises Inscrites</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">2,000+</div>
              <div className="text-blue-100">Partenaires Actifs</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">15M+</div>
              <div className="text-blue-100">MAD de Commissions</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">98%</div>
              <div className="text-blue-100">Satisfaction Client</div>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Notre Équipe</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Des passionnés de technologie et de commerce réunis pour transformer le B2B au Maroc
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-xl shadow-lg text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full mx-auto mb-4"></div>
              <h3 className="font-bold text-gray-900 mb-1">Youssef B.</h3>
              <p className="text-sm text-gray-600 mb-3">CEO & Fondateur</p>
              <p className="text-sm text-gray-700">
                15 ans d'expérience en vente B2B et marketplaces digitales
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full mx-auto mb-4"></div>
              <h3 className="font-bold text-gray-900 mb-1">Fatima Z.</h3>
              <p className="text-sm text-gray-600 mb-3">CTO</p>
              <p className="text-sm text-gray-700">
                Expert en développement de plateformes SaaS et intégrations API
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-green-600 to-teal-600 rounded-full mx-auto mb-4"></div>
              <h3 className="font-bold text-gray-900 mb-1">Omar K.</h3>
              <p className="text-sm text-gray-600 mb-3">CMO</p>
              <p className="text-sm text-gray-700">
                Spécialiste en marketing digital et growth hacking B2B
              </p>
            </div>
          </div>
        </div>

        {/* Technology Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-16">
          <div className="flex items-center space-x-3 mb-6">
            <Globe className="w-8 h-8 text-blue-600" />
            <h2 className="text-3xl font-bold text-gray-900">Notre Technologie</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Sécurité & Performance</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">✓</span>
                  <span>Cryptage SSL/TLS pour toutes les communications</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">✓</span>
                  <span>Infrastructure cloud scalable et résiliente</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">✓</span>
                  <span>Backups automatiques quotidiens</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">✓</span>
                  <span>Conformité RGPD et loi marocaine 09-08</span>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Intégrations</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">✓</span>
                  <span>API REST complète pour intégrations tierces</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">✓</span>
                  <span>Webhooks en temps réel pour synchronisation</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">✓</span>
                  <span>Connexion aux réseaux sociaux (Facebook, Instagram, TikTok)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">✓</span>
                  <span>Paiements sécurisés via CMI, Stripe, PayPal</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Prêt à Commencer ?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Rejoignez des centaines d'entreprises et de partenaires qui grandissent avec nous
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button
              onClick={() => navigate('/register?role=enterprise')}
              className="px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition transform hover:scale-105"
            >
              Je suis une Entreprise
            </button>
            <button
              onClick={() => navigate('/register?role=influencer')}
              className="px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-semibold rounded-lg border-2 border-white hover:bg-white/20 transition transform hover:scale-105"
            >
              Je suis Partenaire
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
