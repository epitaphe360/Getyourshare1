-- ============================================================================
-- MIGRATION IDEMPOTENTE - UNIQUEMENT LES TABLES MANQUANTES
-- ============================================================================
-- Ce script peut être exécuté plusieurs fois sans erreur
-- Il vérifie l'existence avant chaque création
-- Date: 2025-01-XX
-- ============================================================================

-- ============================================================================
-- PARTIE 1: ACTIVATION 2FA (si pas déjà activé)
-- ============================================================================

-- Vérifie si la colonne existe et active 2FA si nécessaire
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'two_fa_enabled'
    ) THEN
        UPDATE users 
        SET two_fa_enabled = true 
        WHERE two_fa_enabled IS NULL OR two_fa_enabled = false;
        RAISE NOTICE 'Colonne two_fa_enabled activée';
    ELSE
        RAISE NOTICE 'Colonne two_fa_enabled n''existe pas';
    END IF;
END $$;

-- ============================================================================
-- PARTIE 2: TABLES PRIORITAIRES - ABONNEMENTS
-- ============================================================================

-- Table: user_subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    plan_type TEXT NOT NULL CHECK (plan_type IN ('free', 'starter', 'professional', 'enterprise')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'suspended')),
    start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    auto_renewal BOOLEAN DEFAULT true,
    payment_method JSONB,
    billing_cycle TEXT CHECK (billing_cycle IN ('monthly', 'yearly')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ============================================================================
-- PARTIE 3: TABLES SUPPORT CLIENT
-- ============================================================================

-- Table: support_tickets
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('technical', 'billing', 'general', 'feature_request', 'bug')),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'waiting_user', 'resolved', 'closed')),
    priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_assigned_to ON support_tickets(assigned_to);

-- Table: ticket_messages
CREATE TABLE IF NOT EXISTS ticket_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_staff_reply BOOLEAN DEFAULT false,
    attachments JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);

-- ============================================================================
-- PARTIE 4: TABLES FORMATION & DOCUMENTATION
-- ============================================================================

-- Table: video_tutorials
CREATE TABLE IF NOT EXISTS video_tutorials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL CHECK (category IN ('getting_started', 'influencer', 'merchant', 'admin', 'advanced')),
    video_url TEXT NOT NULL,
    thumbnail_url TEXT,
    duration_seconds INTEGER,
    difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    order_index INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_video_tutorials_category ON video_tutorials(category);
CREATE INDEX IF NOT EXISTS idx_video_tutorials_published ON video_tutorials(is_published);

-- Table: video_progress
CREATE TABLE IF NOT EXISTS video_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES video_tutorials(id) ON DELETE CASCADE,
    progress_seconds INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT false,
    last_watched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, video_id)
);

CREATE INDEX IF NOT EXISTS idx_video_progress_user_id ON video_progress(user_id);

-- Table: documentation_articles
CREATE TABLE IF NOT EXISTS documentation_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('getting_started', 'features', 'integrations', 'api', 'troubleshooting')),
    tags TEXT[],
    is_published BOOLEAN DEFAULT true,
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documentation_articles_category ON documentation_articles(category);
CREATE INDEX IF NOT EXISTS idx_documentation_articles_published ON documentation_articles(is_published);
CREATE INDEX IF NOT EXISTS idx_documentation_articles_slug ON documentation_articles(slug);

-- ============================================================================
-- PARTIE 5: TABLES AFFILIATION & DEMANDES
-- ============================================================================

-- Table: affiliation_requests
CREATE TABLE IF NOT EXISTS affiliation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE SET NULL,
    merchant_id UUID REFERENCES merchants(id) ON DELETE SET NULL,
    request_type TEXT NOT NULL CHECK (request_type IN ('become_influencer', 'become_merchant', 'partnership')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'under_review')),
    business_info JSONB,
    social_media_links JSONB,
    motivation TEXT,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_affiliation_requests_user_id ON affiliation_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_status ON affiliation_requests(status);

-- ============================================================================
-- PARTIE 6: TABLES ENTREPRISE & CONFIGURATION
-- ============================================================================

