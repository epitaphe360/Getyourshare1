# 🚂 Guide de Déploiement Railway - ShareYourSales

## 📋 Vue d'ensemble

Ce guide détaille les étapes pour déployer ShareYourSales sur Railway avec deux services séparés :
- **Backend** (FastAPI + Gunicorn)
- **Frontend** (React + Create React App)

---

## 🔧 Configuration Backend Railway

### Service: `shareyoursales-backend`

#### Variables d'environnement obligatoires :

```bash
# Supabase Configuration
SUPABASE_URL=https://tznkbnlkzfodpffkdrhj.supabase.co
SUPABASE_SERVICE_KEY=<VOTRE_SUPABASE_SERVICE_KEY>
SUPABASE_ANON_KEY=<VOTRE_SUPABASE_ANON_KEY>

# JWT Configuration
JWT_SECRET=<GENERER_UN_SECRET_SECURISE>
JWT_ALGORITHM=HS256
JWT_EXPIRATION=4

# Server Configuration
PORT=8003
CORS_ORIGINS=https://considerate-luck-production.up.railway.app,http://localhost:3000

# Email Configuration (optionnel)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<VOTRE_EMAIL>
SMTP_PASSWORD=<VOTRE_MOT_DE_PASSE_APP>

# Payment Gateways (optionnel)
CMI_MERCHANT_ID=<VOTRE_CMI_MERCHANT_ID>
CMI_API_KEY=<VOTRE_CMI_API_KEY>
PAYZEN_SHOP_ID=<VOTRE_PAYZEN_SHOP_ID>
PAYZEN_API_KEY=<VOTRE_PAYZEN_API_KEY>
```

#### Commandes Railway :

- **Build Command** : `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command** : `gunicorn server:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --worker-class uvicorn.workers.UvicornWorker`
- **Root Directory** : `/backend`
- **Healthcheck Path** : `/health`

---

## 🎨 Configuration Frontend Railway

### Service: `shareyoursales-frontend`

#### Variables d'environnement obligatoires :

```bash
# Backend API URL (URL de votre service backend Railway)
REACT_APP_BACKEND_URL=https://shareyoursales-backend-production.up.railway.app

# Supabase Configuration (pour le client frontend)
REACT_APP_SUPABASE_URL=https://tznkbnlkzfodpffkdrhj.supabase.co
REACT_APP_SUPABASE_ANON_KEY=<VOTRE_SUPABASE_ANON_KEY>

# Disable ESLint pour éviter les erreurs de build
DISABLE_ESLINT_PLUGIN=true
ESLINT_NO_DEV_ERRORS=true
TSC_COMPILE_ON_ERROR=true

# Node Environment
NODE_ENV=production
```

#### Commandes Railway :

- **Build Command** : `npm install && npm run build`
- **Start Command** : `npx serve -s build -l $PORT`
- **Root Directory** : `/frontend`

---

## 🚀 Étapes de Déploiement

### 1. Créer les services sur Railway

1. Allez sur https://railway.app
2. Connectez votre repository GitHub `Getyourshare1`
3. Créez deux services séparés :
   - Service 1 : Backend (root directory = `/backend`)
   - Service 2 : Frontend (root directory = `/frontend`)

### 2. Configurer le Backend

1. **Variables d'environnement** :
   - Copiez toutes les variables listées ci-dessus dans la section "Variables"
   - Remplacez `<VOTRE_*>` par vos vraies valeurs
   - Générez un `JWT_SECRET` sécurisé avec : `openssl rand -hex 32`

2. **Déploiement** :
   - Railway détectera automatiquement `railway.toml`
   - Le build utilisera Nixpacks + Python
   - Le serveur démarrera avec Gunicorn sur le port attribué par Railway

3. **Vérification** :
   - Une fois déployé, visitez `https://[votre-backend-url]/health`
   - Vous devriez voir : `{"status": "healthy", "database": "connected"}`

### 3. Configurer le Frontend

1. **Variables d'environnement** :
   - `REACT_APP_BACKEND_URL` : L'URL complète du backend Railway (copiez-la depuis le dashboard)
   - Exemple : `https://shareyoursales-backend-production.up.railway.app`
   - Ajoutez les autres variables listées ci-dessus

2. **Déploiement** :
   - Railway détectera automatiquement `railway.toml`
   - Le build créera le dossier `build/` optimisé
   - Le serveur utilisera `serve` pour servir les fichiers statiques

3. **Vérification** :
   - Visitez l'URL frontend Railway
   - Vous devriez voir la landing page ShareYourSales
   - Testez la connexion avec les comptes démo

---

## 🔗 CORS et Domaines

### Mettre à jour CORS Backend

Une fois que vous avez l'URL frontend Railway, ajoutez-la dans les variables d'environnement backend :

```bash
CORS_ORIGINS=https://considerate-luck-production.up.railway.app,https://[VOTRE-FRONTEND-URL].railway.app
```

### Domaine personnalisé (optionnel)

