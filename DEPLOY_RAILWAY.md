# 🚀 Guide de Déploiement Railway + Supabase

Ce guide vous accompagne pas à pas pour déployer **GetYourShare** sur Railway avec Supabase comme base de données.

---

## 📋 Prérequis

- ✅ Compte Railway: https://railway.app
- ✅ Compte Supabase: https://supabase.com
- ✅ Compte Stripe: https://stripe.com (pour les paiements)
- ✅ Git installé localement
- ✅ Code source à jour sur GitHub

---

## 🎯 Architecture de Déploiement

```
┌─────────────────────────────────────────────────────────┐
│                    RAILWAY PLATFORM                      │
├───────────────────────┬─────────────────────────────────┤
│   Backend Service     │      Frontend Service            │
│   (FastAPI)           │      (React + Nginx)             │
│   Port: 8001          │      Port: 80                    │
└───────────┬───────────┴───────────────┬─────────────────┘
            │                           │
            └───────────┬───────────────┘
                        │
            ┌───────────▼──────────────┐
            │   SUPABASE PostgreSQL    │
            │   (Base de données)      │
            └──────────────────────────┘
```

---

## 📦 PARTIE 1: Configuration Supabase

### 1.1 Créer un Projet Supabase

1. Allez sur https://app.supabase.com
2. Cliquez sur **"New Project"**
3. Remplissez:
   - **Name**: `getyourshare-prod`
   - **Database Password**: Générez un mot de passe fort
   - **Region**: Choisissez la plus proche (ex: `Europe West (Paris)`)
4. Cliquez sur **"Create new project"**
5. ⏳ Attendez 2-3 minutes que le projet soit créé

### 1.2 Récupérer les Credentials Supabase

1. Dans votre projet, allez dans **Settings** → **API**
2. Notez ces 3 valeurs importantes:
   ```
   Project URL: https://xxxxxxxxxxxxx.supabase.co
   anon public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### 1.3 Créer les Tables de Base de Données

1. Allez dans **SQL Editor** dans la sidebar
2. Cliquez sur **"New query"**
3. **IMPORTANT**: Exécutez ces scripts SQL dans l'ordre:

#### Script 1: Tables principales
```bash
# Copiez et collez le contenu de votre fichier:
cat backend/create_subscription_tables.sql
```

4. Cliquez sur **"Run"** pour exécuter
5. Vérifiez qu'il n'y a pas d'erreurs

#### Script 2: Vérification
```sql
-- Vérifier que toutes les tables ont été créées
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Vous devriez voir au moins ces tables:
- users
- products
- campaigns
- subscription_plans
- subscriptions
- invoices
- payment_transactions
- etc.

---

## 🚂 PARTIE 2: Configuration Railway

### 2.1 Créer un Compte Railway

1. Allez sur https://railway.app
2. Cliquez sur **"Login"** et utilisez GitHub
3. Autorisez Railway à accéder à vos repos GitHub

### 2.2 Créer un Nouveau Projet

1. Cliquez sur **"New Project"**
2. Sélectionnez **"Deploy from GitHub repo"**
3. Choisissez votre repo: `epitaphe360/Getyourshare1`
4. Railway détectera automatiquement les Dockerfiles

### 2.3 Configuration du Backend

1. Railway créera un service pour le backend
2. Cliquez sur le service **backend**
3. Allez dans **Variables**
4. Cliquez sur **"Raw Editor"**
5. Copiez-collez toutes les variables suivantes:

```env
# SUPABASE
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=votre_anon_key
SUPABASE_SERVICE_ROLE_KEY=votre_service_role_key

# JWT
JWT_SECRET_KEY=generer_avec_commande_ci_dessous
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# STRIPE
STRIPE_SECRET_KEY=sk_test_votre_cle
STRIPE_PUBLISHABLE_KEY=pk_test_votre_cle
STRIPE_WEBHOOK_SECRET=whsec_votre_secret

# APPLICATION
APP_ENV=production
APP_DEBUG=false
PORT=8001

# EMAIL (Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=votre_app_password
SMTP_FROM_EMAIL=noreply@getyourshare.com

# CORS
ALLOWED_ORIGINS=https://votre-frontend.railway.app

# SCHEDULER
AUTO_PAYMENTS_ENABLED=true
SCHEDULER_TIMEZONE=Africa/Casablanca
```

#### Générer JWT_SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

6. Cliquez sur **"Add Variables"**

### 2.4 Configuration du Build Backend

1. Dans le service backend, allez dans **Settings**
2. **Root Directory**: `backend`
3. **Dockerfile Path**: `backend/Dockerfile`
4. **Start Command**: Laissez vide (utilisera la commande du Dockerfile)
5. **Health Check Path**: `/health`
6. Sauvegardez

### 2.5 Configuration du Frontend