-- Table: company_settings
CREATE TABLE IF NOT EXISTS company_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT NOT NULL,
    company_logo_url TEXT,
    company_email TEXT,
    company_phone TEXT,
    company_address TEXT,
    tax_id TEXT,
    currency TEXT DEFAULT 'EUR',
    timezone TEXT DEFAULT 'Europe/Paris',
    language TEXT DEFAULT 'fr',
    commission_model JSONB,
    default_commission_rate DECIMAL(5,2) DEFAULT 10.00,
    min_payout_amount DECIMAL(10,2) DEFAULT 50.00,
    payout_schedule TEXT CHECK (payout_schedule IN ('weekly', 'biweekly', 'monthly')),
    features_enabled JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: payment_gateways
CREATE TABLE IF NOT EXISTS payment_gateways (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    gateway_type TEXT NOT NULL CHECK (gateway_type IN ('stripe', 'paypal', 'bank_transfer', 'crypto')),
    is_active BOOLEAN DEFAULT true,
    configuration JSONB NOT NULL,
    api_keys JSONB,
    webhook_url TEXT,
    supported_currencies TEXT[],
    fees JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: invoices
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number TEXT UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    payment_id UUID REFERENCES payments(id) ON DELETE SET NULL,
    amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'EUR',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'cancelled', 'refunded')),
    due_date TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    invoice_items JSONB,
    billing_address JSONB,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);

-- ============================================================================
-- PARTIE 7: TABLES NOTIFICATIONS & ACTIVITÉ
-- ============================================================================

-- Table: notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('info', 'success', 'warning', 'error', 'sale', 'commission', 'payout')),
    is_read BOOLEAN DEFAULT false,
    action_url TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- Table: activity_log
CREATE TABLE IF NOT EXISTS activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_entity ON activity_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at DESC);

-- ============================================================================
-- PARTIE 8: TABLES PARAMÈTRES AFFILIÉS
-- ============================================================================

-- Table: affiliate_settings
CREATE TABLE IF NOT EXISTS affiliate_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    affiliate_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    payment_method TEXT CHECK (payment_method IN ('bank_transfer', 'paypal', 'stripe', 'crypto')),
    payment_details JSONB,
    min_payout_amount DECIMAL(10,2) DEFAULT 50.00,
    auto_payout BOOLEAN DEFAULT false,
    notification_preferences JSONB,
    tracking_domains TEXT[],
    custom_commission_rate DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(affiliate_id)
);

-- ============================================================================
-- PARTIE 9: TABLES MLM (MARKETING MULTI-NIVEAUX)
-- ============================================================================

-- Table: mlm_settings
CREATE TABLE IF NOT EXISTS mlm_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    is_enabled BOOLEAN DEFAULT false,
    max_levels INTEGER DEFAULT 3,
    level_commission_rates JSONB NOT NULL,
    qualification_rules JSONB,
    bonus_structure JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: mlm_commissions
CREATE TABLE IF NOT EXISTS mlm_commissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    affiliate_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    downline_affiliate_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    level INTEGER NOT NULL,
    commission_amount DECIMAL(10,2) NOT NULL,
    commission_percentage DECIMAL(5,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')),
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mlm_commissions_affiliate_id ON mlm_commissions(affiliate_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_downline_affiliate_id ON mlm_commissions(downline_affiliate_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_sale_id ON mlm_commissions(sale_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_status ON mlm_commissions(status);

-- ============================================================================
-- PARTIE 10: TABLES PARAMÈTRES & INSCRIPTION
-- ============================================================================

-- Table: registration_settings
CREATE TABLE IF NOT EXISTS registration_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_registration_enabled BOOLEAN DEFAULT true,
    influencer_registration_enabled BOOLEAN DEFAULT true,
    require_email_verification BOOLEAN DEFAULT true,
    require_manual_approval BOOLEAN DEFAULT false,
    allowed_domains TEXT[],
    blocked_domains TEXT[],
    custom_fields JSONB,
    terms_url TEXT,
    privacy_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: permissions
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role TEXT NOT NULL CHECK (role IN ('admin', 'merchant', 'influencer', 'affiliate', 'moderator')),
    resource TEXT NOT NULL,
    actions TEXT[] NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role, resource)
);

-- ============================================================================
-- PARTIE 11: TABLES WHITE LABEL & SOURCES DE TRAFIC
-- ============================================================================

-- Table: white_label_settings
CREATE TABLE IF NOT EXISTS white_label_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    custom_domain TEXT,
    brand_name TEXT,
    brand_logo_url TEXT,
    brand_colors JSONB,
    custom_css TEXT,
    custom_email_templates JSONB,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(merchant_id)
);

-- Table: traffic_sources
CREATE TABLE IF NOT EXISTS traffic_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('organic', 'paid', 'social', 'email', 'referral', 'direct')),
    description TEXT,
    tracking_parameters JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: email_templates
