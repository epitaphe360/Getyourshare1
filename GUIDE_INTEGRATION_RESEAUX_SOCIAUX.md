# 📱 Guide d'Intégration des Réseaux Sociaux

## Vue d'ensemble

Le système d'intégration des réseaux sociaux permet aux influenceurs de:
- ✅ Connecter leurs comptes sociaux (Instagram, TikTok, Facebook, etc.)
- ✅ Récupération automatique des statistiques (followers, engagement, posts)
- ✅ Synchronisation quotidienne via Celery
- ✅ Gestion automatique des tokens OAuth
- ✅ Rapports hebdomadaires de performance
- ✅ Profils influenceurs toujours à jour pour les marchands

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React)                           │
│  - SocialMediaConnections.js                                 │
│  - OAuthCallback.js                                          │
│  - SocialMediaHistory.js                                     │
└──────────────────┬──────────────────────────────────────────┘
                   │ API REST
┌──────────────────▼──────────────────────────────────────────┐
│                Backend (FastAPI)                             │
│  - social_media_endpoints.py (REST API)                      │
│  - social_media_service.py (Business Logic)                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌────────────────┐
│Instagram│  │ TikTok  │  │ Facebook Graph │
│Graph API│  │ Creator │  │      API       │
└─────────┘  │   API   │  └────────────────┘
             └─────────┘

┌─────────────────────────────────────────────────────────────┐
│              Celery Workers (Background Tasks)               │
│  - sync_all_active_connections (daily 8:00)                  │
│  - refresh_expiring_tokens (daily 2:00)                      │
│  - send_weekly_reports (monday 9:00)                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
             ┌──────────┐
             │  Redis   │
             │  Queue   │
             └──────────┘
```

## 📋 Table des Matières

1. [Installation et Configuration](#installation-et-configuration)
2. [Configuration OAuth](#configuration-oauth)
3. [Base de Données](#base-de-données)
4. [Backend - Service](#backend---service)
5. [Backend - API Endpoints](#backend---api-endpoints)
6. [Frontend](#frontend)
7. [Celery - Tâches Asynchrones](#celery---tâches-asynchrones)
8. [Déploiement](#déploiement)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Installation et Configuration

### 1. Dépendances Python

```bash
# Backend dependencies
pip install fastapi
pip install httpx  # Pour les appels API externes
pip install celery
pip install redis
pip install structlog
pip install python-multipart
```

### 2. Configuration Redis

```bash
# Docker (recommandé)
docker run -d -p 6379:6379 --name redis redis:alpine

# OU installation locale
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis
```

### 3. Variables d'Environnement

Créer `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/shareyoursales

# Redis
REDIS_URL=redis://localhost:6379/0

# Instagram
INSTAGRAM_CLIENT_ID=your_instagram_app_id
INSTAGRAM_CLIENT_SECRET=your_instagram_app_secret
INSTAGRAM_REDIRECT_URI=https://yourdomain.com/oauth/callback/instagram

# TikTok
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
TIKTOK_REDIRECT_URI=https://yourdomain.com/oauth/callback/tiktok

# Facebook
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_REDIRECT_URI=https://yourdomain.com/oauth/callback/facebook

# Email (pour notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@shareyoursales.ma
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=noreply@shareyoursales.ma

# Encryption
ENCRYPTION_KEY=your-32-character-encryption-key
```

### 4. Frontend Environment Variables

Créer `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_INSTAGRAM_CLIENT_ID=your_instagram_app_id
REACT_APP_INSTAGRAM_CLIENT_SECRET=your_instagram_app_secret
REACT_APP_TIKTOK_CLIENT_KEY=your_tiktok_client_key
REACT_APP_FACEBOOK_APP_ID=your_facebook_app_id
REACT_APP_FACEBOOK_APP_SECRET=your_facebook_app_secret
```

---

## Configuration OAuth

### Instagram OAuth Setup

1. **Créer une application Facebook/Instagram**
   - Aller sur https://developers.facebook.com/apps/
   - Créer une nouvelle application
   - Ajouter le produit "Instagram Basic Display" ou "Instagram Graph API"

2. **Configurer les paramètres OAuth**
   - Valid OAuth Redirect URIs: `https://yourdomain.com/oauth/callback/instagram`
   - Permissions requises:
     - `instagram_basic`
     - `instagram_manage_insights`
     - `pages_read_engagement` (si page Facebook liée)

