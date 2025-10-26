# 🚂 DÉPLOIEMENT RAILWAY - GUIDE COMPLET

## ⚠️ PROBLÈME ACTUEL

**Erreur**: `Dockerfile does not exist`

**Cause**: Votre projet a 2 services (Backend + Frontend) mais Railway cherche un seul Dockerfile à la racine.

---

## ✅ SOLUTION: 2 Services Railway

Vous devez créer **2 services séparés** sur Railway:
1. **Service Backend** (API FastAPI)
2. **Service Frontend** (React)

---

## 📋 ÉTAPE 1: CRÉER SERVICE BACKEND

### 1.1 Créer Nouveau Service

1. Aller sur [railway.app](https://railway.app)
2. Ouvrir votre projet
3. Cliquer **"+ New Service"**
4. Sélectionner **"GitHub Repo"**
5. Choisir: `epitaphe360/Getyourshare1`

### 1.2 Configuration Backend

**Service Settings > Build**:
```
Builder: Dockerfile
Root Directory: backend
Dockerfile Path: Dockerfile
```

**Service Settings > Deploy**:
```
Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT --workers 4
Healthcheck Path: /health
```

### 1.3 Variables d'Environnement Backend

**Service Settings > Variables**:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...votre-clé
SUPABASE_ANON_KEY=eyJhbGc...votre-clé-publique

# Stripe
STRIPE_SECRET_KEY=sk_live_...votre-clé
STRIPE_PUBLISHABLE_KEY=pk_live_...votre-clé
STRIPE_WEBHOOK_SECRET=whsec_...votre-secret

# JWT
JWT_SECRET=votre-secret-aleatoire-tres-long
JWT_ALGORITHM=HS256

# Frontend URL (sera rempli après déploiement frontend)
FRONTEND_URL=https://votre-frontend.up.railway.app

# Port (Railway le définit automatiquement)
PORT=${{PORT}}
```

### 1.4 Déployer Backend

1. Cliquer **"Deploy"**
2. Attendre le build (3-5 minutes)
3. Noter l'URL: `https://your-backend.up.railway.app`

---

## 📋 ÉTAPE 2: CRÉER SERVICE FRONTEND

### 2.1 Créer Nouveau Service

1. Dans le même projet Railway
2. Cliquer **"+ New Service"** (à nouveau)
3. Sélectionner **"GitHub Repo"**
4. Choisir: `epitaphe360/Getyourshare1`

### 2.2 Configuration Frontend

**Service Settings > Build**:
```
Builder: Dockerfile
Root Directory: frontend
Dockerfile Path: Dockerfile
```

**Service Settings > Deploy**:
```
Healthcheck Path: /
Port: 80
```

### 2.3 Variables d'Environnement Frontend

**Service Settings > Variables**:

```bash
# Backend API URL (l'URL du service backend créé à l'étape 1)
REACT_APP_API_URL=https://your-backend.up.railway.app

# Stripe clé publique
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_...

# Supabase publique
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGc...votre-clé-publique
```

### 2.4 Déployer Frontend

1. Cliquer **"Deploy"**
2. Attendre le build (3-5 minutes)
3. Noter l'URL: `https://your-frontend.up.railway.app`

---

## 📋 ÉTAPE 3: METTRE À JOUR BACKEND

### 3.1 Ajouter Frontend URL

1. Retourner au **service Backend**
2. **Settings > Variables**
3. Modifier `FRONTEND_URL`:
   ```bash
   FRONTEND_URL=https://your-frontend.up.railway.app
   ```
4. **Redéployer** le backend

---

## 🔧 ÉTAPE 4: CONFIGURATION SUPABASE

### 4.1 Appliquer les Migrations SQL

1. Aller sur [app.supabase.com](https://app.supabase.com)
2. Ouvrir votre projet
3. **SQL Editor** > **New Query**
4. Copier et exécuter **dans l'ordre**:

```bash
# 1. Tables principales
database/migrations/init.sql

# 2. Système d'abonnement
database/migrations/create_subscriptions.sql

# 3. Système d'annuaires
database/migrations/create_directories_system.sql

# 4. Modification produits
database/migrations/alter_products_add_type.sql
```

### 4.2 Activer RLS (Row Level Security)

Les migrations incluent déjà les politiques RLS. Vérifier:
```sql
-- Vérifier que RLS est activé
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';
```

Toutes les tables doivent avoir `rowsecurity = true`.

---

## 🔧 ÉTAPE 5: CONFIGURATION STRIPE

### 5.1 Créer Produits Stripe

1. Aller sur [dashboard.stripe.com](https://dashboard.stripe.com)
2. **Products** > **Add Product**
3. Créer les 4 plans:

**Plan SMALL BUSINESS**:
```
Name: Small Business
Description: 2 membres d'équipe, 1 domaine
Price: 199 MAD/mois (ou 1990 MAD/an)
Recurring: Monthly
```

**Plan MEDIUM BUSINESS**:
```
Name: Medium Business
Description: 10 membres d'équipe, 2 domaines
Price: 499 MAD/mois (ou 4990 MAD/an)
Recurring: Monthly
```

**Plan LARGE BUSINESS**:
```
Name: Large Business
Description: 30 membres d'équipe, domaines illimités
Price: 799 MAD/mois (ou 7990 MAD/an)
Recurring: Monthly
```

**Plan MARKETPLACE INFLUENCER**:
```
Name: Marketplace Influencer
Description: Accès marketplace pour influenceurs
Price: 99 MAD/mois
Recurring: Monthly
```

### 5.2 Configurer Webhook Stripe

1. **Developers** > **Webhooks** > **Add endpoint**
2. **Endpoint URL**: `https://your-backend.up.railway.app/api/stripe/webhook`
3. **Events to send**:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copier le **Signing Secret** (commence par `whsec_`)
5. Ajouter dans Railway Backend Variables:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

---

## 🌐 ÉTAPE 6: DOMAINE PERSONNALISÉ (Optionnel)

### 6.1 Backend Custom Domain

**Railway Backend Service > Settings > Networking**:
```
Custom Domain: api.shareyoursales.com
```

Puis ajouter dans votre DNS:
```
Type: CNAME
Name: api
Value: your-backend.up.railway.app
```

### 6.2 Frontend Custom Domain

**Railway Frontend Service > Settings > Networking**:
```
Custom Domain: shareyoursales.com (ou www.shareyoursales.com)
```

Puis ajouter dans votre DNS:
```
Type: CNAME
Name: @ (ou www)
Value: your-frontend.up.railway.app
```

### 6.3 Mettre à Jour Variables

Une fois domaines configurés:

**Backend**:
```bash
FRONTEND_URL=https://shareyoursales.com
```

**Frontend**:
```bash
REACT_APP_API_URL=https://api.shareyoursales.com
```

---

## ✅ VÉRIFICATION FINALE

### Test Backend

```bash
curl https://your-backend.up.railway.app/health

# Réponse attendue:
{"status":"healthy"}
```

### Test Frontend

1. Ouvrir: `https://your-frontend.up.railway.app`
2. Vérifier que la page charge
3. Tester connexion utilisateur
4. Vérifier que marketplace fonctionne

### Test Complet

1. **Inscription**: Créer nouveau compte
2. **Login**: Se connecter
3. **Marketplace**: Parcourir produits
4. **Abonnement**: Tester paiement (mode test Stripe)
5. **Dashboard**: Vérifier données affichées

---

## 🐛 RÉSOLUTION PROBLÈMES

### Backend ne démarre pas

**Vérifier les logs**:
1. Railway Backend Service
2. **Deployments** > Dernier déploiement
3. **Logs**

**Erreurs courantes**:
```bash
# Erreur: Missing Supabase variables
→ Vérifier SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY

# Erreur: Missing Stripe variables
→ Vérifier STRIPE_SECRET_KEY et STRIPE_WEBHOOK_SECRET

# Erreur: Port binding
→ Vérifier que START_COMMAND utilise $PORT
```

### Frontend affiche erreur CORS

**Problème**: Backend refuse les requêtes du frontend

**Solution**: Vérifier dans Backend Variables:
```bash
FRONTEND_URL=https://your-frontend.up.railway.app
```

Redéployer le backend.

### Webhook Stripe ne fonctionne pas

**Vérifier**:
1. URL webhook correcte dans Stripe Dashboard
2. `STRIPE_WEBHOOK_SECRET` correctement configuré
3. Logs backend pour voir les erreurs

### Base de données vide

**Problème**: Tables n'existent pas

**Solution**: Exécuter les migrations SQL dans Supabase (Étape 4)

---

## 📦 STRUCTURE FINALE

```
Railway Project: Getyourshare1
│
├── Service 1: Backend (API)
│   ├── URL: https://your-backend.up.railway.app
│   ├── Root: backend/
│   ├── Dockerfile: backend/Dockerfile
│   └── Port: $PORT (assigné par Railway)
│
├── Service 2: Frontend (React)
│   ├── URL: https://your-frontend.up.railway.app
│   ├── Root: frontend/
│   ├── Dockerfile: frontend/Dockerfile
│   └── Port: 80
│
└── Database: Supabase (externe)
    └── URL: https://your-project.supabase.co
```

---

## 💰 COÛTS RAILWAY

**Plan Gratuit (Hobby)**:
- $5 de crédit/mois
- Suffisant pour tester

**Plan Pro ($20/mois)**:
- Requis pour production
- Usage illimité
- Support prioritaire

**Estimation pour votre app**:
- Backend: ~$10/mois
- Frontend: ~$5/mois
- **Total**: ~$15/mois (Plan Pro recommandé)

---

## 📝 CHECKLIST DÉPLOIEMENT

### Avant de déployer

- [ ] Migrations SQL prêtes
- [ ] Variables d'environnement notées
- [ ] Compte Stripe configuré
- [ ] Projet Supabase créé
- [ ] Code pushé sur GitHub

### Service Backend

- [ ] Service créé sur Railway
- [ ] Root directory: `backend`
- [ ] Dockerfile path: `Dockerfile`
- [ ] Variables d'environnement configurées
- [ ] Déployé avec succès
- [ ] Health check passe
- [ ] URL notée

### Service Frontend

- [ ] Service créé sur Railway
- [ ] Root directory: `frontend`
- [ ] Dockerfile path: `Dockerfile`
- [ ] REACT_APP_API_URL configuré
- [ ] Déployé avec succès
- [ ] Page charge correctement
- [ ] URL notée

### Configuration Externe

- [ ] Migrations SQL appliquées sur Supabase
- [ ] Produits Stripe créés
- [ ] Webhook Stripe configuré
- [ ] FRONTEND_URL mis à jour dans backend
- [ ] Backend redéployé

### Tests

- [ ] Backend health check OK
- [ ] Frontend charge
- [ ] Login fonctionne
- [ ] Marketplace visible
- [ ] Paiement test OK (Stripe)
- [ ] Dashboard affiche données

---

## 🆘 BESOIN D'AIDE?

**Documentation Railway**: https://docs.railway.app
**Support Railway**: https://railway.app/help

---

```
╔═══════════════════════════════════════════════════╗
║                                                   ║
║  🚂 DÉPLOIEMENT RAILWAY                           ║
║                                                   ║
║  2 SERVICES REQUIS:                               ║
║                                                   ║
║  1️⃣ Backend (API FastAPI)                        ║
║     Root: backend/                                ║
║     Dockerfile: backend/Dockerfile                ║
║                                                   ║
║  2️⃣ Frontend (React)                             ║
║     Root: frontend/                               ║
║     Dockerfile: frontend/Dockerfile               ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

**Date**: 25 Octobre 2025
**Version**: 1.0
**Statut**: ✅ Prêt pour déploiement
