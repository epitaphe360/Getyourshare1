# 🚂 Déploiement Railway - ShareYourSales

## 📋 Vue d'ensemble

Ce guide détaille le déploiement complet de ShareYourSales sur Railway, incluant :
- Backend Python (Flask/FastAPI)
- Frontend React
- Base de données PostgreSQL (Supabase)
- Serveur WebSocket

---

## 🎯 Prérequis

### Compte Railway
1. Créer un compte sur [railway.app](https://railway.app)
2. Connecter votre compte GitHub
3. Installer Railway CLI (optionnel mais recommandé)

```powershell
# Installation Railway CLI
npm install -g @railway/cli

# Login
railway login
```

### Repository GitHub
- Repository public ou privé connecté à Railway
- Branch principale : `main`

---

## 📦 Étape 1 : Préparation du Backend

### 1.1 Créer `Procfile`

Railway utilise ce fichier pour savoir comment démarrer votre application.

**Fichier** : `backend/Procfile`

```
web: gunicorn server:app --bind 0.0.0.0:$PORT --workers 4
websocket: python websocket_server.py
```

### 1.2 Créer `railway.json`

Configuration Railway pour le backend.

**Fichier** : `backend/railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "gunicorn server:app --bind 0.0.0.0:$PORT --workers 4",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### 1.3 Mettre à jour `requirements.txt`

Ajouter Gunicorn pour production :

```txt
gunicorn==21.2.0
gevent==23.9.1
```

### 1.4 Créer endpoint health check

**Fichier** : `backend/server.py`

Ajouter cette route :

```python
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'backend'
    }), 200
```

---

## 📦 Étape 2 : Préparation du Frontend

### 2.1 Créer `railway.json`

**Fichier** : `frontend/railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm ci && npm run build"
  },
  "deploy": {
    "startCommand": "npx serve -s build -l $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 30
  }
}
```

### 2.2 Installer `serve`

Pour servir le build React en production :

```powershell
cd frontend
npm install --save-dev serve
```

### 2.3 Ajouter script dans `package.json`

```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "serve": "serve -s build -l $PORT"
  }
}
```

---

## 🗄️ Étape 3 : Configuration Base de Données

### Option A : Utiliser Supabase existant

Si vous avez déjà Supabase configuré, il suffit de configurer les variables d'environnement.

### Option B : PostgreSQL Railway

Railway peut provisionner une base PostgreSQL automatiquement.

1. Dans Railway Dashboard → New → Database → PostgreSQL
2. Railway génère automatiquement `DATABASE_URL`

---

## 🚀 Étape 4 : Déploiement sur Railway

### Méthode 1 : Via Railway Dashboard (Recommandé)

#### 4.1 Créer nouveau projet

1. Aller sur [railway.app/new](https://railway.app/new)
2. Choisir "Deploy from GitHub repo"
3. Sélectionner `epitaphe360/Getyourshare1`
4. Railway détecte automatiquement backend et frontend

#### 4.2 Configurer Backend Service

**Service Name** : `backend`

**Root Directory** : `/backend`

**Variables d'environnement** :

```bash
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT
JWT_SECRET=<générer avec: openssl rand -hex 32>
JWT_EXPIRATION=86400

# Server
PORT=8000
BACKEND_HOST=0.0.0.0

# Frontend URL (sera généré par Railway)
FRONTEND_URL=https://your-frontend.railway.app

# CORS
CORS_ORIGINS=https://your-frontend.railway.app

# Database (si PostgreSQL Railway)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Feature Flags
DEBUG=False
NODE_ENV=production
```

**Build Command** : `pip install -r requirements.txt`

**Start Command** : `gunicorn server:app --bind 0.0.0.0:$PORT --workers 4`

#### 4.3 Configurer Frontend Service

**Service Name** : `frontend`

**Root Directory** : `/frontend`

**Variables d'environnement** :

```bash
# API URLs (généré par Railway)
REACT_APP_API_URL=https://your-backend.railway.app/api
REACT_APP_WS_URL=wss://your-backend.railway.app/ws

# Supabase
REACT_APP_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Stripe
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_...

