-- ============================================
-- Migration automatique pour les nouvelles features ShareYourSales
-- Date: 2025-10-26
-- Features: AI Content, Mobile Payments, Smart Match, Trust Score, Dashboard
-- ============================================

-- IMPORTANT: Exécutez ce fichier dans Supabase SQL Editor
-- https://app.supabase.com → SQL Editor → New Query

-- ============================================
-- PARTIE 1: NOUVELLES TABLES
-- ============================================

-- 1. TABLE TRUST_SCORES (Trust Score Anti-Fraude)
CREATE TABLE IF NOT EXISTS trust_scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
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

-- Indexes pour performance
CREATE INDEX IF NOT EXISTS idx_trust_scores_user_id ON trust_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_trust_scores_score ON trust_scores(trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_trust_scores_level ON trust_scores(trust_level);

-- Commentaires
COMMENT ON TABLE trust_scores IS 'Trust Score anti-fraude pour chaque utilisateur';
COMMENT ON COLUMN trust_scores.trust_score IS 'Score de confiance 0-100';
COMMENT ON COLUMN trust_scores.trust_level IS 'Niveau: verified_pro, trusted, reliable, average, unverified, suspicious';


-- 2. TABLE PAYOUTS (Paiements Mobiles Instantanés)
CREATE TABLE IF NOT EXISTS payouts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_payouts_user_id ON payouts(user_id);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
CREATE INDEX IF NOT EXISTS idx_payouts_payout_id ON payouts(payout_id);
CREATE INDEX IF NOT EXISTS idx_payouts_created ON payouts(created_at DESC);

-- Commentaires
COMMENT ON TABLE payouts IS 'Historique des paiements mobiles (CashPlus, Orange Money, etc.)';
COMMENT ON COLUMN payouts.provider IS 'cashplus, orange_money, mt_cash, wafacash, payzone';
COMMENT ON COLUMN payouts.status IS 'pending, processing, completed, failed, refunded';


-- 3. TABLE PAYMENT_ACCOUNTS (Comptes de Paiement Mobile)
CREATE TABLE IF NOT EXISTS payment_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    provider TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    account_name TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, provider, phone_number)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_payment_accounts_user_id ON payment_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_accounts_provider ON payment_accounts(provider);
CREATE INDEX IF NOT EXISTS idx_payment_accounts_default ON payment_accounts(user_id, is_default) WHERE is_default = TRUE;

-- Commentaires
COMMENT ON TABLE payment_accounts IS 'Comptes de paiement mobile enregistrés par les utilisateurs';


