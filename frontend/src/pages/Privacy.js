import React from 'react';
import { Shield, Lock, Eye, Database, UserCheck, FileText } from 'lucide-react';

const Privacy = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <Shield className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Politique de Confidentialité</h1>
              <p className="text-gray-600 mt-2">Dernière mise à jour : 2 novembre 2024</p>
            </div>
          </div>
          
          <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
            <p className="text-blue-900">
              <strong>ShareYourSales</strong> s'engage à protéger vos données personnelles conformément au RGPD 
              et à la loi marocaine n°09-08 relative à la protection des personnes physiques à l'égard du traitement des données à caractère personnel.
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-8">
          
          {/* Section 1 */}
          <section>
            <div className="flex items-start space-x-3 mb-4">
              <Database className="w-6 h-6 text-blue-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">1. Données Collectées</h2>
                <p className="text-gray-700 mb-4">
                  Nous collectons les données suivantes dans le cadre de notre service :
                </p>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Données d'identification</strong> : Nom, prénom, email, numéro de téléphone</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Données professionnelles</strong> : Nom de l'entreprise, RC, IF, ICE</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Données bancaires</strong> : RIB (crypté), informations de paiement</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Données de navigation</strong> : Adresse IP, cookies, pages visitées</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Données transactionnelles</strong> : Commissions, ventes, clics sur liens</span>
                  </li>
                </ul>
              </div>
            </div>
          </section>

          {/* Section 2 */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <Eye className="w-6 h-6 text-blue-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">2. Utilisation des Données</h2>
                <p className="text-gray-700 mb-4">Vos données sont utilisées pour :</p>
                <div className="space-y-3">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Gestion du compte</h3>
                    <p className="text-gray-700 text-sm">Création, authentification et gestion de votre profil utilisateur</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Traitement des transactions</h3>
                    <p className="text-gray-700 text-sm">Calcul et versement des commissions, facturation</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Amélioration du service</h3>
                    <p className="text-gray-700 text-sm">Analyse des performances, optimisation de l'expérience utilisateur</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Communication</h3>
                    <p className="text-gray-700 text-sm">Envoi de notifications, newsletters (avec consentement)</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Section 3 */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <Lock className="w-6 h-6 text-blue-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">3. Protection des Données</h2>
                <p className="text-gray-700 mb-4">
                  Nous mettons en œuvre des mesures de sécurité strictes :
                </p>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="border border-green-200 bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Lock className="w-5 h-5 text-green-600" />
                      <h3 className="font-semibold text-gray-900">Cryptage SSL/TLS</h3>
                    </div>
                    <p className="text-sm text-gray-700">Toutes les communications sont cryptées</p>
                  </div>
                  <div className="border border-green-200 bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Shield className="w-5 h-5 text-green-600" />
                      <h3 className="font-semibold text-gray-900">Serveurs Sécurisés</h3>
                    </div>
                    <p className="text-sm text-gray-700">Hébergement sécurisé avec firewall</p>
                  </div>
                  <div className="border border-green-200 bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <UserCheck className="w-5 h-5 text-green-600" />
                      <h3 className="font-semibold text-gray-900">Accès Restreint</h3>
                    </div>
                    <p className="text-sm text-gray-700">Seul le personnel autorisé accède aux données</p>
                  </div>
                  <div className="border border-green-200 bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Database className="w-5 h-5 text-green-600" />
                      <h3 className="font-semibold text-gray-900">Sauvegardes</h3>
                    </div>
                    <p className="text-sm text-gray-700">Backups réguliers et sécurisés</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Section 4 */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <UserCheck className="w-6 h-6 text-blue-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">4. Vos Droits</h2>
                <p className="text-gray-700 mb-4">
                  Conformément au RGPD, vous disposez des droits suivants :
                </p>
                <div className="space-y-2">
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <span className="text-blue-600 font-bold">✓</span>
                    <span className="text-gray-900"><strong>Droit d'accès</strong> : Consulter vos données</span>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <span className="text-blue-600 font-bold">✓</span>
                    <span className="text-gray-900"><strong>Droit de rectification</strong> : Corriger vos données</span>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <span className="text-blue-600 font-bold">✓</span>
                    <span className="text-gray-900"><strong>Droit à l'effacement</strong> : Supprimer votre compte</span>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <span className="text-blue-600 font-bold">✓</span>
                    <span className="text-gray-900"><strong>Droit d'opposition</strong> : Refuser certains traitements</span>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <span className="text-blue-600 font-bold">✓</span>
                    <span className="text-gray-900"><strong>Droit à la portabilité</strong> : Récupérer vos données</span>
                  </div>
                </div>
                <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                  <p className="text-sm text-gray-800">
                    <strong>Pour exercer vos droits</strong>, contactez-nous à : 
                    <a href="mailto:privacy@shareyoursales.ma" className="text-blue-600 font-semibold ml-1">
                      privacy@shareyoursales.ma
                    </a>
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Section 5 */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <FileText className="w-6 h-6 text-blue-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">5. Cookies</h2>
                <p className="text-gray-700 mb-4">
                  Nous utilisons des cookies pour améliorer votre expérience :
                </p>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Cookies essentiels</strong> : Nécessaires au fonctionnement (authentification)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Cookies analytiques</strong> : Mesure d'audience (Google Analytics)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span><strong>Cookies de préférence</strong> : Mémorisation de vos choix (langue, thème)</span>
                  </li>
                </ul>
                <p className="text-sm text-gray-600 mt-4">
                  Vous pouvez configurer vos préférences de cookies dans les paramètres de votre navigateur.
                </p>
              </div>
            </div>
          </section>

          {/* Section 6 */}
          <section className="border-t pt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">6. Conservation des Données</h2>
            <p className="text-gray-700 mb-4">
              Nous conservons vos données personnelles :
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Pendant la durée de votre compte</strong> + 5 ans (obligations légales)</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Données transactionnelles</strong> : 10 ans (obligations fiscales)</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Après suppression</strong> : Anonymisation immédiate des données</span>
              </li>
            </ul>
          </section>

          {/* Section 7 */}
          <section className="border-t pt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">7. Partage des Données</h2>
            <p className="text-gray-700 mb-4">
              Nous ne vendons jamais vos données. Partage limité à :
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Prestataires de paiement</strong> : CMI, Stripe (cryptage sécurisé)</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Hébergeur</strong> : Serveurs sécurisés au Maroc</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Autorités légales</strong> : Sur réquisition judiciaire uniquement</span>
              </li>
            </ul>
          </section>

          {/* Contact */}
          <section className="border-t pt-8">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-xl">
              <h2 className="text-2xl font-bold mb-3">Nous Contacter</h2>
              <p className="mb-4">Pour toute question relative à vos données personnelles :</p>
              <div className="space-y-2 text-sm">
                <p><strong>Email :</strong> privacy@shareyoursales.ma</p>
                <p><strong>Adresse :</strong> ShareYourSales, Casablanca, Maroc</p>
                <p><strong>Téléphone :</strong> +212 5XX-XXXXXX</p>
              </div>
              <p className="mt-4 text-sm text-blue-100">
                Délai de réponse : 30 jours maximum
              </p>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
};

export default Privacy;
