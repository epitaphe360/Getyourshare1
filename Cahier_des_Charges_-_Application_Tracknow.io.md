# Cahier des Charges - Application Tracknow.io

## 1. Introduction

Ce cahier des charges détaille les fonctionnalités et les exigences techniques pour la reproduction de l'application de gestion d'affiliation Tracknow.io, accessible via `https://jalil-manage.tracknow.io/login`. L'objectif est de créer un clone fonctionnel de l'application, en reprenant les pages, les fonctionnalités et l'expérience utilisateur observées.

## 2. Exigences Fonctionnelles

### 2.0. Fonctionnalités Clés de la Plateforme (Tracknow.io)

La plateforme Tracknow.io, en tant que solution logicielle de suivi d'affiliation, offre un ensemble de fonctionnalités robustes pour le suivi, la gestion et la croissance des programmes d'affiliation. Ces fonctionnalités incluent [1] :

*   **Suivi en Temps Réel :** Tableau de bord pour suivre les performances des affiliés et des influenceurs.
*   **Personnalisation et Marque Blanche :** Ajout de logo, modification des couleurs de thème, configuration SSL, personnalisation des emails et SMTP dédié.
*   **Suivi des Coupons :** Suivi des coupons hors ligne pour récompenser les affiliés.
*   **Marketing Multi-Niveaux (MLM) :** Outil pour développer le réseau d'affiliés et générer des revenus à partir de leurs ventes.
*   **Règles de Commission Avancées :** Personnalisation des commissions par produit, catégorie ou affilié, avec des taux personnalisés.
*   **Détection Avancée de Fraude :** Fonctionnalité anti-fraude pour protéger les revenus.
*   **API Robuste :** Intégration API pour récupérer des données, télécharger des ventes et mettre à jour les statuts de commission.
*   **Intégration Facilitée :** Capacité à s'intégrer avec toutes les plateformes existantes, avec prise en charge de la configuration et de l'intégration.
*   **Gestion Complète des Affiliés :** Plateforme tout-en-un pour la gestion des programmes, le suivi des ventes, les ventes basées sur des coupons, les commissions par catégorie et les niveaux de commission.
*   **Créatifs HTML5 et Vidéo :** Support pour divers types de créatifs.
*   **Contest & Gamification :** Tableaux de classement, récompenses et défis pour stimuler l'engagement et la motivation des affiliés.



### 2.1. Authentification

### 2.2. Plateforme ShareYourSales.com

La plateforme ShareYourSales.com vise à connecter les entreprises, les commerciaux indépendants et les influenceurs grâce à des liens sécurisés et traçables. Elle est structurée autour de trois espaces principaux : un pour les entreprises, un pour les commerciaux indépendants et un pour les influenceurs.

#### 2.2.1. Page Présentative

Maximisez vos revenus avec notre solution Share Your Sales

À l’ère du numérique, le marketing évolue grâce aux influenceurs et aux spécialistes du marketing en ligne. Share Your Sales révolutionne la gestion client (CRM) et la gestion des relations influenceurs (IRM) en combinant le partage de liens et le suivi des clics pour une performance optimale.

Comment ça marche ?
Générez un lien de suivi unique via notre système et partagez-le sur vos réseaux, blogs ou campagnes. Chaque clic est suivi en temps réel, vous offrant des données précieuses : nombre de clics, provenance du trafic et actions des utilisateurs et plus encore vous soyez vos revenus augmenter en direct.

Pourquoi choisir notre solution ?
✅ Monétisation simplifiée – Gagnez des commissions sans intermédiaire.
✅ Transparence totale – Accédez à des rapports précis sur vos performances.
✅ Optimisation en temps réel – Ajustez vos stratégies grâce à des insights détaillés.
✅ ROI garanti – Suivez l’impact réel de vos influenceurs et partenaires.

Que vous soyez une marque ou un influenceur, Share Your Sales vous permet de transformer chaque interaction en opportunité de croissance. Automatisez votre gestion de relations et boostez vos résultats avec une solution puissante et intuitive.

Passez à la vitesse supérieure et commencez dès aujourd’hui !

#### 2.2.2. Marketplace

(Ce que je t’ai mis en descriptif c’est seulement une mise en relation ou une BDD pour faciliter les collaborations) Marketplace :
Ce que ça contient 
Une section qui rassemble les offres de partenariat entre les entreprises et les commerciaux libéraux ou influenceurs.

- Offres des entreprises :
Les entreprises peuvent publier des offres de partenariat, et les influenceurs/commerciaux peuvent y postuler.

Trouvez l'opportunité qui vous correspond. Postulez et démarrez une nouvelle campagne !

•	Recherche de projets : Les commerciaux et influenceurs peuvent naviguer dans les offres disponibles, filtrer par secteur (mode, tech, sport, etc.) et rejoindre les campagnes.

