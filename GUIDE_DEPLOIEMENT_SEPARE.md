# 🚀 Guide Déploiement Séparé Backend/Frontend Railway

## 📋 Vue d'ensemble

Nous avons séparé le backend et le frontend en **deux services Railway distincts** :

- **Backend** : Service Python/FastAPI avec Docker
- **Frontend** : Service React/Node.js avec Nixpacks

## 🔧 Configuration Actuelle

### Backend (`/backend`)
- **Fichier** : `backend/railway.toml`
- **Builder** : Docker
- **Dockerfile** : `backend/Dockerfile`
- **Port** : `$PORT` (Railway auto-assigné)

### Frontend (`/frontend`)
- **Fichier** : `frontend/railway.toml`
- **Builder** : Nixpacks
- **Commandes** :
  - Setup: `npm install`
  - Build: `npm run build`
  - Start: `npx serve -s build -l $PORT`

## 🚀 Déploiement

### 1. Créer Service Backend

```bash
# Via Railway CLI
railway login
railway link --new
railway service --name "getyourshare-backend"

# Déployer
cd backend
railway up
```

### 2. Créer Service Frontend

```bash
# Nouveau service
railway service --name "getyourshare-frontend"

# Déployer
cd ../frontend
railway up
```

### 3. Variables d'Environnement

#### Backend Variables :
```bash
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SECRET_KEY=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
JWT_SECRET=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
CORS_ORIGINS=https://getyourshare-frontend.railway.app,http://localhost:3000
```

#### Frontend Variables :
```bash
REACT_APP_API_URL=https://getyourshare-backend.railway.app
REACT_APP_SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🔗 Connexion Frontend ↔ Backend

1. **Backend URL** : `https://getyourshare-backend.railway.app`
2. **Frontend URL** : `https://getyourshare-frontend.railway.app`
3. **CORS** : Configuré pour accepter le frontend

## ✅ Avantages de la Séparation

- **Déploiement indépendant** : Backend et frontend séparés
- **Scaling optimisé** : Resources dédiées à chaque service
- **Debugging facilité** : Logs séparés
- **Maintenance simplifiée** : Updates indépendants

## 🔍 Vérification

### Backend Health Check :
```bash
curl https://getyourshare-backend.railway.app/health
```

### Frontend Access :
```
https://getyourshare-frontend.railway.app
```

## 🛠️ Troubleshooting

### Backend ne démarre pas :
- Vérifier les variables d'environnement
- Vérifier les logs Railway : `railway logs`

### Frontend build échoue :
- Vérifier `package.json` et `npm install`
- Vérifier les variables `REACT_APP_*`

### CORS errors :
- Vérifier `CORS_ORIGINS` dans le backend
- S'assurer que l'URL frontend est incluse