CREATE TABLE IF NOT EXISTS email_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT,
    variables JSONB,
    category TEXT CHECK (category IN ('transactional', 'marketing', 'notification', 'system')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PARTIE 12: TRIGGERS POUR LES TIMESTAMPS (IDEMPOTENT)
-- ============================================================================

-- Fonction pour mettre à jour updated_at (si pas déjà existante)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Supprime et recrée les triggers (idempotent)
DROP TRIGGER IF EXISTS update_user_subscriptions_updated_at ON user_subscriptions;
CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_support_tickets_updated_at ON support_tickets;
CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_video_tutorials_updated_at ON video_tutorials;
CREATE TRIGGER update_video_tutorials_updated_at BEFORE UPDATE ON video_tutorials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_documentation_articles_updated_at ON documentation_articles;
CREATE TRIGGER update_documentation_articles_updated_at BEFORE UPDATE ON documentation_articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_affiliation_requests_updated_at ON affiliation_requests;
CREATE TRIGGER update_affiliation_requests_updated_at BEFORE UPDATE ON affiliation_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_company_settings_updated_at ON company_settings;
CREATE TRIGGER update_company_settings_updated_at BEFORE UPDATE ON company_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_payment_gateways_updated_at ON payment_gateways;
CREATE TRIGGER update_payment_gateways_updated_at BEFORE UPDATE ON payment_gateways
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_invoices_updated_at ON invoices;
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_affiliate_settings_updated_at ON affiliate_settings;
CREATE TRIGGER update_affiliate_settings_updated_at BEFORE UPDATE ON affiliate_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_mlm_settings_updated_at ON mlm_settings;
CREATE TRIGGER update_mlm_settings_updated_at BEFORE UPDATE ON mlm_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_mlm_commissions_updated_at ON mlm_commissions;
CREATE TRIGGER update_mlm_commissions_updated_at BEFORE UPDATE ON mlm_commissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_registration_settings_updated_at ON registration_settings;
CREATE TRIGGER update_registration_settings_updated_at BEFORE UPDATE ON registration_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_permissions_updated_at ON permissions;
CREATE TRIGGER update_permissions_updated_at BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_white_label_settings_updated_at ON white_label_settings;
CREATE TRIGGER update_white_label_settings_updated_at BEFORE UPDATE ON white_label_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_traffic_sources_updated_at ON traffic_sources;
CREATE TRIGGER update_traffic_sources_updated_at BEFORE UPDATE ON traffic_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_email_templates_updated_at ON email_templates;
CREATE TRIGGER update_email_templates_updated_at BEFORE UPDATE ON email_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PARTIE 13: PERMISSIONS PAR DÉFAUT (IDEMPOTENT)
-- ============================================================================

-- Insère uniquement si la permission n'existe pas déjà
INSERT INTO permissions (role, resource, actions, description)
VALUES 
    ('admin', 'users', ARRAY['create', 'read', 'update', 'delete'], 'Gestion complète des utilisateurs'),
    ('admin', 'merchants', ARRAY['create', 'read', 'update', 'delete'], 'Gestion complète des marchands'),
    ('admin', 'influencers', ARRAY['create', 'read', 'update', 'delete'], 'Gestion complète des influenceurs'),
    ('admin', 'products', ARRAY['create', 'read', 'update', 'delete'], 'Gestion complète des produits'),
    ('admin', 'sales', ARRAY['read', 'update', 'delete'], 'Gestion des ventes'),
    ('admin', 'commissions', ARRAY['read', 'update', 'approve', 'delete'], 'Gestion des commissions'),
    ('admin', 'settings', ARRAY['read', 'update'], 'Accès aux paramètres système'),
    ('admin', 'reports', ARRAY['read', 'export'], 'Accès à tous les rapports'),
    
    ('merchant', 'products', ARRAY['create', 'read', 'update', 'delete'], 'Gestion de ses propres produits'),
    ('merchant', 'sales', ARRAY['read'], 'Lecture de ses propres ventes'),
    ('merchant', 'commissions', ARRAY['read'], 'Lecture des commissions liées à ses produits'),
    ('merchant', 'campaigns', ARRAY['create', 'read', 'update', 'delete'], 'Gestion de ses campagnes'),
    ('merchant', 'influencers', ARRAY['read'], 'Lecture des influenceurs'),
    ('merchant', 'reports', ARRAY['read'], 'Rapports pour ses produits'),
    
    ('influencer', 'trackable_links', ARRAY['create', 'read', 'update', 'delete'], 'Gestion de ses liens'),
    ('influencer', 'sales', ARRAY['read'], 'Lecture de ses ventes'),
    ('influencer', 'commissions', ARRAY['read'], 'Lecture de ses commissions'),
    ('influencer', 'products', ARRAY['read'], 'Lecture des produits disponibles'),
    ('influencer', 'campaigns', ARRAY['read'], 'Lecture des campagnes disponibles'),
    ('influencer', 'reports', ARRAY['read'], 'Ses propres statistiques'),
    
    ('affiliate', 'trackable_links', ARRAY['create', 'read', 'update', 'delete'], 'Gestion de ses liens affiliés'),
    ('affiliate', 'sales', ARRAY['read'], 'Lecture de ses ventes'),
    ('affiliate', 'commissions', ARRAY['read'], 'Lecture de ses commissions'),
    ('affiliate', 'products', ARRAY['read'], 'Lecture des produits disponibles')
ON CONFLICT (role, resource) DO NOTHING;

-- ============================================================================
-- PARTIE 14: TEMPLATES D'EMAILS PAR DÉFAUT (IDEMPOTENT)
-- ============================================================================

-- Insère uniquement si le template n'existe pas déjà
INSERT INTO email_templates (template_key, name, subject, body_html, body_text, variables, category)
VALUES 
    (
        'welcome_email',
        'Email de bienvenue',
        'Bienvenue sur ShareYourSales - {{user_name}}!',
        '<html><body><h1>Bienvenue {{user_name}}!</h1><p>Merci de vous être inscrit sur ShareYourSales.</p></body></html>',
        'Bienvenue {{user_name}}! Merci de vous être inscrit sur ShareYourSales.',
        '["user_name", "user_email", "platform_name"]'::jsonb,
        'transactional'
    ),
    (
        'commission_earned',
        'Commission gagnée',
        'Nouvelle commission de {{commission_amount}} €',
        '<html><body><h2>Félicitations!</h2><p>Vous avez gagné une commission de {{commission_amount}} €.</p></body></html>',
        'Félicitations! Vous avez gagné une commission de {{commission_amount}} €.',
        '["commission_amount", "product_name", "sale_date"]'::jsonb,
        'notification'
    ),
    (
        'payout_processed',
        'Paiement traité',
        'Votre paiement de {{payout_amount}} € a été traité',
        '<html><body><h2>Paiement confirmé</h2><p>Votre paiement de {{payout_amount}} € a été envoyé.</p></body></html>',
        'Paiement confirmé. Votre paiement de {{payout_amount}} € a été envoyé.',
        '["payout_amount", "payout_date", "payment_method"]'::jsonb,
        'transactional'
    )
ON CONFLICT (template_key) DO NOTHING;

-- ============================================================================
-- PARTIE 15: VÉRIFICATION FINALE
-- ============================================================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration terminée avec succès!';
    RAISE NOTICE 'Nombre total de tables: %', table_count;
    RAISE NOTICE '========================================';
END $$;

-- Liste finale de toutes les tables
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE columns.table_name = tables.table_name) as column_count
FROM information_schema.tables
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
ORDER BY table_name;
