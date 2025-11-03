-- ============================================
-- MIGRATION 003: SYSTÈME D'ABONNEMENTS COMPLET
-- Date: 2024-11-03
-- Description: Tables pour gérer les abonnements utilisateurs avec Stripe
-- ============================================

-- Vérifier que la table users existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'users') THEN
        RAISE EXCEPTION 'La table users n''existe pas. Veuillez la créer d''abord.';
    END IF;
END $$;

-- ============================================
-- 1. TABLE: subscription_plans
-- Plans d'abonnement disponibles (Freemium, Standard, Premium, Enterprise)
-- ============================================
DROP TABLE IF EXISTS subscription_usage CASCADE;
DROP TABLE IF EXISTS subscription_history CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS subscription_plans CASCADE;

CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    user_type TEXT NOT NULL CHECK (user_type IN ('merchant', 'influencer', 'commercial')),
    
    -- Prix
    price_monthly DECIMAL(10,2) DEFAULT 0,
    price_yearly DECIMAL(10,2) DEFAULT 0,
    currency TEXT DEFAULT 'EUR',
    
    -- Limites pour marchands
    max_products INTEGER,
    max_campaigns INTEGER,
    max_affiliates INTEGER,
    
    -- Limites pour influenceurs
    commission_rate DECIMAL(5,2), -- Ex: 5.00 pour 5%
    campaigns_per_month INTEGER,
    instant_payout BOOLEAN DEFAULT false,
    analytics_level TEXT CHECK (analytics_level IN ('basic', 'advanced', 'premium')),
    
    -- Fonctionnalités additionnelles
    features JSONB DEFAULT '[]'::jsonb,
    custom_domain BOOLEAN DEFAULT false,
    priority_support BOOLEAN DEFAULT false,
    api_access BOOLEAN DEFAULT false,
    white_label BOOLEAN DEFAULT false,
    
    -- Stripe
    stripe_price_id_monthly TEXT,
    stripe_price_id_yearly TEXT,
    stripe_product_id TEXT,
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour requêtes fréquentes
DROP INDEX IF EXISTS idx_subscription_plans_code;
DROP INDEX IF EXISTS idx_subscription_plans_user_type;
DROP INDEX IF EXISTS idx_subscription_plans_active;

CREATE INDEX idx_subscription_plans_code ON subscription_plans(code);
CREATE INDEX idx_subscription_plans_user_type ON subscription_plans(user_type);
CREATE INDEX idx_subscription_plans_active ON subscription_plans(is_active);

-- ============================================
-- 2. TABLE: subscriptions
-- Abonnements actifs des utilisateurs
-- ============================================
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    
    -- Statut
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('trialing', 'active', 'past_due', 'canceled', 'incomplete', 'incomplete_expired', 'unpaid')),
    
    -- Période
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    
    -- Annulation
    cancel_at_period_end BOOLEAN DEFAULT false,
    canceled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    
    -- Stripe
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT UNIQUE,
    stripe_latest_invoice_id TEXT,
    
    -- Paiement
    billing_cycle TEXT DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'yearly')),
    amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    currency TEXT DEFAULT 'EUR',
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour performances
DROP INDEX IF EXISTS idx_subscriptions_user_id;
DROP INDEX IF EXISTS idx_subscriptions_status;
DROP INDEX IF EXISTS idx_subscriptions_stripe_customer;
DROP INDEX IF EXISTS idx_subscriptions_stripe_subscription;
DROP INDEX IF EXISTS idx_subscriptions_period_end;
DROP INDEX IF EXISTS idx_subscriptions_user_active_unique;

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_stripe_customer ON subscriptions(stripe_customer_id);
CREATE INDEX idx_subscriptions_stripe_subscription ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_subscriptions_period_end ON subscriptions(current_period_end);

-- Index unique partiel: un seul abonnement actif par utilisateur
CREATE UNIQUE INDEX idx_subscriptions_user_active_unique 
    ON subscriptions(user_id) 
    WHERE status IN ('active', 'trialing');

-- ============================================
-- 3. TABLE: subscription_history
-- Historique des changements d'abonnement (audit trail)
-- ============================================
CREATE TABLE subscription_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Action
    action TEXT NOT NULL CHECK (action IN ('created', 'upgraded', 'downgraded', 'canceled', 'reactivated', 'renewed', 'payment_failed', 'trial_started', 'trial_ended')),
    
    -- Détails
    from_plan_id UUID REFERENCES subscription_plans(id),
    to_plan_id UUID REFERENCES subscription_plans(id),
    old_status TEXT,
    new_status TEXT,
    
    -- Montants
    amount DECIMAL(10,2),
    currency TEXT DEFAULT 'EUR',
    
    -- Stripe event
    stripe_event_id TEXT,
    stripe_event_type TEXT,
    
    -- Metadata
    reason TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour historique
