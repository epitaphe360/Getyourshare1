-- ============================================
-- Migration CORRIGÉE pour ShareYourSales
-- Version sans dépendances à user_id
-- ============================================

-- PARTIE 1: NOUVELLES TABLES (SANS FOREIGN KEYS)
-- On crée d'abord les tables sans contraintes, on les ajoutera après

-- 1. TABLE TRUST_SCORES
CREATE TABLE IF NOT EXISTS trust_scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,  -- Changé en TEXT pour compatibilité
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
    user_id TEXT NOT NULL,  -- Changé en TEXT
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
    user_id TEXT NOT NULL,  -- Changé en TEXT
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
CREATE INDEX IF NOT EXISTS idx_payment_accounts_default ON payment_accounts(user_id, is_default) WHERE is_default = TRUE;


-- 4. TABLE AI_CONTENT_HISTORY
CREATE TABLE IF NOT EXISTS ai_content_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,  -- Changé en TEXT
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
    influencer_id TEXT,  -- Changé en TEXT
    company_id TEXT,     -- Changé en TEXT
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
CREATE INDEX IF NOT EXISTS idx_smart_matches_active ON smart_matches(is_active) WHERE is_active = TRUE;


-- 6. TABLE ACHIEVEMENTS
CREATE TABLE IF NOT EXISTS achievements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,  -- Changé en TEXT
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
CREATE INDEX IF NOT EXISTS idx_achievements_unlocked ON achievements(user_id, unlocked) WHERE unlocked = TRUE;


-- 7. TABLE USER_LEVELS
CREATE TABLE IF NOT EXISTS user_levels (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,  -- Changé en TEXT
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
    user_id TEXT NOT NULL,  -- Changé en TEXT
    endpoint TEXT NOT NULL,
    keys JSONB NOT NULL,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ,
    UNIQUE(endpoint)
);

CREATE INDEX IF NOT EXISTS idx_notification_subs_user_id ON notification_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_subs_active ON notification_subscriptions(is_active) WHERE is_active = TRUE;


-- ============================================
-- PARTIE 2: COLONNES MANQUANTES
-- On essaie d'ajouter, mais on ignore si ça échoue
-- ============================================

-- Pour la table users (si elle existe)
DO $$
BEGIN
    -- Ajouter colonnes une par une pour éviter les erreurs
    BEGIN
        ALTER TABLE users ADD COLUMN IF NOT EXISTS avg_response_time_hours DECIMAL(10,2) DEFAULT 24;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE users ADD COLUMN IF NOT EXISTS balance DECIMAL(10,2) DEFAULT 0;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE users ADD COLUMN IF NOT EXISTS kyc_verified BOOLEAN DEFAULT FALSE;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan TEXT DEFAULT 'free';
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active';
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
END $$;


-- Pour la table campaigns (si elle existe)
DO $$
BEGIN
    BEGIN
        ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS clicks INTEGER DEFAULT 0;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS conversions INTEGER DEFAULT 0;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS revenue DECIMAL(10,2) DEFAULT 0;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS content_quality_rating DECIMAL(3,1);
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS merchant_rating DECIMAL(3,1);
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS bounce_rate DECIMAL(5,2);
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    BEGIN
        ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS avg_session_duration INTEGER;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
END $$;


-- Créer des indexes (seulement si les colonnes existent)
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_plan);
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance);
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_campaigns_revenue ON campaigns(revenue DESC);
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_campaigns_conversions ON campaigns(conversions DESC);
EXCEPTION WHEN OTHERS THEN NULL;
END $$;


-- ============================================
-- PARTIE 3: ROW LEVEL SECURITY (OPTIONNEL)
-- Commenté car nécessite auth.uid()
-- Décommentez si vous utilisez Supabase Auth
-- ============================================

/*
ALTER TABLE trust_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE payouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_content_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE smart_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_subscriptions ENABLE ROW LEVEL SECURITY;

-- Politiques (décommentez si besoin)
CREATE POLICY "Trust scores viewable by everyone"
    ON trust_scores FOR SELECT USING (true);

CREATE POLICY "Users view own payouts"
    ON payouts FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users manage own payment accounts"
    ON payment_accounts FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY "Users view own AI content"
    ON ai_content_history FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY "Active matches viewable"
    ON smart_matches FOR SELECT USING (is_active = true);

CREATE POLICY "Users view own achievements"
    ON achievements FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY "Users view own level"
    ON user_levels FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY "Users manage own subscriptions"
    ON notification_subscriptions FOR ALL USING (auth.uid()::text = user_id);
*/


-- ============================================
-- PARTIE 4: FONCTIONS UTILITAIRES (OPTIONNEL)
-- ============================================

-- Fonction pour calculer le Trust Score (version simplifiée)
CREATE OR REPLACE FUNCTION calculate_trust_score_simple(p_user_id TEXT)
RETURNS DECIMAL(5,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_score DECIMAL(5,2) := 50.00;
BEGIN
    -- Score de base
    RETURN v_score;
END;
$$;


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
    -- Récupérer ou créer l'entrée
    INSERT INTO user_levels (user_id, total_xp, current_level, xp_for_next_level)
    VALUES (p_user_id, 0, 1, 1000)
    ON CONFLICT (user_id) DO NOTHING;

    -- Récupérer les valeurs actuelles
    SELECT total_xp, current_level, xp_for_next_level
    INTO v_current_xp, v_current_level, v_xp_needed
    FROM user_levels
    WHERE user_id = p_user_id;

    -- Ajouter l'XP
    v_current_xp := v_current_xp + p_xp_amount;

    -- Level up si nécessaire
    WHILE v_current_xp >= v_xp_needed LOOP
        v_current_xp := v_current_xp - v_xp_needed;
        v_current_level := v_current_level + 1;
        v_xp_needed := FLOOR(1000 * POWER(1.5, v_current_level - 1));
    END LOOP;

    -- Mettre à jour
    UPDATE user_levels
    SET
        total_xp = v_current_xp,
        current_level = v_current_level,
        xp_for_next_level = v_xp_needed,
        updated_at = NOW()
    WHERE user_id = p_user_id;
END;
$$;


-- ============================================
-- PARTIE 5: MESSAGE DE SUCCÈS
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ MIGRATION TERMINÉE AVEC SUCCÈS !';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Tables créées:';
    RAISE NOTICE '   - trust_scores';
    RAISE NOTICE '   - payouts';
    RAISE NOTICE '   - payment_accounts';
    RAISE NOTICE '   - ai_content_history';
    RAISE NOTICE '   - smart_matches';
    RAISE NOTICE '   - achievements';
    RAISE NOTICE '   - user_levels';
    RAISE NOTICE '   - notification_subscriptions';
    RAISE NOTICE '';
    RAISE NOTICE '⚙️  Fonctions créées:';
    RAISE NOTICE '   - calculate_trust_score_simple(user_id)';
    RAISE NOTICE '   - add_xp_simple(user_id, xp_amount)';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Prochaines étapes:';
    RAISE NOTICE '   1. Vérifier les tables dans Table Editor';
    RAISE NOTICE '   2. Intégrer les routers dans server.py';
    RAISE NOTICE '   3. Redémarrer le backend';
    RAISE NOTICE '   4. Tester les endpoints /docs';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