3. **Récupérer les credentials**
   - Instagram App ID → `INSTAGRAM_CLIENT_ID`
   - Instagram App Secret → `INSTAGRAM_CLIENT_SECRET`

4. **Mode en production**
   - Soumettre l'app pour review
   - Passer en mode "Live"
   - Ajouter les utilisateurs testeurs en mode Dev

### TikTok OAuth Setup

1. **Créer une application TikTok Developers**
   - Aller sur https://developers.tiktok.com/
   - Créer une nouvelle application
   - Activer "Login Kit"

2. **Configurer les paramètres OAuth**
   - Redirect URI: `https://yourdomain.com/oauth/callback/tiktok`
   - Scopes:
     - `user.info.basic`
     - `video.list`

3. **Récupérer les credentials**
   - Client Key → `TIKTOK_CLIENT_KEY`
   - Client Secret → `TIKTOK_CLIENT_SECRET`

### Facebook OAuth Setup

1. **Même application que Instagram**
2. **Ajouter le produit "Facebook Login"**
3. **Permissions**:
   - `pages_read_engagement`
   - `pages_show_list`

---

## Base de Données

### 1. Exécuter la Migration

```bash
# Via Supabase Dashboard
1. Aller dans l'éditeur SQL
2. Copier le contenu de database/migrations/social_media_integration.sql
3. Exécuter

# Via psql
psql -U postgres -d shareyoursales -f database/migrations/social_media_integration.sql
```

### 2. Tables Créées

- **social_media_connections** - Connexions OAuth (tokens chiffrés)
- **social_media_stats** - Historique des statistiques
- **social_media_posts** - Historique des publications
- **social_media_sync_logs** - Logs de synchronisation (audit)

### 3. Vues Matérialisées

- **mv_latest_social_stats** - Dernières stats par connexion (performance)
- **mv_top_influencers_by_engagement** - Top 100 influenceurs

### 4. Chiffrement des Tokens

Les tokens OAuth sont chiffrés avec `pgcrypto`:

```sql
-- Chiffrer un token
UPDATE social_media_connections
SET access_token_encrypted = pgp_sym_encrypt('token_value', 'encryption_key')
WHERE id = 'connection_id';

-- Déchiffrer un token
SELECT pgp_sym_decrypt(access_token_encrypted::bytea, 'encryption_key')
FROM social_media_connections
WHERE id = 'connection_id';
```

---

## Backend - Service

### Architecture du Service

Le fichier `backend/services/social_media_service.py` contient toute la logique métier:

```python
class SocialMediaService:
    # Connexion
    async def connect_instagram(user_id, instagram_user_id, access_token)
    async def connect_tiktok(user_id, authorization_code)
    async def disconnect_platform(connection_id, user_id)

    # Synchronisation
    async def sync_all_user_stats(user_id, platforms=None)
    async def fetch_instagram_stats(instagram_user_id, access_token)
    async def fetch_tiktok_stats(open_id, access_token)

    # Gestion tokens
    async def refresh_expiring_tokens(days_before=7)
    async def _exchange_instagram_token(short_lived_token)

    # Récupération données
    async def get_user_connections(user_id, platform=None, status_filter=None)
    async def get_latest_stats(user_id, platform=None)
    async def get_stats_history(user_id, platform, days=30)
    async def get_top_posts(user_id, platform=None, limit=10)
```

### Exemple d'Utilisation

```python
from services.social_media_service import SocialMediaService

service = SocialMediaService()

# Connecter Instagram
result = await service.connect_instagram(
    user_id="user-uuid",
    instagram_user_id="17841400000000",
    access_token="short_lived_token"
)

# Synchroniser les stats
results = await service.sync_all_user_stats(
    user_id="user-uuid",
    platforms=["instagram", "tiktok"]
)
```

---

## Backend - API Endpoints

### Routes Disponibles

```
POST   /api/social-media/connect/instagram      - Connecter Instagram
POST   /api/social-media/connect/tiktok         - Connecter TikTok
POST   /api/social-media/connect/facebook       - Connecter Facebook
GET    /api/social-media/connections            - Liste des connexions
DELETE /api/social-media/connections/{id}       - Déconnecter
GET    /api/social-media/connections/{id}/status - Statut connexion
POST   /api/social-media/sync                   - Sync manuel
GET    /api/social-media/stats                  - Stats récentes
GET    /api/social-media/stats/history          - Historique
GET    /api/social-media/posts/top              - Top posts
GET    /api/social-media/dashboard              - Dashboard complet
POST   /api/social-media/admin/refresh-tokens   - [ADMIN] Refresh tokens
GET    /api/social-media/admin/sync-logs        - [ADMIN] Logs
```

