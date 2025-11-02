-- ============================================
-- TABLE SUBSCRIPTIONS
-- Historique et gestion des abonnements actifs
-- ============================================

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    
    -- Statut de l'abonnement
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'trialing', 'past_due', 'canceled', 'expired')),
    
    -- Périodes
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    
    -- Annulation
    cancel_at TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    -- Intégration paiement
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    payment_method VARCHAR(50) DEFAULT 'cmi',
    
    -- Utilisation actuelle
    current_team_members INTEGER DEFAULT 0,
    current_domains INTEGER DEFAULT 0,
    current_products INTEGER DEFAULT 0,
    current_campaigns INTEGER DEFAULT 0,
    current_affiliates INTEGER DEFAULT 0,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(user_id, status) WHERE status IN ('active', 'trialing');

-- Fonction updated_at
CREATE OR REPLACE FUNCTION update_subscriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
DROP TRIGGER IF EXISTS subscriptions_updated_at ON subscriptions;
CREATE TRIGGER subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_subscriptions_updated_at();

-- ============================================
-- VUE: Abonnements actifs avec détails du plan
-- ============================================

CREATE OR REPLACE VIEW v_active_subscriptions AS
SELECT 
    s.id as subscription_id,
    s.user_id,
    s.status,
    s.current_period_start,
    s.current_period_end,
    s.trial_end,
    s.cancel_at,
    
    -- Info du plan
    sp.id as plan_id,
    sp.name as plan_name,
    sp.code as plan_code,
    sp.type as plan_type,
    sp.price_mad as plan_price,
    sp.commission_rate,
    sp.platform_fee_rate,
    
    -- Limites du plan
    sp.max_products as plan_max_products,
    sp.max_campaigns as plan_max_campaigns,
    sp.max_affiliates as plan_max_affiliates,
    sp.max_team_members as plan_max_team_members,
    sp.max_domains as plan_max_domains,
    
    -- Utilisation actuelle
    s.current_products,
    s.current_campaigns,
    s.current_affiliates,
    s.current_team_members,
    s.current_domains,
    
    -- Features
    sp.features as plan_features,
    
    -- Peut ajouter ?
    CASE WHEN sp.max_products IS NULL THEN TRUE
         WHEN s.current_products < sp.max_products THEN TRUE
         ELSE FALSE
    END as can_add_product,
    
    CASE WHEN sp.max_campaigns IS NULL THEN TRUE
         WHEN s.current_campaigns < sp.max_campaigns THEN TRUE
         ELSE FALSE
    END as can_add_campaign,
    
    CASE WHEN sp.max_affiliates IS NULL THEN TRUE
         WHEN s.current_affiliates < sp.max_affiliates THEN TRUE
         ELSE FALSE
    END as can_add_affiliate,
    
    CASE WHEN sp.max_team_members IS NULL THEN TRUE
         WHEN s.current_team_members < sp.max_team_members THEN TRUE
         ELSE FALSE
    END as can_add_team_member,
    
    CASE WHEN sp.max_domains IS NULL THEN TRUE
         WHEN s.current_domains < sp.max_domains THEN TRUE
         ELSE FALSE
    END as can_add_domain
    
FROM subscriptions s
JOIN subscription_plans sp ON s.plan_id = sp.id
WHERE s.status IN ('active', 'trialing');

-- ============================================
-- FONCTION: Vérifier les limites
-- ============================================

CREATE OR REPLACE FUNCTION check_subscription_limit(
    p_user_id UUID,
    p_limit_type VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    v_sub RECORD;
BEGIN
    -- Récupérer l'abonnement actif
    SELECT * INTO v_sub
    FROM v_active_subscriptions
    WHERE user_id = p_user_id
    LIMIT 1;
    
    -- Si pas d'abonnement, refuser
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Vérifier selon le type
    CASE p_limit_type
        WHEN 'products' THEN
            RETURN v_sub.can_add_product;
        WHEN 'campaigns' THEN
            RETURN v_sub.can_add_campaign;
        WHEN 'affiliates' THEN
            RETURN v_sub.can_add_affiliate;
        WHEN 'team_members' THEN
            RETURN v_sub.can_add_team_member;
        WHEN 'domains' THEN
            RETURN v_sub.can_add_domain;
        ELSE
            RETURN FALSE;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Incrémenter l'utilisation
-- ============================================

CREATE OR REPLACE FUNCTION increment_subscription_usage(
    p_user_id UUID,
    p_usage_type VARCHAR,
    p_amount INTEGER DEFAULT 1
)
RETURNS BOOLEAN AS $$
DECLARE
    v_subscription_id UUID;
BEGIN
    -- Trouver l'abonnement actif
    SELECT id INTO v_subscription_id
    FROM subscriptions
    WHERE user_id = p_user_id 
    AND status IN ('active', 'trialing')
    LIMIT 1;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Incrémenter selon le type
    CASE p_usage_type
        WHEN 'products' THEN
            UPDATE subscriptions 
            SET current_products = current_products + p_amount
            WHERE id = v_subscription_id;
        WHEN 'campaigns' THEN
            UPDATE subscriptions 
            SET current_campaigns = current_campaigns + p_amount
            WHERE id = v_subscription_id;
        WHEN 'affiliates' THEN
            UPDATE subscriptions 
            SET current_affiliates = current_affiliates + p_amount
            WHERE id = v_subscription_id;
        WHEN 'team_members' THEN
            UPDATE subscriptions 
            SET current_team_members = current_team_members + p_amount
            WHERE id = v_subscription_id;
        WHEN 'domains' THEN
            UPDATE subscriptions 
            SET current_domains = current_domains + p_amount
            WHERE id = v_subscription_id;
        ELSE
            RETURN FALSE;
    END CASE;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Décrémenter l'utilisation
-- ============================================

CREATE OR REPLACE FUNCTION decrement_subscription_usage(
    p_user_id UUID,
    p_usage_type VARCHAR,
    p_amount INTEGER DEFAULT 1
)
RETURNS BOOLEAN AS $$
DECLARE
    v_subscription_id UUID;
BEGIN
    SELECT id INTO v_subscription_id
    FROM subscriptions
    WHERE user_id = p_user_id 
    AND status IN ('active', 'trialing')
    LIMIT 1;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    CASE p_usage_type
        WHEN 'products' THEN
            UPDATE subscriptions 
            SET current_products = GREATEST(0, current_products - p_amount)
            WHERE id = v_subscription_id;
        WHEN 'campaigns' THEN
            UPDATE subscriptions 
            SET current_campaigns = GREATEST(0, current_campaigns - p_amount)
            WHERE id = v_subscription_id;
        WHEN 'affiliates' THEN
            UPDATE subscriptions 
            SET current_affiliates = GREATEST(0, current_affiliates - p_amount)
            WHERE id = v_subscription_id;
        WHEN 'team_members' THEN
            UPDATE subscriptions 
            SET current_team_members = GREATEST(0, current_team_members - p_amount)
            WHERE id = v_subscription_id;
        WHEN 'domains' THEN
            UPDATE subscriptions 
            SET current_domains = GREATEST(0, current_domains - p_amount)
            WHERE id = v_subscription_id;
        ELSE
            RETURN FALSE;
    END CASE;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VÉRIFICATION
-- ============================================

SELECT '✅ Table subscriptions créée' as status;
SELECT '✅ Vue v_active_subscriptions créée' as status;
SELECT '✅ Fonctions de gestion créées' as status;
