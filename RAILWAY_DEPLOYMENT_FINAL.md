# 🚀 SOLUTION FINALE - DÉPLOIEMENT RAILWAY

## LE PROBLÈME
Railway ne peut pas déployer un monorepo avec plusieurs services différents depuis un seul repo GitHub.
Il essaie de build depuis la racine et échoue car il ne trouve pas de package.json ou requirements.txt.

## ✅ SOLUTION : Déployer 2 services séparés

### ÉTAPE 1 : Créer le service Backend

1. Va sur https://railway.app
2. Clique sur "New Project"
3. Sélectionne "Deploy from GitHub repo"
4. Choisis ton repo `Getyourshare1`
5. **IMPORTANT** : Dans les paramètres du service :
   - Va dans "Settings" → "Service Settings"
   - **Root Directory** : Change de `/` à `/backend`
   - **Build Command** : `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command** : `gunicorn server:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --graceful-timeout 30 --keep-alive 5`
6. Ajoute les variables d'environnement :
   ```
   SUPABASE_URL=https://tznkbnlkzfodpffkdrhj.supabase.co
   SUPABASE_SERVICE_KEY=ton_service_key_ici
   JWT_SECRET=ton_jwt_secret_ici
   SECRET_KEY=ton_secret_key_ici
   PORT=8001
   ```
   **Note**: Railway définit automatiquement `$PORT`, mais tu peux le mettre pour la cohérence.
7. Deploy

### ÉTAPE 2 : Créer le service Frontend

1. Dans le même projet Railway, clique sur "New Service"
2. Sélectionne le même repo `Getyourshare1`
3. **IMPORTANT** : Dans les paramètres du service :
   - Va dans "Settings" → "Service Settings"
   - **Root Directory** : Change de `/` à `/frontend`
   - ⚠️ **N'ajoute PAS de Build Command ni Start Command** - Le fichier `nixpacks.toml` dans `/frontend` s'en charge automatiquement
4. Ajoute les variables d'environnement :
   ```
   REACT_APP_SUPABASE_URL=https://tznkbnlkzfodpffkdrhj.supabase.co
   REACT_APP_SUPABASE_ANON_KEY=ton_anon_key
   REACT_APP_API_URL=https://ton-backend-url.railway.app/api
   ```
5. Deploy

### ÉTAPE 3 : Lier les services

1. Une fois les deux services déployés, copie l'URL du backend
2. Va dans les variables d'environnement du frontend
3. Mets à jour `REACT_APP_API_URL` avec l'URL du backend
4. Redéploie le frontend

## 🎯 RÉSULTAT
- Backend : https://ton-backend.railway.app
- Frontend : https://ton-frontend.railway.app
- Les deux services fonctionnent indépendamment

---

## ALTERNATIVE : Utiliser Render.com (Plus simple pour les monorepos)

Si Railway continue à poser problème, Render.com gère mieux les monorepos :

### Backend sur Render :
1. New → Web Service
2. Connect GitHub repo
3. **Root Directory** : `backend`
4. **Build Command** : `pip install -r requirements.txt`
5. **Start Command** : `gunicorn server:app`
6. Ajoute les variables d'environnement

### Frontend sur Render :
1. New → Static Site
2. Connect GitHub repo
3. **Root Directory** : `frontend`
4. **Build Command** : `npm ci && npm run build`
5. **Publish Directory** : `build`

---

## POURQUOI ÇA N'A PAS MARCHÉ AVANT ?

1. **railway.toml** ne supporte PAS les multi-services de cette manière
2. **nixpacks.toml** ne peut gérer qu'UN SEUL service à la fois
3. Railway lit TOUJOURS depuis la racine du repo
4. La seule solution est de spécifier le **Root Directory** dans l'UI Railway

## 🚀 PROCHAINES ÉTAPES

1. Supprime tous les fichiers de config inutiles (railway.toml, nixpacks.toml)
2. Suis les étapes ci-dessus pour créer 2 services séparés
3. Configure le Root Directory pour chaque service dans l'UI Railway
4. C'est tout !
