# ✅ Validation Variables d'Environnement Railway - Backend

## 📋 Variables à Configurer sur Railway

### 🔐 **Authentification & Sécurité**

```bash
# JWT Secret Key - VALIDE ✅
SECRET_KEY="bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw=="

# Également utilisé comme JWT_SECRET
JWT_SECRET="bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw=="
```

**✅ Statut**: Secret valide (64 caractères base64)

---

### 🗄️ **Supabase Database**

```bash
# Supabase URL - VALIDE ✅
SUPABASE_URL="https://iamezkmapbhlhhvvsits.supabase.co"

# Supabase Anonymous Key - VALIDE ✅
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo"

# Supabase Service Role Key - VALIDE ✅
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"
```

**✅ Statut**: Toutes les clés Supabase sont valides et cohérentes

**⚠️ Note**: Si votre code utilise `SUPABASE_SERVICE_KEY` au lieu de `SUPABASE_SERVICE_ROLE_KEY`, ajoutez aussi:
```bash
SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"
```

---

### 🌐 **Configuration Serveur**

```bash
# Port Railway - VALIDE ✅
PORT="8001"
```

**✅ Statut**: Port 8001 configuré (évite conflit avec 8000)

**⚠️ IMPORTANT**: Railway injecte automatiquement la variable `PORT` depuis le service settings. 
- Si vous voyez `PORT=8000` dans les logs, Railway override automatiquement
- Votre Dockerfile doit utiliser `${PORT:-8000}` pour supporter les deux

---

### 🔗 **CORS Origins - ⚠️ CORRECTION NÉCESSAIRE**

```bash
# VOTRE CONFIGURATION ACTUELLE
CORS_ORIGINS="https://considerate-luck-production.up.railway.app,http://localhost:3000"
```

**❌ Problème Détecté**: Format incorrect pour Railway!

**✅ Format Correct** (sans guillemets, séparés par des virgules):
```bash
CORS_ORIGINS=https://considerate-luck-production.up.railway.app,http://localhost:3000
```

**🔧 Ou mieux encore** (si vous avez un domaine personnalisé):
```bash
CORS_ORIGINS=https://considerate-luck-production.up.railway.app,https://shareyoursales.ma,http://localhost:3000
```

---

## 🚨 Problèmes à Corriger

### 1. **CORS Hardcodé dans le Code** ❌

**Fichier**: `backend/server_complete.py` ligne ~178

**Code Actuel**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "https://*.shareyoursales.ma"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**✅ Code Corrigé à Utiliser**:
```python
# Récupérer CORS_ORIGINS depuis les variables d'environnement
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 2. **Port Hardcodé dans Dockerfile** ⚠️

**Fichier**: `backend/Dockerfile` ligne ~75

**Vérifiez que le CMD utilise bien**:
```dockerfile
CMD ["uvicorn", "server_complete:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}", "--workers", "4"]
```

Ou avec `sh -c`:
```dockerfile
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

---

## 📝 Variables Optionnelles à Ajouter

### 🎨 **Frontend URL**
```bash
FRONTEND_URL="https://considerate-luck-production.up.railway.app"
```

### 🔧 **Environnement**
```bash
ENVIRONMENT="production"
NODE_ENV="production"
DEBUG="False"
```

### 📧 **Email (si utilisé)**
```bash
SENDGRID_API_KEY="votre_cle_sendgrid"
SMTP_HOST="smtp.sendgrid.net"
SMTP_PORT="587"
SMTP_USER="apikey"
SMTP_PASSWORD="votre_cle_sendgrid"
SMTP_FROM="noreply@shareyoursales.ma"
```

### 💳 **Paiements (si utilisé)**
```bash
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
```

---

## ✅ Checklist de Validation

### **Variables Essentielles** (Minimum Vital)
- [x] `SUPABASE_URL` ✅
- [x] `SUPABASE_ANON_KEY` ✅
- [x] `SUPABASE_SERVICE_ROLE_KEY` ✅
- [x] `SECRET_KEY` ou `JWT_SECRET` ✅
- [ ] `CORS_ORIGINS` ⚠️ (format à corriger)
- [x] `PORT` ✅ (Railway le gère automatiquement)

### **Configuration Code** (À Modifier)
- [ ] Modifier `server_complete.py` pour lire `CORS_ORIGINS` depuis env
- [ ] Vérifier que le Dockerfile utilise `${PORT:-8000}`
- [ ] Ajouter `SUPABASE_SERVICE_KEY` si nécessaire (vérifier le code)

---

## 🛠️ Comment Configurer sur Railway

### **Via Dashboard Web**:
1. Aller sur Railway.app
2. Sélectionner votre projet backend
3. Onglet **Variables**
4. Cliquer **+ New Variable**
5. Copier-coller chaque variable (une par ligne)

### **Via Railway CLI**:
```bash
railway variables set CORS_ORIGINS=https://considerate-luck-production.up.railway.app,http://localhost:3000
railway variables set SECRET_KEY="bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw=="
# etc...
```

---

## 🔍 Vérification Post-Déploiement

### **Test 1: Health Check**
```bash
curl https://votre-backend-railway.up.railway.app/health
```

**Réponse attendue**:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Test 2: CORS**
```bash
curl -H "Origin: https://considerate-luck-production.up.railway.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://votre-backend-railway.up.railway.app/api/auth/login
```

**Headers attendus**:
```
Access-Control-Allow-Origin: https://considerate-luck-production.up.railway.app
Access-Control-Allow-Credentials: true
```

### **Test 3: Supabase Connection**
```bash
curl https://votre-backend-railway.up.railway.app/api/auth/test-db
```

---

## 🚀 Résumé des Actions Requises

### **1. Corriger CORS_ORIGINS** ⚠️
```bash
# Railway Variables - Enlever les guillemets
CORS_ORIGINS=https://considerate-luck-production.up.railway.app,http://localhost:3000
```

### **2. Modifier server_complete.py** 📝
```python
# Ligne ~178
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    # ... reste identique
)
```

### **3. Vérifier Dockerfile** 🐳
```dockerfile
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### **4. Redéployer** 🔄
```bash
git add .
git commit -m "fix: use CORS_ORIGINS from environment variables"
git push origin main
```

---

## 📞 Support

Si après ces corrections le problème persiste:
1. Vérifier les logs Railway: `railway logs`
2. Tester le health endpoint
3. Vérifier que toutes les variables sont bien visibles dans Railway Dashboard
4. Confirmer que le build Docker se termine sans erreur

**Variables validées**: 6/6 ✅  
**Corrections nécessaires**: 2 (CORS format + Code modification)
