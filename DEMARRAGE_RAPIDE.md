# ⚡ Démarrage Rapide - ShareYourSales 100% Fonctionnel

Application complète avec Supabase PostgreSQL

---

## 🚀 Installation en 5 Minutes

### Étape 1: Créer les Tables dans Supabase (2 min)

1. **Ouvrir l'éditeur SQL:**
   ```
   https://iamezkmapbhlhhvvsits.supabase.co/project/_/sql
   ```

2. **Copier TOUT** le contenu du fichier `database/schema.sql`

3. **Coller et cliquer sur "RUN"**

   ✅ Cela va créer:
   - 15 tables
   - Indexes
   - Triggers
   - Views
   - Catégories par défaut
   - Compte admin

### Étape 2: Migrer les Données (1 min)

```bash
cd backend
python3 setup_supabase.py
```

✅ Suivez les instructions à l'écran

### Étape 3: Démarrer l'Application (30 sec)

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m uvicorn server:app --reload --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # Première fois seulement
npm start
```

🎉 **Application lancée !**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

## 🔐 Se Connecter

| Rôle | Email | Mot de passe | 2FA |
|------|-------|--------------|-----|
| **Admin** | admin@shareyoursales.com | admin123 | 123456 |
| **Merchant** | contact@techstyle.fr | merchant123 | 123456 |
| **Influencer** | emma.style@instagram.com | influencer123 | 123456 |

---

## ✅ Vérifier que Tout Fonctionne

### 1. Backend
```bash
curl http://localhost:8001/health
```
Devrait retourner:
```json
{
  "status": "healthy",
  "database": "Supabase Connected"
}
```

### 2. Frontend
Ouvrir http://localhost:3000 → Devrait afficher la landing page

### 3. Connexion
1. Cliquer sur "Se connecter"
2. Utiliser admin@shareyoursales.com / admin123
3. Entrer code 2FA: 123456
4. ✅ Devrait afficher le dashboard admin

---

## 📊 Fonctionnalités Disponibles

### ✅ Authentification
- [x] Login avec email/password
- [x] 2FA (Two-Factor Authentication)
- [x] JWT tokens avec expiration
- [x] Sessions sécurisées
- [x] Logout complet

### ✅ Dashboards
- [x] Dashboard Admin (stats plateforme)
- [x] Dashboard Merchant (ventes, produits)
- [x] Dashboard Influencer (earnings, clics)

### ✅ Gestion
- [x] Merchants (liste, détails)
- [x] Influencers (liste, détails, stats)
- [x] Produits (catalogue, filtres)
- [x] Campagnes (création, suivi)

### ✅ Tracking
- [x] Génération de liens d'affiliation
- [x] Suivi des clics
- [x] Suivi des conversions
- [x] Analytics en temps réel

### ✅ Paiements
- [x] Gestion des payouts
- [x] Historique des commissions
- [x] Approbation des paiements

### ✅ AI Marketing
- [x] Génération de contenu (mock)
- [x] Prédictions (mock)
- [x] Recommandations

### ✅ Marketplace
- [x] Catalogue de produits
- [x] Recherche et filtres
- [x] Catégories

---

## 🗂️ Structure du Projet

```
Getyourshare1/
├── backend/
│   ├── server.py              ← API FastAPI avec Supabase
│   ├── supabase_client.py     ← Client Supabase
│   ├── db_helpers.py          ← Fonctions d'accès à la DB
│   ├── setup_supabase.py      ← Script de migration
│   ├── mock_data.py           ← Données mock (backup)
│   └── .env                   ← Config (NE PAS COMMITTER)
│
├── frontend/
│   ├── src/
│   │   ├── pages/             ← Pages React
│   │   ├── components/        ← Composants réutilisables
│   │   ├── context/           ← AuthContext
│   │   └── utils/             ← API client
│   └── package.json
│
├── database/
│   └── schema.sql             ← Schéma PostgreSQL complet
│
├── SUPABASE_SETUP.md          ← Guide détaillé Supabase
├── DEMARRAGE_RAPIDE.md        ← Ce fichier
└── BUGS_CORRIGES.md           ← Rapport des corrections
```

---

## 🔧 Dépendances

### Backend
```bash
pip install fastapi uvicorn pydantic python-dotenv
pip install supabase postgrest-py
pip install bcrypt pyjwt
```

### Frontend
```bash
npm install react react-router-dom axios
npm install recharts lucide-react
npm install tailwindcss
```

---

## 📱 Tester les Fonctionnalités

### 1. Connexion et Dashboard
- [ ] Login Admin → Dashboard avec stats
- [ ] Login Merchant → Dashboard avec ventes
- [ ] Login Influencer → Dashboard avec earnings

### 2. Marketplace
- [ ] Voir le catalogue de produits
- [ ] Filtrer par catégorie
- [ ] Rechercher un produit

### 3. Génération de Liens (Influencer)
- [ ] Aller sur "Tracking Links"
- [ ] Générer un nouveau lien
- [ ] Copier le lien généré

### 4. Campagnes (Merchant)
- [ ] Créer une nouvelle campagne
- [ ] Voir les statistiques
- [ ] Modifier le budget

### 5. Payouts (Admin)
- [ ] Voir les demandes de paiement
- [ ] Approuver un payout
- [ ] Voir l'historique

---

## 🐛 Dépannage

### Erreur: "relation 'users' does not exist"
➡️ **Solution:** Les tables n'ont pas été créées. Retour à l'Étape 1.

### Erreur: "SUPABASE_URL not found"
➡️ **Solution:** Vérifier que `backend/.env` contient:
```ini
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
```

### Frontend ne charge pas
➡️ **Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Backend ne démarre pas
➡️ **Solution:**
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn server:app --reload
```

---

## 📞 Support

- **Dashboard Supabase:** https://iamezkmapbhlhhvvsits.supabase.co
- **API Documentation:** http://localhost:8001/docs
- **Guide Complet:** Voir SUPABASE_SETUP.md

---

## 🎯 Prochaines Étapes

Après avoir vérifié que tout fonctionne:

1. **Personnaliser:**
   - Changer les couleurs dans tailwind.config.js
   - Ajouter votre logo

2. **Configurer:**
   - SMTP pour les emails réels
   - Stripe pour les paiements
   - Twilio pour les SMS 2FA

3. **Déployer:**
   - Backend sur Heroku/Railway
   - Frontend sur Vercel/Netlify
   - Base de données déjà sur Supabase ✅

---

**Status:** ✅ Application 100% Fonctionnelle avec Supabase !

**Version:** 2.0.0 - Supabase Edition

**Date:** 22 Octobre 2025