DROP INDEX IF EXISTS idx_subscription_history_user_id;
DROP INDEX IF EXISTS idx_subscription_history_subscription_id;
DROP INDEX IF EXISTS idx_subscription_history_action;
DROP INDEX IF EXISTS idx_subscription_history_created_at;

CREATE INDEX idx_subscription_history_user_id ON subscription_history(user_id);
CREATE INDEX idx_subscription_history_subscription_id ON subscription_history(subscription_id);
CREATE INDEX idx_subscription_history_action ON subscription_history(action);
CREATE INDEX idx_subscription_history_created_at ON subscription_history(created_at DESC);

-- ============================================
-- 4. TABLE: subscription_usage
-- Suivi de l'utilisation des limites par abonnement
-- ============================================
CREATE TABLE subscription_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Compteurs actuels
    products_count INTEGER DEFAULT 0,
    campaigns_count INTEGER DEFAULT 0,
    affiliates_count INTEGER DEFAULT 0,
    
    -- Compteurs période
    api_calls_this_month INTEGER DEFAULT 0,
    campaigns_this_month INTEGER DEFAULT 0,
    
    -- Timestamps
    last_reset_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Contrainte: une seule ligne par abonnement
    UNIQUE(subscription_id)
);

-- Index
DROP INDEX IF EXISTS idx_subscription_usage_user_id;
DROP INDEX IF EXISTS idx_subscription_usage_subscription_id;

CREATE INDEX idx_subscription_usage_user_id ON subscription_usage(user_id);
CREATE INDEX idx_subscription_usage_subscription_id ON subscription_usage(subscription_id);

-- ============================================
-- 5. TRIGGERS: Auto-update timestamps
-- ============================================

-- Fonction générique pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour updated_at
DROP TRIGGER IF EXISTS update_subscription_plans_updated_at ON subscription_plans;
CREATE TRIGGER update_subscription_plans_updated_at
    BEFORE UPDATE ON subscription_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_subscription_usage_updated_at ON subscription_usage;
