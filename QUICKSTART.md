# ⚡ Démarrage Rapide - Railway + Supabase

Guide ultra-rapide pour déployer en **moins de 15 minutes**.

---

## 🎯 Vue d'Ensemble Rapide

1. **Supabase** (5 min) → Créer BDD + Tables
2. **Railway** (5 min) → Déployer Backend + Frontend
3. **Configuration** (5 min) → Variables d'environnement + Tests

**Total: ~15 minutes** ⏱️

---

## 📋 Checklist Avant de Commencer

- [ ] Compte GitHub avec le code poussé
- [ ] Compte Railway: https://railway.app (gratuit)
- [ ] Compte Supabase: https://supabase.com (gratuit)
- [ ] Compte Stripe: https://stripe.com (mode test)

---

## 🚀 ÉTAPE 1: Supabase (5 min)

### 1.1 Créer le Projet
```
1. https://app.supabase.com → New Project
2. Name: getyourshare-prod
3. Password: (générer un fort)
4. Region: Europe West (Paris)
5. Create → Attendre 2 min
```

### 1.2 Récupérer les Credentials
```
Settings → API → Copier:
✅ Project URL
✅ anon public
✅ service_role
```

### 1.3 Créer les Tables
```sql
-- SQL Editor → New Query → Coller:
-- Contenu de: backend/create_subscription_tables.sql
-- Run → Vérifier succès ✅
```

**✅ Supabase prêt!**

---

## 🚂 ÉTAPE 2: Railway Backend (5 min)

### 2.1 Créer le Projet
```
1. https://railway.app → New Project
2. Deploy from GitHub → Sélectionner: Getyourshare1
3. Railway détecte automatiquement
```

### 2.2 Configurer Backend

**Dans le service détecté:**
```
Settings → Root Directory: backend
Variables → Raw Editor → Coller:
```

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
JWT_SECRET_KEY=GENERER_CI_DESSOUS
JWT_ALGORITHM=HS256
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
APP_ENV=production
PORT=8001
ALLOWED_ORIGINS=*
AUTO_PAYMENTS_ENABLED=true
```

**Générer JWT_SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.3 Générer le Domaine
```
Settings → Networking → Generate Domain
Copier: https://backend-xxx.up.railway.app
```

**✅ Backend déployé!**

---

## 🌐 ÉTAPE 3: Railway Frontend (3 min)

### 3.1 Ajouter le Service Frontend

**Dans le même projet Railway:**
```
New Service → GitHub Repo → Même repo
Settings → Root Directory: frontend
```

### 3.2 Variables Frontend
```env
REACT_APP_API_URL=https://backend-xxx.up.railway.app
REACT_APP_SUPABASE_URL=https://xxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGc...
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
REACT_APP_ENVIRONMENT=production
PORT=80
```

### 3.3 Générer le Domaine Frontend
```
Settings → Networking → Generate Domain
Copier: https://frontend-xxx.up.railway.app
```

### 3.4 Mettre à Jour CORS Backend
```
Retour au service Backend
Variables → Modifier:
ALLOWED_ORIGINS=https://frontend-xxx.up.railway.app
```

**✅ Frontend déployé!**

---

## ✅ ÉTAPE 4: Tests (2 min)

### 4.1 Tester le Backend
```bash
curl https://backend-xxx.up.railway.app/health
# Devrait retourner: {"status":"healthy"}
```

### 4.2 Tester l'API Docs
```
Ouvrir: https://backend-xxx.up.railway.app/docs
Devrait afficher Swagger UI ✅
```

### 4.3 Tester le Frontend
```
Ouvrir: https://frontend-xxx.up.railway.app
Devrait afficher la page d'accueil ✅
```

### 4.4 Créer un Compte
```
1. Cliquer sur "S'inscrire"
2. Remplir le formulaire
3. Vérifier que ça fonctionne
```

**🎉 Application déployée et fonctionnelle!**

---

## 🔧 Configuration Avancée (Optionnel)

### Stripe Webhooks (Production)
```
1. https://dashboard.stripe.com/webhooks
2. Add endpoint: https://backend-xxx.up.railway.app/api/webhooks/stripe
3. Events: payment_intent.*, customer.subscription.*, invoice.*
4. Copier Signing Secret
5. Railway Backend → Variables → STRIPE_WEBHOOK_SECRET
```

### Email SMTP (Gmail)
```
1. Gmail → Security → 2FA → App Passwords
2. Generate → Mail → Copier le password
3. Railway Backend → Variables:
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=votre@gmail.com
   SMTP_PASSWORD=mot_de_passe_app
```

### Domaine Personnalisé
```
Railway → Settings → Custom Domain
Ajouter: api.votredomaine.com (backend)
Ajouter: app.votredomaine.com (frontend)

Chez votre registrar (Namecheap, GoDaddy, etc.):
CNAME api → backend-xxx.up.railway.app
CNAME app → frontend-xxx.up.railway.app
```

---

## 📊 Monitoring

### Voir les Logs
```
Railway → Service → Logs (onglet)
Rafraîchir pour voir en temps réel
```

### Métriques
```
Railway → Service → Metrics
CPU, RAM, Requêtes/sec
```

### Base de Données
```
Supabase → Table Editor
Voir les données en temps réel
```

---

## 🐛 Dépannage Express

### Backend ne démarre pas
```bash
# Vérifier les logs Railway
Railway → Backend → Logs

# Erreurs communes:
- Variables mal configurées → Revérifier .env
- Supabase inaccessible → Tester connexion
- Port déjà utilisé → Railway gère automatiquement
```

### Frontend ne se connecte pas
```bash
# Vérifier CORS
Backend Variables → ALLOWED_ORIGINS correct?

# Vérifier l'URL API
Frontend Variables → REACT_APP_API_URL correct?
```

### Erreur 502 Bad Gateway
```
Attendre 2-3 minutes (cold start)
Railway démarre le conteneur à la première requête
```

---

## 📚 Prochaines Étapes

1. **Documentation complète**: Lire `DEPLOY_RAILWAY.md`
2. **Système d'abonnement**: Lire `SUBSCRIPTION_SYSTEM.md`
3. **Tests avancés**: Tester tous les dashboards
4. **Sécurité**: Configurer Stripe Webhooks en production
5. **Domaine custom**: Configurer votre propre domaine

---

## 🆘 Besoin d'Aide?

- 📖 **Doc complète**: `DEPLOY_RAILWAY.md`
- 🐛 **Problèmes**: Consultez les logs Railway
- 💬 **Support Railway**: https://discord.gg/railway
- 📊 **Status Supabase**: https://status.supabase.com

---

## ✨ Résumé de Votre Déploiement

À la fin, vous aurez:

```
✅ Backend FastAPI sur Railway
✅ Frontend React sur Railway
✅ Base de données Supabase PostgreSQL
✅ API Documentation (Swagger)
✅ Système d'abonnement SaaS fonctionnel
✅ Dashboards Admin, Merchant, Influencer
✅ Paiements Stripe intégrés
✅ HTTPS automatique
✅ Monitoring Railway
✅ Sauvegardes automatiques Supabase
```

**🎊 Félicitations! Votre application est en production!**

---

*⚡ Generated with [Claude Code](https://claude.com/claude-code)*