1. Cliquez sur **"New Service"** → **"GitHub Repo"**
2. Sélectionnez le même repo
3. Configurez:
   - **Root Directory**: `frontend`
   - **Dockerfile Path**: `frontend/Dockerfile`

4. Allez dans **Variables** du frontend:
```env
REACT_APP_API_URL=https://votre-backend.railway.app
REACT_APP_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=votre_anon_key
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_votre_cle
REACT_APP_ENVIRONMENT=production
PORT=80
```

### 2.6 Générer les Domaines

1. Pour le **Backend**:
   - Allez dans **Settings** → **Networking**
   - Cliquez sur **"Generate Domain"**
   - Notez l'URL: `https://backend-production-xxxx.up.railway.app`

2. Pour le **Frontend**:
   - Même chose, générez un domaine
   - Notez l'URL: `https://frontend-production-xxxx.up.railway.app`

3. **IMPORTANT**: Mettez à jour les variables d'environnement:
   - Dans le **Frontend**: `REACT_APP_API_URL` = URL du backend
   - Dans le **Backend**: `ALLOWED_ORIGINS` = URL du frontend

---

## 🔧 PARTIE 3: Déploiement et Tests

### 3.1 Déclencher le Déploiement

Railway déploiera automatiquement. Suivez les logs:

1. Cliquez sur le service **backend**
2. Allez dans **Deployments**
3. Cliquez sur le dernier déploiement
4. Regardez les logs en temps réel

Attendez les messages:
```
✅ Build successful
✅ Deployment successful
🚀 Démarrage du serveur ShareYourSales API
📊 Base de données: Supabase PostgreSQL
```

### 3.2 Vérifier la Santé du Backend

```bash
# Testez l'endpoint de santé
curl https://votre-backend.railway.app/health

# Devrait retourner: {"status": "healthy"}
```

### 3.3 Tester l'API Documentation

Ouvrez dans votre navigateur:
```
https://votre-backend.railway.app/docs
```

Vous devriez voir la documentation Swagger interactive.

### 3.4 Vérifier le Frontend

1. Ouvrez: `https://votre-frontend.railway.app`
2. La page d'accueil devrait s'afficher
3. Testez l'inscription/connexion

---

## 🔐 PARTIE 4: Sécurisation Production

### 4.1 Configurer Stripe Webhooks

1. Allez sur https://dashboard.stripe.com/webhooks
2. Cliquez sur **"Add endpoint"**
3. URL: `https://votre-backend.railway.app/api/webhooks/stripe`
4. Sélectionnez ces événements:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
5. Notez le **Signing secret** et ajoutez-le dans Railway: `STRIPE_WEBHOOK_SECRET`

### 4.2 Configurer Email SMTP (Gmail)

1. Allez sur https://myaccount.google.com/security
2. Activez la **Validation en deux étapes**
3. Allez dans **Mots de passe d'application**
4. Créez un mot de passe pour "Mail"
5. Copiez le mot de passe (16 caractères)
6. Dans Railway, mettez à jour:
   - `SMTP_USER`: votre.email@gmail.com
   - `SMTP_PASSWORD`: le mot de passe généré

### 4.3 Configurer CORS Proprement

Dans Railway Backend, mettez à jour `ALLOWED_ORIGINS`:
```env
ALLOWED_ORIGINS=https://votre-frontend.railway.app,https://votre-domaine-custom.com
```

### 4.4 Configurer un Domaine Personnalisé (Optionnel)

1. Dans Railway, allez dans **Settings** → **Domains**
2. Cliquez sur **"Custom Domain"**
3. Entrez votre domaine: `api.votre-domaine.com` (backend)
4. Ajoutez un enregistrement CNAME chez votre registrar:
   ```
   Type: CNAME
   Name: api
   Value: backend-production-xxxx.up.railway.app
   ```

5. Répétez pour le frontend: `app.votre-domaine.com`

---

## 📊 PARTIE 5: Monitoring et Maintenance

### 5.1 Surveiller les Logs

Dans Railway, chaque service a un onglet **Logs**:
- Consultez régulièrement les erreurs
- Configurez des alertes si nécessaire

### 5.2 Métriques

Railway affiche automatiquement:
- CPU usage
- Memory usage
- Network in/out
- Request count

### 5.3 Base de Données Supabase

1. Dashboard: https://app.supabase.com
2. Consultez:
   - **Table Editor**: Voir les données
   - **SQL Editor**: Exécuter des requêtes
   - **Database** → **Backups**: Sauvegardes automatiques

### 5.4 Sauvegardes Automatiques

Supabase fait des sauvegardes automatiques:
- **Quotidiennes** pour les projets gratuits
- **Point-in-time recovery** pour les projets Pro

