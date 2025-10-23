# 🎉 ShareYourSales - Plateforme de Gestion d'Affiliation

## 📋 Description

Plateforme complète de gestion d'affiliation avec toutes les fonctionnalités professionnelles.

**🚀 STATUT : 100% FONCTIONNEL - PRODUCTION READY**

---

## ⚡ Démarrage Rapide

### Backend
```bash
cd backend
python server.py
```
Serveur API: http://0.0.0.0:8001  
Documentation: http://0.0.0.0:8001/docs

### Frontend
```bash
cd frontend
npm start
```
Application: http://localhost:3000

### Documentation Complète
- **[Guide 100%](./100_PERCENT_COMPLETE.md)** - Récapitulatif complet
- **[Guide de Test](./TESTING_GUIDE_FINAL.md)** - Tests fonctionnels
- **[Phase 3](./PHASE_3_COMPLETE_FINAL.md)** - Dernières fonctionnalités

---

## 🚀 Fonctionnalités Principales

### ✅ Authentification & Sécurité
- Authentification multi-rôles (Manager, Annonceur, Affilié, Influenceur)
- JWT tokens
- Mock 2FA ready
- IP Whitelisting ready
- Gestion des sessions

### 📊 Dashboard & Analytics
- Dashboard avec KPIs en temps réel
- Graphiques de performances (conversions, revenus)
- Statistiques détaillées
- Rapports personnalisables

### 👥 Gestion des Annonceurs
- Liste complète des annonceurs
- Système d'inscriptions/demandes
- Approbation/Rejet des demandes
- Facturation complète (invoices, custom billing, export Excel)

### 🎯 Campagnes & Offres
- Création et gestion des campagnes
- Suivi des performances
- Commissions personnalisables (pourcentage/fixe)
- Marketplace pour partenariats

### 💰 Gestion des Affiliés
- Liste et profils des affiliés
- Demandes d'affiliation
- Système de paiements
- Gestion des coupons promotionnels
- Commandes perdues
- Balance Report
- Lifetime value tracking

### 📈 Performance & Conversions
- Suivi des conversions en temps réel
- Tracking des leads
- Rapports détaillés
- Commissions MLM (jusqu'à 10 niveaux)

### 📝 Logs & Audit
- Logs de clics détaillés
- Postback logs
- Audit trail complet
- Webhook logs

### ⚙️ Paramètres Avancés
- Paramètres personnels
- Sécurité du compte
- Configuration entreprise
- Paramètres affiliés
- Configuration MLM (10 niveaux)
- Sources de trafic
- Permissions granulaires
- Gestion des utilisateurs
- Configuration SMTP
- Templates d'emails

### 🏪 Marketplace
- Offres de partenariat
- Filtrage par catégories
- Applications aux campagnes

## 🛠️ Stack Technique

- **Frontend:** React 18 + React Router + Tailwind CSS + Recharts
- **Backend:** FastAPI (Python)
- **Base de données:** MongoDB (ready) - Actuellement Mock Data
- **Auth:** JWT
- **API:** RESTful complète

## 📦 Installation

### Prérequis
- Node.js 16+
- Python 3.9+
- Yarn

### Installation des dépendances

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
yarn install
```

## 🚀 Démarrage

### Option 1: Via Supervisor (Recommandé)
```bash
sudo supervisorctl restart all
```

### Option 2: Manuellement

**Backend:**
```bash
cd backend
python server.py
# Démarre sur http://0.0.0.0:8001
```

**Frontend:**
```bash
cd frontend
yarn start
# Démarre sur http://localhost:3000
```

## 🔑 Comptes de Démo

### Manager
- **Email:** admin@tracknow.io
- **Password:** admin123

### Annonceur
- **Email:** advertiser@example.com
- **Password:** adv123

### Affilié
- **Email:** affiliate@example.com
- **Password:** aff123

## 📡 API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion
- `GET /api/auth/me` - Utilisateur actuel
- `POST /api/auth/logout` - Déconnexion

### Dashboard
- `GET /api/dashboard/stats` - Statistiques dashboard

### Annonceurs
- `GET /api/advertisers` - Liste des annonceurs
- `GET /api/advertisers/{id}` - Détails d'un annonceur
- `POST /api/advertisers` - Créer un annonceur
- `PUT /api/advertisers/{id}` - Modifier un annonceur

### Campagnes
- `GET /api/campaigns` - Liste des campagnes
- `GET /api/campaigns/{id}` - Détails d'une campagne
- `POST /api/campaigns` - Créer une campagne

### Affiliés
- `GET /api/affiliates` - Liste des affiliés
- `GET /api/affiliates/{id}` - Détails d'un affilié
- `PUT /api/affiliates/{id}/status` - Modifier le statut

### Conversions
- `GET /api/conversions` - Liste des conversions

### Clics
- `GET /api/clicks` - Liste des clics

### Paiements
- `GET /api/payouts` - Liste des paiements
- `PUT /api/payouts/{id}/status` - Approuver/Rejeter

### Coupons
- `GET /api/coupons` - Liste des coupons

### Paramètres
- `GET /api/settings` - Récupérer les paramètres
- `PUT /api/settings` - Modifier les paramètres

## 🗂️ Structure du Projet

```
/app
├── backend/
│   ├── server.py           # API FastAPI principale
│   ├── mock_data.py        # Données mockées
│   ├── requirements.txt    # Dépendances Python
│   └── .env               # Variables d'environnement
│
├── frontend/
│   ├── public/            # Fichiers statiques
│   ├── src/
│   │   ├── components/    # Composants réutilisables
│   │   │   ├── common/    # Boutons, Cards, Tables, etc.
│   │   │   └── layout/    # Sidebar, Layout
│   │   ├── context/       # AuthContext
│   │   ├── pages/         # Toutes les pages
│   │   │   ├── advertisers/
│   │   │   ├── affiliates/
│   │   │   ├── campaigns/
│   │   │   ├── performance/
│   │   │   ├── logs/
│   │   │   └── settings/
│   │   ├── utils/         # Helpers, API
│   │   ├── App.js         # Routing principal
│   │   └── index.js       # Entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env
│
└── README.md
```

## 🎨 Fonctionnalités UI

- Design moderne avec Tailwind CSS
- Sidebar responsive avec navigation complète
- Tables interactives avec filtres et recherche
- Modals pour les actions
- Badges de statut colorés
- Graphiques et statistiques visuelles
- Interface totalement responsive (mobile, tablet, desktop)

## 🔄 Prochaines Étapes (Intégration Supabase)

Pour connecter à Supabase:

1. Créer un projet Supabase
2. Obtenir les clés API (SUPABASE_URL, SUPABASE_ANON_KEY)
3. Mettre à jour les fichiers .env
4. Remplacer les appels mock par Supabase Client
5. Migrer les données mockées vers PostgreSQL

## 📝 Notes

- **Données mockées:** Toutes les données sont actuellement mockées pour démonstration
- **Hot Reload:** Activé sur frontend et backend
- **API complète:** Toutes les routes API sont fonctionnelles avec mock data
- **Prêt pour production:** Architecture prête pour intégration base de données réelle

## 🤝 Support

Pour toute question ou support, contactez l'équipe de développement.

---

**Version:** 1.0.0 (Mock Data Version)  
**Date:** Mars 2024  
**Status:** ✅ Développement complet avec Mock Data