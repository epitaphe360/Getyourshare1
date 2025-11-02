-- ============================================
-- TABLE SUBSCRIPTION_PLANS
-- Plans d'abonnement centralisés
-- ============================================
-- Exécutez ce script dans Supabase SQL Editor

-- Créer la table des plans d'abonnement
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('merchant', 'influencer')),
    price_mad DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'MAD',
    
    -- Limites du plan (NULL = illimité)
    max_products INTEGER,
    max_campaigns INTEGER,
    max_affiliates INTEGER,
    max_team_members INTEGER,
    max_domains INTEGER,
    
    -- Taux de commission/frais
    commission_rate DECIMAL(5, 2),
    platform_fee_rate DECIMAL(5, 2),
    
    -- Features incluses
    features JSONB DEFAULT '[]'::jsonb,
    description TEXT,
    
    -- Configuration
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    stripe_price_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_subscription_plans_code ON subscription_plans(code);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_type ON subscription_plans(type);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(is_active);

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_subscription_plans_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour updated_at
DROP TRIGGER IF EXISTS subscription_plans_updated_at ON subscription_plans;
CREATE TRIGGER subscription_plans_updated_at
    BEFORE UPDATE ON subscription_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_subscription_plans_updated_at();

-- ============================================
-- INSERTION DES PLANS D'ABONNEMENT
-- ============================================

-- PLANS MERCHANTS
INSERT INTO subscription_plans (name, code, type, price_mad, commission_rate, max_products, max_campaigns, max_affiliates, features, description, display_order)
VALUES 
    (
        'Free',
        'merchant_free',
        'merchant',
        0.00,
        5.00,
        10,
        5,
        50,
        '["Dashboard basique", "Support email", "Rapports mensuels", "10 produits max", "5 campagnes max", "50 affiliés max"]'::jsonb,
        'Plan gratuit pour débuter avec les bases',
        1
    ),
    (
        'Starter',
        'merchant_starter',
        'merchant',
        299.00,
        4.00,
        50,
        20,
        200,
        '["Dashboard avancé", "Support prioritaire", "Rapports hebdomadaires", "50 produits", "20 campagnes", "200 affiliés", "Analytics avancées", "Export de données"]'::jsonb,
        'Pour les petites entreprises en croissance',
        2
    ),
    (
        'Pro',
        'merchant_pro',
        'merchant',
        799.00,
        3.00,
        200,
        100,
        1000,
        '["Dashboard premium", "Support 24/7", "Rapports en temps réel", "200 produits", "100 campagnes", "1000 affiliés", "Analytics premium", "API access", "White label", "Multi-utilisateurs"]'::jsonb,
        'Pour les entreprises établies',
        3
    ),
    (
        'Enterprise',
        'merchant_enterprise',
        'merchant',
        1999.00,
        2.00,
        NULL,
        NULL,
        NULL,
        '["Dashboard enterprise", "Support dédié", "Rapports personnalisés", "Produits illimités", "Campagnes illimitées", "Affiliés illimités", "Analytics custom", "API illimitée", "Full white label", "Multi-utilisateurs illimités", "Account manager dédié", "Formation sur mesure"]'::jsonb,
        'Pour les grandes entreprises',
        4
    )
ON CONFLICT (code) DO NOTHING;

-- PLANS INFLUENCERS
INSERT INTO subscription_plans (name, code, type, price_mad, platform_fee_rate, max_campaigns, max_affiliates, features, description, display_order)
VALUES 
    (
        'Starter',
        'influencer_starter',
        'influencer',
        0.00,
        5.00,
        5,
        10,
        '["Dashboard basique", "5 campagnes actives", "10 liens d''affiliation", "Statistiques de base", "Paiement mensuel", "Support email"]'::jsonb,
        'Plan gratuit pour influenceurs débutants',
        5
    ),
    (
        'Pro',
        'influencer_pro',
        'influencer',
        99.00,
        3.00,
        50,
        100,
        '["Dashboard avancé", "50 campagnes actives", "100 liens d''affiliation", "Analytics avancées", "Paiement hebdomadaire", "Support prioritaire", "Liens personnalisés", "Intégration réseaux sociaux"]'::jsonb,
        'Pour influenceurs professionnels',
        6
    ),
    (
        'Elite',
        'influencer_elite',
        'influencer',
        299.00,
        2.00,
        NULL,
        NULL,
        '["Dashboard premium", "Campagnes illimitées", "Liens illimités", "Analytics en temps réel", "Paiement instantané", "Support 24/7", "Account manager dédié", "Liens ultra-personnalisés", "Intégration complète", "Accès API", "Formations exclusives"]'::jsonb,
        'Pour top influenceurs et créateurs',
        7
    )
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- VÉRIFICATION
-- ============================================

SELECT 
    '✅ PLANS CRÉÉS' as status,
    COUNT(*) as total_plans_created
FROM subscription_plans;

-- Afficher tous les plans
SELECT 
    name,
    code,
    type,
    price_mad,
    COALESCE(commission_rate, platform_fee_rate) as rate,
    CASE 
        WHEN max_products IS NULL THEN '∞'
        ELSE max_products::TEXT
    END as products,
    CASE 
        WHEN max_campaigns IS NULL THEN '∞'
        ELSE max_campaigns::TEXT
    END as campaigns,
    is_active
FROM subscription_plans
ORDER BY display_order;