Pour restaurer:
1. Allez dans **Database** → **Backups**
2. Sélectionnez la sauvegarde
3. Cliquez sur **"Restore"**

---

## 🐛 PARTIE 6: Troubleshooting

### Problème 1: Backend ne démarre pas

**Vérifiez les logs Railway:**
```
Error: Could not connect to database
```

**Solution:**
- Vérifiez `SUPABASE_URL` et `SUPABASE_KEY`
- Testez la connexion depuis votre machine locale
- Vérifiez que Supabase n'a pas de limitations IP

### Problème 2: Frontend ne se connecte pas au Backend

**Erreur dans la console:**
```
CORS error: No 'Access-Control-Allow-Origin' header
```

**Solution:**
1. Dans Railway Backend, vérifiez `ALLOWED_ORIGINS`
2. Ajoutez l'URL exacte du frontend (avec https://)
3. Redéployez le backend

### Problème 3: Les paiements Stripe ne marchent pas

**Vérifications:**
1. Mode Test vs Production:
   - Clés `sk_test_` pour test
   - Clés `sk_live_` pour production
2. Webhooks configurés correctement
3. `STRIPE_WEBHOOK_SECRET` correspond au webhook Railway

### Problème 4: Emails ne partent pas

**Vérifiez:**
1. App Password Gmail généré correctement
2. Variables `SMTP_*` correctement renseignées
3. Port 587 non bloqué
4. Testez avec un outil: https://www.smtper.net/

### Problème 5: Build échoue

**Erreur commune:**
```
Error: Cannot find module 'xyz'
```

**Solutions:**
1. Vérifiez `requirements.txt` (backend) ou `package.json` (frontend)
2. Ajoutez la dépendance manquante
3. Committez et poussez sur GitHub
4. Railway redéploiera automatiquement

---

## 🎉 PARTIE 7: Post-Déploiement

### 7.1 Créer un Compte Admin

```bash
# Exécutez depuis votre machine locale
curl -X POST https://votre-backend.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@getyourshare.com",
    "password": "VotreMotDePasseSecurise123!",
    "user_type": "admin",
    "company_name": "GetYourShare Admin"
  }'
```

### 7.2 Générer des Données de Test

```bash
# SSH vers Railway (si nécessaire)
railway run python backend/seed_comprehensive_dashboard_data.py
```

Ou utilisez l'interface Supabase SQL Editor.

### 7.3 Tester le Système d'Abonnement

1. Créez un compte marchand
2. Allez dans **Abonnements**
3. Sélectionnez un plan (utilisez une carte de test Stripe)
4. Vérifiez que:
   - Le paiement est enregistré
   - L'abonnement est actif
   - Une facture PDF est générée

### 7.4 Tester les Dashboards

1. **Admin Dashboard**: `https://votre-frontend/admin/dashboard`
2. **Merchant Dashboard**: `https://votre-frontend/merchant/dashboard`
3. **Influencer Dashboard**: `https://votre-frontend/influencer/dashboard`

Vérifiez que toutes les données s'affichent correctement.

---

## 📚 Ressources Utiles

- **Railway Docs**: https://docs.railway.app
- **Supabase Docs**: https://supabase.com/docs
- **Stripe Docs**: https://stripe.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

---

## 🆘 Support

En cas de problème:

1. **Logs Railway**: Consultez toujours les logs en premier
2. **Supabase Status**: https://status.supabase.com
3. **Railway Status**: https://railway.statuspage.io
4. **Community Discord Railway**: https://discord.gg/railway
5. **GitHub Issues**: Créez une issue sur votre repo

---

## ✅ Checklist Finale de Déploiement

Avant de considérer le déploiement comme terminé:

- [ ] Backend déployé et accessible
- [ ] Frontend déployé et accessible
- [ ] Base de données Supabase opérationnelle
- [ ] Tables créées et données de test insérées
- [ ] Stripe configuré (clés + webhooks)
- [ ] SMTP configuré (emails de test envoyés)
- [ ] CORS configuré correctement
- [ ] Domaines personnalisés configurés (si applicable)
- [ ] Monitoring activé
- [ ] Sauvegardes Supabase activées
- [ ] Variables d'environnement de production définies
- [ ] Tests de bout en bout effectués
- [ ] Compte admin créé
- [ ] Dashboards testés et fonctionnels

---

## 🎊 Félicitations!

Votre application **GetYourShare** est maintenant déployée en production sur Railway avec Supabase! 🚀

**URLs Importantes:**
- Frontend: `https://votre-frontend.railway.app`
- Backend API: `https://votre-backend.railway.app`
- API Docs: `https://votre-backend.railway.app/docs`
- Supabase Dashboard: `https://app.supabase.com`
- Railway Dashboard: `https://railway.app/dashboard`

---

*📖 Generated with [Claude Code](https://claude.com/claude-code)*
