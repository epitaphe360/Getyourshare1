# 🚂 Guide de Déploiement Railway - GetYourShare

## ✅ Fichiers de Configuration Créés

Tous les fichiers nécessaires sont maintenant en place:

```
✅ Dockerfile              - Configuration Docker principale
✅ .dockerignore          - Optimisation du build Docker
✅ railway.json           - Configuration Railway (builder: DOCKERFILE)
✅ railway.toml           - Variables d'environnement Railway
✅ Procfile               - Fallback start command
✅ nixpacks.toml          - Fallback Nixpacks config
✅ .env.example           - Template des variables d'environnement
```

---

## 🚀 Déploiement sur Railway

### Méthode 1: Via Railway CLI

```bash
# 1. Installer Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Lier au projet
railway link

# 4. Déployer
railway up
```

### Méthode 2: Via GitHub (Recommandé)

1. **Push le code sur GitHub**
```bash
git add .
git commit -m "feat: Add Railway deployment files"
git push origin main
```

2. **Connecter Railway à GitHub**
   - Aller sur [railway.app](https://railway.app)
   - "New Project" → "Deploy from GitHub repo"
   - Sélectionner le repository `Getyourshare1`
   - Railway détectera automatiquement le Dockerfile

3. **Configuration automatique**
   - Railway utilisera `Dockerfile` pour le build
   - Le health check sera sur `/api/health`
   - Le port sera automatiquement configuré

---

## 🔐 Variables d'Environnement Requises

### Critiques (REQUIRED)

```bash
# Database - Supabase
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...

# Authentication
JWT_SECRET=votre_secret_jwt_minimum_32_caracteres

# Payments - Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Application
ENVIRONMENT=production
PORT=8000
FRONTEND_URL=https://votre-app.railway.app
ALLOWED_ORIGINS=https://votre-app.railway.app,https://shareyoursales.ma
```

### Optionnelles (Feature-specific)

```bash
# AI Features (Pro/Enterprise tiers)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
STABILITY_API_KEY=sk-...

# WhatsApp Business
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_ACCESS_TOKEN=...

# TikTok Shop
TIKTOK_SHOP_APP_KEY=...
TIKTOK_SHOP_APP_SECRET=...

# Social Media
INSTAGRAM_APP_ID=...
FACEBOOK_APP_ID=...
YOUTUBE_API_KEY=...
TWITTER_BEARER_TOKEN=...

# Mobile Payments Morocco
CASHPLUS_API_KEY=...
WAFACASH_API_KEY=...
ORANGE_MONEY_API_KEY=...
INWI_MONEY_API_KEY=...
MAROC_TELECOM_API_KEY=...
CIH_MOBILE_API_KEY=...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
REDIS_URL=redis://...
```

---

## 📝 Ajouter les Variables sur Railway

### Via Dashboard:

1. Aller sur votre projet Railway
2. Cliquer sur l'onglet **"Variables"**
3. Ajouter chaque variable une par une
4. OU importer en bloc:

```
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
JWT_SECRET=your_secret_here
STRIPE_SECRET_KEY=sk_...
ENVIRONMENT=production
FRONTEND_URL=https://your-app.railway.app
```

### Via CLI:

```bash
# Ajouter une variable
railway variables set SUPABASE_URL="https://..."

# Importer depuis .env
railway variables set < .env.production
```

---

## 🏗️ Processus de Build

Railway exécutera automatiquement:

```dockerfile
1. FROM python:3.11-slim
2. Install system dependencies (gcc, libpq-dev, etc.)
3. pip install -r requirements.txt
4. Copy backend code
5. Health check configuration
6. Start: uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Temps de build estimé:** 3-5 minutes

---

## ✅ Vérification du Déploiement

### 1. Health Check

```bash
# Une fois déployé, tester:
curl https://your-app.railway.app/health

# Réponse attendue:
{
  "status": "healthy",
  "timestamp": "2025-11-02T...",
  "version": "1.0.0",
  "database": "connected"
}
```

### 2. Endpoints API

```bash
# Test API docs
curl https://your-app.railway.app/docs

# Test API principale
curl https://your-app.railway.app/api/
```

### 3. Logs

```bash
# Via CLI
railway logs

# Via Dashboard
# Onglet "Deployments" → Cliquer sur le dernier déploiement
```

---

## 🐛 Troubleshooting

### Erreur: "Dockerfile not found"

**Solution:** Le Dockerfile existe maintenant à la racine. Vérifier que:
```bash
ls -la Dockerfile
# Devrait afficher: -rw-r--r-- 1 ... Dockerfile
```

Si Railway ne le trouve pas:
1. Vérifier que `railway.json` a: `"builder": "DOCKERFILE"`
2. Forcer un nouveau build: `railway up --detach`

### Erreur: "Health check failed"

**Solutions:**
1. Vérifier les variables d'environnement (surtout SUPABASE_URL, SUPABASE_ANON_KEY)
2. Vérifier les logs: `railway logs`
3. Tester localement:
```bash
docker build -t getyourshare .
docker run -p 8000:8000 --env-file .env.production getyourshare
curl http://localhost:8000/health
```

### Erreur: "Module not found"

**Solution:** Vérifier que `requirements.txt` contient tous les packages:
```bash
# Rebuild dependencies
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "fix: Update requirements.txt"
git push
```

### Erreur: "Database connection failed"

**Solutions:**
1. Vérifier Supabase URL et keys
2. Vérifier que l'IP de Railway est autorisée dans Supabase
3. Dans Supabase Dashboard → Settings → API → Allow all IPs

---

## 📊 Monitoring Post-Déploiement

### Métriques à surveiller:

1. **Response Time**
   - Railway Dashboard → Metrics → Response Time
   - Objectif: < 200ms

2. **Error Rate**
   - Railway Dashboard → Metrics → Error Rate
   - Objectif: < 1%

3. **Memory Usage**
   - Railway Dashboard → Metrics → Memory
   - Limite: 512MB (Plan Starter)

4. **CPU Usage**
   - Railway Dashboard → Metrics → CPU
   - Normal: 5-20%

### Alertes

Configurer via Railway Dashboard:
- Memory > 80% → Scale up
- Error rate > 5% → Check logs
- Response time > 500ms → Investigate

---

## 🔄 Mise à Jour

```bash
# 1. Push changes
git add .
git commit -m "feat: Update features"
git push

# 2. Railway redéploie automatiquement
# 3. Vérifier les logs
railway logs --follow

# 4. Tester le nouveau déploiement
curl https://your-app.railway.app/health
```

---

## 💰 Coûts Estimés

**Railway Starter Plan (5$/mois):**
- 512MB RAM
- 1GB Disk
- 5$ de crédits inclus
- ~500,000 requests/mois

**Railway Pro Plan (20$/mois):**
- 8GB RAM
- 100GB Disk
- 20$ de crédits inclus
- Illimité requests

**Estimation GetYourShare:**
- Starter: OK pour < 1000 users
- Pro: Recommandé pour production

---

## 📚 Ressources

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## ✅ Checklist Pré-Déploiement

- [ ] Dockerfile créé ✅
- [ ] railway.json configuré ✅
- [ ] Variables d'environnement préparées
- [ ] Supabase configuré et accessible
- [ ] Stripe configuré (webhooks)
- [ ] Health check fonctionne
- [ ] Tests passent (185/185) ✅
- [ ] Git repository à jour
- [ ] Documentation à jour ✅

---

## 🚀 Déploiement Rapide (TL;DR)

```bash
# 1. Push to GitHub
git add .
git commit -m "feat: Railway deployment ready"
git push origin main

# 2. Railway
railway login
railway link
railway up

# 3. Ajouter variables d'environnement via Dashboard

# 4. Vérifier
curl https://your-app.railway.app/health

# ✅ Done!
```

---

**Status:** ✅ Prêt pour déploiement Railway

**Dernière mise à jour:** 2025-11-02