-- 4. TABLE AI_CONTENT_HISTORY (Historique Génération Contenu IA)
CREATE TABLE IF NOT EXISTS ai_content_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_content_user_id ON ai_content_history(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_content_platform ON ai_content_history(platform);
CREATE INDEX IF NOT EXISTS idx_ai_content_created ON ai_content_history(created_at DESC);

-- Commentaires
COMMENT ON TABLE ai_content_history IS 'Historique des contenus générés par IA';
COMMENT ON COLUMN ai_content_history.platform IS 'tiktok, instagram, youtube_shorts, facebook, twitter';


-- 5. TABLE SMART_MATCHES (Cache Résultats Matching IA)
CREATE TABLE IF NOT EXISTS smart_matches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    influencer_id UUID,
    company_id UUID,
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_smart_matches_influencer ON smart_matches(influencer_id);
CREATE INDEX IF NOT EXISTS idx_smart_matches_company ON smart_matches(company_id);
CREATE INDEX IF NOT EXISTS idx_smart_matches_score ON smart_matches(compatibility_score DESC);
CREATE INDEX IF NOT EXISTS idx_smart_matches_active ON smart_matches(is_active) WHERE is_active = TRUE;

-- Commentaires
COMMENT ON TABLE smart_matches IS 'Cache des résultats de matching IA influenceurs-marques';


-- 6. TABLE ACHIEVEMENTS (Gamification - Achievements)
CREATE TABLE IF NOT EXISTS achievements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_achievements_user_id ON achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_achievements_unlocked ON achievements(user_id, unlocked) WHERE unlocked = TRUE;

-- Commentaires
COMMENT ON TABLE achievements IS 'Achievements et badges gamification';
COMMENT ON COLUMN achievements.rarity IS 'common, rare, epic, legendary';


-- 7. TABLE USER_LEVELS (Gamification - Niveaux et XP)
CREATE TABLE IF NOT EXISTS user_levels (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    current_level INTEGER DEFAULT 1,
    total_xp INTEGER DEFAULT 0,
    xp_for_next_level INTEGER DEFAULT 1000,
    last_level_up TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_levels_user_id ON user_levels(user_id);
CREATE INDEX IF NOT EXISTS idx_user_levels_level ON user_levels(current_level DESC);
CREATE INDEX IF NOT EXISTS idx_user_levels_xp ON user_levels(total_xp DESC);

-- Commentaires
COMMENT ON TABLE user_levels IS 'Système de niveaux et XP pour gamification';


-- 8. TABLE NOTIFICATION_SUBSCRIPTIONS (PWA Push Notifications)
CREATE TABLE IF NOT EXISTS notification_subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    endpoint TEXT NOT NULL,
    keys JSONB NOT NULL,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ,
    UNIQUE(endpoint)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_notification_subs_user_id ON notification_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_subs_active ON notification_subscriptions(is_active) WHERE is_active = TRUE;

-- Commentaires
COMMENT ON TABLE notification_subscriptions IS 'Subscriptions Push Notifications pour PWA';


-- ============================================
-- PARTIE 2: COLONNES MANQUANTES AUX TABLES EXISTANTES
-- ============================================

-- Ajouter colonnes à la table users (si elle existe)
ALTER TABLE users ADD COLUMN IF NOT EXISTS avg_response_time_hours DECIMAL(10,2) DEFAULT 24;
ALTER TABLE users ADD COLUMN IF NOT EXISTS balance DECIMAL(10,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS kyc_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan TEXT DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active';

-- Ajouter colonnes à la table campaigns (si elle existe)
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS clicks INTEGER DEFAULT 0;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS conversions INTEGER DEFAULT 0;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS revenue DECIMAL(10,2) DEFAULT 0;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS content_quality_rating DECIMAL(3,1);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS merchant_rating DECIMAL(3,1);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS bounce_rate DECIMAL(5,2);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS avg_session_duration INTEGER;

-- Créer des indexes sur les nouvelles colonnes
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_plan);
CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance);
CREATE INDEX IF NOT EXISTS idx_campaigns_revenue ON campaigns(revenue DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_conversions ON campaigns(conversions DESC);


-- ============================================
-- PARTIE 3: DONNÉES INITIALES (SEED)
-- ============================================

-- Initialiser les niveaux pour tous les utilisateurs existants
INSERT INTO user_levels (user_id, current_level, total_xp)
SELECT id, 1, 0
FROM users
ON CONFLICT (user_id) DO NOTHING;

-- Initialiser les trust scores pour tous les utilisateurs
INSERT INTO trust_scores (user_id, username, trust_score, trust_level)
SELECT id, email, 50.00, 'average'
FROM users
ON CONFLICT (user_id) DO NOTHING;


-- ============================================
-- PARTIE 4: POLITIQUES RLS (Row Level Security)
-- ============================================

-- Activer RLS sur toutes les nouvelles tables
ALTER TABLE trust_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE payouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_content_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE smart_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_subscriptions ENABLE ROW LEVEL SECURITY;

-- Politiques pour trust_scores (visible par tous, modifiable par le propriétaire)
CREATE POLICY "Trust scores are viewable by everyone"
    ON trust_scores FOR SELECT
    USING (true);

CREATE POLICY "Users can update their own trust score"
    ON trust_scores FOR UPDATE
    USING (auth.uid() = user_id);

-- Politiques pour payouts (uniquement le propriétaire)
CREATE POLICY "Users can view their own payouts"
    ON payouts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own payouts"
    ON payouts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Politiques pour payment_accounts
CREATE POLICY "Users can view their own payment accounts"
    ON payment_accounts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own payment accounts"
    ON payment_accounts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own payment accounts"
    ON payment_accounts FOR UPDATE
    USING (auth.uid() = user_id);

-- Politiques pour ai_content_history
CREATE POLICY "Users can view their own AI content history"
    ON ai_content_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own AI content"
    ON ai_content_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Politiques pour smart_matches (visible par tous les actifs)
CREATE POLICY "Active smart matches are viewable by everyone"
    ON smart_matches FOR SELECT
    USING (is_active = true);

-- Politiques pour achievements
CREATE POLICY "Users can view their own achievements"
    ON achievements FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own achievements"
    ON achievements FOR UPDATE
    USING (auth.uid() = user_id);

-- Politiques pour user_levels
CREATE POLICY "Users can view their own level"
    ON user_levels FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own level"
    ON user_levels FOR UPDATE
    USING (auth.uid() = user_id);

-- Politiques pour notification_subscriptions
CREATE POLICY "Users can manage their own subscriptions"
    ON notification_subscriptions FOR ALL
    USING (auth.uid() = user_id);


-- ============================================
-- PARTIE 5: FONCTIONS UTILITAIRES
-- ============================================

-- Fonction pour calculer automatiquement le Trust Score
CREATE OR REPLACE FUNCTION calculate_trust_score(p_user_id UUID)
RETURNS DECIMAL(5,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_score DECIMAL(5,2);
BEGIN
    -- Logique simple de calcul (à améliorer avec les vraies données)
    SELECT COALESCE(
        (
            -- Base score de 50
            50.00 +
            -- +10 pour chaque 10 campagnes complétées
            (COUNT(*) FILTER (WHERE status = 'completed') * 1.0) +
            -- +5 pour KYC vérifié
            (CASE WHEN (SELECT kyc_verified FROM users WHERE id = p_user_id) THEN 5 ELSE 0 END)
        ),
        50.00
    )
    INTO v_score
    FROM campaigns
    WHERE user_id = p_user_id;

    -- Cap à 100
    RETURN LEAST(v_score, 100.00);
END;
$$;

-- Fonction pour ajouter de l'XP et level up automatique
CREATE OR REPLACE FUNCTION add_xp(p_user_id UUID, p_xp_amount INTEGER)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_xp INTEGER;
    v_current_level INTEGER;
    v_xp_needed INTEGER;
BEGIN
    -- Récupérer les infos actuelles
    SELECT total_xp, current_level, xp_for_next_level
    INTO v_current_xp, v_current_level, v_xp_needed
    FROM user_levels
    WHERE user_id = p_user_id;

    -- Ajouter l'XP
    v_current_xp := v_current_xp + p_xp_amount;

    -- Vérifier si level up
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

-- Trigger pour ajouter automatiquement de l'XP quand une campagne est complétée
CREATE OR REPLACE FUNCTION trigger_add_xp_on_campaign_complete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        PERFORM add_xp(NEW.user_id, 100); -- 100 XP par campagne complétée
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER campaign_completed_xp
    AFTER UPDATE ON campaigns
    FOR EACH ROW
    WHEN (NEW.status = 'completed' AND OLD.status IS DISTINCT FROM 'completed')
    EXECUTE FUNCTION trigger_add_xp_on_campaign_complete();


-- ============================================
-- FIN DE LA MIGRATION
-- ============================================

-- Afficher un message de succès
DO $$
BEGIN
    RAISE NOTICE '✅ Migration terminée avec succès !';
    RAISE NOTICE '📊 Tables créées: trust_scores, payouts, payment_accounts, ai_content_history, smart_matches, achievements, user_levels, notification_subscriptions';
    RAISE NOTICE '🔐 Politiques RLS activées pour toutes les tables';
    RAISE NOTICE '⚙️  Fonctions utilitaires créées: calculate_trust_score(), add_xp()';
    RAISE NOTICE '🎯 Prochaine étape: Redémarrez votre backend et testez les nouvelles features !';
END $$;
