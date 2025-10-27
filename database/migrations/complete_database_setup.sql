-- ============================================================================
-- MIGRATION COMPLETE - SHAREYOURSALES DATABASE
-- ============================================================================
-- Ce fichier contient TOUTES les tables manquantes pour l'application
-- À exécuter dans Supabase Dashboard > SQL Editor
-- Date: 26 Octobre 2025
-- ============================================================================

-- ============================================================================
-- PARTIE 1: ACTIVATION 2FA POUR TOUS LES UTILISATEURS
-- ============================================================================

-- Activer la 2FA pour tous les utilisateurs
UPDATE users 
SET two_fa_enabled = true 
WHERE two_fa_enabled = false OR two_fa_enabled IS NULL;

-- ============================================================================
-- PARTIE 2: TABLES D'ABONNEMENTS
-- ============================================================================

-- Table: user_subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type TEXT NOT NULL CHECK (plan_type IN ('free', 'starter', 'pro', 'enterprise', 'merchant_basic', 'merchant_standard', 'merchant_premium', 'merchant_enterprise')),
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled', 'expired', 'pending')) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    auto_renew BOOLEAN DEFAULT true,
    payment_method TEXT,
    last_payment_date TIMESTAMP,
    next_billing_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour user_subscriptions
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);

-- ============================================================================
-- PARTIE 3: SYSTÈME DE SUPPORT
-- ============================================================================

-- Table: support_tickets
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('technical', 'billing', 'account', 'feature_request', 'other')),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'waiting_response', 'resolved', 'closed')) DEFAULT 'open',
    description TEXT NOT NULL,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Table: ticket_messages
CREATE TABLE IF NOT EXISTS ticket_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    attachments JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour support
CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_assigned ON support_tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket ON ticket_messages(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_messages_user ON ticket_messages(user_id);

-- ============================================================================
-- PARTIE 4: VIDÉOS TUTORIELS
-- ============================================================================

-- Table: video_tutorials
CREATE TABLE IF NOT EXISTS video_tutorials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    video_url TEXT NOT NULL,
    thumbnail_url TEXT,
    duration INTEGER, -- en secondes
    category TEXT NOT NULL CHECK (category IN ('getting_started', 'influencer', 'merchant', 'admin', 'advanced')),
    difficulty TEXT NOT NULL CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')) DEFAULT 'beginner',
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    is_published BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: video_progress
CREATE TABLE IF NOT EXISTS video_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES video_tutorials(id) ON DELETE CASCADE,
    progress_seconds INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT false,
    last_watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, video_id)
);

-- Index pour vidéos
CREATE INDEX IF NOT EXISTS idx_video_tutorials_category ON video_tutorials(category);
CREATE INDEX IF NOT EXISTS idx_video_tutorials_published ON video_tutorials(is_published);
CREATE INDEX IF NOT EXISTS idx_video_progress_user ON video_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_video_progress_video ON video_progress(video_id);

-- ============================================================================
-- PARTIE 5: DOCUMENTATION
-- ============================================================================

-- Table: documentation_articles
CREATE TABLE IF NOT EXISTS documentation_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('getting_started', 'influencer', 'merchant', 'api', 'troubleshooting', 'faq')),
    tags TEXT[],
    views INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT true,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour documentation
CREATE INDEX IF NOT EXISTS idx_documentation_slug ON documentation_articles(slug);
CREATE INDEX IF NOT EXISTS idx_documentation_category ON documentation_articles(category);
CREATE INDEX IF NOT EXISTS idx_documentation_published ON documentation_articles(is_published);

-- ============================================================================
-- PARTIE 6: DEMANDES D'AFFILIATION
-- ============================================================================

