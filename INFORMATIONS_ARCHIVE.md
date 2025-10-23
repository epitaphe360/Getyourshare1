# 📦 Archive ShareYourSales - Informations Complètes

## 🎯 Fichiers Créés

### Archive Principale
```
📦 shareyoursales-projet-complet.tar.gz (671 KB)
🔐 shareyoursales-projet-complet.tar.gz.sha256 (Checksum)
```

### Documentation
```
📖 GUIDE_INSTALLATION_LOCALE.md (Guide complet d'installation)
📄 README_EXTRACTION.txt (Instructions rapides)
📋 INFORMATIONS_ARCHIVE.md (Ce fichier)
```

---

## 📥 Téléchargement

Les fichiers sont disponibles dans le dossier `/app/` :

1. **shareyoursales-projet-complet.tar.gz** (671 KB)
2. **shareyoursales-projet-complet.tar.gz.sha256** (Checksum)
3. **GUIDE_INSTALLATION_LOCALE.md** (Documentation)
4. **README_EXTRACTION.txt** (Instructions)

---

## 🔐 Vérification d'Intégrité

### SHA-256 Checksum
```
08c057bdd042df34d12e36c981b7bd6f06c5c650ee15bbdcfdbb90a177d8e9cb
```

### Commande de Vérification
```bash
sha256sum -c shareyoursales-projet-complet.tar.gz.sha256
```

**Résultat attendu**: `shareyoursales-projet-complet.tar.gz: OK`

---

## 📦 Contenu de l'Archive

### Structure Complète (256 fichiers/dossiers)

```
shareyoursales/
│
├── 📁 backend/                          # Backend FastAPI
│   ├── server.py                        # Serveur principal
│   ├── requirements.txt                 # Dépendances Python
│   ├── .env                             # Configuration Supabase
│   ├── db_helpers.py                    # Helpers DB
│   ├── supabase_client.py              # Client Supabase
│   ├── mock_data.py                    # Données de test
│   ├── advanced_endpoints.py           # Endpoints avancés
│   ├── influencer_search_endpoints.py  # Recherche influenceurs
│   └── upload_endpoints.py             # Upload de fichiers
│
├── 📁 frontend/                         # Frontend React
│   ├── src/
│   │   ├── App.js                       # Application principale
│   │   ├── 📁 pages/                    # Pages
│   │   │   ├── Login.js
│   │   │   ├── Dashboard.js
│   │   │   ├── LandingPage.js
│   │   │   ├── Marketplace.js
│   │   │   ├── TrackingLinks.js
│   │   │   └── ...
│   │   ├── 📁 components/               # Composants
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.js           # Menu différencié par rôle
│   │   │   │   ├── Layout.js
│   │   │   │   └── Header.js
│   │   │   └── common/
│   │   │       ├── Button.js
│   │   │       ├── Card.js
│   │   │       └── ...
│   │   ├── 📁 context/                  # Context API
│   │   │   └── AuthContext.js           # Authentification
│   │   └── 📁 utils/                    # Utilitaires
│   │       └── api.js
│   ├── package.json                     # Dépendances Node
│   ├── tailwind.config.js              # Config Tailwind
│   └── .env                            # Config frontend
│
├── 📁 database/                        # Base de données
│   ├── schema.sql                      # Schéma complet
│   ├── test_data.sql                   # Données de test
│   ├── DATABASE_DOCUMENTATION.md       # Documentation DB
│   └── ER_DIAGRAM.md                   # Diagramme relationnel
│
├── 📁 scripts/                         # Scripts utilitaires
│
├── 📖 GUIDE_INSTALLATION_LOCALE.md     # Guide complet
├── 📄 README_EXTRACTION.txt            # Instructions rapides
├── 📋 INFORMATIONS_ARCHIVE.md          # Ce fichier
└── 📝 README.md                        # README principal
```

### Fichiers Exclus (pour réduire la taille)
- ❌ `node_modules/` (sera réinstallé avec `yarn install`)
- ❌ `__pycache__/` (cache Python)
- ❌ `.cache/` (cache de build)
- ❌ `*.log` (fichiers logs)
- ❌ `.git/` (historique git)
- ❌ `frontend/build/` (build de production)

---

## 🚀 Installation Rapide

### 1️⃣ Extraction
```bash
tar -xzf shareyoursales-projet-complet.tar.gz
cd shareyoursales/
```

### 2️⃣ Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
```
→ Backend disponible sur **http://localhost:8001**

### 3️⃣ Frontend
```bash
cd frontend
yarn install
yarn start
```
→ Frontend disponible sur **http://localhost:3000**

### 4️⃣ Connexion
- **URL**: http://localhost:3000
- **Email**: admin@shareyoursales.com
- **Password**: admin123
- **Code 2FA**: 123456

---

## 👥 Comptes de Test Disponibles

| Rôle | Email | Mot de passe | Code 2FA | Accès |
|------|-------|--------------|----------|-------|
| **Admin** | admin@shareyoursales.com | admin123 | 123456 | Accès complet |
| **Marchand** | contact@techstyle.fr | merchant123 | 123456 | Gestion campagnes |
| **Influenceur** | emma.style@instagram.com | influencer123 | 123456 | Marketplace |

---

## 🗄️ Configuration Base de Données

### Supabase (PostgreSQL Cloud) - Configuré par défaut

Le projet utilise **Supabase** avec les credentials dans `backend/.env` :

```env
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Tables Principales
- `users` - Utilisateurs (admin, merchant, influencer)
- `campaigns` - Campagnes d'affiliation
- `products` - Produits à promouvoir
- `affiliate_links` - Liens de tracking
- `sales` - Ventes réalisées
- `commissions` - Commissions gagnées
- `messages` - Système de messagerie
- `notifications` - Notifications

