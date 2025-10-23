╔═══════════════════════════════════════════════════════════════════════════╗
║                    SHAREYOURSALES - ARCHIVE COMPLÈTE                      ║
║                 SHARING IS WINNING - CHA-CHING! 💰                        ║
╚═══════════════════════════════════════════════════════════════════════════╝

📦 CONTENU DE L'ARCHIVE
─────────────────────────────────────────────────────────────────────────────
✅ Backend FastAPI complet (Python)
✅ Frontend React complet (Node.js)
✅ Configuration Supabase
✅ Base de données (schémas SQL)
✅ Documentation complète
✅ Guide d'installation locale


🚀 EXTRACTION RAPIDE
─────────────────────────────────────────────────────────────────────────────
# Extraire l'archive
tar -xzf shareyoursales-complete-YYYYMMDD-HHMMSS.tar.gz

# Lire le guide complet
cat GUIDE_INSTALLATION_LOCALE.md


⚡ DÉMARRAGE ULTRA-RAPIDE (3 étapes)
─────────────────────────────────────────────────────────────────────────────
1️⃣  BACKEND (Terminal 1)
   cd backend
   pip install -r requirements.txt
   python server.py
   → http://localhost:8001

2️⃣  FRONTEND (Terminal 2)
   cd frontend
   yarn install
   yarn start
   → http://localhost:3000

3️⃣  CONNEXION
   Ouvrir: http://localhost:3000
   Email: admin@shareyoursales.com
   Mot de passe: admin123
   Code 2FA: 123456


👥 COMPTES DE TEST
─────────────────────────────────────────────────────────────────────────────
┌─────────────┬────────────────────────────────┬──────────────┬───────────┐
│    RÔLE     │            EMAIL               │  MOT PASSE   │ CODE 2FA  │
├─────────────┼────────────────────────────────┼──────────────┼───────────┤
│ Admin       │ admin@shareyoursales.com       │ admin123     │ 123456    │
│ Marchand    │ contact@techstyle.fr           │ merchant123  │ 123456    │
│ Influenceur │ emma.style@instagram.com       │ influencer123│ 123456    │
└─────────────┴────────────────────────────────┴──────────────┴───────────┘


📁 STRUCTURE DU PROJET
─────────────────────────────────────────────────────────────────────────────
shareyoursales/
├── backend/                    # Backend FastAPI
│   ├── server.py              # Point d'entrée
│   ├── requirements.txt       # Dépendances Python
│   ├── .env                   # Configuration (Supabase, JWT)
│   ├── db_helpers.py          # Helpers base de données
│   └── supabase_client.py     # Client Supabase
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── App.js             # Composant principal
│   │   ├── pages/             # Pages (Login, Dashboard, etc.)
│   │   └── components/        # Composants réutilisables
│   ├── package.json           # Dépendances Node.js
│   ├── .env                   # Configuration frontend
│   └── tailwind.config.js     # Tailwind CSS
│
├── database/                   # Scripts SQL
│   ├── schema.sql
│   └── test_data.sql
│
├── GUIDE_INSTALLATION_LOCALE.md   # 📖 GUIDE COMPLET (LIRE EN PREMIER!)
└── README.md


🔧 PRÉREQUIS
─────────────────────────────────────────────────────────────────────────────
✅ Python 3.11 ou supérieur
✅ Node.js 16 ou supérieur
✅ Yarn (npm install -g yarn)
✅ Base de données (Supabase configuré par défaut)


🗄️ BASE DE DONNÉES
─────────────────────────────────────────────────────────────────────────────
Le projet est configuré avec Supabase (PostgreSQL cloud).
Les credentials sont dans backend/.env :

SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

⚠️  Pour utiliser une autre base de données, modifiez ces valeurs.


🌐 CONFIGURATION
─────────────────────────────────────────────────────────────────────────────
Backend (.env):
- PORT: 8001
- CORS: Activé pour tous les domaines (*)
- JWT: Secret configuré

Frontend (.env):
- REACT_APP_BACKEND_URL=http://localhost:8001
- PORT=3000


🎯 FONCTIONNALITÉS
─────────────────────────────────────────────────────────────────────────────
✅ Authentification 2FA sécurisée
✅ 3 types de comptes (Admin, Marchand, Influenceur)
✅ Dashboard personnalisé par rôle
✅ Système d'affiliation complet
✅ Génération de liens trackés
✅ Marketplace d'influenceurs
✅ Commissions automatiques
✅ Messagerie intégrée
✅ Rapports et analytics en temps réel
✅ Paiements sécurisés
✅ Devise: Dirham marocain (Dh)


📚 DOCUMENTATION
─────────────────────────────────────────────────────────────────────────────
1. GUIDE_INSTALLATION_LOCALE.md    → Installation complète pas à pas
2. database/DATABASE_DOCUMENTATION.md → Documentation base de données
3. database/ER_DIAGRAM.md          → Schéma relationnel
4. DEMARRAGE_RAPIDE.md             → Démarrage en 3 étapes


🐛 PROBLÈMES COURANTS
─────────────────────────────────────────────────────────────────────────────
❌ Backend ne démarre pas
   → Vérifier que Python 3.11+ est installé
   → Vérifier que le port 8001 est libre
   → Réinstaller: pip install -r requirements.txt

❌ Frontend ne compile pas
   → Supprimer node_modules et réinstaller: yarn install
   → Vérifier Node.js >= 16

❌ Erreur de connexion DB
   → Vérifier les credentials Supabase dans backend/.env
   → Tester la connexion internet


📞 SUPPORT
─────────────────────────────────────────────────────────────────────────────
Pour toute question, consulter la documentation complète dans:
→ GUIDE_INSTALLATION_LOCALE.md


🎉 BON DÉVELOPPEMENT !
─────────────────────────────────────────────────────────────────────────────
Version: 1.0.0
Date: Octobre 2025
Plateforme: ShareYourSales
Tagline: SHARING IS WINNING - CHA-CHING! 💰

╔═══════════════════════════════════════════════════════════════════════════╗
║              © 2025 ShareYourSales - Tous droits réservés                 ║
╚═══════════════════════════════════════════════════════════════════════════╝
