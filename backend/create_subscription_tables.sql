-- ============================================
-- SYSTÈME D'ABONNEMENT SaaS COMPLET
-- Tables pour gérer les abonnements, plans, paiements et facturation
-- ============================================

-- 1. TABLE: subscription_plans
-- Définit les différents plans d'abonnement disponibles
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    user_type VARCHAR(20) NOT NULL, -- 'merchant' ou 'influencer'
    price_monthly DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    price_yearly DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'MAD',

    -- Fonctionnalités
    max_products INTEGER,
    max_campaigns INTEGER,
    max_affiliates INTEGER,
    ai_content_generation BOOLEAN DEFAULT FALSE,
    advanced_analytics BOOLEAN DEFAULT FALSE,
    priority_support BOOLEAN DEFAULT FALSE,
    custom_branding BOOLEAN DEFAULT FALSE,
    api_access BOOLEAN DEFAULT FALSE,
    export_data BOOLEAN DEFAULT FALSE,
    commission_rate DECIMAL(5, 2), -- Taux de commission en %

    -- Trial settings
    trial_days INTEGER DEFAULT 0,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    features JSONB, -- Liste détaillée des fonctionnalités

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TABLE: subscriptions
-- Abonnements actifs des utilisateurs
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'trialing', 'past_due', 'canceled', 'expired'

    -- Dates
    start_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_date TIMESTAMPTZ,
    trial_end_date TIMESTAMPTZ,
    canceled_at TIMESTAMPTZ,

    -- Billing
    billing_cycle VARCHAR(20) DEFAULT 'monthly', -- 'monthly', 'yearly'
    current_period_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_period_end TIMESTAMPTZ NOT NULL,

    -- Paiement
    payment_method_id UUID REFERENCES payment_methods(id),
    next_billing_date TIMESTAMPTZ,
    auto_renew BOOLEAN DEFAULT TRUE,

    -- Proration & Upgrades
    prorated_amount DECIMAL(10, 2) DEFAULT 0.00,

    -- Coupon
    coupon_code VARCHAR(50),
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    discount_percentage DECIMAL(5, 2) DEFAULT 0.00,

    -- Metadata
    metadata JSONB,
    cancellation_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. TABLE: payment_methods
-- Méthodes de paiement enregistrées
CREATE TABLE IF NOT EXISTS payment_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Type de méthode
    payment_type VARCHAR(20) NOT NULL, -- 'card', 'bank_transfer', 'wallet'
    provider VARCHAR(50), -- 'stripe', 'cmi', 'payzen', 'sg_maroc'

    -- Données de la carte (tokenizées)
    stripe_payment_method_id VARCHAR(255),
    card_brand VARCHAR(20), -- 'visa', 'mastercard', 'amex'
    card_last4 VARCHAR(4),
    card_exp_month INTEGER,
    card_exp_year INTEGER,

    -- Statut
    is_default BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Metadata
    metadata JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. TABLE: invoices
-- Factures générées
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,

    -- Montants
    subtotal DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0.00,
    tax DECIMAL(10, 2) DEFAULT 0.00,
    total DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'MAD',

    -- Statut
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'pending', 'paid', 'failed', 'refunded'

    -- Dates
    issue_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    due_date TIMESTAMPTZ NOT NULL,
    paid_at TIMESTAMPTZ,

    -- Paiement
    payment_method VARCHAR(50),
    payment_intent_id VARCHAR(255), -- Stripe Payment Intent ID

    -- PDF
    pdf_url TEXT,
    pdf_generated_at TIMESTAMPTZ,

    -- Line items
    items JSONB NOT NULL, -- Array d'objets avec description, amount, quantity

    -- Notes
    notes TEXT,
    metadata JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. TABLE: payment_transactions
-- Historique des transactions de paiement
CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,

    -- Transaction details
    transaction_type VARCHAR(20) NOT NULL, -- 'charge', 'refund', 'dispute'
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'MAD',

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'succeeded', 'failed', 'refunded'

    -- Provider
    payment_provider VARCHAR(50), -- 'stripe', 'cmi', etc.
    provider_transaction_id VARCHAR(255),
    provider_response JSONB,

    -- Error handling
    failure_code VARCHAR(50),
    failure_message TEXT,

    -- Metadata
    metadata JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. TABLE: subscription_coupons
