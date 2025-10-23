# 🚀 DÉMARRAGE EN 3 ÉTAPES

## ⚡ Guide Ultra-Rapide

---

## ÉTAPE 1: Créer les Tables (2 min) ⏱️

### Option A: Via Interface Supabase (Recommandé)
1. Ouvrir https://supabase.com/dashboard
2. Sélectionner le projet `iamezkmapbhlhhvvsits`
3. Cliquer sur **SQL Editor** (menu gauche)
4. Cliquer sur **New Query**
5. Copier/Coller le contenu de `database/create_tables_missing.sql`
6. Cliquer sur **Run** (ou Ctrl+Enter)
7. Vérifier le message: ✅ "Success. No rows returned"

### Option B: Copier le SQL Directement
```sql
-- Table invitations
CREATE TABLE IF NOT EXISTS invitations (
    id SERIAL PRIMARY KEY,
    merchant_id INTEGER REFERENCES users(id),
    influencer_id INTEGER REFERENCES users(id),
    campaign_id INTEGER REFERENCES campaigns(id),
    status VARCHAR(20) DEFAULT 'pending',
    message TEXT,
    commission_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    responded_at TIMESTAMP
);

-- Table settings
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table campaign_products
CREATE TABLE IF NOT EXISTS campaign_products (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(campaign_id, product_id)
);

-- Paramètres par défaut
INSERT INTO settings (key, value, description) VALUES
('platform_name', 'ShareYourSales', 'Nom de la plateforme'),
('commission_rate', '10', 'Taux de commission par défaut (%)'),
('min_payout', '50', 'Montant minimum pour un paiement (€)'),
('currency', 'EUR', 'Devise utilisée'),
('enable_2fa', 'false', 'Activer l''authentification 2FA')
ON CONFLICT (key) DO NOTHING;

-- Index
CREATE INDEX IF NOT EXISTS idx_invitations_merchant ON invitations(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invitations_influencer ON invitations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_campaign_products_campaign ON campaign_products(campaign_id);
```

✅ **Fait !** Les tables sont créées.

---

## ÉTAPE 2: Démarrer l'Application (30 sec) ⏱️

### Option A: Script Automatique (Le Plus Simple)
```powershell
.\start.ps1
```
✅ Démarre tout automatiquement  
✅ Ouvre le navigateur  
✅ Affiche tous les liens

### Option B: Manuel
```powershell
# Terminal 1 - Backend
cd backend
python server.py

# Terminal 2 - Frontend
cd frontend
serve -s build
```

**Résultat Attendu:**
```
✅ Tous les endpoints avancés ont été intégrés
✅ Endpoints avancés chargés avec succès
🚀 Démarrage du serveur Supabase...
INFO:     Uvicorn running on http://0.0.0.0:8001
```

---

## ÉTAPE 3: Tester (2 min) ⏱️

### Option A: Test Automatique
```powershell
cd backend
.\test_simple.ps1
```

**Résultat Attendu:**
```
🔐 Test de connexion...
✅ Connexion réussie - Token obtenu

📦 Test GET /api/products...
✅ 3 produits trouvés

🎯 Test GET /api/campaigns...
✅ 4 campagnes trouvées

💰 Test GET /api/sales/1...
✅ 8 ventes trouvées

📊 Test GET /api/reports/performance...
✅ Rapport généré:
   Total ventes: 8
   Revenus: 2547.92€
   Commissions: 254.79€
```

### Option B: Test Manuel
1. Ouvrir http://localhost:52112
2. Cliquer sur un bouton de connexion rapide:
   - 🟣 **Admin** (admin@shareyoursales.com)
   - 🔵 **Marchand** (contact@techstyle.fr)
   - 🌸 **Influenceur** (emma.style@instagram.com)
3. Explorer le Dashboard
4. Vérifier que les données apparaissent

---

## ✅ CHECKLIST COMPLÈTE