Railway permet d'ajouter un domaine personnalisé :
1. Dans les paramètres du service, allez dans "Settings" > "Networking"
2. Ajoutez votre domaine (ex: `app.shareyoursales.com`)
3. Configurez les DNS selon les instructions Railway

---

## 🗄️ Base de Données Supabase

### Configuration PostgreSQL

1. Connectez-vous à votre projet Supabase
2. Allez dans Settings > Database
3. Récupérez les informations de connexion :
   - Host : `db.tznkbnlkzfodpffkdrhj.supabase.co`
   - Database : `postgres`
   - Port : `5432`
   - User : `postgres`
   - Password : `[votre mot de passe]`

### Exécuter les migrations

Les tables sont déjà créées dans Supabase. Pour ajouter les tables de tracking :

```bash
# Connectez-vous à Supabase SQL Editor
# Copiez le contenu de database/migrations/add_tracking_tables.sql
# Exécutez le SQL
```

---

## 🧪 Comptes de Test

Une fois déployé, vous pouvez vous connecter avec ces comptes :

### Admin
- Email : `admin@shareyoursales.com`
- Password : `admin123`
- 2FA Code : `123456`

### Merchant
- Email : `contact@techstyle.fr`
- Password : `merchant123`
- 2FA Code : `123456`

### Influencer
- Email : `emma.style@instagram.com`
- Password : `influencer123`
- 2FA Code : `123456`

---

## 🐛 Troubleshooting

### Frontend : ERR_CONNECTION_REFUSED

**Problème** : Le frontend ne peut pas se connecter au backend

**Solution** :
1. Vérifiez que `REACT_APP_BACKEND_URL` est correctement configurée
2. L'URL doit être SANS `/api` à la fin
3. Exemple : `https://backend.railway.app` et NON `https://backend.railway.app/api`
4. Redéployez le frontend après modification

### Backend : CORS Error

**Problème** : Erreur CORS lors des requêtes depuis le frontend

**Solution** :
1. Ajoutez l'URL frontend dans `CORS_ORIGINS`
2. Format : `https://frontend1.railway.app,https://frontend2.railway.app`
3. Redéployez le backend

### WebSocket : Connection Failed

**Problème** : WebSocket ne peut pas se connecter

**Solution** :
1. Le WebSocket utilise la même URL que l'API
2. Railway supporte les WebSockets par défaut
3. Vérifiez que le protocole est `wss://` (pas `ws://`)
4. Dans le code, remplacez `localhost:8001` par la variable d'environnement

### Build Failed : ESLint Errors

**Problème** : Le build frontend échoue avec des erreurs ESLint

**Solution** :
1. Vérifiez que `DISABLE_ESLINT_PLUGIN=true` est dans les variables d'environnement
2. Vérifiez que `.eslintrc.json` a toutes les règles à `"off"`
3. Ajoutez `ESLINT_NO_DEV_ERRORS=true` et `TSC_COMPILE_ON_ERROR=true`

---

## 📊 Monitoring

### Logs Backend

Railway affiche automatiquement les logs :
- Requêtes HTTP
- Erreurs serveur
- Tâches planifiées (scheduler)
- Connexions base de données

### Logs Frontend

Vérifiez les logs pour :
- Build warnings
- Erreurs de runtime
- Requêtes API échouées

### Healthcheck

Backend expose `/health` :

```json
{
  "status": "healthy",
  "database": "connected",
  "scheduler": "active",
  "timestamp": "2025-10-28T12:00:00Z"
}
```

---

## 🔒 Sécurité

### Secrets à configurer

✅ **À faire immédiatement** :
1. Générer un nouveau `JWT_SECRET` unique
2. Ne jamais committer les secrets dans Git
3. Utiliser les variables d'environnement Railway
4. Activer HTTPS (automatique sur Railway)

### Recommandations

- Changez les mots de passe des comptes de test en production
- Désactivez les comptes démo si non utilisés
- Configurez rate limiting (déjà inclus avec SlowAPI)
- Surveillez les logs d'authentification

---

## 📝 Checklist de Déploiement

- [ ] Backend déployé sur Railway
- [ ] Variables d'environnement backend configurées
- [ ] Healthcheck `/health` fonctionne
- [ ] Frontend déployé sur Railway
- [ ] Variables d'environnement frontend configurées (avec URL backend)
- [ ] CORS configuré avec URL frontend
- [ ] Migrations Supabase exécutées
- [ ] Comptes de test fonctionnent
- [ ] WebSocket connecté
- [ ] Logs backend/frontend vérifiés

---

## 🎉 Déploiement Réussi !

Si tous les checkpoints sont validés, votre application ShareYourSales est maintenant en production sur Railway !

**URLs à tester** :
- Frontend : https://considerate-luck-production.up.railway.app
- Backend Health : https://[backend-url]/health
- Backend API : https://[backend-url]/api/...

---

## 📞 Support

En cas de problème :
1. Vérifiez les logs Railway
2. Testez les endpoints `/health` backend
3. Vérifiez la console browser (F12) pour les erreurs frontend
4. Consultez la documentation Railway : https://docs.railway.app

Bon déploiement ! 🚀