-- Coupons de réduction et promotions
CREATE TABLE IF NOT EXISTS subscription_coupons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    description TEXT,

    -- Type de réduction
    discount_type VARCHAR(20) NOT NULL, -- 'percentage', 'fixed_amount'
    discount_value DECIMAL(10, 2) NOT NULL,

    -- Applicabilité
    applicable_to VARCHAR(20) DEFAULT 'all', -- 'all', 'specific_plans'
    plan_ids JSONB, -- Array d'IDs de plans si specific_plans
    user_type VARCHAR(20), -- 'merchant', 'influencer', 'all'

    -- Durée
    duration VARCHAR(20) DEFAULT 'once', -- 'once', 'repeating', 'forever'
    duration_in_months INTEGER,

    -- Limites
    max_redemptions INTEGER,
    redemptions_count INTEGER DEFAULT 0,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ,

    -- First time users only
    first_time_only BOOLEAN DEFAULT FALSE,

    -- Statut
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. TABLE: subscription_usage
-- Suivi de l'utilisation des fonctionnalités
CREATE TABLE IF NOT EXISTS subscription_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,

    -- Période
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Usage counters
    products_count INTEGER DEFAULT 0,
    campaigns_count INTEGER DEFAULT 0,
    affiliates_count INTEGER DEFAULT 0,
    ai_requests_count INTEGER DEFAULT 0,
    api_calls_count INTEGER DEFAULT 0,

    -- Metadata
    metadata JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(subscription_id, period_start)
);

-- 8. TABLE: subscription_events
-- Log des événements liés aux abonnements
CREATE TABLE IF NOT EXISTS subscription_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Event details
    event_type VARCHAR(50) NOT NULL, -- 'created', 'updated', 'canceled', 'renewed', 'payment_failed', 'upgraded', 'downgraded'
    description TEXT,

    -- Old/New values for changes
    old_data JSONB,
    new_data JSONB,

    -- Metadata
    metadata JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES pour performance
