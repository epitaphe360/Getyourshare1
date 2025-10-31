-- ============================================
-- SYSTÈME D'ABONNEMENTS - Share Your Sales
-- Plans Entreprise + Marketplace Indépendants
-- ============================================

-- ============================================
-- Table: subscription_plans
-- Plans d'abonnement disponibles
-- ============================================

CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Informations du plan
    name VARCHAR(100) NOT NULL, -- 'Small', 'Medium', 'Large', 'Marketplace'
    code VARCHAR(50) UNIQUE NOT NULL, -- 'enterprise_small', 'enterprise_medium', etc.
    type VARCHAR(50) NOT NULL CHECK (type IN ('enterprise', 'marketplace')),

    -- Tarification
    price_mad DECIMAL(10,2) NOT NULL, -- Prix mensuel en MAD
    currency VARCHAR(3) DEFAULT 'MAD',

    -- Limites du plan (pour entreprises)
    max_team_members INTEGER, -- 2, 10, 30 ou NULL pour marketplace
    max_domains INTEGER, -- 1, 2, NULL (illimité) pour multi-sites

    -- Fonctionnalités
    features JSONB DEFAULT '[]'::jsonb, -- Array de features

    -- Stripe
    stripe_price_id VARCHAR(255), -- ID du prix dans Stripe
    stripe_product_id VARCHAR(255), -- ID du produit dans Stripe

    -- Métadonnées
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_subscription_plans_type ON subscription_plans(type);
CREATE INDEX idx_subscription_plans_code ON subscription_plans(code);
CREATE INDEX idx_subscription_plans_active ON subscription_plans(is_active);

-- ============================================
-- Table: subscriptions
-- Abonnements actifs des utilisateurs
-- ============================================

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Utilisateur
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),

    -- Statut
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN (
        'active',      -- Abonnement actif et payé
        'trialing',    -- Période d'essai
        'past_due',    -- Paiement en retard
        'canceled',    -- Annulé par l'utilisateur
        'unpaid',      -- Paiement échoué
        'paused'       -- Suspendu temporairement
    )),

    -- Dates
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    cancel_at TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,

    -- Paiement
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),

    -- Utilisation actuelle (pour limites)
    current_team_members INTEGER DEFAULT 0,
    current_domains INTEGER DEFAULT 0,

    -- Métadonnées
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_plan_id ON subscriptions(plan_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_stripe_sub ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_subscriptions_period_end ON subscriptions(current_period_end);

-- Un utilisateur ne peut avoir qu'UN seul abonnement actif à la fois
CREATE UNIQUE INDEX idx_subscriptions_user_active
    ON subscriptions(user_id)
    WHERE status IN ('active', 'trialing', 'past_due');

-- ============================================
-- Table: team_members
-- Membres d'équipe rattachés à une entreprise
-- ============================================

CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    company_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- L'entreprise propriétaire
    member_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,  -- Le commercial/influenceur

    -- Rôle dans l'équipe
    team_role VARCHAR(50) NOT NULL CHECK (team_role IN (
        'commercial',
        'influencer',
        'manager'  -- Peut gérer l'équipe
    )),

    -- Permissions
    can_view_all_sales BOOLEAN DEFAULT FALSE,
    can_manage_products BOOLEAN DEFAULT FALSE,

    -- Statut
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN (
        'active',
        'inactive',
        'pending_invitation'
    )),

    -- Commission personnalisée (override du produit)
    custom_commission_rate DECIMAL(5,2), -- NULL = utilise le taux du produit

    -- Invitation
    invited_email VARCHAR(255),
    invitation_token VARCHAR(255) UNIQUE,
    invitation_sent_at TIMESTAMP WITH TIME ZONE,
    invitation_accepted_at TIMESTAMP WITH TIME ZONE,

    -- Métadonnées
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_team_members_company ON team_members(company_id);
CREATE INDEX idx_team_members_member ON team_members(member_id);
CREATE INDEX idx_team_members_status ON team_members(status);
CREATE INDEX idx_team_members_invitation ON team_members(invitation_token);

