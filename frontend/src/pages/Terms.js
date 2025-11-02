import React from 'react';
import { FileText, CheckCircle, AlertCircle, Scale, DollarSign, Users } from 'lucide-react';

const Terms = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
              <FileText className="w-8 h-8 text-purple-600" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Conditions Générales de Vente</h1>
              <p className="text-gray-600 mt-2">Dernière mise à jour : 2 novembre 2024</p>
            </div>
          </div>
          
          <div className="bg-purple-50 border-l-4 border-purple-600 p-4 rounded">
            <p className="text-purple-900">
              Les présentes Conditions Générales de Vente (CGV) régissent l'utilisation de la plateforme 
              <strong> ShareYourSales</strong> et les relations contractuelles entre les utilisateurs.
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-8">
          
          {/* Article 1 */}
          <section>
            <div className="flex items-start space-x-3 mb-4">
              <Scale className="w-6 h-6 text-purple-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">Article 1 - Définitions</h2>
                <div className="space-y-3">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-700">
                      <strong>La Plateforme :</strong> ShareYourSales, service en ligne d'affiliation B2B accessible via shareyoursales.ma
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-700">
                      <strong>Entreprise :</strong> Personne morale souscrivant à un abonnement pour publier des offres
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-700">
                      <strong>Partenaire :</strong> Commercial ou influenceur promouvant des offres via des liens d'affiliation
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-700">
                      <strong>Commission :</strong> Rémunération versée au Partenaire sur les ventes générées
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Article 2 */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <Users className="w-6 h-6 text-purple-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">Article 2 - Inscription et Compte</h2>
                <p className="text-gray-700 mb-4">
                  <strong>2.1 Conditions d'inscription</strong>
                </p>
                <ul className="space-y-2 text-gray-700 mb-4">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                    <span>Être âgé de 18 ans minimum ou entreprise légalement constituée</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                    <span>Fournir des informations exactes et à jour</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                    <span>Entreprises : Fournir RC, IF, ICE valides</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                    <span>Partenaires : Fournir CNIE et RIB</span>
                  </li>
                </ul>
                
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                  <p className="text-sm text-gray-800">
                    <AlertCircle className="w-4 h-4 inline mr-2" />
                    <strong>Vérification :</strong> Tous les documents sont vérifiés avant activation du compte.
                    Délai : 24-48h ouvrées.
                  </p>
                </div>

                <p className="text-gray-700 mt-4 mb-2">
                  <strong>2.2 Responsabilités du compte</strong>
                </p>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>Vous êtes responsable de la confidentialité de vos identifiants</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>Toute activité via votre compte vous est imputable</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>En cas de compromission, informez-nous immédiatement</span>
                  </li>
                </ul>
              </div>
            </div>
          </section>

          {/* Article 3 */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <DollarSign className="w-6 h-6 text-purple-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">Article 3 - Tarifs et Paiements</h2>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">3.1 Abonnements Entreprise</h3>
                <div className="grid md:grid-cols-3 gap-4 mb-6">
                  <div className="border border-gray-200 p-4 rounded-lg">
                    <h4 className="font-bold text-gray-900">Small Business</h4>
                    <p className="text-2xl font-bold text-purple-600">199 MAD/mois</p>
                    <p className="text-sm text-gray-600">2 membres, 1 domaine</p>
                  </div>
                  <div className="border border-purple-200 bg-purple-50 p-4 rounded-lg">
                    <h4 className="font-bold text-gray-900">Medium Business</h4>
                    <p className="text-2xl font-bold text-purple-600">499 MAD/mois</p>
                    <p className="text-sm text-gray-600">10 membres, 2 domaines</p>
                  </div>
                  <div className="border border-gray-200 p-4 rounded-lg">
                    <h4 className="font-bold text-gray-900">Large Business</h4>
                    <p className="text-2xl font-bold text-purple-600">799 MAD/mois</p>
                    <p className="text-sm text-gray-600">30 membres, illimité</p>
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">3.2 Marketplace (Partenaires)</h3>
                <div className="bg-blue-50 p-4 rounded-lg mb-4">
                  <p className="text-gray-800">
                    <strong>99 MAD/mois</strong> - Accès complet à la marketplace, commissions jusqu'à 30%
                  </p>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">3.3 Commission Plateforme</h3>
                <div className="bg-green-50 border-l-4 border-green-600 p-4 rounded">
                  <p className="text-gray-800">
                    <strong>5% de commission plateforme</strong> sur chaque vente réalisée via ShareYourSales
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Exemple : Vente 1000 MAD, commission partenaire 20% = 200 MAD → 
                    Partenaire reçoit 190 MAD (200 - 5%)
                  </p>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">3.4 Modalités de paiement</h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>Paiement mensuel par carte bancaire, virement ou CMI</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>Renouvellement automatique sauf résiliation 7 jours avant échéance</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>Commissions versées le 5 de chaque mois (délai validation 30 jours)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>Seuil minimum de retrait : 50 MAD</span>
                  </li>
                </ul>
              </div>
            </div>
          </section>

          {/* Article 4 */}
          <section className="border-t pt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Article 4 - Obligations des Parties</h2>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-2">4.1 Obligations de l'Entreprise</h3>
            <ul className="space-y-2 text-gray-700 mb-4">
              <li className="flex items-start">
                <span className="text-purple-600 mr-2">✓</span>
                <span>Fournir des descriptions de produits/services exactes</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 mr-2">✓</span>
                <span>Honorer les ventes générées par les Partenaires</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 mr-2">✓</span>
                <span>Verser les commissions dans les délais convenus</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 mr-2">✓</span>
                <span>Respecter les taux de commission annoncés</span>
              </li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">4.2 Obligations du Partenaire</h3>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start">
                <span className="text-purple-600 mr-2">✓</span>
                <span>Promouvoir de manière honnête et non trompeuse</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 mr-2">✓</span>
                <span>Ne pas utiliser de techniques illégales (spam, bots, etc.)</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 mr-2">✓</span>
                <span>Respecter les droits de propriété intellectuelle</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 mr-2">✓</span>
                <span>Déclarer ses revenus conformément à la législation marocaine</span>
              </li>
            </ul>
          </section>

          {/* Article 5 */}
          <section className="border-t pt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Article 5 - Litiges et Résiliation</h2>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-2">5.1 Résiliation</h3>
            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  <span><strong>Par l'utilisateur :</strong> À tout moment depuis les paramètres du compte</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  <span><strong>Par ShareYourSales :</strong> En cas de violation des CGV (préavis 15 jours)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  <span><strong>Immédiate :</strong> En cas de fraude, activité illégale ou impayés</span>
                </li>
              </ul>
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">5.2 Droit applicable et juridiction</h3>
            <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
              <p className="text-gray-800">
                Les présentes CGV sont régies par le droit marocain. En cas de litige, et à défaut d'accord amiable, 
                les tribunaux de <strong>Casablanca</strong> seront seuls compétents.
              </p>
            </div>
          </section>

          {/* Article 6 */}
          <section className="border-t pt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Article 6 - Limitation de Responsabilité</h2>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start">
                <AlertCircle className="w-5 h-5 text-orange-500 mr-2 mt-0.5" />
                <span>ShareYourSales est un intermédiaire et n'est pas partie aux transactions entre Entreprises et Partenaires</span>
              </li>
              <li className="flex items-start">
                <AlertCircle className="w-5 h-5 text-orange-500 mr-2 mt-0.5" />
                <span>Nous ne garantissons pas de résultats spécifiques en termes de ventes ou commissions</span>
              </li>
              <li className="flex items-start">
                <AlertCircle className="w-5 h-5 text-orange-500 mr-2 mt-0.5" />
                <span>Notre responsabilité est limitée au montant des frais d'abonnement payés</span>
              </li>
              <li className="flex items-start">
                <AlertCircle className="w-5 h-5 text-orange-500 mr-2 mt-0.5" />
                <span>Nous ne sommes pas responsables des interruptions de service (maintenance, force majeure)</span>
              </li>
            </ul>
          </section>

          {/* Contact */}
          <section className="border-t pt-8">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 rounded-xl">
              <h2 className="text-2xl font-bold mb-3">Questions sur les CGV ?</h2>
              <p className="mb-4">Contactez notre service juridique :</p>
              <div className="space-y-2 text-sm">
                <p><strong>Email :</strong> legal@shareyoursales.ma</p>
                <p><strong>Adresse :</strong> ShareYourSales SARL, Casablanca, Maroc</p>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
};

export default Terms;