-- ============================================

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_plan_id ON subscriptions(plan_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_end_date ON subscriptions(end_date);

CREATE INDEX idx_payment_methods_user_id ON payment_methods(user_id);
CREATE INDEX idx_payment_methods_default ON payment_methods(is_default);

CREATE INDEX idx_invoices_user_id ON invoices(user_id);
CREATE INDEX idx_invoices_subscription_id ON invoices(subscription_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);

CREATE INDEX idx_payment_transactions_user_id ON payment_transactions(user_id);
CREATE INDEX idx_payment_transactions_subscription_id ON payment_transactions(subscription_id);
CREATE INDEX idx_payment_transactions_invoice_id ON payment_transactions(invoice_id);

CREATE INDEX idx_coupons_code ON subscription_coupons(code);
CREATE INDEX idx_coupons_active ON subscription_coupons(is_active);

CREATE INDEX idx_subscription_usage_user_id ON subscription_usage(user_id);
CREATE INDEX idx_subscription_usage_subscription_id ON subscription_usage(subscription_id);

CREATE INDEX idx_subscription_events_subscription_id ON subscription_events(subscription_id);
CREATE INDEX idx_subscription_events_user_id ON subscription_events(user_id);
CREATE INDEX idx_subscription_events_type ON subscription_events(event_type);

-- ============================================
-- TRIGGERS pour updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_subscription_plans_updated_at BEFORE UPDATE ON subscription_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payment_methods_updated_at BEFORE UPDATE ON payment_methods FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payment_transactions_updated_at BEFORE UPDATE ON payment_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscription_coupons_updated_at BEFORE UPDATE ON subscription_coupons FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscription_usage_updated_at BEFORE UPDATE ON subscription_usage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SEED DATA - Plans d'abonnement par défaut
-- ============================================

-- Plans pour Merchants
INSERT INTO subscription_plans (name, slug, description, user_type, price_monthly, price_yearly, max_products, max_campaigns, max_affiliates, ai_content_generation, advanced_analytics, priority_support, custom_branding, api_access, export_data, commission_rate, trial_days, features, is_featured, display_order)
VALUES
-- Freemium Merchant
('Freemium', 'merchant-freemium', 'Plan gratuit pour démarrer', 'merchant', 0.00, 0.00, 5, 1, 10, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, 15.00, 0,
'["5 produits maximum", "1 campagne active", "10 affiliés maximum", "Support email", "Dashboard basique", "Commission: 15%"]'::jsonb, FALSE, 1),

-- Standard Merchant
('Standard', 'merchant-standard', 'Pour les petites et moyennes entreprises', 'merchant', 299.00, 2990.00, 50, 10, 100, TRUE, FALSE, FALSE, FALSE, FALSE, TRUE, 10.00, 14,
'["50 produits", "10 campagnes actives", "100 affiliés", "Génération de contenu IA", "Export de données", "Support prioritaire", "Commission: 10%"]'::jsonb, FALSE, 2),

-- Premium Merchant
('Premium', 'merchant-premium', 'Pour les entreprises en croissance', 'merchant', 799.00, 7990.00, 200, 50, 500, TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, 7.00, 14,
'["200 produits", "50 campagnes actives", "500 affiliés", "IA avancée", "Analytics avancés", "Support prioritaire 24/7", "Branding personnalisé", "Commission: 7%"]'::jsonb, TRUE, 3),

-- Enterprise Merchant
('Enterprise', 'merchant-enterprise', 'Solution sur mesure pour grandes entreprises', 'merchant', 1999.00, 19990.00, NULL, NULL, NULL, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 5.00, 30,
'["Produits illimités", "Campagnes illimitées", "Affiliés illimités", "IA illimitée", "Analytics personnalisés", "Account manager dédié", "API complète", "Branding complet", "Commission: 5%"]'::jsonb, TRUE, 4),

-- Plans pour Influencers
-- Free Influencer
('Free', 'influencer-free', 'Plan gratuit pour influenceurs débutants', 'influencer', 0.00, 0.00, NULL, NULL, NULL, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, NULL, 0,
'["Accès marketplace", "Liens trackés basiques", "Dashboard basique", "Support communauté"]'::jsonb, FALSE, 1),

-- Pro Influencer
('Pro', 'influencer-pro', 'Pour influenceurs actifs', 'influencer', 99.00, 990.00, NULL, NULL, NULL, TRUE, TRUE, TRUE, FALSE, FALSE, TRUE, NULL, 7,
'["Analytics avancés", "Boost de visibilité", "Génération de contenu IA", "Support prioritaire", "Export de données", "Liens personnalisés"]'::jsonb, TRUE, 2),

-- Elite Influencer
('Elite', 'influencer-elite', 'Pour influenceurs professionnels', 'influencer', 299.00, 2990.00, NULL, NULL, NULL, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, NULL, 7,
'["Tous les avantages Pro", "Branding personnalisé", "API access", "Account manager", "Programmes exclusifs", "Priorité sur les campagnes"]'::jsonb, TRUE, 3);

-- Coupons de lancement
INSERT INTO subscription_coupons (code, name, description, discount_type, discount_value, applicable_to, duration, duration_in_months, max_redemptions, valid_until, is_active)
VALUES
('LAUNCH50', 'Lancement 50%', 'Réduction de 50% sur le premier mois', 'percentage', 50.00, 'all', 'once', NULL, 1000, NOW() + INTERVAL '90 days', TRUE),
('YEARLY20', 'Réduction Annuelle', '20% de réduction sur abonnement annuel', 'percentage', 20.00, 'all', 'once', NULL, NULL, NOW() + INTERVAL '365 days', TRUE),
('FIRSTTIME', 'Premier Abonnement', '30% de réduction pour nouveaux clients', 'percentage', 30.00, 'all', 'once', NULL, NULL, NOW() + INTERVAL '180 days', TRUE);