-- Un membre ne peut être dans la même équipe qu'une fois
CREATE UNIQUE INDEX idx_team_members_unique
    ON team_members(company_id, member_id)
    WHERE status != 'pending_invitation';

-- ============================================
-- Table: allowed_domains
-- Domaines autorisés pour redirections (selon plan)
-- ============================================

CREATE TABLE IF NOT EXISTS allowed_domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Entreprise
    company_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Domaine
    domain VARCHAR(255) NOT NULL, -- 'example.com', 'shop.example.com'
    is_verified BOOLEAN DEFAULT FALSE,

    -- Vérification
    verification_token VARCHAR(255),
    verified_at TIMESTAMP WITH TIME ZONE,

    -- Statut
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_allowed_domains_company ON allowed_domains(company_id);
CREATE INDEX idx_allowed_domains_domain ON allowed_domains(domain);
CREATE INDEX idx_allowed_domains_active ON allowed_domains(is_active, is_verified);

-- Un domaine ne peut être ajouté qu'une fois par entreprise
CREATE UNIQUE INDEX idx_allowed_domains_unique ON allowed_domains(company_id, domain);

-- ============================================
-- Trigger: Auto-update updated_at
-- ============================================

CREATE TRIGGER trigger_subscription_plans_updated_at
    BEFORE UPDATE ON subscription_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_team_members_updated_at
    BEFORE UPDATE ON team_members
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_allowed_domains_updated_at
    BEFORE UPDATE ON allowed_domains
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- Function: Check subscription limits
-- ============================================

CREATE OR REPLACE FUNCTION check_subscription_limit(
    p_user_id UUID,
    p_limit_type VARCHAR -- 'team_members' ou 'domains'
) RETURNS BOOLEAN AS $$
DECLARE
    v_subscription_id UUID;
    v_plan_max INTEGER;
    v_current_count INTEGER;
BEGIN
    -- Récupérer l'abonnement actif
    SELECT s.id,
           CASE
               WHEN p_limit_type = 'team_members' THEN sp.max_team_members
               WHEN p_limit_type = 'domains' THEN sp.max_domains
           END as plan_max,
           CASE
               WHEN p_limit_type = 'team_members' THEN s.current_team_members
               WHEN p_limit_type = 'domains' THEN s.current_domains
           END as current_count
    INTO v_subscription_id, v_plan_max, v_current_count
    FROM subscriptions s
    JOIN subscription_plans sp ON s.plan_id = sp.id
    WHERE s.user_id = p_user_id
      AND s.status IN ('active', 'trialing')
    LIMIT 1;

    -- Si pas d'abonnement, refuser
    IF v_subscription_id IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Si max_limit NULL = illimité
    IF v_plan_max IS NULL THEN
        RETURN TRUE;
    END IF;

    -- Vérifier si limite atteinte
    RETURN v_current_count < v_plan_max;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- INSERT Plans d'Abonnement par Défaut
-- ============================================

-- Plans Entreprise
INSERT INTO subscription_plans (name, code, type, price_mad, max_team_members, max_domains, features, description, display_order) VALUES

('Small', 'enterprise_small', 'enterprise', 199.00, 2, 1,
'["2 comptes commerciaux/influenceurs", "1 site web autorisé", "Dashboard entreprise", "Liens trackables illimités", "Support email"]'::jsonb,
'Idéal pour PME. Chaque compte génère ses propres liens.',
1),

('Medium', 'enterprise_medium', 'enterprise', 499.00, 10, 2,
'["10 comptes commerciaux/influenceurs", "2 sites web autorisés", "Dashboard entreprise", "Liens trackables illimités", "Support prioritaire", "Analytics avancés"]'::jsonb,
'Pour entreprises multi-équipes ou multi-marques.',
2),

('Large', 'enterprise_large', 'enterprise', 799.00, 30, NULL,
'["30 comptes commerciaux/influenceurs", "Sites web illimités", "Dashboard entreprise", "Liens trackables illimités", "Support VIP 24/7", "Analytics avancés", "API access", "White-label option"]'::jsonb,
'Gestion étendue et suivi multi-domaines.',
3),