Explorez les projets et décrochez des ventes dès maintenant.

•	Filtre par secteur : Facilite la recherche en permettant aux utilisateurs de filtrer les projets en fonction de leur expertise ou de leur audience.

• 	Les influenceurs ou commerciaux pourront également s’inscrire en remplissant leur secteur d’activités ainsi que leurs réalisations pour que les entreprises puissent les contacter pour collaboration.

Que vous soyez dans la mode, la tech ou l’alimentaire, trouvez votre créne
*   **Page de Connexion :** Permettre aux utilisateurs de se connecter avec un email et un mot de passe.
    *   Champs: Email (`jal18@live.fr`), Mot de passe (`J@lil180683`).
    *   Validation des identifiants.
    *   Gestion des erreurs de connexion (identifiants incorrects).

### 2.3. Navigation et Structure Générale

L'application doit reproduire la structure de navigation latérale observée, avec les sections principales et leurs sous-menus.

### 2.4. Pages Principales

#### 2.4.1. Getting Started (Accueil)

*   Présentation des informations de base ou des étapes pour commencer.
*   Contient des liens vers d'autres sections ou des tutoriels.

#### 2.4.2. Dashboard (Tableau de Bord)

*   Vue d'ensemble des métriques clés de performance.
*   Widgets personnalisables affichant des données importantes (conversions, revenus, etc.).

#### 2.4.3. News & Newsletter

*   Affichage des actualités et des newsletters de la plateforme.
*   Possibilité de consulter les archives ou de s'abonner.

#### 2.4.4. Advertisers (Annonceurs)

*   **Liste des Annonceurs :** Afficher une liste de tous les annonceurs enregistrés.
    *   Fonctionnalités de recherche, filtrage et tri.
    *   Détails de chaque annonceur (nom, statut, etc.).
*   **Registrations (Inscriptions) :** Gérer les demandes d'inscription des annonceurs.
    *   Affichage des inscriptions en attente, approuvées, refusées.
    *   Actions : approuver, refuser, modifier les inscriptions.
*   **Billing (Facturation) :** Gérer la facturation liée aux annonceurs.
    *   Historique des factures, paiements.
    *   Fonctionnalités d'ajout de factures personnalisées (`Add Custom Billing`, `Add Billing`).
    *   Filtres par date, statut, annonceur.
    *   Export des données.
    *   **Gestion des statuts via Excel :** Possibilité de modifier les statuts (APPROVED, PENDING, DENIED) via un fichier Excel et de le télécharger.

#### 2.4.5. Campaigns/Offers (Campagnes/Offres)

*   Liste et gestion des campagnes et offres disponibles.
*   Détails de chaque campagne (statut, dates, annonceur, etc.).
*   Fonctionnalités de recherche, filtrage et tri.

#### 2.4.6. Performance

*   **Conversions :** Statistiques détaillées sur les conversions.
    *   Filtres par date, campagne, affilié.
    *   Graphiques et tableaux de données.
*   **MLM Commissions (Commissions MLM) :** Rapports sur les commissions du marketing multi-niveaux.
    *   Vue des gains par niveau MLM.
*   **Leads :** Statistiques sur les leads générés.
    *   Filtres et options de tri.
*   **Reports (Rapports) :** Génération de divers rapports de performance.
    *   Rapports sur les statistiques de campagne.
    *   Options de personnalisation des rapports.

#### 2.4.7. Affiliates (Affiliés)

*   **Payouts (Paiements) :** Gestion des paiements aux affiliés.
    *   Liste des paiements effectués et en attente.
    *   Fonctionnalités d'approbation/rejet des paiements.
