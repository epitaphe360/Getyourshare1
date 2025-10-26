# 🚀 Instructions SQL pour Supabase - ShareYourSales

## ✅ ÉTAPE FINALE : Créer les 8 Nouvelles Tables

Maintenant que le backend est prêt, il faut créer les tables dans Supabase.

---

## 📋 Étapes à Suivre

### 1️⃣ Ouvrir Supabase SQL Editor

1. Va sur https://app.supabase.com
2. Sélectionne ton projet **ShareYourSales**
3. Dans le menu de gauche, clique sur **SQL Editor**
4. Clique sur **New Query**

---

### 2️⃣ Copier le SQL

**Ouvre ce fichier** :
```
/home/user/Getyourshare1/database/migrations/create_tables_SIMPLE.sql
```

**Ou copie le contenu ci-dessous** (246 lignes) :

<details>
<summary>📄 Voir le SQL complet (cliquer pour développer)</summary>

```sql
-- ============================================
-- Migration ULTRA-SIMPLIFIÉE ShareYourSales
-- Crée UNIQUEMENT les 8 nouvelles tables
-- NE TOUCHE À AUCUNE TABLE EXISTANTE
-- ============================================

-- 1. TABLE TRUST_SCORES
CREATE TABLE IF NOT EXISTS trust_scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    username TEXT,
    trust_score DECIMAL(5,2) NOT NULL DEFAULT 50.00,
    trust_level TEXT DEFAULT 'average',
    breakdown JSONB DEFAULT '{}'::jsonb,
    badges TEXT[] DEFAULT ARRAY[]::TEXT[],
    fraud_indicators JSONB DEFAULT '[]'::jsonb,
    campaign_stats JSONB DEFAULT '{}'::jsonb,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_trust_scores_user_id ON trust_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_trust_scores_score ON trust_scores(trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_trust_scores_level ON trust_scores(trust_level);


-- 2. TABLE PAYOUTS
CREATE TABLE IF NOT EXISTS payouts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    fee DECIMAL(10,2) NOT NULL DEFAULT 0,
    net_amount DECIMAL(10,2) NOT NULL,
    provider TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    payout_id TEXT UNIQUE,
    transaction_id TEXT,
    qr_code_url TEXT,
    estimated_completion TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_payouts_user_id ON payouts(user_id);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
CREATE INDEX IF NOT EXISTS idx_payouts_payout_id ON payouts(payout_id);
CREATE INDEX IF NOT EXISTS idx_payouts_created ON payouts(created_at DESC);


-- 3. TABLE PAYMENT_ACCOUNTS
CREATE TABLE IF NOT EXISTS payment_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    account_name TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, provider, phone_number)
);

CREATE INDEX IF NOT EXISTS idx_payment_accounts_user_id ON payment_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_accounts_provider ON payment_accounts(provider);


-- 4. TABLE AI_CONTENT_HISTORY
CREATE TABLE IF NOT EXISTS ai_content_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    platform TEXT,
    content_type TEXT,
    product_name TEXT,
    product_description TEXT,
    generated_content TEXT,
    script TEXT,
    hooks TEXT[],
    hashtags TEXT[],
    call_to_action TEXT,
    estimated_engagement DECIMAL(5,2),
    trending_keywords TEXT[],
    best_posting_time TEXT,
    tips TEXT[],
    language TEXT DEFAULT 'fr',
    tone TEXT DEFAULT 'engaging',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_content_user_id ON ai_content_history(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_content_platform ON ai_content_history(platform);
CREATE INDEX IF NOT EXISTS idx_ai_content_created ON ai_content_history(created_at DESC);


-- 5. TABLE SMART_MATCHES
CREATE TABLE IF NOT EXISTS smart_matches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    influencer_id TEXT,
    company_id TEXT,
    compatibility_score DECIMAL(5,2),
    match_reasons TEXT[],
    potential_issues TEXT[],
    predicted_roi DECIMAL(10,2),
    predicted_reach INTEGER,
    predicted_conversions INTEGER,
    recommended_commission DECIMAL(5,2),
    confidence_level TEXT,
    match_data JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days')
);

CREATE INDEX IF NOT EXISTS idx_smart_matches_influencer ON smart_matches(influencer_id);
CREATE INDEX IF NOT EXISTS idx_smart_matches_company ON smart_matches(company_id);
CREATE INDEX IF NOT EXISTS idx_smart_matches_score ON smart_matches(compatibility_score DESC);


-- 6. TABLE ACHIEVEMENTS
CREATE TABLE IF NOT EXISTS achievements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    achievement_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    rarity TEXT DEFAULT 'common',
    progress DECIMAL(5,2) DEFAULT 0,
    unlocked BOOLEAN DEFAULT FALSE,
    unlocked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX IF NOT EXISTS idx_achievements_user_id ON achievements(user_id);


-- 7. TABLE USER_LEVELS
CREATE TABLE IF NOT EXISTS user_levels (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    current_level INTEGER DEFAULT 1,
    total_xp INTEGER DEFAULT 0,
    xp_for_next_level INTEGER DEFAULT 1000,
    last_level_up TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_levels_user_id ON user_levels(user_id);
CREATE INDEX IF NOT EXISTS idx_user_levels_level ON user_levels(current_level DESC);
CREATE INDEX IF NOT EXISTS idx_user_levels_xp ON user_levels(total_xp DESC);


-- 8. TABLE NOTIFICATION_SUBSCRIPTIONS
CREATE TABLE IF NOT EXISTS notification_subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    keys JSONB NOT NULL,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ,
    UNIQUE(endpoint)
);

CREATE INDEX IF NOT EXISTS idx_notification_subs_user_id ON notification_subscriptions(user_id);


-- ============================================
-- FONCTIONS UTILITAIRES
-- ============================================

-- Fonction pour ajouter de l'XP
CREATE OR REPLACE FUNCTION add_xp_simple(p_user_id TEXT, p_xp_amount INTEGER)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_xp INTEGER;
    v_current_level INTEGER;
    v_xp_needed INTEGER;
BEGIN
    -- Créer l'entrée si elle n'existe pas
    INSERT INTO user_levels (user_id, total_xp, current_level, xp_for_next_level)
    VALUES (p_user_id, 0, 1, 1000)
    ON CONFLICT (user_id) DO NOTHING;

    -- Récupérer les valeurs
    SELECT total_xp, current_level, xp_for_next_level
    INTO v_current_xp, v_current_level, v_xp_needed
    FROM user_levels
    WHERE user_id = p_user_id;

    -- Ajouter l'XP
    v_current_xp := v_current_xp + p_xp_amount;

    -- Level up
    WHILE v_current_xp >= v_xp_needed LOOP
        v_current_xp := v_current_xp - v_xp_needed;
        v_current_level := v_current_level + 1;
        v_xp_needed := FLOOR(1000 * POWER(1.5, v_current_level - 1));
    END LOOP;

    -- Sauvegarder
    UPDATE user_levels
    SET total_xp = v_current_xp,
        current_level = v_current_level,
        xp_for_next_level = v_xp_needed,
        updated_at = NOW()
    WHERE user_id = p_user_id;
END;
$$;


-- ============================================
-- MESSAGE DE SUCCÈS
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ MIGRATION RÉUSSIE !';
    RAISE NOTICE '========================================';
    RAISE NOTICE '📊 8 tables créées:';
    RAISE NOTICE '   ✅ trust_scores';
    RAISE NOTICE '   ✅ payouts';
    RAISE NOTICE '   ✅ payment_accounts';
    RAISE NOTICE '   ✅ ai_content_history';
    RAISE NOTICE '   ✅ smart_matches';
    RAISE NOTICE '   ✅ achievements';
    RAISE NOTICE '   ✅ user_levels';
    RAISE NOTICE '   ✅ notification_subscriptions';
    RAISE NOTICE '';
    RAISE NOTICE '⚙️  1 fonction créée:';
    RAISE NOTICE '   ✅ add_xp_simple(user_id, xp_amount)';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Vérifiez dans Table Editor !';
    RAISE NOTICE '========================================';
END $$;
```

