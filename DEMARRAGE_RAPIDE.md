# ⚡ Démarrage Rapide - ShareYourSales 100% Fonctionnel

Application complète avec Supabase PostgreSQL + Système d'Abonnement

**Dernière mise à jour :** Novembre 2025

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
python3 server_complete.py
# OU avec uvicorn:
# python3 -m uvicorn server_complete:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # Première fois seulement
npm start
```

🎉 **Application lancée !**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔐 Se Connecter

| Rôle | Email | Mot de passe | 2FA |
|------|-------|--------------|-----|
| **Admin** | admin@shareyoursales.com | admin123 | 123456 |
| **Merchant** | contact@techstyle.fr | merchant123 | 123456 |
| **Influencer** | emma.style@instagram.com | influencer123 | 123456 |

**Note:** Les comptes de test ont des abonnements actifs pour tester toutes les fonctionnalités !

---

## ✅ Vérifier que Tout Fonctionne

### 1. Backend
```bash
curl http://localhost:8000/health
```
Devrait retourner:
```json
{
  "status": "healthy",
  "database": "Supabase Connected",
  "version": "2.0"
}
```

### 2. Abonnements (Nouveau ✨)
```bash
curl http://localhost:8000/api/subscriptions/current
```
Devrait retourner les détails de l'abonnement de l'utilisateur connecté.

### 2. Frontend
Ouvrir http://localhost:3000 → Devrait afficher la landing page

### 3. Connexion + Abonnement
1. Cliquer sur "Se connecter"
2. Utiliser admin@shareyoursales.com / admin123
3. Entrer code 2FA: 123456
4. ✅ Devrait afficher le dashboard admin

**Pour Merchant/Influencer:**
- Connectez-vous avec les comptes de test
- **Vérifiez la carte "Mon Abonnement"** dans le dashboard
- Testez le bouton "Améliorer mon Plan"

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
- [x] **Abonnements (plans, limites, upgrades)**

### ✅ Tracking
- [x] Génération de liens d'affiliation
- [x] Suivi des clics
- [x] Suivi des conversions
- [x] Analytics en temps réel

### ✅ Paiements
- [x] Gestion des payouts
- [x] Historique des commissions
- [x] Approbation des paiements
- [x] **Paiements mobiles Maroc (Orange, Inwi, Maroc Telecom)**
- [x] **Montant minimum de retrait configurable**

### ✅ Système d'Abonnement
- [x] **Plans Merchant (Freemium, Standard, Premium, Enterprise)**
- [x] **Plans Influenceur (Free, Pro, Elite)**
- [x] **Limites dynamiques (produits, campagnes, affiliés)**
- [x] **Taux de commission variables par plan**
- [x] **Affichage en temps réel dans les dashboards**
- [x] **Paiements instantanés pour plans premium**

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
- [ ] Login Merchant → Dashboard avec ventes **+ carte abonnement**
- [ ] Login Influencer → Dashboard avec earnings **+ carte abonnement**

### 2. Système d'Abonnement (NOUVEAU ✨)
- [ ] **Merchant:** Voir le plan actuel (Freemium par défaut)
- [ ] **Merchant:** Vérifier les limites (produits, campagnes, affiliés)
- [ ] **Influencer:** Voir le taux de commission (5% Free, 3% Pro)
- [ ] **Tester upgrade:** Cliquer sur "Améliorer mon Plan"
- [ ] **Admin:** Gérer les abonnements depuis `/admin/subscriptions`

### 3. Marketplace
- [ ] Voir le catalogue de produits
- [ ] Filtrer par catégorie
- [ ] Rechercher un produit

### 4. Génération de Liens (Influencer)
- [ ] Aller sur "Tracking Links"
- [ ] Générer un nouveau lien
- [ ] Copier le lien généré

### 5. Campagnes (Merchant)
- [ ] Créer une nouvelle campagne
- [ ] Voir les statistiques
- [ ] Modifier le budget

### 6. Payouts (Influencer)
- [ ] **Vérifier le montant minimum:** 50€ par défaut
- [ ] **Demander un paiement bancaire**
- [ ] **Tester paiement mobile Maroc** (Orange Money, Inwi Money, Cash Plus)
- [ ] Voir l'historique des paiements

### 7. Payouts (Admin)
- [ ] Voir les demandes de paiement
- [ ] Approuver un payout
- [ ] Voir l'historique
- [ ] **Configurer le montant minimum** via `/admin/platform-settings`

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

Après avoir vérifié que tout fonctionne (y compris le système d'abonnement):

1. **Personnaliser:**
   - Changer les couleurs dans tailwind.config.js
   - Ajouter votre logo
   - Configurer les plans d'abonnement

2. **Configurer Paiements:**
   - SMTP pour les emails réels
   - Stripe pour les paiements d'abonnement
   - Twilio pour les SMS 2FA
   - **Gateways Maroc (Orange Money, Inwi Money, Cash Plus)**

3. **Déployer:**
   - Backend sur Railway (voir GUIDE_DEPLOIEMENT_RAILWAY.md)
   - Frontend sur Vercel/Netlify
   - Base de données déjà sur Supabase ✅

4. **Tester les Abonnements:**
   - Créer un compte Stripe test
   - Tester les upgrades de plan
   - Vérifier les limites en temps réel

---

## 🆕 Nouvelles Fonctionnalités (Novembre 2025)

### ✨ Système d'Abonnement Complet
- **5 Plans Merchant:** Freemium, Standard, Premium, Enterprise, Custom
- **3 Plans Influenceur:** Free, Pro, Elite
- **Limites dynamiques:** Produits, campagnes, affiliés
- **Taux de commission:** Variables selon le plan (5% → 3% → 1%)
- **Affichage temps réel:** Dans tous les dashboards

### 💳 Paiements Mobiles Maroc
- **Orange Money, Inwi Money, Maroc Telecom**
- **Montant minimum configurable** (par défaut 50€)
- **Widget dédié** pour les paiements mobiles

### 📊 Analytics Avancés
- **Taux de conversion par plan**
- **ROI par niveau d'abonnement**
- **Prédictions de revenus**

---

**Status:** ✅ Application 100% Fonctionnelle avec Supabase + Système d'Abonnement !

**Version:** 3.0.0 - Subscription Edition

**Date:** Novembre 2025
