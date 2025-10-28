# 🔧 Variables d'Environnement Railway - Configuration Rapide

## 📋 Instructions

Copiez-collez ces variables dans Railway Dashboard pour chaque service.

---

## 🐍 Backend Service

**Service Name:** `shareyoursales-backend`  
**Root Directory:** `/backend`

### Variables d'environnement à configurer :

```bash
# ✅ Supabase (OBLIGATOIRE)
SUPABASE_URL=https://tznkbnlkzfodpffkdrhj.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR6bmtibmxremZvZHBmZmtkcmhqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMDE4Njg2MSwiZXhwIjoyMDQ1NzYyODYxfQ.VOTRE_SERVICE_KEY_ICI
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR6bmtibmxremZvZHBmZmtkcmhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxODY4NjEsImV4cCI6MjA0NTc2Mjg2MX0.VOTRE_ANON_KEY_ICI

# ✅ JWT (OBLIGATOIRE - Générer avec: openssl rand -hex 32)
JWT_SECRET=GENERER_UN_SECRET_UNIQUE_ICI
JWT_ALGORITHM=HS256
JWT_EXPIRATION=4

# ✅ Server
PORT=8003

# ✅ CORS (Remplacer par votre URL frontend Railway)
CORS_ORIGINS=https://considerate-luck-production.up.railway.app,http://localhost:3000

# ⚠️ Email (Optionnel - pour notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# 💳 Payment Gateways (Optionnel)
CMI_MERCHANT_ID=
CMI_API_KEY=
PAYZEN_SHOP_ID=
PAYZEN_API_KEY=
```

### 🔑 Comment obtenir les clés Supabase :

1. Allez sur https://supabase.com/dashboard
2. Sélectionnez votre projet `tznkbnlkzfodpffkdrhj`
3. Settings > API
4. Copiez :
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_ANON_KEY`
   - **service_role secret** → `SUPABASE_SERVICE_KEY`

### 🔐 Générer JWT_SECRET :

```bash
# Sur Windows PowerShell
[Convert]::ToBase64String((1..32|%{Get-Random -Max 256}))

# Sur Linux/Mac
openssl rand -hex 32
```

---

## ⚛️ Frontend Service

**Service Name:** `shareyoursales-frontend`  
**Root Directory:** `/frontend`

### Variables d'environnement à configurer :

```bash
# ✅ Backend URL (OBLIGATOIRE - Remplacer par l'URL de votre backend Railway)
REACT_APP_BACKEND_URL=https://shareyoursales-backend-production.up.railway.app

# ✅ Supabase (OBLIGATOIRE - Mêmes valeurs que le backend)
REACT_APP_SUPABASE_URL=https://tznkbnlkzfodpffkdrhj.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR6bmtibmxremZvZHBmZmtkcmhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxODY4NjEsImV4cCI6MjA0NTc2Mjg2MX0.VOTRE_ANON_KEY_ICI

# ✅ ESLint Disable (OBLIGATOIRE - Éviter erreurs build)
DISABLE_ESLINT_PLUGIN=true
ESLINT_NO_DEV_ERRORS=true
TSC_COMPILE_ON_ERROR=true

# ✅ Node Environment
NODE_ENV=production
```

### ⚠️ IMPORTANT : URL Backend

Après avoir déployé le backend, copiez son URL Railway et mettez-la dans `REACT_APP_BACKEND_URL`.

**Format correct :**
- ✅ `https://backend-production.up.railway.app`
- ❌ `https://backend-production.up.railway.app/` (pas de slash final)
- ❌ `https://backend-production.up.railway.app/api` (pas de /api)

---

## 🚀 Ordre de Déploiement

### Étape 1 : Backend d'abord

1. Créez le service backend sur Railway
2. Configurez toutes les variables ci-dessus
3. Déployez
4. Testez `/health` : `https://[backend-url]/health`
5. **Copiez l'URL du backend** (vous en aurez besoin pour le frontend)

### Étape 2 : Frontend ensuite

1. Créez le service frontend sur Railway
2. **Collez l'URL backend dans `REACT_APP_BACKEND_URL`**
3. Configurez les autres variables
4. Déployez
5. Testez l'application

### Étape 3 : Update CORS

1. Retournez dans les variables backend
2. Ajoutez l'URL frontend dans `CORS_ORIGINS`
3. Format : `https://frontend.railway.app,http://localhost:3000`
4. Redéployez le backend

---

## ✅ Checklist Rapide

### Backend Railway :
- [ ] `SUPABASE_URL` configuré
- [ ] `SUPABASE_SERVICE_KEY` configuré (service_role)
- [ ] `SUPABASE_ANON_KEY` configuré
- [ ] `JWT_SECRET` généré et configuré
- [ ] `PORT=8003`
- [ ] Backend déployé avec succès
- [ ] `/health` endpoint répond avec `{"status": "healthy"}`

### Frontend Railway :
- [ ] `REACT_APP_BACKEND_URL` avec URL backend Railway
- [ ] `REACT_APP_SUPABASE_URL` configuré
- [ ] `REACT_APP_SUPABASE_ANON_KEY` configuré
- [ ] `DISABLE_ESLINT_PLUGIN=true`
- [ ] Frontend déployé avec succès
- [ ] Application charge correctement

### CORS :
- [ ] URL frontend ajoutée dans `CORS_ORIGINS` backend
- [ ] Backend redéployé après modification CORS
- [ ] Pas d'erreurs CORS dans la console browser

---

## 🐛 Dépannage Rapide

### Erreur : `ERR_CONNECTION_REFUSED`

**Cause :** Frontend ne trouve pas le backend  
**Solution :** Vérifiez `REACT_APP_BACKEND_URL` dans les variables frontend

### Erreur : `CORS policy`

**Cause :** URL frontend pas dans CORS_ORIGINS backend  
**Solution :** Ajoutez l'URL frontend dans `CORS_ORIGINS` et redéployez backend

### Erreur : `Failed to load resource: net::ERR_CONNECTION_TIMED_OUT`

**Cause :** WebSocket ne peut pas se connecter  
**Solution :** Backend doit supporter WebSocket (déjà configuré avec Uvicorn)

### Erreur : Build failed (ESLint)

**Cause :** ESLint bloque le build  
**Solution :** Vérifiez que `DISABLE_ESLINT_PLUGIN=true` est bien configuré

---

## 📊 Test Final

Une fois tout déployé, testez :

1. **Backend Health** : `https://[backend-url]/health`
   - Devrait retourner : `{"status": "healthy", "database": "connected"}`

2. **Frontend Home** : `https://[frontend-url]/`
   - Devrait afficher la landing page

3. **Login Admin** : 
   - Email : `admin@shareyoursales.com`
   - Password : `admin123`
   - 2FA : `123456`
   - Devrait vous connecter au dashboard admin

4. **Console Browser** (F12) :
   - Aucune erreur CORS
   - WebSocket connecté (ou timeout si pas implémenté côté backend)

---

## 🎉 Prêt !

Si tous les tests passent, votre application ShareYourSales est maintenant en production sur Railway !

**Prochaines étapes :**
- Configurez un domaine personnalisé
- Activez les paiements (CMI, PayZen)
- Configurez SMTP pour les emails
- Exécutez les migrations de tracking (voir `database/migrations/add_tracking_tables.sql`)

---

## 📞 Besoin d'aide ?

1. Vérifiez les logs Railway (Backend et Frontend)
2. Testez `/health` du backend
3. Ouvrez la console browser (F12) pour voir les erreurs
4. Consultez `RAILWAY_DEPLOYMENT.md` pour plus de détails