-- Table: affiliation_requests
CREATE TABLE IF NOT EXISTS affiliation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    requested_commission_rate DECIMAL(5,2),
    message TEXT,
    merchant_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour affiliation_requests
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_influencer ON affiliation_requests(influencer_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_merchant ON affiliation_requests(merchant_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_status ON affiliation_requests(status);

-- ============================================================================
-- PARTIE 7: PARAMÈTRES ENTREPRISE
-- ============================================================================

-- Table: company_settings
CREATE TABLE IF NOT EXISTS company_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    company_name TEXT,
    industry TEXT,
    website TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    postal_code TEXT,
    country TEXT DEFAULT 'Morocco',
    logo_url TEXT,
    favicon_url TEXT,
    primary_color TEXT DEFAULT '#3B82F6',
    secondary_color TEXT DEFAULT '#10B981',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour company_settings
CREATE INDEX IF NOT EXISTS idx_company_settings_user ON company_settings(user_id);

-- ============================================================================
-- PARTIE 8: GATEWAYS DE PAIEMENT (MAROC)
-- ============================================================================

-- Table: payment_gateways
CREATE TABLE IF NOT EXISTS payment_gateways (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    gateway_name TEXT NOT NULL CHECK (gateway_name IN ('cmi', 'payzen', 'sg_maroc')),
    api_key TEXT,
    secret_key TEXT,
    merchant_id_gateway TEXT,
    is_active BOOLEAN DEFAULT false,
    is_test_mode BOOLEAN DEFAULT true,
    configuration JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(merchant_id, gateway_name)
);

-- Index pour payment_gateways
CREATE INDEX IF NOT EXISTS idx_payment_gateways_merchant ON payment_gateways(merchant_id);
CREATE INDEX IF NOT EXISTS idx_payment_gateways_active ON payment_gateways(is_active);

-- ============================================================================
-- PARTIE 9: FACTURATION
-- ============================================================================

-- Table: invoices
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    invoice_number TEXT UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'MAD',
    status TEXT NOT NULL CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')) DEFAULT 'draft',
    due_date DATE,
    paid_date DATE,
    items JSONB DEFAULT '[]',
    pdf_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour invoices
CREATE INDEX IF NOT EXISTS idx_invoices_merchant ON invoices(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number);

-- ============================================================================
-- PARTIE 10: NOTIFICATIONS
-- ============================================================================

-- Table: notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('sale', 'commission', 'message', 'system', 'payment')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    link TEXT,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at);

-- ============================================================================
-- PARTIE 11: JOURNAL D'ACTIVITÉ
-- ============================================================================

-- Table: activity_log
CREATE TABLE IF NOT EXISTS activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour activity_log
CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_action ON activity_log(action);
CREATE INDEX IF NOT EXISTS idx_activity_log_created ON activity_log(created_at);

-- ============================================================================
-- PARTIE 12: PARAMÈTRES AFFILIÉS
-- ============================================================================

-- Table: affiliate_settings
CREATE TABLE IF NOT EXISTS affiliate_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    min_payout_amount DECIMAL(10,2) DEFAULT 50.00,
    payout_frequency TEXT CHECK (payout_frequency IN ('weekly', 'biweekly', 'monthly')) DEFAULT 'monthly',
    auto_approve_affiliates BOOLEAN DEFAULT false,
    default_commission_rate DECIMAL(5,2) DEFAULT 10.00,
    cookie_duration_days INTEGER DEFAULT 30,
    require_approval BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour affiliate_settings
CREATE INDEX IF NOT EXISTS idx_affiliate_settings_user ON affiliate_settings(user_id);

-- ============================================================================
-- PARTIE 13: PARAMÈTRES MLM (Multi-Level Marketing)
-- ============================================================================

-- Table: mlm_settings
CREATE TABLE IF NOT EXISTS mlm_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    enabled BOOLEAN DEFAULT false,
    max_levels INTEGER DEFAULT 3,
    level_commissions JSONB DEFAULT '{"level_1": 5, "level_2": 3, "level_3": 2}',
    require_purchase BOOLEAN DEFAULT false,
    min_referrals_per_level INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: mlm_commissions
CREATE TABLE IF NOT EXISTS mlm_commissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    referrer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    level INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status TEXT CHECK (status IN ('pending', 'paid')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP
);

-- Index pour MLM
CREATE INDEX IF NOT EXISTS idx_mlm_settings_user ON mlm_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_sale ON mlm_commissions(sale_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_influencer ON mlm_commissions(influencer_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_referrer ON mlm_commissions(referrer_id);

-- ============================================================================
-- PARTIE 14: PARAMÈTRES D'INSCRIPTION
-- ============================================================================

-- Table: registration_settings
CREATE TABLE IF NOT EXISTS registration_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    require_email_verification BOOLEAN DEFAULT true,
    require_phone_verification BOOLEAN DEFAULT false,
    require_admin_approval BOOLEAN DEFAULT false,
    allowed_domains TEXT[],
    blocked_domains TEXT[],
    min_age INTEGER DEFAULT 18,
    terms_url TEXT,
    privacy_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour registration_settings
CREATE INDEX IF NOT EXISTS idx_registration_settings_user ON registration_settings(user_id);

-- ============================================================================
-- PARTIE 15: PERMISSIONS
-- ============================================================================

-- Table: permissions
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role TEXT NOT NULL CHECK (role IN ('admin', 'merchant', 'influencer')),
    resource TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('create', 'read', 'update', 'delete')),
    allowed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role, resource, action)
);