CREATE TRIGGER update_subscription_usage_updated_at
    BEFORE UPDATE ON subscription_usage
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 6. FONCTION: Obtenir l'abonnement actif d'un utilisateur
-- ============================================
CREATE OR REPLACE FUNCTION get_user_active_subscription(p_user_id UUID)
RETURNS TABLE (
    subscription_id UUID,
    plan_code TEXT,
    plan_name TEXT,
    status TEXT,
    max_products INTEGER,
    max_campaigns INTEGER,
    max_affiliates INTEGER,
    commission_rate DECIMAL,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        sp.code,
        sp.name,
        s.status,
        sp.max_products,
        sp.max_campaigns,
        sp.max_affiliates,
        sp.commission_rate,
        s.current_period_end,
        s.cancel_at_period_end
    FROM subscriptions s
    JOIN subscription_plans sp ON s.plan_id = sp.id
    WHERE s.user_id = p_user_id
        AND s.status IN ('active', 'trialing')
    ORDER BY s.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 7. FONCTION: Vérifier si l'utilisateur peut créer une ressource
-- ============================================
CREATE OR REPLACE FUNCTION can_user_create_resource(
    p_user_id UUID,
    p_resource_type TEXT -- 'product', 'campaign', 'affiliate'
)
RETURNS BOOLEAN AS $$
DECLARE
    v_subscription RECORD;
    v_current_count INTEGER;
    v_max_allowed INTEGER;
BEGIN
    -- Récupérer l'abonnement actif
    SELECT * INTO v_subscription FROM get_user_active_subscription(p_user_id);
    
    -- Si pas d'abonnement, retourner false
    IF v_subscription IS NULL THEN
        RETURN false;
    END IF;
    
    -- Récupérer le compteur actuel selon le type de ressource
    IF p_resource_type = 'product' THEN
        SELECT COUNT(*) INTO v_current_count FROM products WHERE merchant_id = p_user_id;
        v_max_allowed := v_subscription.max_products;
    ELSIF p_resource_type = 'campaign' THEN
        SELECT COUNT(*) INTO v_current_count FROM campaigns WHERE merchant_id = p_user_id;
        v_max_allowed := v_subscription.max_campaigns;
    ELSIF p_resource_type = 'affiliate' THEN
        SELECT COUNT(*) INTO v_current_count FROM affiliates WHERE merchant_id = p_user_id;
        v_max_allowed := v_subscription.max_affiliates;
    ELSE
        RETURN false;
    END IF;
    
    -- Vérifier si la limite est atteinte (-1 = illimité)
    IF v_max_allowed = -1 THEN
        RETURN true;
    END IF;
    
    RETURN v_current_count < v_max_allowed;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 8. DONNÉES INITIALES: Plans d'abonnement
-- ============================================

-- Nettoyer les plans existants si relance du script
DELETE FROM subscription_plans WHERE code LIKE 'merchant_%' OR code LIKE 'influencer_%';

-- Plans pour MARCHANDS
INSERT INTO subscription_plans (
    name, code, description, user_type,
    price_monthly, price_yearly,
    max_products, max_campaigns, max_affiliates,
    commission_rate, custom_domain, priority_support, api_access, white_label,
    features, display_order
) VALUES
-- Freemium (Gratuit)
(
    'Freemium', 'merchant_freemium', 
    'Plan gratuit pour débuter',
    'merchant',
    0, 0,
    5, 1, 10,
    0, false, false, false, false,
    '["5 produits", "1 campagne", "10 affiliés", "Support standard", "Analytics basiques"]'::jsonb,
    1
),
-- Standard
(
    'Standard', 'merchant_standard',
    'Pour petites entreprises',
    'merchant',
    49, 490,
    50, 10, 100,
    0, true, true, true, false,
    '["50 produits", "10 campagnes", "100 affiliés", "Domaine personnalisé", "Support prioritaire", "Analytics avancées", "API"]'::jsonb,
    2
),
-- Premium
(
    'Premium', 'merchant_premium',
    'Pour moyennes entreprises',
    'merchant',
    99, 990,
    200, -1, 500,
    0, true, true, true, true,
    '["200 produits", "Campagnes illimitées", "500 affiliés", "Multi-domaines", "Support 24/7", "Analytics premium + IA", "API illimitée", "White label"]'::jsonb,
    3
),
-- Enterprise
(
    'Enterprise', 'merchant_enterprise',
    'Pour grandes entreprises',
    'merchant',
    299, 2990,
    -1, -1, -1,
    0, true, true, true, true,
    '["Produits illimités", "Campagnes illimitées", "Affiliés illimités", "Infrastructure dédiée", "Account manager", "Analytics enterprise + IA", "Contrat SLA", "Développement sur-mesure"]'::jsonb,
    4
);

-- Plans pour INFLUENCEURS
INSERT INTO subscription_plans (
    name, code, description, user_type,
    price_monthly, price_yearly,
    commission_rate, campaigns_per_month, instant_payout, analytics_level,
    features, display_order
) VALUES
-- Free
(
    'Free', 'influencer_free',
    'Plan gratuit pour débuter',
    'influencer',
    0, 0,
    5.00, 3, false, 'basic',
    '["Commission 5%", "3 campagnes/mois", "Analytics basiques", "Support communautaire"]'::jsonb,
    1
),
-- Pro
(
    'Pro', 'influencer_pro',
    'Pour influenceurs sérieux',
    'influencer',
    29, 290,
    3.00, 20, true, 'advanced',
    '["Commission 3%", "20 campagnes/mois", "Paiement instantané", "Analytics avancées", "Support prioritaire"]'::jsonb,
    2
),
-- Elite
(
    'Elite', 'influencer_elite',
    'Pour top influenceurs',
    'influencer',
    99, 990,
    2.00, -1, true, 'premium',
    '["Commission 2%", "Campagnes illimitées", "Paiement instantané", "Analytics premium + IA", "Support dédié", "Coaching personnalisé"]'::jsonb,
    3
);

-- ============================================
-- 9. VUES: Analytics abonnements (pour admin)
-- ============================================

DROP VIEW IF EXISTS v_subscription_stats;
CREATE VIEW v_subscription_stats AS
SELECT
    sp.name AS plan_name,
    sp.user_type,
    COUNT(s.id) AS active_subscriptions,
    SUM(s.amount) AS mrr_total,
    AVG(s.amount) AS avg_amount
FROM subscriptions s
JOIN subscription_plans sp ON s.plan_id = sp.id
WHERE s.status IN ('active', 'trialing')
GROUP BY sp.name, sp.user_type;

-- ============================================
-- 10. COMMENTAIRES
-- ============================================
COMMENT ON TABLE subscription_plans IS 'Plans d''abonnement disponibles sur la plateforme';
COMMENT ON TABLE subscriptions IS 'Abonnements actifs et historiques des utilisateurs';
COMMENT ON TABLE subscription_history IS 'Audit trail de tous les changements d''abonnement';
COMMENT ON TABLE subscription_usage IS 'Suivi de l''utilisation des limites par abonnement';

COMMENT ON FUNCTION get_user_active_subscription IS 'Récupère l''abonnement actif d''un utilisateur';
COMMENT ON FUNCTION can_user_create_resource IS 'Vérifie si l''utilisateur peut créer une ressource selon son plan';

-- ============================================
-- FIN DE LA MIGRATION
-- ============================================
