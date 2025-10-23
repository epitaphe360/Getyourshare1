# 📚 INDEX - SHAREYOURSALES PROJECT

## 📖 Documentation Principale

### 🚀 Guides de Démarrage
1. **[DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md)** - Guide de démarrage rapide
2. **[GUIDE_CREATION_TABLES.md](GUIDE_CREATION_TABLES.md)** - Création des tables Supabase (2-3 min)
3. **[DEVELOPPEMENT_COMPLET_RESUME.md](DEVELOPPEMENT_COMPLET_RESUME.md)** - Résumé complet du développement

### 📋 Documentation Technique
4. **[DEVELOPPEMENT_COMPLET.md](DEVELOPPEMENT_COMPLET.md)** - Plan de développement détaillé
5. **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** - Configuration Supabase
6. **[database/DATABASE_DOCUMENTATION.md](database/DATABASE_DOCUMENTATION.md)** - Documentation BDD

### 🐛 Suivi & Bugs
7. **[BUGS_CORRIGES.md](BUGS_CORRIGES.md)** - Historique des bugs corrigés
8. **[SESSION_FIXES.md](SESSION_FIXES.md)** - Corrections de session
9. **[PHASES_COMPLETEES.md](PHASES_COMPLETEES.md)** - Phases complétées

### 📐 Spécifications
10. **[Cahier_des_Charges_-_Application_Tracknow.io.md](Cahier_des_Charges_-_Application_Tracknow.io.md)** - Cahier des charges
11. **[SHAREYOURSALES_PROJECT.md](SHAREYOURSALES_PROJECT.md)** - Vue d'ensemble du projet

---

## 🎯 DÉMARRAGE RAPIDE (5 minutes)

### 1. Backend
```powershell
cd backend
python server.py
```
✅ Serveur sur http://localhost:8001

### 2. Frontend (Production)
```powershell
cd frontend
serve -s build
```
✅ Application sur http://localhost:52112

### 3. Créer les tables Supabase
📖 Voir **[GUIDE_CREATION_TABLES.md](GUIDE_CREATION_TABLES.md)**

---

## 🔑 COMPTES DE TEST

### Admin
- **Email:** admin@shareyoursales.com
- **Password:** Admin123!

### Marchand
- **Email:** contact@techstyle.fr
- **Password:** Merchant123!

### Influenceur
- **Email:** emma.style@instagram.com
- **Password:** Influencer123!

---

## 📁 STRUCTURE DU PROJET

```
Getyourshare1/
├── backend/               # API FastAPI + Supabase
│   ├── server.py         # Serveur principal ⭐
│   ├── advanced_helpers.py    # Fonctions CRUD ⭐
│   ├── advanced_endpoints.py  # Endpoints API ⭐
│   ├── .env              # Configuration Supabase
│   └── test_simple.ps1   # Script de test
│
├── frontend/             # Application React
│   ├── src/
│   │   ├── pages/       # Pages de l'application
│   │   ├── components/  # Composants réutilisables
│   │   └── context/     # Contextes React
│   └── build/           # Version compilée
│
├── database/            # Scripts SQL
│   ├── schema.sql       # Schéma principal
│   └── create_tables_missing.sql  # Tables à créer ⭐
│
└── docs/                # Documentation (ce fichier)
```

⭐ = Fichiers récemment créés/modifiés

---

## 🛠️ COMMANDES UTILES

### Backend
```powershell
# Démarrer le serveur
cd backend
python server.py

# Tester les endpoints
.\test_simple.ps1

# Seed la base de données
python seed_all_data.py

# Corriger les mots de passe
python fix_passwords.py
```

### Frontend
```powershell
# Mode développement
cd frontend
npm start

# Build production
npm run build

# Servir le build
serve -s build
```

### Base de données
```powershell
# Créer les tables manquantes
# 1. Ouvrir Supabase SQL Editor
# 2. Exécuter database/create_tables_missing.sql
```

---