-- Index pour permissions
CREATE INDEX IF NOT EXISTS idx_permissions_role ON permissions(role);
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);

-- ============================================================================
-- PARTIE 16: PARAMÈTRES WHITE LABEL
-- ============================================================================

-- Table: white_label_settings
CREATE TABLE IF NOT EXISTS white_label_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    domain TEXT,
    brand_name TEXT,
    logo_url TEXT,
    favicon_url TEXT,
    primary_color TEXT DEFAULT '#3B82F6',
    secondary_color TEXT DEFAULT '#10B981',
    custom_css TEXT,
    custom_js TEXT,
    meta_title TEXT,
    meta_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour white_label_settings
CREATE INDEX IF NOT EXISTS idx_white_label_settings_user ON white_label_settings(user_id);

-- ============================================================================
-- PARTIE 17: SOURCES DE TRAFIC
-- ============================================================================

-- Table: traffic_sources
CREATE TABLE IF NOT EXISTS traffic_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    total_clicks INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour traffic_sources
CREATE INDEX IF NOT EXISTS idx_traffic_sources_active ON traffic_sources(is_active);
CREATE INDEX IF NOT EXISTS idx_traffic_sources_utm ON traffic_sources(utm_source, utm_medium, utm_campaign);

-- ============================================================================
-- PARTIE 18: TEMPLATES D'EMAILS
-- ============================================================================

