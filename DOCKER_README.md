# 🐳 Docker Setup - ShareYourSales

Guide complet pour déployer ShareYourSales avec Docker en développement et production.

## 📋 Prérequis

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **4 GB RAM** minimum (8 GB recommandé)
- **20 GB** espace disque

## 🚀 Démarrage Rapide (Développement)

### 1. Configuration Environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos valeurs
nano .env
```

### 2. Démarrer l'Application

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f backend
```

### 3. Accéder aux Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Outils Optionnels

```bash
# Démarrer avec les outils de développement
docker-compose --profile tools up -d

# Accéder aux outils
# - pgAdmin: http://localhost:5050
# - Redis Commander: http://localhost:8081
# - Flower (Celery): http://localhost:5555
```

## 🏭 Production

### 1. Configuration Production

```bash
# Copier et configurer .env pour production
cp .env.example .env.production

# IMPORTANT: Changer TOUTES les valeurs par défaut
# - JWT_SECRET (minimum 32 caractères)
# - REDIS_PASSWORD
# - DATABASE_PASSWORD
# - Clés API (Stripe, Instagram, TikTok, etc.)
```

### 2. Build Production

```bash
# Build les images
docker-compose -f docker-compose.prod.yml build

# Démarrer en production
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Services Production

Les services suivants sont démarrés:
- **Backend API** (4 workers)
- **Frontend** (build statique optimisé)
- **Nginx** (reverse proxy + SSL)
- **PostgreSQL**
- **Redis**
- **Celery Worker** (4 workers)
- **Celery Beat** (scheduler)
- **Flower** (monitoring)
- **DB Backup** (backups automatiques)

## 📊 Monitoring & Logs

### Logs

```bash
# Tous les logs
docker-compose logs -f

# Logs backend uniquement
docker-compose logs -f backend

# Logs avec timestamps
docker-compose logs -f --timestamps

# Dernières 100 lignes
docker-compose logs --tail=100
```

### Health Checks

```bash
# Vérifier santé des services
docker-compose ps

# Health check API
curl http://localhost:8000/health

# Health check détaillé
curl http://localhost:8000/health | jq
```

### Métriques

```bash
# Stats en temps réel
docker stats

# Métriques Celery (Flower)
open http://localhost:5555
```

## 🔧 Commandes Utiles

### Gestion Services

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart backend

# Rebuild après changement de code
docker-compose up -d --build
```

### Base de Données

```bash
# Exécuter migrations
docker-compose exec backend alembic upgrade head

# Créer une migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Backup manuel
docker-compose exec postgres pg_dump -U postgres shareyoursales > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres shareyoursales < backup.sql

# Console PostgreSQL
docker-compose exec postgres psql -U postgres shareyoursales
```

### Redis

```bash
# Console Redis
docker-compose exec redis redis-cli

# Avec authentification
docker-compose exec redis redis-cli -a your_redis_password

# Vider le cache
docker-compose exec redis redis-cli FLUSHALL
```

### Celery

```bash
# Voir les workers actifs
docker-compose exec celery_worker celery -A tasks inspect active

# Voir les tâches planifiées
docker-compose exec celery_beat celery -A tasks inspect scheduled

# Purger toutes les tâches
docker-compose exec celery_worker celery -A tasks purge
```

### Shell Backend

```bash
# Shell Python dans le backend
docker-compose exec backend python

# Shell interactif FastAPI
docker-compose exec backend python -i -c "from server import app"
```

## 🧪 Tests

```bash
# Lancer tous les tests
docker-compose exec backend pytest

# Tests avec coverage
docker-compose exec backend pytest --cov=. --cov-report=html

# Tests spécifiques
docker-compose exec backend pytest tests/test_auth.py

# Tests en parallèle
docker-compose exec backend pytest -n 4
```

## 🔐 Sécurité Production

### SSL/TLS

```bash
# Générer certificats auto-signés (dev)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem
```

### Secrets

```bash
# Ne JAMAIS commiter .env
echo ".env" >> .gitignore

# Utiliser Docker secrets en production
docker secret create jwt_secret ./secrets/jwt_secret.txt
```

### Firewall

```bash
# Autoriser seulement ports nécessaires
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## 🗄️ Backups

### Backup Automatique

Le service `db_backup` fait des backups quotidiens à 3h du matin dans `./database/backups/`

### Backup Manuel

```bash
# Backup complet
./scripts/backup.sh

# Backup vers S3
docker-compose exec db_backup sh -c "pg_dump -U postgres shareyoursales | gzip | aws s3 cp - s3://bucket/backup-$(date +%Y%m%d).sql.gz"
```

### Restore

```bash
# Arrêter l'application
docker-compose down

# Restore backup
docker-compose up -d postgres
docker-compose exec -T postgres psql -U postgres shareyoursales < backup.sql

# Redémarrer
docker-compose up -d
```

## 🐛 Troubleshooting

### Services ne démarrent pas

```bash
# Vérifier logs
docker-compose logs

# Vérifier santé des services
docker-compose ps

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Problèmes de permissions

```bash
# Fix permissions uploads
sudo chown -R 1000:1000 ./uploads

# Fix permissions logs
sudo chown -R 1000:1000 ./logs
```

### Espace disque

```bash
# Nettoyer images inutilisées
docker system prune -a

# Nettoyer volumes
docker volume prune

# Voir espace utilisé
docker system df
```

### Problèmes réseau

```bash
# Recréer le réseau
docker-compose down
docker network prune
docker-compose up -d
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scaler backend à 3 instances
docker-compose up -d --scale backend=3

# Scaler Celery workers
docker-compose up -d --scale celery_worker=5
```

### Load Balancing

Nginx fait automatiquement le load balancing entre les instances backend.

## 🔄 Mises à Jour

### Update Code

```bash
# Pull derniers changements
git pull

# Rebuild et redémarrer
docker-compose up -d --build

# Migrations DB si nécessaire
docker-compose exec backend alembic upgrade head
```

### Update Images

```bash
# Update images Docker
docker-compose pull

# Redémarrer avec nouvelles images
docker-compose up -d
```

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)

## ⚠️ Important

### Développement
- ✅ Hot reload activé
- ✅ Volumes montés pour le code
- ✅ Debug mode ON
- ✅ Ports exposés

### Production
- ⚠️ Changer TOUS les secrets
- ⚠️ SSL/TLS obligatoire
- ⚠️ Sentry activé
- ⚠️ Backups automatiques
- ⚠️ Ne pas exposer ports DB/Redis
- ⚠️ Utiliser Nginx comme reverse proxy

## 🆘 Support

Pour des questions ou problèmes:
- GitHub Issues: [github.com/shareyoursales/platform/issues](https://github.com/shareyoursales/platform/issues)
- Email: support@shareyoursales.ma
