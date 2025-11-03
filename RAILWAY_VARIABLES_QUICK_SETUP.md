# 🚀 Railway Backend - Configuration Rapide des Variables

## ⚡ Copy-Paste Direct (Pour Railway Dashboard)

### **1️⃣ Variables Essentielles** (Obligatoires)

```env
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g
SECRET_KEY=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
JWT_SECRET=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
CORS_ORIGINS=https://considerate-luck-production.up.railway.app,http://localhost:3000
PORT=8001
```

### **2️⃣ Variables de Configuration** (Recommandées)

```env
ENVIRONMENT=production
NODE_ENV=production
DEBUG=False
FRONTEND_URL=https://considerate-luck-production.up.railway.app
```

---

## 📋 Étapes de Configuration Railway

### **Via Dashboard Web** (Recommandé)

1. **Aller sur Railway**
   - Ouvrir [railway.app](https://railway.app)
   - Sélectionner votre projet
   - Cliquer sur le service **backend**

2. **Ajouter les Variables**
   - Onglet **Variables** (ou **Settings** > **Variables**)
   - Cliquer **+ New Variable**
   - Pour chaque variable ci-dessus:
     - **Name**: Le nom (ex: `SUPABASE_URL`)
     - **Value**: La valeur (ex: `https://iamezkmapbhlhhvvsits.supabase.co`)
   - Cliquer **Add** ou **Save**

3. **Vérifier & Déployer**
   - Les variables s'affichent dans la liste
   - Railway redéploie automatiquement
   - Attendre le build (2-3 min)

---

### **Via Railway CLI** (Avancé)

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Login
railway login

# Linker le projet
railway link

# Ajouter les variables (une par une)
railway variables set SUPABASE_URL="https://iamezkmapbhlhhvvsits.supabase.co"
railway variables set SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo"
railway variables set SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"
railway variables set SECRET_KEY="bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw=="
railway variables set JWT_SECRET="bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw=="
railway variables set CORS_ORIGINS="https://considerate-luck-production.up.railway.app,http://localhost:3000"
railway variables set PORT="8001"

# Vérifier
railway variables

# Redéployer
railway up
```

---

## ✅ Checklist Post-Configuration

### **1. Vérifier les Variables**
Dans Railway Dashboard > Backend Service > Variables, vous devez voir:
- ✅ `SUPABASE_URL`
- ✅ `SUPABASE_ANON_KEY`
- ✅ `SUPABASE_SERVICE_ROLE_KEY`
- ✅ `SECRET_KEY`
- ✅ `JWT_SECRET`
- ✅ `CORS_ORIGINS`
- ✅ `PORT`

### **2. Attendre le Build**
- Railway redémarre automatiquement
- Logs: Onglet **Deployments** > Dernier déploiement
- Chercher: `🔐 CORS Origins configurés: [...]`

### **3. Tester les Endpoints**

#### **Health Check**
```bash
curl https://[VOTRE-BACKEND-URL].up.railway.app/health
```

**Réponse attendue**:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-03T...",
  "environment": "production"
}
```

#### **Test CORS**
```bash
curl -I \
  -H "Origin: https://considerate-luck-production.up.railway.app" \
  https://[VOTRE-BACKEND-URL].up.railway.app/health
```

**Headers attendus**:
```
Access-Control-Allow-Origin: https://considerate-luck-production.up.railway.app
Access-Control-Allow-Credentials: true
```

#### **Test Supabase Connection**
```bash
curl https://[VOTRE-BACKEND-URL].up.railway.app/api/users
```

**Doit retourner**: Liste de users ou `[]` (pas d'erreur 500)

---

## 🔍 Debugging

### **Problème 1: "CORS error" dans le frontend**

**Symptôme**: Console frontend montre `Access to fetch blocked by CORS policy`

**Solution**:
1. Vérifier `CORS_ORIGINS` dans Railway contient bien l'URL du frontend
2. Vérifier format: **pas de guillemets**, URLs séparées par **virgules** (pas d'espaces)
   ```
   ✅ Correct: https://frontend.railway.app,http://localhost:3000
   ❌ Incorrect: "https://frontend.railway.app, http://localhost:3000"
   ```

### **Problème 2: "Database connection failed"**

**Symptôme**: Logs Railway montrent `Failed to connect to Supabase`

**Solution**:
1. Vérifier `SUPABASE_URL` est correcte (copier depuis Supabase Dashboard)
2. Vérifier `SUPABASE_SERVICE_ROLE_KEY` (Settings > API > service_role key)
3. Tester manuellement:
   ```bash
   curl https://iamezkmapbhlhhvvsits.supabase.co/rest/v1/
   ```

### **Problème 3: "Port already in use"**

**Symptôme**: Build échoue avec `EADDRINUSE`

**Solution**:
- Railway injecte automatiquement `PORT`
- Votre Dockerfile **doit** utiliser `${PORT:-8000}`
- Vérifier ligne CMD dans `backend/Dockerfile`:
  ```dockerfile
  CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]
  ```

### **Problème 4: Variables non détectées**

**Symptôme**: Logs montrent valeurs par défaut au lieu des variables Railway

**Solution**:
1. Vérifier que les variables sont dans le **bon service** (backend, pas frontend)
2. Redéployer manuellement: Settings > **Redeploy**
3. Vérifier logs de build pour `🔐 CORS Origins configurés:`

---

## 📊 Variables Status

| Variable | Status | Utilisé Pour |
|----------|--------|--------------|
| `SUPABASE_URL` | ✅ Valide | Connexion BDD |
| `SUPABASE_ANON_KEY` | ✅ Valide | Auth frontend |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Valide | Backend admin |
| `SECRET_KEY` | ✅ Valide | JWT signature |
| `JWT_SECRET` | ✅ Valide | JWT fallback |
| `CORS_ORIGINS` | ⚠️ Vérifier format | CORS middleware |
| `PORT` | ✅ Valide | Server binding |

---

## 🎯 URLs Importantes

### **Backend Railway**
```
https://[VOTRE-SERVICE-NAME].up.railway.app
```

### **Frontend Railway**
```
https://considerate-luck-production.up.railway.app
```

### **Supabase Dashboard**
```
https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits
```

### **Railway Dashboard**
```
https://railway.app/dashboard
```

---

## 💡 Tips

1. **Variables Sensibles**: 
   - Railway masque automatiquement les valeurs dans l'UI
   - Ne jamais commit les clés dans Git

2. **Mise à Jour**:
   - Modifier une variable redéploie automatiquement
   - Pas besoin de redémarrer manuellement

3. **Backups**:
   - Railway garde l'historique des variables
   - On peut rollback si besoin

4. **Environnements**:
   - Créer un service par environnement (dev, staging, prod)
   - Variables différentes par service

---

## 🆘 Support

**Railway Issues**:
- [Documentation Railway](https://docs.railway.app)
- [Discord Railway](https://discord.gg/railway)

**Supabase Issues**:
- [Documentation Supabase](https://supabase.com/docs)
- [Discord Supabase](https://discord.supabase.com)

---

**Dernière mise à jour**: Novembre 3, 2024  
**Commit**: `82295ee` - fix: use CORS_ORIGINS from environment variables