### Intégrer dans FastAPI

```python
# backend/server.py
from fastapi import FastAPI
from social_media_endpoints import router as social_media_router

app = FastAPI()

# Enregistrer le router
app.include_router(social_media_router)
```

### Exemples de Requêtes

```bash
# Connecter Instagram
curl -X POST "http://localhost:8000/api/social-media/connect/instagram" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_user_id": "17841400000000",
    "access_token": "short_lived_token"
  }'

# Récupérer les connexions
curl "http://localhost:8000/api/social-media/connections" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Synchroniser manuellement
curl -X POST "http://localhost:8000/api/social-media/sync" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["instagram"]}'
```

---

## Frontend

### Routes React

Ajouter dans `frontend/src/App.js`:

```jsx
import SocialMediaConnections from './pages/influencer/SocialMediaConnections';
import SocialMediaHistory from './pages/influencer/SocialMediaHistory';
import OAuthCallback from './pages/oauth/OAuthCallback';

// Dans le Router
<Route path="/influencer/social-media" element={<SocialMediaConnections />} />
<Route path="/influencer/social-media/history" element={<SocialMediaHistory />} />
<Route path="/oauth/callback/:platform" element={<OAuthCallback />} />
```

### Workflow OAuth Frontend

1. **Utilisateur clique "Connecter Instagram"**
   ```jsx
   const handleConnectInstagram = () => {
     const authUrl = `https://api.instagram.com/oauth/authorize?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&scope=instagram_basic,instagram_manage_insights&response_type=code`;
     window.location.href = authUrl;
   };
   ```

2. **Instagram redirige vers `/oauth/callback/instagram?code=XXX`**

3. **OAuthCallback.js échange le code**
   ```jsx
   // Échanger code contre token
   const tokenResponse = await fetch('https://api.instagram.com/oauth/access_token', {
     method: 'POST',
     body: new URLSearchParams({
       client_id: CLIENT_ID,
       client_secret: CLIENT_SECRET,
       grant_type: 'authorization_code',
       redirect_uri: REDIRECT_URI,
       code: code
     })
   });

   // Envoyer au backend
   await api.post('/api/social-media/connect/instagram', {
     instagram_user_id: tokenData.user_id,
     access_token: tokenData.access_token
   });
   ```

4. **Backend sauvegarde et récupère les stats**

### Composants Créés

- **SocialMediaConnections.js** - Page de gestion des connexions
- **SocialMediaHistory.js** - Historique et graphiques
- **OAuthCallback.js** - Gestionnaire de callback OAuth universel

---

## Celery - Tâches Asynchrones

### 1. Démarrer les Workers

```bash
# Terminal 1 - Worker principal
celery -A celery_app worker --loglevel=info --queue=social_media

# Terminal 2 - Worker notifications
celery -A celery_app worker --loglevel=info --queue=notifications

# Terminal 3 - Worker rapports
celery -A celery_app worker --loglevel=info --queue=reports

# Terminal 4 - Beat (scheduler)
celery -A celery_app beat --loglevel=info
```

### 2. Tâches Planifiées

| Tâche | Schedule | Description |
|-------|----------|-------------|
| `sync_all_active_connections` | Quotidien 8:00 | Synchronise tous les comptes actifs |
| `refresh_expiring_tokens` | Quotidien 2:00 | Rafraîchit les tokens expirant dans 7 jours |
| `check_and_repair_connections` | Quotidien 10:00 | Répare les connexions en erreur |
| `refresh_materialized_views` | Toutes les 6h | Rafraîchit les vues matérialisées |
| `send_weekly_reports` | Lundi 9:00 | Envoie les rapports hebdomadaires |
| `notify_token_expiration` | Quotidien 9:00 | Notifie les tokens expirant dans 3 jours |
| `cleanup_old_logs` | Dimanche 3:00 | Nettoie les logs > 90 jours |

### 3. Exécuter une Tâche Manuellement

```python
from celery_tasks.social_media_tasks import sync_user_connections