## 📊 ENDPOINTS API DISPONIBLES

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/me` - Profil utilisateur

### Produits
- `GET /api/products` - Liste
- `POST /api/products` - Créer
- `PUT /api/products/{id}` - Modifier
- `DELETE /api/products/{id}` - Supprimer

### Campagnes
- `GET /api/campaigns` - Liste
- `PUT /api/campaigns/{id}` - Modifier
- `DELETE /api/campaigns/{id}` - Supprimer
- `POST /api/campaigns/{id}/products` - Assigner produits

### Invitations
- `POST /api/invitations` - Créer
- `POST /api/invitations/accept` - Accepter
- `GET /api/invitations/user/{id}` - Par utilisateur

### Ventes & Commissions
- `POST /api/sales` - Enregistrer vente
- `GET /api/sales/{id}` - Ventes influenceur
- `GET /api/commissions/{id}` - Commissions

### Paiements
- `POST /api/payouts/request` - Demander
- `PUT /api/payouts/{id}/approve` - Approuver
- `GET /api/payouts/user/{id}` - Par utilisateur

### Tracking
- `POST /api/tracking/click` - Enregistrer clic
- `GET /api/tracking/stats/{id}` - Statistiques

### Rapports
- `GET /api/reports/performance` - Performance

### Paramètres
- `GET /api/settings` - Liste
- `PUT /api/settings/{key}` - Modifier

**Total:** 30+ endpoints fonctionnels

---

## ✅ CHECKLIST DE MISE EN ROUTE

- [ ] Backend démarré (`python server.py`)
- [ ] Frontend démarré (`serve -s build`)
- [ ] Tables Supabase créées (voir GUIDE_CREATION_TABLES.md)
- [ ] Endpoints testés (`.\test_simple.ps1`)
- [ ] Connexion testée (admin@shareyoursales.com)
- [ ] Produits visibles dans Marketplace
- [ ] Campagnes visibles dans Dashboard

---

## 🆘 BESOIN D'AIDE ?

### Le serveur ne démarre pas
➡️ Vérifier que le port 8001 est libre
➡️ Vérifier le fichier `.env` dans backend/

### Erreur 401 Unauthorized
➡️ Vérifier que vous êtes connecté
➡️ Tester avec les comptes de test ci-dessus

### Erreur 404 sur un endpoint
➡️ Vérifier que le serveur backend est démarré
➡️ Vérifier l'URL: http://localhost:8001

### Les produits n'apparaissent pas
➡️ Exécuter `python seed_all_data.py` dans backend/
➡️ Vérifier la console du navigateur pour les erreurs

### Tables manquantes
➡️ Suivre le guide: **GUIDE_CREATION_TABLES.md**
➡️ Exécuter le SQL dans Supabase

---

## 📈 PROCHAINES ÉTAPES

1. ✅ Backend développé (30+ endpoints)
2. ✅ Frontend connecté (pages principales)
3. ⏳ Créer les 3 tables manquantes dans Supabase
4. ⏳ Tester tous les endpoints
5. ⏳ Ajouter l'upload de fichiers
6. ⏳ Implémenter les notifications email

---

## 📞 INFORMATIONS TECHNIQUES

### Stack Technologique
- **Backend:** Python 3.13 + FastAPI
- **Frontend:** React 18 + Tailwind CSS
- **Base de données:** Supabase PostgreSQL
- **Authentification:** JWT
- **Serveur:** Uvicorn (dev)

### URLs
- **Frontend:** http://localhost:52112
- **Backend API:** http://localhost:8001
- **Supabase:** https://iamezkmapbhlhhvvsits.supabase.co

### Dépendances
- Python: fastapi, supabase-py, bcrypt, uvicorn, pydantic
- Node: react, react-router-dom, tailwindcss, lucide-react

---

**Dernière mise à jour:** 22 octobre 2025  
**Version:** 2.0.0  
**Status:** ✅ Backend complet, ⏳ Tables à créer, ⏳ Tests à faire
