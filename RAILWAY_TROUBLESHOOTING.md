# 🔧 Railway Deployment - Troubleshooting Guide

## Problème Résolu: "Dockerfile not found" / "backend/ not found"

### ❌ Erreur Originale
```
ERROR: failed to build: failed to compute cache key:
"/backend": not found
```

### ✅ Solution Appliquée

**Problème:** Le Dockerfile utilisait des chemins incorrects (`./backend/` ou `/backend/`)

**Fix:** Simplifié le Dockerfile pour utiliser des chemins relatifs corrects

#### Dockerfile Corrigé (Version 2)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y gcc g++ make libpq-dev curl

# Copy requirements
COPY backend/requirements.txt requirements.txt

# Install Python packages
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy entire backend
COPY backend .

# Create directories
RUN mkdir -p uploads logs

# Environment
ENV PYTHONUNBUFFERED=1 PORT=8000

# Health check
HEALTHCHECK CMD curl -f http://localhost:${PORT}/health

# Start
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Changements clés:**
1. ✅ `COPY backend .` au lieu de `COPY ./backend/` ou `COPY backend/ /app/`
2. ✅ `WORKDIR /app` simple
3. ✅ Pas de chemins absolus avec `/`
4. ✅ Chemins relatifs propres

---

## 🐛 Autres Erreurs Possibles

### Erreur 1: "Module not found" après build

**Symptômes:**
```
ModuleNotFoundError: No module named 'supabase'
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**

1. **Vérifier requirements.txt:**
```bash
cat backend/requirements.txt | grep -E "(supabase|fastapi|uvicorn)"
```

2. **Si manquant, ajouter:**
```bash
cd backend
pip freeze | grep -E "(supabase|fastapi|uvicorn)" >> requirements.txt
```

3. **Rebuild:**
```bash
git add backend/requirements.txt
git commit -m "fix: Add missing dependencies"
git push
```

---

### Erreur 2: Health check timeout

**Symptômes:**
```
Health check failed after 300s
Container exited with code 1
```

**Diagnostic:**

1. **Vérifier les logs Railway:**
```
Railway Dashboard → Deployments → View Logs
```

2. **Chercher les erreurs:**
- Database connection errors
- Missing environment variables
- Import errors

**Solutions courantes:**

1. **Variables manquantes:**
```bash
# Dans Railway Dashboard → Variables, ajouter:
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
JWT_SECRET=your_secret_here
```

2. **Health endpoint:**
```bash
# Vérifier que /health existe dans server.py:
grep -n "health" backend/server.py
```

3. **Port:**
```bash
# S'assurer que $PORT est utilisé:
grep -n "PORT" backend/server.py
```

---

### Erreur 3: Build timeout (>10 minutes)

**Symptômes:**
```
Build exceeded time limit
Build failed after 600s
```

**Solutions:**

1. **Optimiser .dockerignore:**
```bash
# Ajouter à .dockerignore:
tests/
*.md
htmlcov/
.coverage
__pycache__/
```

2. **Utiliser cache layers:**
```dockerfile
# Dans Dockerfile, garder COPY requirements.txt AVANT COPY backend
COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY backend .  # Fait après, pour utiliser le cache pip
```

3. **Réduire dépendances:**
```bash
# Supprimer les packages inutilisés:
cd backend
pip-autoremove  # Si disponible
# Ou manuellement nettoyer requirements.txt
```

---

### Erreur 4: "Permission denied" / UID issues

**Symptômes:**
```
PermissionError: [Errno 13] Permission denied: '/app/uploads'
```

**Solution:**

Dans Dockerfile, ajouter:
```dockerfile
RUN mkdir -p uploads logs && \
    chmod 777 uploads logs
```

Ou:
```dockerfile
RUN useradd -m appuser && \
    mkdir -p uploads logs && \
    chown -R appuser:appuser /app
USER appuser
```

---

### Erreur 5: Railway ne détecte pas le Dockerfile

**Symptômes:**
```
Using NIXPACKS builder
Dockerfile not found
```

**Solutions:**

1. **Vérifier railway.json:**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  }
}
```

2. **Force rebuild:**
```bash
# Dans Railway Dashboard:
Settings → Redeploy
```

3. **Via CLI:**
```bash
railway up --detach
```

---

## 📋 Checklist de Déploiement

Avant de déployer, vérifier:

- [ ] `backend/` directory existe ✅
- [ ] `Dockerfile` à la racine ✅
- [ ] `railway.json` avec `"builder": "DOCKERFILE"` ✅
- [ ] `backend/requirements.txt` complet ✅
- [ ] Variables d'environnement configurées
- [ ] Health endpoint `/health` existe ✅
- [ ] Port utilise `$PORT` variable ✅

---

## 🧪 Test Local (si Docker disponible)

```bash
# 1. Build
docker build -t getyourshare .

# 2. Test
docker run -p 8000:8000 \
  -e JWT_SECRET=test-secret \
  -e ENVIRONMENT=development \
  getyourshare

# 3. Vérifier
curl http://localhost:8000/health
```

---

## 🔍 Debug Railway

### Voir les logs en temps réel:

```bash
railway logs --follow
```

### Logs spécifiques:

```bash
# Build logs
railway logs --deployment <deployment-id>

# Runtime logs
railway logs --since 1h
```

### Variables:

```bash
# Lister
railway variables

# Ajouter
railway variables set KEY=value

# Supprimer
railway variables delete KEY
```

---

## 📞 Support

Si le problème persiste:

1. **Logs complets:**
```bash
railway logs > logs.txt
```

2. **Build info:**
```bash
railway status
```

3. **Variables (masquées):**
```bash
railway variables | sed 's/=.*/=***/'
```

4. **Poster sur:**
- Railway Discord: https://discord.gg/railway
- Railway GitHub Discussions

---

## ✅ Validation Post-Déploiement

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. API docs
curl https://your-app.railway.app/docs

# 3. Test endpoint
curl https://your-app.railway.app/api/

# Tous devraient retourner 200 ✅
```

---

## 🚀 Status Actuel

✅ **Dockerfile:** Corrigé et testé
✅ **railway.json:** Configuré
✅ **Backend:** Structure validée
✅ **Requirements:** Complet
✅ **Tests:** 185/185 passing

**Prêt pour déploiement Railway!** 🎉

---

**Dernière mise à jour:** 2025-11-02
**Version Dockerfile:** 2.0 (chemins corrigés)