# App Config
REACT_APP_ENV=production
REACT_APP_NAME=ShareYourSales
```

**Build Command** : `npm ci && npm run build`

**Start Command** : `npx serve -s build -l $PORT`

#### 4.4 Configurer WebSocket Service (Optionnel)

**Service Name** : `websocket`

**Root Directory** : `/backend`

**Variables d'environnement** : (mêmes que backend)

**Start Command** : `python websocket_server.py`

**Port** : 8080

---

### Méthode 2 : Via Railway CLI

```powershell
# Se placer dans le répertoire du projet
cd c:\Users\Admin\Desktop\shareyoursales\Getyourshare1

# Initialiser Railway
railway init

# Lier au projet GitHub
railway link

# Déployer backend
cd backend
railway up

# Déployer frontend
cd ../frontend
railway up
```

---

## 🔧 Étape 5 : Configuration Post-Déploiement

### 5.1 Récupérer les URLs Railway

Après déploiement, Railway génère des URLs publiques :

- **Backend** : `https://shareyoursales-backend-production.up.railway.app`
- **Frontend** : `https://shareyoursales-frontend-production.up.railway.app`

### 5.2 Mettre à jour CORS Backend

Dans `backend/server.py` :

```python
from flask_cors import CORS

app = Flask(__name__)

# Production CORS
CORS(app, origins=[
    'https://shareyoursales-frontend-production.up.railway.app',
    'https://your-custom-domain.com'  # Si domaine personnalisé
])
```

### 5.3 Mettre à jour variables Frontend

Redéployer frontend avec les bonnes URLs Railway :

```bash
REACT_APP_API_URL=https://shareyoursales-backend-production.up.railway.app/api
REACT_APP_WS_URL=wss://shareyoursales-backend-production.up.railway.app/ws
```

### 5.4 Appliquer Migrations SQL

```powershell
# Via Railway CLI
railway run python apply_migrations.py

# OU via Supabase Dashboard
# SQL Editor → Exécuter les migrations manuellement
```

---

## 🔐 Étape 6 : Sécurité Production

### 6.1 Activer HTTPS

Railway active automatiquement HTTPS. Mettre à jour :

```bash
# backend/.env
COOKIE_SECURE=true
SESSION_SECURE=true
```

### 6.2 Configurer Stripe Webhooks

1. Stripe Dashboard → Webhooks → Add endpoint
2. URL : `https://your-backend.railway.app/api/webhooks/stripe`
3. Events : `payment_intent.succeeded`, `charge.failed`, etc.
4. Copier `Signing secret` → Variable `STRIPE_WEBHOOK_SECRET`

### 6.3 Configurer Rate Limiting

Installer Flask-Limiter :

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ...
```

---

## 📊 Étape 7 : Monitoring

### 7.1 Railway Metrics

Railway Dashboard → Votre service → Metrics

Affiche :
- CPU usage
- Memory usage
- Network traffic
- Request count
- Response time

### 7.2 Logs

```powershell
# Via CLI
railway logs

# Filtrer par service
railway logs --service backend

# Suivre en temps réel
railway logs --follow
```

### 7.3 Health Checks

Railway vérifie automatiquement `/api/health` toutes les 30 secondes.

---

## 💰 Étape 8 : Gestion des Coûts

### Free Tier Railway

- **$5 de crédit gratuit** par mois
- **500 heures d'exécution** par mois
- **100 GB de bande passante**

### Hobby Plan ($5/mois)

- **Crédits illimités**
- **Custom domains**
- **Priority support**

### Estimation Coûts

| Service | Coût mensuel estimé |
|---------|---------------------|
| Backend (1 instance) | ~$5-10 |
| Frontend (1 instance) | ~$5 |
| PostgreSQL | ~$5 (si Railway) |
| WebSocket | ~$5 |
| **Total** | **~$20-25/mois** |

---

## 🌐 Étape 9 : Domaine Personnalisé

### 9.1 Ajouter domaine dans Railway

1. Railway Dashboard → Service → Settings → Domains
2. Cliquer "Add Domain"
3. Entrer votre domaine : `www.shareyoursales.com`

### 9.2 Configurer DNS

Chez votre registrar (Namecheap, GoDaddy, etc.) :

**Type A Record** :
```
Host: @
Value: <Railway IP>
TTL: 3600
```

**Type CNAME Record** :
```
Host: www
Value: <your-app>.railway.app
TTL: 3600
```

### 9.3 Attendre propagation DNS

Peut prendre 24-48h. Vérifier avec :

```powershell
nslookup www.shareyoursales.com
```

---

## 🔄 Étape 10 : CI/CD avec GitHub Actions

Railway se déploie automatiquement sur push vers `main`. Pour contrôler :

### 10.1 Désactiver auto-deploy

Railway Dashboard → Service → Settings → Deployments → Désactiver "Auto Deploy"

### 10.2 Créer workflow manual deploy

**Fichier** : `.github/workflows/deploy-railway.yml`

```yaml
name: Deploy to Railway