</details>

---

### 3️⃣ Exécuter le SQL

1. **Colle** tout le SQL dans l'éditeur Supabase
2. Clique sur **RUN** (en bas à droite)
3. Attends 5-10 secondes

---

### 4️⃣ Vérifier le Succès

Tu devrais voir ce message en **vert** :

```
✅ MIGRATION RÉUSSIE !

📊 8 tables créées:
   ✅ trust_scores
   ✅ payouts
   ✅ payment_accounts
   ✅ ai_content_history
   ✅ smart_matches
   ✅ achievements
   ✅ user_levels
   ✅ notification_subscriptions

⚙️  1 fonction créée:
   ✅ add_xp_simple(user_id, xp_amount)

🎯 Vérifiez dans Table Editor !
```

---

### 5️⃣ Vérifier les Tables

Va dans **Table Editor** (menu de gauche) et vérifie que tu vois :

- ✅ `trust_scores`
- ✅ `payouts`
- ✅ `payment_accounts`
- ✅ `ai_content_history`
- ✅ `smart_matches`
- ✅ `achievements`
- ✅ `user_levels`
- ✅ `notification_subscriptions`

---

## 🧪 Tester les Tables (Optionnel)

### Test 1 : Insérer un Trust Score

```sql
INSERT INTO trust_scores (user_id, username, trust_score, trust_level)
VALUES ('test_user_1', 'Test User', 75.5, 'trusted');

SELECT * FROM trust_scores WHERE user_id = 'test_user_1';
```

