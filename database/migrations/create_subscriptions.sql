-- ============================================
-- MIGRATION: Système d'Abonnement SaaS (Stripe)
-- Description: Tables pour gérer les abonnements Stripe
-- ============================================

-- Table des abonnements utilisateurs
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relation utilisateur
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL UNIQUE,

    -- Stripe IDs
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255) UNIQUE,

    -- Plan et cycle
    plan VARCHAR(50) NOT NULL CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')) DEFAULT 'free',
    billing_cycle VARCHAR(20) CHECK (billing_cycle IN ('monthly', 'yearly')),

    -- Statut
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'trialing', 'past_due', 'canceled', 'unpaid')) DEFAULT 'active',

    -- Périodes
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    trial_start TIMESTAMP,
    trial_end TIMESTAMP,

    -- Annulation
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP,

    -- Prix
    price_amount INTEGER,  -- En centimes (ex: 29900 = 299 MAD)
    currency VARCHAR(3) DEFAULT 'MAD',

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Index
    INDEX idx_user_subscriptions_user (user_id),
    INDEX idx_user_subscriptions_stripe_customer (stripe_customer_id),
    INDEX idx_user_subscriptions_status (status),
    INDEX idx_user_subscriptions_plan (plan)
);

-- Table des factures
CREATE TABLE IF NOT EXISTS subscription_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    subscription_id UUID REFERENCES user_subscriptions(id) ON DELETE CASCADE,

    -- Stripe
    stripe_invoice_id VARCHAR(255) UNIQUE,
    stripe_payment_intent_id VARCHAR(255),

    -- Montants
    amount_due INTEGER NOT NULL,
    amount_paid INTEGER,
    amount_remaining INTEGER,
    currency VARCHAR(3) DEFAULT 'MAD',

    -- Statut
    status VARCHAR(50) CHECK (status IN ('draft', 'open', 'paid', 'uncollectible', 'void')),

    -- Dates
    invoice_date TIMESTAMP,
    due_date TIMESTAMP,
    paid_at TIMESTAMP,

    -- PDF
    invoice_pdf_url TEXT,
    hosted_invoice_url TEXT,

    -- Métadonnées
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_invoices_user (user_id),
    INDEX idx_invoices_subscription (subscription_id),
    INDEX idx_invoices_status (status),
    INDEX idx_invoices_date (invoice_date DESC)
);

-- Table des événements Stripe (webhooks)
CREATE TABLE IF NOT EXISTS stripe_webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Stripe
    stripe_event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,

    -- Données
    payload JSONB NOT NULL,

    -- Traitement
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_webhook_events_type (event_type),
    INDEX idx_webhook_events_processed (processed),
    INDEX idx_webhook_events_created (created_at DESC)
);

-- Table des quotas utilisateur (pour limiter selon le plan)
CREATE TABLE IF NOT EXISTS user_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL UNIQUE,

    -- Compteurs actuels
    products_count INTEGER DEFAULT 0,
    influencers_count INTEGER DEFAULT 0,
    links_count INTEGER DEFAULT 0,

    -- Quotas max (selon le plan)
    max_products INTEGER DEFAULT 5,
    max_influencers INTEGER DEFAULT 3,
    max_links INTEGER DEFAULT 10,

    -- Features
    social_media_sync_enabled BOOLEAN DEFAULT FALSE,
    ai_bot_enabled BOOLEAN DEFAULT FALSE,
    custom_domain_enabled BOOLEAN DEFAULT FALSE,
    api_access_enabled BOOLEAN DEFAULT FALSE,

    -- Frais de commission plateforme (%)
    platform_commission_rate DECIMAL(5,2) DEFAULT 10.0,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_quotas_user (user_id)
);

-- ============================================
-- FONCTIONS AUTOMATIQUES
-- ============================================

-- Fonction: Mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_subscription_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_subscription_updated_at
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_subscription_updated_at();

-- Fonction: Mettre à jour les quotas selon le plan
CREATE OR REPLACE FUNCTION update_user_quotas_on_plan_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Mettre à jour les quotas selon le nouveau plan
    UPDATE user_quotas
    SET
        max_products = CASE NEW.plan
            WHEN 'free' THEN 5
            WHEN 'starter' THEN 50
            WHEN 'pro' THEN 200
            WHEN 'enterprise' THEN -1  -- Illimité
        END,
        max_influencers = CASE NEW.plan
            WHEN 'free' THEN 3
            WHEN 'starter' THEN 20
            WHEN 'pro' THEN 100
            WHEN 'enterprise' THEN -1
        END,
        max_links = CASE NEW.plan
            WHEN 'free' THEN 10
            WHEN 'starter' THEN 100
            WHEN 'pro' THEN 500
            WHEN 'enterprise' THEN -1
        END,
        platform_commission_rate = CASE NEW.plan
            WHEN 'free' THEN 10.0
            WHEN 'starter' THEN 5.0
            WHEN 'pro' THEN 3.0
            WHEN 'enterprise' THEN 2.0
        END,
        social_media_sync_enabled = CASE NEW.plan
            WHEN 'free' THEN FALSE
            ELSE TRUE
        END,
        ai_bot_enabled = CASE NEW.plan
            WHEN 'free' THEN FALSE
            ELSE TRUE
        END,
        custom_domain_enabled = CASE NEW.plan
            WHEN 'free' THEN FALSE
            WHEN 'starter' THEN FALSE
            ELSE TRUE
        END,
        api_access_enabled = CASE NEW.plan
            WHEN 'free' THEN FALSE
            WHEN 'starter' THEN FALSE
            WHEN 'pro' THEN TRUE
            WHEN 'enterprise' THEN TRUE
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_quotas_on_plan_change
    AFTER INSERT OR UPDATE OF plan ON user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_quotas_on_plan_change();

