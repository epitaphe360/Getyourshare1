# Guide d'Installation Locale - ShareYourSales

## 📦 Extraction de l'Archive

```bash
# Extraire l'archive
tar -xzf shareyoursales-backup-YYYYMMDD-HHMMSS.tar.gz

# Aller dans le dossier
cd shareyoursales/
```

## 🔧 Prérequis

- **Python 3.11+**
- **Node.js 16+** et **Yarn**
- **MongoDB** ou **PostgreSQL (Supabase)**

## 🚀 Installation Backend (FastAPI)

### 1. Créer un environnement virtuel Python

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# Ou sur Windows: venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration .env

Le fichier `backend/.env` contient déjà les configurations Supabase:

```env
# Supabase Configuration
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT Secret Key
SECRET_KEY=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
JWT_SECRET=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Configuration
CORS_ORIGINS=*
```

**⚠️ IMPORTANT**: Si vous utilisez une autre base de données, modifiez ces valeurs.

### 4. Démarrer le backend

```bash
# En mode développement
python server.py

# Le backend démarre sur http://localhost:8001
```

---

## 🎨 Installation Frontend (React)

### 1. Installer les dépendances

```bash
cd frontend
yarn install
```

### 2. Configuration .env

Le fichier `frontend/.env` doit pointer vers votre backend:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
HTTPS=false
PORT=3000
REACT_APP_ENABLE_VISUAL_EDITS=true
ENABLE_HEALTH_CHECK=false
```

**⚠️ Pour production**: Changez `REACT_APP_BACKEND_URL` vers votre domaine backend.

### 3. Démarrer le frontend

```bash
# En mode développement
yarn start

# Le frontend démarre sur http://localhost:3000
```

### 4. Build pour production

```bash
yarn build
# Les fichiers optimisés seront dans le dossier build/
```

---

## 👤 Comptes de Test

| Rôle | Email | Mot de passe | Code 2FA |
|------|-------|--------------|----------|
| **Admin** | admin@shareyoursales.com | admin123 | 123456 |
| **Marchand** | contact@techstyle.fr | merchant123 | 123456 |
| **Influenceur** | emma.style@instagram.com | influencer123 | 123456 |

---

## 🗄️ Base de Données

### Option 1: Utiliser Supabase (Configuré)

Le projet est déjà configuré pour utiliser Supabase PostgreSQL. Les credentials sont dans `backend/.env`.

**Tables principales**:
- `users` - Utilisateurs (admin, merchant, influencer)
- `campaigns` - Campagnes d'affiliation
- `products` - Produits
- `affiliate_links` - Liens de tracking
- `sales` - Ventes
- `commissions` - Commissions
- `messages` - Messagerie

### Option 2: Utiliser MongoDB local

1. Installer MongoDB
2. Modifier `backend/.env`:
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=shareyoursales
   ```
3. Adapter le code pour utiliser MongoDB au lieu de Supabase

---

## 📁 Structure du Projet

```
shareyoursales/
├── backend/                 # Backend FastAPI
│   ├── server.py           # Point d'entrée principal
│   ├── requirements.txt    # Dépendances Python
│   ├── db_helpers.py       # Helpers base de données
│   ├── supabase_client.py  # Client Supabase
│   ├── mock_data.py        # Données de test
│   └── .env                # Configuration backend
│
├── frontend/                # Frontend React
│   ├── src/
│   │   ├── App.js          # Composant principal
│   │   ├── pages/          # Pages de l'application
│   │   ├── components/     # Composants réutilisables
│   │   └── context/        # Context API (Auth, etc.)
│   ├── package.json        # Dépendances Node.js
│   ├── tailwind.config.js  # Configuration Tailwind CSS
│   └── .env                # Configuration frontend
│
├── database/               # Scripts SQL et documentation
│   ├── schema.sql
│   └── test_data.sql
│
└── README.md
```

---

## 🔥 Démarrage Rapide (3 commandes)

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python server.py

# Terminal 2 - Frontend
cd frontend && yarn start

# Ouvrir http://localhost:3000 dans le navigateur
```

---

## 🌐 Déploiement en Production

### Backend

**Option 1: Serveur Linux (Ubuntu/Debian)**
```bash
# Installer supervisor
sudo apt-get install supervisor

# Créer un fichier de config
sudo nano /etc/supervisor/conf.d/shareyoursales-backend.conf
```

Contenu:
```ini
[program:shareyoursales-backend]
command=/path/to/venv/bin/python /path/to/backend/server.py
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/shareyoursales/backend.err.log
stdout_logfile=/var/log/shareyoursales/backend.out.log
```

**Option 2: Docker**
```dockerfile
# Dockerfile pour backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "server.py"]
```

### Frontend

**Build optimisé**
```bash
cd frontend
yarn build
```

**Déployer sur Nginx**
```nginx
server {
    listen 80;
    server_name votredomaine.com;
    
    root /path/to/frontend/build;
    index index.html;
    
    location / {
        try_files $uri /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🐛 Résolution de Problèmes

### Backend ne démarre pas
```bash
# Vérifier les logs
cat /var/log/shareyoursales/backend.err.log

# Vérifier que le port 8001 est libre
lsof -i :8001

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Frontend ne compile pas
```bash
# Nettoyer le cache
rm -rf node_modules package-lock.json
yarn install

# Vérifier la version de Node
node --version  # Doit être >= 16
```

### Erreur de connexion à la base de données
```bash
# Vérifier les credentials dans backend/.env
# Tester la connexion Supabase
python -c "from supabase_client import supabase; print(supabase.table('users').select('*').limit(1).execute())"
```

---

## 📝 Notes Importantes

1. **Sécurité**: Changez tous les secrets (`JWT_SECRET`, `SECRET_KEY`) en production
2. **CORS**: Configurez correctement `CORS_ORIGINS` pour votre domaine
3. **HTTPS**: Utilisez HTTPS en production (Let's Encrypt gratuit)
4. **Base de données**: Sauvegardez régulièrement votre base Supabase
5. **Logs**: Surveillez les logs pour détecter les erreurs

---

## 📞 Support

Pour toute question ou problème:
- Documentation complète dans `/database/DATABASE_DOCUMENTATION.md`
- Schéma de la base dans `/database/ER_DIAGRAM.md`
- Guide de démarrage rapide: `/DEMARRAGE_RAPIDE.md`

---

## 🎯 Fonctionnalités Principales

✅ Authentification 2FA
✅ Gestion multi-rôles (Admin, Marchand, Influenceur)
✅ Système d'affiliation complet
✅ Génération de liens trackés
✅ Dashboard temps réel
✅ Marketplace d'influenceurs
✅ Système de commissions automatique
✅ Messagerie intégrée
✅ Rapports et analytics
✅ Paiements sécurisés

---

**Version**: 1.0.0  
**Date**: Octobre 2025  
**Plateforme**: ShareYourSales - SHARING IS WINNING - CHA-CHING! 🎉