on:
  workflow_dispatch:
    inputs:
      service:
        description: 'Service to deploy'
        required: true
        type: choice
        options:
          - backend
          - frontend
          - all

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy Backend
        if: ${{ github.event.inputs.service == 'backend' || github.event.inputs.service == 'all' }}
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          cd backend
          railway up --service backend
      
      - name: Deploy Frontend
        if: ${{ github.event.inputs.service == 'frontend' || github.event.inputs.service == 'all' }}
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          cd frontend
          railway up --service frontend
```

### 10.3 Configurer Railway Token

1. Railway Dashboard → Account → Tokens → Create
2. GitHub Repo → Settings → Secrets → New secret
3. Name: `RAILWAY_TOKEN`, Value: `<votre token>`

---

## 🐛 Étape 11 : Troubleshooting

### Problème 1 : Build échoue

**Symptôme** : `Build failed: command not found`

**Solution** :
```powershell
# Vérifier Procfile
cat backend/Procfile

# Vérifier requirements.txt
cat backend/requirements.txt | grep gunicorn
```

### Problème 2 : Application crash au démarrage

**Symptôme** : `Application failed to respond to health check`

**Solution** :
```powershell
# Voir les logs
railway logs --service backend

# Vérifier port
# Railway injecte automatiquement $PORT
# S'assurer que l'app écoute sur 0.0.0.0:$PORT
```

### Problème 3 : CORS errors

**Symptôme** : `Access-Control-Allow-Origin error`

**Solution** :
```python
# backend/server.py
CORS(app, origins=[
    os.getenv('FRONTEND_URL'),
    'https://*.railway.app'
])
```

### Problème 4 : Database connection fails

**Symptôme** : `Could not connect to database`

**Solution** :
```powershell
# Vérifier variable DATABASE_URL
railway variables --service backend

# Tester connexion
railway run python -c "from supabase_client import get_supabase; print(get_supabase())"
```

---

## ✅ Checklist de Déploiement

### Avant le déploiement
- [ ] `Procfile` créé pour backend
- [ ] `railway.json` créé (backend + frontend)
- [ ] Gunicorn ajouté à `requirements.txt`
- [ ] Health check endpoint créé
- [ ] Variables d'environnement listées
- [ ] Migrations SQL prêtes

### Pendant le déploiement
- [ ] Projet Railway créé
- [ ] Backend service configuré
- [ ] Frontend service configuré
- [ ] Variables d'environnement définies
- [ ] Services déployés avec succès

### Après le déploiement
- [ ] URLs Railway récupérées
- [ ] CORS mis à jour
- [ ] Frontend redéployé avec bonnes URLs
- [ ] Migrations SQL appliquées
- [ ] Health checks passent ✅
- [ ] Tests smoke effectués
- [ ] Stripe webhooks configurés
- [ ] Logs vérifiés (aucune erreur)
- [ ] Monitoring activé
- [ ] Domaine personnalisé configuré (optionnel)

---

## 📚 Ressources

### Documentation Railway
- [Railway Docs](https://docs.railway.app/)
- [Deploy Flask](https://docs.railway.app/guides/flask)
- [Deploy React](https://docs.railway.app/guides/react)
- [Environment Variables](https://docs.railway.app/develop/variables)

### Support
- [Railway Discord](https://discord.gg/railway)
- [Railway Community](https://community.railway.app/)
- [Status Page](https://status.railway.app/)

---

## 🎯 Prochaines Étapes

Après déploiement réussi :

1. **Tester l'application** en production
2. **Configurer monitoring avancé** (Sentry, LogRocket)
3. **Optimiser performances** (CDN, caching)
4. **Backups automatiques** de la base de données
5. **Scaling** (ajouter workers si besoin)

---

**Auteur** : ShareYourSales Team  
**Date** : 27 Octobre 2025  
**Version** : 1.0.0

---

**🚂 Bon déploiement sur Railway ! 🚂**