-- Plan Marketplace Indépendant
('Marketplace', 'marketplace_independent', 'marketplace', 99.00, NULL, NULL,
'["Accès complet Marketplace", "Sélection produits & services", "Suivi de ventes personnel", "Support email", "Formation vidéo"]'::jsonb,
'Pour commerciaux et influenceurs indépendants. Accès complet à la Marketplace sans génération de leads entrants.',
4);

-- ============================================
-- RLS Policies
-- ============================================

ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE allowed_domains ENABLE ROW LEVEL SECURITY;

-- Plans: Lecture publique
CREATE POLICY subscription_plans_public_read
    ON subscription_plans FOR SELECT
    USING (is_active = TRUE);

-- Plans: Admin seulement peut modifier
CREATE POLICY subscription_plans_admin_all
    ON subscription_plans FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Subscriptions: Utilisateur voit ses propres abonnements
CREATE POLICY subscriptions_user_select
    ON subscriptions FOR SELECT
    USING (user_id = auth.uid());

-- Subscriptions: Admin voit tout
CREATE POLICY subscriptions_admin_all
    ON subscriptions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Team Members: Entreprise gère ses membres
CREATE POLICY team_members_company_all
    ON team_members FOR ALL
    USING (company_id = auth.uid());

-- Team Members: Membre voit son propre profil
CREATE POLICY team_members_self_select
    ON team_members FOR SELECT
    USING (member_id = auth.uid());

-- Team Members: Admin voit tout
CREATE POLICY team_members_admin_all
    ON team_members FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Allowed Domains: Entreprise gère ses domaines
CREATE POLICY allowed_domains_company_all
    ON allowed_domains FOR ALL
    USING (company_id = auth.uid());

-- Allowed Domains: Admin voit tout
CREATE POLICY allowed_domains_admin_all
    ON allowed_domains FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================
-- Views
-- ============================================

-- Vue: Abonnements actifs avec détails du plan
CREATE OR REPLACE VIEW v_active_subscriptions AS
SELECT
    s.*,
    sp.name as plan_name,
    sp.code as plan_code,
    sp.type as plan_type,
    sp.price_mad,
    sp.max_team_members as plan_max_team_members,
    sp.max_domains as plan_max_domains,
    sp.features as plan_features,
    u.email as user_email,
    u.first_name,
    u.last_name,
    u.role as user_role
FROM subscriptions s
JOIN subscription_plans sp ON s.plan_id = sp.id
JOIN users u ON s.user_id = u.id
WHERE s.status IN ('active', 'trialing');

-- Vue: Équipes avec infos membres
CREATE OR REPLACE VIEW v_team_members_details AS
SELECT
    tm.*,
    c.email as company_email,
    c.first_name as company_name,
    m.email as member_email,
    m.first_name as member_first_name,
    m.last_name as member_last_name,
    m.role as member_role
FROM team_members tm
JOIN users c ON tm.company_id = c.id
JOIN users m ON tm.member_id = m.id;

-- ============================================
-- Commentaires
-- ============================================

COMMENT ON TABLE subscription_plans IS 'Plans d''abonnement (Small 199, Medium 499, Large 799, Marketplace 99 MAD)';
COMMENT ON TABLE subscriptions IS 'Abonnements actifs des entreprises et commerciaux/influenceurs indépendants';
COMMENT ON TABLE team_members IS 'Membres d''équipe rattachés à une entreprise selon le plan';
COMMENT ON TABLE allowed_domains IS 'Domaines autorisés pour redirections selon le plan d''abonnement';

COMMENT ON COLUMN subscription_plans.max_team_members IS '2 pour Small, 10 pour Medium, 30 pour Large, NULL pour Marketplace';
COMMENT ON COLUMN subscription_plans.max_domains IS '1 pour Small, 2 pour Medium, NULL (illimité) pour Large et Marketplace';
COMMENT ON COLUMN team_members.team_role IS 'commercial, influencer, ou manager dans l''équipe';
COMMENT ON COLUMN allowed_domains.domain IS 'Domaine autorisé pour redirection (sans https://)';