- [ ] **Tables créées** dans Supabase
- [ ] **Backend démarré** (http://localhost:8001)
- [ ] **Frontend démarré** (http://localhost:52112)
- [ ] **Connexion réussie** avec un compte de test
- [ ] **Données visibles** dans le dashboard
- [ ] **Tests exécutés** avec succès

---

## 🎯 URLS IMPORTANTES

| Service | URL | Description |
|---------|-----|-------------|
| 🌐 **Application** | http://localhost:52112 | Interface utilisateur |
| 🔧 **API** | http://localhost:8001 | Backend REST API |
| 📖 **API Docs** | http://localhost:8001/docs | Documentation Swagger |
| 🗄️ **Supabase** | https://supabase.com/dashboard | Base de données |

---

## 🔑 COMPTES DE TEST

| Rôle | Email | Password | Bouton |
|------|-------|----------|--------|
| 👤 **Admin** | admin@shareyoursales.com | Admin123! | 🟣 Violet |
| 🏪 **Marchand** | contact@techstyle.fr | Merchant123! | 🔵 Bleu |
| 📸 **Influenceur** | emma.style@instagram.com | Influencer123! | 🌸 Rose |

---

## 📊 CE QUI FONCTIONNE MAINTENANT

### ✅ Authentification
- Login/Logout
- Session JWT
- Vérification automatique
- Quick login buttons

### ✅ Produits
- Liste complète (GET /api/products)
- Création (POST /api/products)
- Modification (PUT /api/products/{id})
- Suppression (DELETE /api/products/{id})

### ✅ Campagnes
- Liste complète (GET /api/campaigns)
- Modification (PUT /api/campaigns/{id})
- Suppression (DELETE /api/campaigns/{id})
- Assignation produits (POST /api/campaigns/{id}/products)

### ✅ Invitations
- Créer invitation (POST /api/invitations)
- Accepter invitation (POST /api/invitations/accept)
- Lister invitations (GET /api/invitations/user/{id})

### ✅ Ventes & Commissions
- Enregistrer vente (POST /api/sales)
- Consulter ventes (GET /api/sales/{id})
- Consulter commissions (GET /api/commissions/{id})
- Calcul automatique des commissions

### ✅ Paiements
- Demander paiement (POST /api/payouts/request)
- Approuver paiement (PUT /api/payouts/{id}/approve)
- Historique (GET /api/payouts/user/{id})

### ✅ Tracking
- Enregistrer clics (POST /api/tracking/click)
- Statistiques (GET /api/tracking/stats/{id})

### ✅ Rapports
- Performance détaillée (GET /api/reports/performance)
- Métriques calculées en temps réel

### ✅ Paramètres
- Liste paramètres (GET /api/settings)
- Modifier paramètre (PUT /api/settings/{key})

**TOTAL: 30+ endpoints opérationnels**

---

## 🚨 EN CAS DE PROBLÈME

### Le serveur ne démarre pas
```powershell
# Vérifier que le port est libre
netstat -ano | findstr :8001

# Tuer le processus si nécessaire
taskkill /PID <PID> /F

# Redémarrer
cd backend
python server.py
```

### Erreur "Table does not exist"
➡️ Retourner à l'**ÉTAPE 1** et créer les tables

### Erreur 401 Unauthorized
➡️ Se reconnecter avec un compte de test

### Les données ne s'affichent pas
```powershell
# Re-seed la base de données
cd backend
python seed_all_data.py
```

---

## 📚 POUR ALLER PLUS LOIN

### Documentation Complète
- **INDEX.md** - Index de toute la documentation
- **STATUT_FINAL.md** - État détaillé du projet
- **DEVELOPPEMENT_COMPLET_RESUME.md** - Résumé technique
- **GUIDE_CREATION_TABLES.md** - Guide détaillé SQL

### Commandes Avancées
```powershell
# Voir les logs backend en temps réel
cd backend
python server.py

# Tester un endpoint spécifique
curl http://localhost:8001/api/products

# Rebuild le frontend
cd frontend
npm run build
```

---

## 🎉 C'EST PRÊT !

Après ces 3 étapes simples, votre application est **100% fonctionnelle** !

🚀 **Profitez-en !**

---

**Temps Total:** ~5 minutes  
**Difficulté:** ⭐⭐ (Facile)  
**Résultat:** Application complète avec backend fonctionnel !