---

## 🎯 Fonctionnalités Implémentées

### ✅ Authentification & Sécurité
- Authentification 2FA sécurisée
- JWT tokens avec expiration
- Gestion des sessions
- Hash des mots de passe (bcrypt)

### ✅ Gestion Multi-Rôles
- **Admin**: Accès complet à la plateforme
- **Marchand**: Gestion campagnes, produits, affiliés
- **Influenceur**: Marketplace, liens, commissions

### ✅ Système d'Affiliation
- Génération de liens trackés uniques
- Suivi des clics en temps réel
- Calcul automatique des commissions
- Système MLM (Multi-Level Marketing)

### ✅ Dashboard Personnalisé
- KPIs spécifiques par rôle
- Graphiques en temps réel
- Top performers
- Rapports détaillés

### ✅ Marketplace
- Recherche d'influenceurs
- Filtres avancés (secteur, audience, taux)
- Système de notation
- Collaboration directe

### ✅ Commissions & Paiements
- Calcul automatique des commissions
- Historique des paiements
- Demandes de retrait
- Support Dh (Dirham marocain)

### ✅ Messagerie
- Communication inter-utilisateurs
- Notifications en temps réel
- Historique des conversations

---

## 🔧 Technologies Utilisées

### Backend
- **Python 3.11+** - Langage
- **FastAPI** - Framework web
- **Supabase** - Base de données PostgreSQL
- **JWT** - Authentification
- **Bcrypt** - Hash de mots de passe
- **Uvicorn** - Serveur ASGI

### Frontend
- **React 18** - Framework UI
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Lucide React** - Icônes
- **Recharts** - Graphiques
- **Axios** - Requêtes HTTP

### Base de Données
- **PostgreSQL** (via Supabase)
- **Tables**: 15+ tables relationnelles
- **Relations**: Foreign keys, indexes

---

## 📊 Statistiques du Projet

- **Lignes de code Backend**: ~5,000
- **Lignes de code Frontend**: ~8,000
- **Composants React**: 50+
- **Pages**: 25+
- **API Endpoints**: 40+
- **Tables DB**: 15+

---

## 🌐 Déploiement Production

### Recommandations

1. **Backend**
   - Utiliser Gunicorn ou Uvicorn avec workers
   - Configurer HTTPS (Let's Encrypt)
   - Limiter CORS aux domaines autorisés
   - Changer tous les secrets (JWT_SECRET, etc.)

2. **Frontend**
   - Build optimisé: `yarn build`
   - CDN pour les assets statiques
   - Compression Gzip/Brotli
   - Cache headers configurés

3. **Base de Données**
   - Sauvegardes automatiques quotidiennes
   - Monitoring des performances
   - Index sur les colonnes fréquemment recherchées

4. **Sécurité**
   - HTTPS uniquement
   - Rate limiting sur les API
   - Validation des inputs
   - Protection CSRF
   - Headers de sécurité (HSTS, CSP, etc.)

---

## 📚 Documentation Complète

### Guides Disponibles
1. **GUIDE_INSTALLATION_LOCALE.md** - Installation pas à pas complète
2. **README_EXTRACTION.txt** - Instructions rapides d'extraction
3. **database/DATABASE_DOCUMENTATION.md** - Documentation base de données
4. **database/ER_DIAGRAM.md** - Schéma relationnel complet
5. **DEMARRAGE_RAPIDE.md** - Démarrage en 3 étapes

### Lire en Premier
👉 **GUIDE_INSTALLATION_LOCALE.md** pour l'installation complète

---

## 🐛 Support & Dépannage

### Problèmes Courants

**Backend ne démarre pas**
```bash
# Vérifier Python 3.11+
python3 --version

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall

# Vérifier le port 8001
lsof -i :8001
```

**Frontend ne compile pas**
```bash
# Supprimer cache et réinstaller
rm -rf node_modules yarn.lock
yarn install

# Vérifier Node.js >= 16
node --version
```

**Erreur base de données**
```bash
# Tester connexion Supabase
python -c "from supabase_client import supabase; print('OK')"

# Vérifier credentials dans backend/.env
cat backend/.env | grep SUPABASE
```

---

## 📝 Notes Importantes

### ⚠️ Avant le Déploiement en Production

1. **Changer tous les secrets**
   - `JWT_SECRET` dans `backend/.env`
   - `SECRET_KEY` dans `backend/.env`

2. **Configurer CORS**
   - Modifier `CORS_ORIGINS` pour votre domaine uniquement

3. **Base de données**
   - Créer des sauvegardes automatiques
   - Configurer les connexions SSL

4. **SSL/HTTPS**
   - Obligatoire en production
   - Utiliser Let's Encrypt (gratuit)

5. **Monitoring**
   - Logs centralisés
   - Alertes sur les erreurs
   - Surveillance des performances

---

## 📞 Contact & Support

Pour toute question ou assistance:

1. Consulter **GUIDE_INSTALLATION_LOCALE.md**
2. Lire la documentation dans `database/`
3. Vérifier les logs d'erreur

---

## 🎉 Version & Date

- **Version**: 1.0.0
- **Date de création**: Octobre 2025
- **Dernière mise à jour**: 23 Octobre 2025
- **Taille archive**: 671 KB
- **Fichiers**: 256 fichiers/dossiers

---

## 📜 License

© 2025 ShareYourSales - Tous droits réservés

---

╔═══════════════════════════════════════════════════════════════════╗
║                    SHAREYOURSALES                                  ║
║           SHARING IS WINNING - CHA-CHING! 💰                      ║
╚═══════════════════════════════════════════════════════════════════╝
