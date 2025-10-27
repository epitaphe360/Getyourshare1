# 🚂 Déploiement Railway - Configuration Automatique

## 🎯 Configuration Ultra-Rapide (1 clic)

Railway détecte automatiquement votre projet grâce aux fichiers `railway.toml` !

---

## 📦 Option 1 : Déploiement GitHub (Recommandé)

### Étape 1 : Connecter GitHub à Railway

1. Aller sur **[railway.app/new](https://railway.app/new)**
2. Cliquer sur **"Deploy from GitHub repo"**
3. Autoriser Railway à accéder à votre GitHub
4. Sélectionner le repository **`epitaphe360/Getyourshare1`**

### Étape 2 : Railway détecte automatiquement

Railway va automatiquement :
- ✅ Détecter les fichiers `railway.toml`
- ✅ Créer 2 services : **backend** et **frontend**
- ✅ Configurer les build commands
- ✅ Configurer les start commands
- ✅ Activer les health checks

**Aucune configuration manuelle nécessaire !** 🎉

### Étape 3 : Ajouter uniquement les variables d'environnement

#### Backend Service

Cliquer sur **backend** → **Variables** → Ajouter :

```bash
# ⚠️ OBLIGATOIRE - VOS VRAIES DONNÉES
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g
JWT_SECRET=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
SECRET_KEY=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==

# 🔧 Auto-configuré par Railway
PORT=${{PORT}}  # Railway l'injecte automatiquement

# 🌐 À configurer après déploiement frontend
FRONTEND_URL=${{frontend.url}}
CORS_ORIGINS=${{frontend.url}}
```

#### Frontend Service

Cliquer sur **frontend** → **Variables** → Ajouter :

```bash
# ⚠️ OBLIGATOIRE - VOS VRAIES DONNÉES
REACT_APP_API_URL=${{backend.url}}/api
REACT_APP_WS_URL=wss://${{backend.url}}/ws
REACT_APP_SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo

# 📱 Optionnel
REACT_APP_ENV=production
```

### Étape 4 : Déployer

Cliquer sur **"Deploy"** → Railway build et déploie automatiquement ! ⚡

**Temps estimé** : 3-5 minutes

### Étape 5 : Récupérer les URLs

Railway génère automatiquement :
- **Backend** : `https://backend-production-xxxx.up.railway.app`
- **Frontend** : `https://frontend-production-xxxx.up.railway.app`

### Étape 6 : Mettre à jour les variables croisées

Maintenant que vous avez les URLs, mettez à jour :

**Backend** :
```bash
FRONTEND_URL=https://frontend-production-xxxx.up.railway.app
CORS_ORIGINS=https://frontend-production-xxxx.up.railway.app
```

**Frontend** :
```bash
REACT_APP_API_URL=https://backend-production-xxxx.up.railway.app/api
REACT_APP_WS_URL=wss://backend-production-xxxx.up.railway.app/ws
```

Railway redéploie automatiquement après changement de variables.

---

## 📦 Option 2 : Déploiement CLI (Avancé)

### Installation Railway CLI

```powershell
npm install -g @railway/cli
```

### Login

```powershell
railway login
```

### Initialiser le projet

```powershell
cd c:\Users\Admin\Desktop\shareyoursales\Getyourshare1

# Créer nouveau projet
railway init

# Railway détecte automatiquement railway.toml
```

### Créer services

```powershell
# Backend
cd backend
railway up

# Frontend
cd ../frontend
railway up
```

### Configurer variables

```powershell
# Backend
railway variables set SUPABASE_URL=https://votre-projet.supabase.co
railway variables set SUPABASE_SERVICE_KEY=eyJhbGci...
railway variables set JWT_SECRET=$(openssl rand -hex 32)

# Frontend
railway variables set REACT_APP_API_URL=https://backend.railway.app/api
railway variables set REACT_APP_SUPABASE_URL=https://votre-projet.supabase.co
```

### Déployer

```powershell
railway up
```

---

## 🔧 Fichiers de Configuration Créés

### Backend (`backend/railway.toml`)
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "gunicorn server:app --bind 0.0.0.0:$PORT --workers 4"
healthcheckPath = "/health"
```

### Frontend (`frontend/railway.toml`)
```toml
[build]
builder = "NIXPACKS"
buildCommand = "npm ci && npm run build"

[deploy]
startCommand = "npx serve -s build -l $PORT"
healthcheckPath = "/"
```

### Racine (`railway.toml`) - Optionnel
Configuration monorepo pour gérer les 2 services d'un coup.

---

## ⚡ Fonctionnalités Automatiques

Railway configure automatiquement :

✅ **Build**
- Détection Python/Node.js
- Installation dépendances
- Compilation assets

✅ **Deploy**
- Port dynamique (`$PORT`)
- Health checks
- Restart automatique en cas d'erreur

✅ **Networking**
- HTTPS automatique
- URL publique
- Variables `${{service.url}}`

✅ **Monitoring**
- Logs en temps réel
- Métriques (CPU, RAM, réseau)
- Alertes

---

## 🎛️ Variables Railway Spéciales

Railway injecte automatiquement ces variables :

```bash
# Port automatique
${{PORT}}  # Ex: 8000

# URLs inter-services
${{backend.url}}  # URL du service backend
${{frontend.url}}  # URL du service frontend

# Database (si PostgreSQL Railway)
${{Postgres.DATABASE_URL}}
${{Postgres.POSTGRES_HOST}}
${{Postgres.POSTGRES_USER}}
```

Utilisez-les dans vos variables d'environnement !

---

## 🔄 Déploiement Automatique

Railway redéploie automatiquement sur :
- ✅ Push vers `main` (GitHub)
- ✅ Changement de variables d'environnement
- ✅ Modification `railway.toml`

**Désactiver auto-deploy** (optionnel) :
Railway Dashboard → Service → Settings → Deployments → Toggle OFF

---

## 🐛 Troubleshooting Automatique

Railway affiche automatiquement :

### Build logs
```powershell
railway logs --build
```

### Runtime logs
```powershell
railway logs
```

### Health check status
Dashboard → Service → Metrics → Health

Si health check échoue :
1. Vérifier que l'app écoute sur `0.0.0.0:$PORT`
2. Vérifier endpoint `/health` existe
3. Augmenter `healthcheckTimeout` si slow startup

---

## 💰 Pricing Auto-Calculé

Railway calcule automatiquement les coûts basés sur :
- ⏱️ Uptime (heures)
- 💾 RAM utilisée
- 🌐 Bandwidth

**Free Tier** : $5 de crédit/mois

**Estimation** :
- Backend : ~$5-8/mois
- Frontend : ~$3-5/mois
- **Total** : ~$8-13/mois

Dashboard → Billing → Usage pour voir en temps réel

---

## ✅ Checklist Déploiement Automatique

### Avant
- [x] `railway.toml` créé (backend + frontend)
- [x] `Procfile` créé
- [x] `requirements.txt` avec gunicorn
- [x] `package.json` avec script serve
- [x] `/health` endpoint existe

### Pendant
- [ ] Railway détecte automatiquement les services ✅
- [ ] Variables d'environnement configurées
- [ ] Build réussi (3-5 min)
- [ ] Deploy réussi
- [ ] Health checks passent

### Après
- [ ] URLs récupérées
- [ ] Variables croisées mises à jour
- [ ] Application accessible
- [ ] Tests smoke réussis

---

## 🚀 Commandes Rapides

```powershell
# Voir tous les services
railway status

# Logs temps réel
railway logs --follow

# Redéployer
railway up

# Variables
railway variables

# Ouvrir dashboard
railway open

# Lier à un service
railway link

# Exécuter commande dans environment Railway
railway run python manage.py migrate
```

---

## 📊 Monitoring Automatique

Railway Dashboard affiche automatiquement :

### Metrics
- CPU Usage (%)
- Memory Usage (MB)
- Network In/Out (GB)
- Request Count
- Response Time (ms)

### Logs
- Build logs
- Deploy logs
- Application logs
- Error logs

### Alerts
Configurez des alertes automatiques :
- CPU > 80%
- Memory > 90%
- Health check fails
- Deploy fails

---

## 🎯 Déploiement Zero-Config

Si vous avez tout configuré correctement, le déploiement est **littéralement 1 clic** :

1. Railway.app → Deploy from GitHub
2. Sélectionner repo
3. Ajouter variables d'environnement
4. ✅ **C'EST TOUT !**

Railway s'occupe de **TOUT** automatiquement :
- ✅ Détection du langage
- ✅ Installation dépendances
- ✅ Build
- ✅ Deploy
- ✅ HTTPS
- ✅ Health checks
- ✅ Monitoring
- ✅ Logs
- ✅ Auto-restart

---

## 🆘 Support

Railway a un support excellent :

- 💬 [Discord](https://discord.gg/railway) - Réponse rapide
- 📚 [Docs](https://docs.railway.app)
- 🎥 [YouTube Tutorials](https://youtube.com/@railwayapp)
- 📧 Support email pour plans payants

---

**🚂 Déploiement ultra-simplifié grâce à `railway.toml` ! 🚂**

**Temps total** : 5-10 minutes au lieu de 30+ ⚡
