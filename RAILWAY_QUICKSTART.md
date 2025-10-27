# 🚀 Guide Rapide - Déploiement Railway

## Configuration Rapide (5 minutes)

### 1. Créer compte Railway
👉 [railway.app/new](https://railway.app/new)

### 2. Nouveau projet depuis GitHub
- Cliquer "Deploy from GitHub repo"
- Sélectionner `epitaphe360/Getyourshare1`
- Railway détecte automatiquement backend et frontend

### 3. Configurer Backend

**Variables d'environnement minimales** :
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
JWT_SECRET=<générer: openssl rand -hex 32>
PORT=8000
FRONTEND_URL=<sera généré par Railway>
```

**Root Directory** : `/backend`

### 4. Configurer Frontend

**Variables d'environnement** :
```bash
REACT_APP_API_URL=<URL backend Railway>/api
REACT_APP_SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo
```

**Root Directory** : `/frontend`

### 5. Déployer
Cliquer "Deploy" et attendre 3-5 minutes ⏱️

### 6. Récupérer URLs
Railway génère :
- Backend: `https://backend-production-xxxx.up.railway.app`
- Frontend: `https://frontend-production-xxxx.up.railway.app`

### 7. Mettre à jour CORS
Ajouter URL frontend dans `backend/.env` :
```bash
CORS_ORIGINS=https://frontend-production-xxxx.up.railway.app
```

Redéployer backend.

### 8. Tester
Ouvrir URL frontend → Application fonctionne ! 🎉

---

## Variables d'environnement complètes

<details>
<summary><b>Backend (cliquer pour voir)</b></summary>

```bash
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
SUPABASE_ANON_KEY=eyJhbGci...

# JWT
JWT_SECRET=<openssl rand -hex 32>
JWT_EXPIRATION=86400

# Server
PORT=8000
BACKEND_HOST=0.0.0.0

# URLs
FRONTEND_URL=https://frontend-production-xxxx.up.railway.app
CORS_ORIGINS=https://frontend-production-xxxx.up.railway.app

# Stripe (optionnel)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Config
DEBUG=False
NODE_ENV=production
```
</details>

<details>
<summary><b>Frontend (cliquer pour voir)</b></summary>

```bash
# API
REACT_APP_API_URL=https://backend-production-xxxx.up.railway.app/api
REACT_APP_WS_URL=wss://backend-production-xxxx.up.railway.app/ws

# Supabase
REACT_APP_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGci...

# Stripe (optionnel)
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_...

# Config
REACT_APP_ENV=production
```
</details>

---

## Commandes Utiles

```powershell
# Installer Railway CLI
npm install -g @railway/cli

# Login
railway login

# Voir logs
railway logs --service backend

# Variables
railway variables

# Redéployer
railway up
```

---

## Troubleshooting Rapide

### Build échoue
```powershell
# Vérifier requirements.txt contient gunicorn
cat backend/requirements.txt | grep gunicorn

# Vérifier Procfile existe
cat backend/Procfile
```

### CORS errors
Ajouter URL frontend dans CORS_ORIGINS et redéployer.

### Health check fails
Vérifier que l'app écoute sur `0.0.0.0:$PORT`.

---

## 📚 Documentation Complète

Voir `RAILWAY_DEPLOYMENT_GUIDE.md` pour guide détaillé.

---

**🚂 Temps total : ~10 minutes 🚂**