### Test 2 : Ajouter de l'XP

```sql
-- Créer un utilisateur niveau 1
INSERT INTO user_levels (user_id, current_level, total_xp)
VALUES ('test_user_1', 1, 0);

-- Ajouter 500 XP
SELECT add_xp_simple('test_user_1', 500);

-- Vérifier
SELECT * FROM user_levels WHERE user_id = 'test_user_1';
```

### Test 3 : Historique AI Content

```sql
INSERT INTO ai_content_history (
    user_id,
    platform,
    content_type,
    product_name,
    generated_content
)
VALUES (
    'test_user_1',
    'instagram',
    'post',
    'Produit Test',
    'Découvrez ce produit incroyable ! 🔥 #test #morocco'
);

SELECT * FROM ai_content_history WHERE user_id = 'test_user_1';
```

---

## ✅ C'est Fait !

Une fois le SQL exécuté avec succès, **TOUTES les 6 nouvelles features sont prêtes** :

| Feature | Backend | Base de Données | Status |
|---------|---------|-----------------|--------|
| 🤖 **AI Content Generator** | ✅ | ✅ | PRÊT |
| 💰 **Mobile Payments** | ✅ | ✅ | PRÊT |
| 🎯 **Smart Match** | ✅ | ✅ | PRÊT |
| 🛡️ **Trust Score** | ✅ | ✅ | PRÊT |
| 🏆 **Gamification** | ✅ | ✅ | PRÊT |
| 📱 **PWA Notifications** | ✅ | ✅ | PRÊT |

---

## 🚀 Prochaines Étapes

1. **Redémarrer le backend** :
   ```bash
   cd /home/user/Getyourshare1/backend
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Tester les endpoints dans Swagger** :
   - Ouvre http://localhost:8000/docs
   - Tu verras 5 nouvelles sections :
     - 🤖 AI Content Generator
     - 💰 Mobile Payments
     - 🎯 Smart Match
     - 🛡️ Trust Score
     - 📊 Predictive Dashboard

3. **Créer les composants frontend** (optionnel) :
   - AI Content Generator UI
   - Mobile Payment Interface
   - Trust Score Display
   - Smart Match Dashboard

---

## 🔥 Si Tu Vois des Erreurs

### Erreur : "relation already exists"
→ **C'est normal** ! La table existe déjà. Continue, les autres seront créées.

### Erreur : "permission denied"
→ Vérifie que tu es bien **admin** du projet Supabase.

### Erreur : "column does not exist"
→ Utilise le fichier **FIXED** : `database/migrations/create_new_features_tables_FIXED.sql`

### Autre erreur
→ Copie l'erreur complète et cherche dans `database/INSTALLATION_RAPIDE.md`

---

## 📞 Support

Si tu rencontres un problème, vérifie ces fichiers :
- 📖 `/home/user/Getyourshare1/database/GUIDE_MIGRATION.md`
- 📖 `/home/user/Getyourshare1/database/INSTALLATION_RAPIDE.md`
- 📖 `/home/user/Getyourshare1/NOUVELLES_FEATURES.md`

---

**Fait avec ❤️ par Claude Code**
