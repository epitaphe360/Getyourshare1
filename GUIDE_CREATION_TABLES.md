# 🚀 GUIDE RAPIDE - CRÉATION DES TABLES SUPABASE

## Étape 1: Ouvrir Supabase

1. Aller sur: https://supabase.com/dashboard
2. Sélectionner le projet: **iamezkmapbhlhhvvsits**
3. Cliquer sur **SQL Editor** dans le menu de gauche

## Étape 2: Créer les Tables

1. Cliquer sur **New Query**
2. Copier le contenu du fichier `database/create_tables_missing.sql`
3. Coller dans l'éditeur SQL
4. Cliquer sur **Run** (ou Ctrl+Enter)

## Étape 3: Vérifier

1. Aller dans **Table Editor**
2. Vérifier que ces 3 tables existent:
   - ✅ **invitations**
   - ✅ **settings**
   - ✅ **campaign_products**

## 📋 SQL à Exécuter

```sql
-- Table invitations pour le système d'invitation marchant->influenceur
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

-- Table settings pour les paramètres de la plateforme
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table junction campaign_products pour relier campagnes et produits
CREATE TABLE IF NOT EXISTS campaign_products (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(campaign_id, product_id)
);

-- Insertion des paramètres par défaut
INSERT INTO settings (key, value, description) VALUES
('platform_name', 'ShareYourSales', 'Nom de la plateforme'),
('commission_rate', '10', 'Taux de commission par défaut (%)'),
('min_payout', '50', 'Montant minimum pour un paiement (€)'),
('currency', 'EUR', 'Devise utilisée'),
('enable_2fa', 'false', 'Activer l''authentification 2FA'),
('email_notifications', 'true', 'Activer les notifications email'),
('max_commission_rate', '30', 'Taux de commission maximum (%)'),
('cookie_duration', '30', 'Durée du cookie de tracking (jours)')
ON CONFLICT (key) DO NOTHING;

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_invitations_merchant ON invitations(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invitations_influencer ON invitations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON invitations(status);
CREATE INDEX IF NOT EXISTS idx_invitations_campaign ON invitations(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_products_campaign ON campaign_products(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_products_product ON campaign_products(product_id);
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
```

## ✅ Après l'Exécution

Vous devriez voir:
```
Success. No rows returned
```

Cela signifie que les tables ont été créées avec succès!

## 🧪 Tester

Une fois les tables créées, testez les endpoints:

```powershell
cd backend
.\test_simple.ps1
```

Ou ouvrez l'application et testez les fonctionnalités!

---

**Temps estimé:** 2-3 minutes
**Difficulté:** Facile
**Prérequis:** Accès au tableau de bord Supabase