-- Fonction: Créer quotas par défaut pour nouvel utilisateur
CREATE OR REPLACE FUNCTION create_default_quotas_for_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Créer subscription gratuit par défaut
    INSERT INTO user_subscriptions (user_id, plan, status)
    VALUES (NEW.id, 'free', 'active')
    ON CONFLICT (user_id) DO NOTHING;

    -- Créer quotas par défaut
    INSERT INTO user_quotas (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_default_quotas
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION create_default_quotas_for_user();

-- Fonction: Vérifier quota avant insertion
CREATE OR REPLACE FUNCTION check_quota_before_insert()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id UUID;
    v_current_count INTEGER;
    v_max_count INTEGER;
    v_resource_type VARCHAR(50);
BEGIN
    -- Déterminer le type de ressource et l'user_id
    IF TG_TABLE_NAME = 'products' THEN
        v_resource_type := 'products';
        v_user_id := (SELECT user_id FROM merchants WHERE id = NEW.merchant_id);
    ELSIF TG_TABLE_NAME = 'trackable_links' THEN
        v_resource_type := 'links';
        v_user_id := (SELECT user_id FROM influencers WHERE id = NEW.influencer_id);
    END IF;

    -- Récupérer quotas
    IF v_resource_type = 'products' THEN
        SELECT products_count, max_products INTO v_current_count, v_max_count
        FROM user_quotas WHERE user_id = v_user_id;
    ELSIF v_resource_type = 'links' THEN
        SELECT links_count, max_links INTO v_current_count, v_max_count
        FROM user_quotas WHERE user_id = v_user_id;
    END IF;

    -- Vérifier quota (sauf si illimité = -1)
    IF v_max_count != -1 AND v_current_count >= v_max_count THEN
        RAISE EXCEPTION 'Quota exceeded for %. Current: %, Max: %. Upgrade your plan!',
            v_resource_type, v_current_count, v_max_count;
    END IF;

    -- Incrémenter compteur
    IF v_resource_type = 'products' THEN
        UPDATE user_quotas SET products_count = products_count + 1 WHERE user_id = v_user_id;
    ELSIF v_resource_type = 'links' THEN
        UPDATE user_quotas SET links_count = links_count + 1 WHERE user_id = v_user_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer trigger sur products et trackable_links
CREATE TRIGGER trigger_check_product_quota
    BEFORE INSERT ON products
    FOR EACH ROW
    EXECUTE FUNCTION check_quota_before_insert();

CREATE TRIGGER trigger_check_link_quota
    BEFORE INSERT ON trackable_links
    FOR EACH ROW
    EXECUTE FUNCTION check_quota_before_insert();

-- ============================================
-- VUES
-- ============================================

-- Vue: Abonnements actifs
CREATE OR REPLACE VIEW v_active_subscriptions AS
SELECT
    us.id,
    us.user_id,
    u.email,
    u.full_name,
    us.plan,
    us.billing_cycle,
    us.status,
    us.current_period_end,
    us.cancel_at_period_end,
    uq.products_count,
    uq.max_products,
    uq.links_count,
    uq.max_links
FROM user_subscriptions us
JOIN users u ON us.user_id = u.id
LEFT JOIN user_quotas uq ON us.user_id = uq.user_id
WHERE us.status IN ('active', 'trialing');

-- Vue: Revenue mensuel
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT
    DATE_TRUNC('month', invoice_date) as month,
    COUNT(*) as invoice_count,
    SUM(amount_paid) as total_revenue,
    AVG(amount_paid) as avg_invoice_value
FROM subscription_invoices
WHERE status = 'paid'
GROUP BY month
ORDER BY month DESC;

-- ============================================
-- RLS (Row Level Security)
-- ============================================

ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_quotas ENABLE ROW LEVEL SECURITY;

-- Users can view their own subscription
CREATE POLICY "Users can view their own subscription" ON user_subscriptions
    FOR SELECT USING (user_id::text = auth.uid()::text);

-- Users can view their own invoices
CREATE POLICY "Users can view their own invoices" ON subscription_invoices
    FOR SELECT USING (user_id::text = auth.uid()::text);

-- Users can view their own quotas
CREATE POLICY "Users can view their own quotas" ON user_quotas
    FOR SELECT USING (user_id::text = auth.uid()::text);

-- Admins can view everything
CREATE POLICY "Admins can view all subscriptions" ON user_subscriptions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text AND role = 'admin'
        )
    );

CREATE POLICY "Admins can view all invoices" ON subscription_invoices
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text AND role = 'admin'
        )
    );

-- ============================================
-- DONNÉES INITIALES
-- ============================================

-- Créer abonnement gratuit pour utilisateurs existants
INSERT INTO user_subscriptions (user_id, plan, status)
SELECT id, 'free', 'active'
FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM user_subscriptions WHERE user_id = users.id
)
ON CONFLICT (user_id) DO NOTHING;

-- Créer quotas pour utilisateurs existants
INSERT INTO user_quotas (user_id)
SELECT id
FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM user_quotas WHERE user_id = users.id
)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE user_subscriptions IS 'Abonnements Stripe des utilisateurs';
COMMENT ON TABLE subscription_invoices IS 'Factures générées par Stripe';
COMMENT ON TABLE stripe_webhook_events IS 'Événements webhooks Stripe pour audit';
COMMENT ON TABLE user_quotas IS 'Quotas et features selon le plan d\'abonnement';

COMMENT ON COLUMN user_subscriptions.cancel_at_period_end IS 'True si annulation programmée à la fin de la période';
COMMENT ON COLUMN user_quotas.platform_commission_rate IS 'Taux de commission prélevé par la plateforme (%)';