# Synchroniser un utilisateur spécifique
task = sync_user_connections.delay(
    user_id="user-uuid",
    platforms=["instagram", "tiktok"]
)

# Récupérer le résultat
result = task.get(timeout=30)
print(result)
```

### 4. Monitoring Celery

```bash
# Flower (Web UI pour Celery)
pip install flower
celery -A celery_app flower --port=5555

# Ouvrir http://localhost:5555
```

---

## Déploiement

### 1. Docker Compose

Créer `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker:
    build: ./backend
    command: celery -A celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - redis

  celery_beat:
    build: ./backend
    command: celery -A celery_app beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - redis

volumes:
  redis_data:
```

### 2. Production Best Practices

```bash
# Utiliser Supervisor pour gérer les workers
sudo apt-get install supervisor

# Créer /etc/supervisor/conf.d/celery.conf
[program:celery_worker]
command=celery -A celery_app worker --loglevel=info
directory=/var/www/shareyoursales/backend
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:celery_beat]
command=celery -A celery_app beat --loglevel=info
directory=/var/www/shareyoursales/backend
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

---

## Monitoring

### 1. Vérifier l'État des Connexions

```sql
-- Connexions actives par plateforme
SELECT platform, COUNT(*) as count
FROM social_media_connections
WHERE connection_status = 'active'
GROUP BY platform;

-- Connexions expirant bientôt
SELECT * FROM get_expiring_connections(7);

-- Dernières synchronisations
SELECT
    u.email,
    smc.platform,
    smc.last_synced_at,
    smc.connection_status
FROM social_media_connections smc
JOIN users u ON smc.user_id = u.id
ORDER BY last_synced_at DESC NULLS LAST
LIMIT 20;
```

### 2. Logs Celery

```python
# Récupérer les logs de sync
SELECT * FROM social_media_sync_logs
WHERE sync_status = 'failed'
ORDER BY created_at DESC
LIMIT 50;
```

### 3. Métriques Importantes

- **Taux de succès des syncs** : > 95%
- **Temps moyen de sync** : < 5 secondes
- **Tokens expirés** : < 1%
- **Connexions en erreur** : < 5%

---

## Troubleshooting

### Problème: Token Instagram invalide

**Symptôme**: Erreur 400 "Invalid access token"

**Solution**:
```python
# Rafraîchir le token
service = SocialMediaService()
await service.refresh_expiring_tokens(days_before=60)
```

### Problème: Celery worker ne démarre pas

**Symptôme**: `celery.exceptions.ImproperlyConfigured`

**Solution**:
```bash
# Vérifier Redis
redis-cli ping  # Doit répondre "PONG"

# Vérifier REDIS_URL
echo $REDIS_URL

# Redémarrer Redis
docker restart redis
```

### Problème: Stats ne se synchronisent pas

**Vérifications**:
1. Vérifier que Celery Beat est lancé
2. Vérifier les logs: `tail -f /var/log/celery/beat.log`
3. Vérifier la connexion: `SELECT connection_status FROM social_media_connections WHERE id = 'xxx';`
4. Forcer une sync manuelle via l'API

### Problème: Limites de taux API dépassées

**Instagram**: 200 requêtes/heure
**TikTok**: 100 requêtes/heure

**Solution**:
- Ajuster `rate_limit` dans `celery_app.py`
- Espacer les syncs
- Utiliser des caches Redis

---

## Sécurité

### 1. Chiffrement des Tokens

**JAMAIS** stocker les tokens OAuth en clair!

```python
# Utiliser pgcrypto
from cryptography.fernet import Fernet

cipher = Fernet(ENCRYPTION_KEY)
encrypted_token = cipher.encrypt(access_token.encode())
```

### 2. HTTPS Obligatoire

OAuth nécessite HTTPS en production. Utiliser Let's Encrypt:

```bash
sudo certbot --nginx -d yourdomain.com
```

### 3. Rate Limiting

```python
# Dans FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/social-media/sync")
@limiter.limit("5/minute")
async def sync_endpoint():
    ...
```

---

## Contact & Support

- **Documentation Instagram API**: https://developers.facebook.com/docs/instagram-api
- **Documentation TikTok API**: https://developers.tiktok.com/
- **Support**: support@shareyoursales.ma

---

**✅ Système d'intégration des réseaux sociaux complet et prêt pour la production!**