-- Table: email_templates
CREATE TABLE IF NOT EXISTS email_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT,
    variables JSONB DEFAULT '[]',
    category TEXT CHECK (category IN ('welcome', 'notification', 'marketing', 'transactional', 'system')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour email_templates
CREATE INDEX IF NOT EXISTS idx_email_templates_name ON email_templates(name);
CREATE INDEX IF NOT EXISTS idx_email_templates_category ON email_templates(category);
CREATE INDEX IF NOT EXISTS idx_email_templates_active ON email_templates(is_active);

-- ============================================================================
-- PARTIE 19: TRIGGERS POUR updated_at
-- ============================================================================

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Appliquer les triggers sur toutes les tables
CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_video_tutorials_updated_at BEFORE UPDATE ON video_tutorials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documentation_articles_updated_at BEFORE UPDATE ON documentation_articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_affiliation_requests_updated_at BEFORE UPDATE ON affiliation_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_settings_updated_at BEFORE UPDATE ON company_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_gateways_updated_at BEFORE UPDATE ON payment_gateways
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_affiliate_settings_updated_at BEFORE UPDATE ON affiliate_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mlm_settings_updated_at BEFORE UPDATE ON mlm_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_registration_settings_updated_at BEFORE UPDATE ON registration_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_white_label_settings_updated_at BEFORE UPDATE ON white_label_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_traffic_sources_updated_at BEFORE UPDATE ON traffic_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_email_templates_updated_at BEFORE UPDATE ON email_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PARTIE 20: INSERTION DE PERMISSIONS PAR DÉFAUT
-- ============================================================================

-- Permissions Admin (accès complet)
INSERT INTO permissions (role, resource, action, allowed) VALUES
('admin', 'users', 'create', true),
('admin', 'users', 'read', true),
('admin', 'users', 'update', true),
('admin', 'users', 'delete', true),
('admin', 'products', 'create', true),
('admin', 'products', 'read', true),
('admin', 'products', 'update', true),
('admin', 'products', 'delete', true),
('admin', 'settings', 'create', true),
('admin', 'settings', 'read', true),
('admin', 'settings', 'update', true),
('admin', 'settings', 'delete', true)
ON CONFLICT (role, resource, action) DO NOTHING;

-- Permissions Merchant
INSERT INTO permissions (role, resource, action, allowed) VALUES
('merchant', 'products', 'create', true),
('merchant', 'products', 'read', true),
('merchant', 'products', 'update', true),
('merchant', 'products', 'delete', true),
('merchant', 'campaigns', 'create', true),
('merchant', 'campaigns', 'read', true),
('merchant', 'campaigns', 'update', true),
('merchant', 'campaigns', 'delete', true),
('merchant', 'affiliates', 'read', true),
('merchant', 'sales', 'read', true)
ON CONFLICT (role, resource, action) DO NOTHING;

-- Permissions Influencer
INSERT INTO permissions (role, resource, action, allowed) VALUES
('influencer', 'tracking_links', 'create', true),
('influencer', 'tracking_links', 'read', true),
('influencer', 'tracking_links', 'update', true),
('influencer', 'products', 'read', true),
('influencer', 'sales', 'read', true),
('influencer', 'commissions', 'read', true)
ON CONFLICT (role, resource, action) DO NOTHING;

-- ============================================================================
-- PARTIE 21: INSERTION DE TEMPLATES D'EMAILS PAR DÉFAUT
-- ============================================================================

INSERT INTO email_templates (name, subject, body_html, body_text, variables, category) VALUES
(
    'welcome_email',
    'Bienvenue sur ShareYourSales !',
    '<h1>Bienvenue {{name}} !</h1><p>Merci de rejoindre notre plateforme.</p>',
    'Bienvenue {{name}} ! Merci de rejoindre notre plateforme.',
    '["name", "email"]',
    'welcome'
),
(
    'sale_notification',
    'Nouvelle vente réalisée !',
    '<h2>Félicitations !</h2><p>Vous avez réalisé une vente de {{amount}} {{currency}}.</p>',
    'Félicitations ! Vous avez réalisé une vente de {{amount}} {{currency}}.',
    '["amount", "currency", "product_name"]',
    'notification'
),
(
    'commission_paid',
    'Commission payée',
    '<h2>Paiement effectué</h2><p>Votre commission de {{amount}} {{currency}} a été payée.</p>',
    'Paiement effectué. Votre commission de {{amount}} {{currency}} a été payée.',
    '["amount", "currency", "transaction_id"]',
    'transactional'
)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- PARTIE 22: VÉRIFICATION FINALE
-- ============================================================================

-- Afficher un résumé des tables créées
SELECT 
    '2FA Activation' as operation,
    (SELECT COUNT(*) FROM users WHERE two_fa_enabled = true) as count
UNION ALL
SELECT 'user_subscriptions', COUNT(*) FROM user_subscriptions
UNION ALL
SELECT 'support_tickets', COUNT(*) FROM support_tickets
UNION ALL
SELECT 'ticket_messages', COUNT(*) FROM ticket_messages
UNION ALL
SELECT 'video_tutorials', COUNT(*) FROM video_tutorials
UNION ALL
SELECT 'video_progress', COUNT(*) FROM video_progress
UNION ALL
SELECT 'documentation_articles', COUNT(*) FROM documentation_articles
UNION ALL
SELECT 'affiliation_requests', COUNT(*) FROM affiliation_requests
UNION ALL
SELECT 'company_settings', COUNT(*) FROM company_settings
UNION ALL
SELECT 'payment_gateways', COUNT(*) FROM payment_gateways
UNION ALL
SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL
SELECT 'notifications', COUNT(*) FROM notifications
UNION ALL
SELECT 'activity_log', COUNT(*) FROM activity_log
UNION ALL
SELECT 'affiliate_settings', COUNT(*) FROM affiliate_settings
UNION ALL
SELECT 'mlm_settings', COUNT(*) FROM mlm_settings
UNION ALL
SELECT 'mlm_commissions', COUNT(*) FROM mlm_commissions
UNION ALL
SELECT 'registration_settings', COUNT(*) FROM registration_settings
UNION ALL
SELECT 'permissions', COUNT(*) FROM permissions
UNION ALL
SELECT 'white_label_settings', COUNT(*) FROM white_label_settings
UNION ALL
SELECT 'traffic_sources', COUNT(*) FROM traffic_sources
UNION ALL
SELECT 'email_templates', COUNT(*) FROM email_templates;

-- ============================================================================
-- FIN DE LA MIGRATION COMPLÈTE
-- ============================================================================
-- Total: 19 nouvelles tables + activation 2FA + permissions + templates
-- ============================================================================