*   **Affiliate Applications (Demandes d'Affiliation) :** Gérer les demandes d'inscription des affiliés.
    *   Processus similaire aux inscriptions des annonceurs.
*   **Affiliate Management (Gestion des Affiliés) :** Liste et gestion des affiliés enregistrés.
    *   Détails de chaque affilié, statut, performance.
*   **Lost Orders (Commandes Perdues) :** Suivi des commandes qui n'ont pas été attribuées.
*   **Lifetime (Durée de Vie) :** Rapports sur la valeur à vie des affiliés.
*   **Balance Report (Rapport de Solde) :** Rapports financiers sur les soldes des affiliés.
*   **Balance Report (Dates) :** Rapports de solde avec filtres par date.
*   **Coupons Management (Gestion des Coupons) :** Création et gestion des coupons promotionnels.

#### 2.4.8. Logs (Journaux)

*   **Clicks (Clics) :** Journaux détaillés des clics.
    *   Enregistrement des clics, sources, campagnes.
*   **Postback :** Journaux des postbacks.
    *   Suivi des notifications de conversion.
*   **Audit :** Journal d'audit des actions des utilisateurs.
    *   Enregistrement des modifications, connexions, etc.
    *   Filtres par date, entité, utilisateur.
*   **Webhook Logs :** Journaux des webhooks envoyés/reçus.
    *   Détails des requêtes et réponses des webhooks.

#### 2.4.9. Settings (Paramètres)

*   **Personal Settings (Paramètres Personnels) :** Gestion des informations personnelles de l'utilisateur connecté.
    *   Nom, prénom, numéro de téléphone, thème, langue, fuseau horaire, format de l'heure.
    *   Informations de contact (Email, Teams, Whatsapp, Linkedin, WeChat, Telegram, Calendly).
    *   Téléchargement d'image de profil.
*   **Security (Sécurité) :** Paramètres de sécurité du compte.
    *   Changement d'email et de mot de passe.
    *   Gestion des IPs autorisées (`Allowed IPs`).
    *   Authentification à deux facteurs (2FA).
*   **Company Settings (Paramètres de l'Entreprise) :** Informations et paramètres généraux de l'entreprise.
    *   Nom de l'entreprise, adresse, ID fiscal.
    *   IPs autorisées pour l'API et les managers.
    *   Email de contact pour les affiliés.
    *   Devise, symbole de devise personnalisé, placement du symbole.
    *   Option d'affichage du menu d'accessibilité.
*   **Affiliate Settings (Paramètres des Affiliés) :** Configuration du comportement des affiliés.
    *   Filtre de date par défaut, montant minimum de retrait.
    *   Vérification d'email pour les nouveaux affiliés.
    *   Mode d'approbation des affiliés (manuel ou automatique).
    *   Mode campagne unique, sélection de campagne par défaut.
    *   Paramètres avancés (ajout de domaines de parking, contrôle de grille, affichage de l'ID personnalisé, alertes email).
    *   Paramètres de paiement (automatique ou sur demande, suppression de la demande de retrait, autorisation de saisie du montant, autorisation de pièce jointe, délai de demande de paiement).
*   **Registration Settings (Paramètres d'Inscription) :** Configuration du processus d'inscription.
    *   Manager par défaut, type d'allocation de manager.
    *   Pays autorisés/non autorisés pour l'inscription.
    *   Autoriser l'inscription des affiliés/annonceurs.
    *   Champs requis (pays, nom de l'entreprise, statut juridique).
    *   Exigence d'invitation pour l'inscription (via URL de parrainage MLM).
    *   Exigence 2FA pour les affiliés.
    *   Alertes email pour les nouvelles inscriptions.
    *   Consentement au matériel promotionnel.
    *   Affichage d'un message d'activation en popup.
*   **Multi Level Marketing (MLM) :** Configuration des niveaux MLM.
    *   Activation et pourcentages pour jusqu'à 10 niveaux MLM.
    *   Type de MLM (basé sur les commissions).
*   **Traffic Sources (Sources de Trafic) :** Gestion des sources de trafic.
    *   Ajout, modification, suppression de sources de trafic (ex: Cashback, Facebook, Google, Incentive).
*   **Affiliate Default Permissions (Permissions par Défaut des Affiliés) :** Définition des permissions par défaut pour les affiliés.
    *   Écrans visibles (Performance, Clics, Impressions, Conversions, Leads, Références, Campagnes/Offres, Commandes Perdues).
    *   Champs visibles (Montant de conversion, Lien court, ID de commande de conversion).
    *   Actions autorisées (API, Voir informations personnelles).
*   **User Management (Gestion des Utilisateurs) :** Gestion des managers utilisateurs.
    *   Ajout, modification, suppression de managers.
    *   Détails : Pays, Photo de profil, Nom, Email, Bloqué, 2FA Actif, Site Web, Numéro de téléphone.
*   **Advertiser User Management (Gestion des Utilisateurs Annonceurs) :** Gestion des utilisateurs liés aux annonceurs.
    *   Ajout, modification, suppression d'utilisateurs annonceurs.
    *   Détails : Pays, Nom, Email, Bloqué, Annonceur, Site Web, Numéro de téléphone.
*   **SMTP :** Paramètres de configuration SMTP pour l'envoi d'emails.
*   **Affiliate Emails :** Gestion des modèles d'emails envoyés aux affiliés.

#### 2.4.10. Integrations (Intégrations)

*   Gestion des intégrations avec des services tiers.
    *   Détails des intégrations configurées.
    *   Ajout de nouvelles intégrations.

## 3. Exigences Non-Fonctionnelles

### 3.1. Performance

*   L'application doit être réactive avec des temps de chargement de page inférieurs à 3 secondes pour les opérations courantes.
*   Les requêtes de données complexes (rapports, listes filtrées) doivent être optimisées pour un affichage rapide.

### 3.2. Sécurité

*   Implémentation des meilleures pratiques de sécurité pour la protection des données (chiffrement, protection contre les injections SQL, XSS).
*   Gestion sécurisée des mots de passe (hachage).
*   Respect des IPs autorisées pour l'accès (managers, API).
*   Support de l'authentification à deux facteurs (2FA).

### 3.3. Scalabilité

*   L'architecture doit être conçue pour supporter une augmentation du nombre d'utilisateurs, d'annonceurs, d'affiliés et de données sans dégradation significative des performances.

### 3.4. Maintenabilité

*   Le code doit être propre, bien documenté et suivre les standards de développement pour faciliter la maintenance et les évolutions futures.

### 3.5. Compatibilité

*   L'application doit être compatible avec les navigateurs web modernes (Chrome, Firefox, Safari, Edge).
*   Conception responsive pour une utilisation sur différents appareils (ordinateurs de bureau, tablettes, mobiles).

### 3.6. Localisation

*   Support de plusieurs langues (au moins Français et Anglais, selon l'observation de la page des paramètres personnels).
*   Gestion des fuseaux horaires et des formats de date/heure.

## 4. Technologies Proposées (Exemple)

*   **Frontend :** React.js / Vue.js / Angular (pour une interface utilisateur dynamique et réactive).
*   **Backend :** Node.js (Express) / Python (Django/Flask) / PHP (Laravel) (pour une API RESTful).
*   **Base de Données :** PostgreSQL / MySQL (pour la gestion des données relationnelles).
*   **Authentification :** JWT (JSON Web Tokens) ou OAuth2.
*   **Déploiement :** Docker, Kubernetes (pour la conteneurisation et l'orchestration).

## 5. Annexes

### 5.1. Références

[1] Tracknow - Best Affiliate Tracking Software. Disponible sur : [https://www.tracknow.io/](https://www.tracknow.io/)



*   **Identifiants de connexion fournis :**
    *   Email : `jal18@live.fr`
    *   Mot de passe : `J@lil180683`

---

**Auteur :** Manus AI
**Date :** 22 Octobre 2025



## 3. Spécifications Techniques - Développement React avec Supabase

### 3.1. Architecture Générale

L'application sera développée en utilisant une architecture front-end moderne basée sur React, avec un back-end "as a service" fourni par Supabase. Cette approche permet de se concentrer sur l'expérience utilisateur tout en bénéficiant d'une infrastructure back-end robuste et scalable.

### 3.2. Technologies Front-end

- **Framework :** React (v18 ou supérieure)
- **Langage :** TypeScript
- **State Management :** React Context API pour les états simples, ou une bibliothèque comme Zustand ou Redux Toolkit pour les états plus complexes.
- **Routing :** React Router
- **Styling :** Tailwind CSS ou un autre framework CSS-in-JS comme Styled Components.
- **UI Components :** Une bibliothèque de composants comme Material-UI, Ant Design, ou des composants personnalisés.
- **Tests :** Jest et React Testing Library pour les tests unitaires et d'intégration.

### 3.3. Technologies Back-end (Supabase)

- **Base de données :** PostgreSQL (fourni par Supabase)
- **Authentification :** Supabase Auth pour la gestion des utilisateurs (inscription, connexion, réinitialisation de mot de passe, authentification via des fournisseurs tiers comme Google ou Facebook).
- **API :** Supabase Auto-generated APIs pour l'accès aux données de la base de données via des requêtes RESTful ou GraphQL.
- **Stockage :** Supabase Storage pour le stockage des fichiers (par exemple, les avatars des utilisateurs, les images des produits).
- **Fonctions Edge :** Supabase Edge Functions pour l'exécution de code côté serveur (par exemple, pour la logique métier complexe, les webhooks, ou l'intégration avec des services tiers).

### 3.4. Structure de la Base de Données (Schéma PostgreSQL)

Un schéma de base de données sera conçu pour supporter les fonctionnalités de l'application, incluant les tables suivantes :

- `users` : pour stocker les informations des utilisateurs (entreprises, commerciaux, influenceurs).
- `profiles` : pour stocker les informations de profil des utilisateurs.
- `offers` : pour stocker les offres de partenariat des entreprises.
- `applications` : pour stocker les candidatures des commerciaux et influenceurs aux offres.
- `links` : pour stocker les liens de suivi générés.
- `clicks` : pour suivre les clics sur les liens.
- `sales` : pour suivre les ventes générées via les liens.
- `commissions` : pour gérer les commissions des utilisateurs.

### 3.5. Déploiement

- **Front-end :** Déploiement sur une plateforme d'hébergement statique comme Vercel, Netlify, ou AWS S3/CloudFront.
- **Back-end :** L'infrastructure Supabase sera utilisée pour le back-end.
- **Intégration Continue / Déploiement Continu (CI/CD) :** Mise en place d'un pipeline CI/CD avec des outils comme GitHub Actions pour automatiser les tests et le déploiement.

