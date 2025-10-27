-- ============================================================================
-- MIGRATION INTELLIGENTE - UNIQUEMENT LES TABLES MANQUANTES
-- ============================================================================
-- Basé sur l'analyse de votre base de données Supabase
-- Tables existantes: 36
-- Tables à créer: SEULEMENT celles qui manquent
-- Date: 26 Janvier 2025
-- ============================================================================

-- ============================================================================
-- TABLES EXISTANTES (36) - NE PAS RECRÉER:
-- ============================================================================
-- ✓ affiliate_settings
-- ✓ affiliation_requests
-- ✓ affiliation_request_history
-- ✓ ai_analytics
-- ✓ campaigns
-- ✓ categories
-- ✓ click_logs
-- ✓ click_tracking
-- ✓ commissions
-- ✓ conversations
-- ✓ documentation_articles
-- ✓ engagement_metrics
-- ✓ influencers
-- ✓ merchants
-- ✓ messages
-- ✓ mlm_settings
-- ✓ notifications
-- ✓ payments
-- ✓ payouts
-- ✓ permissions_settings
-- ✓ products
-- ✓ registration_settings
-- ✓ reviews
-- ✓ sales
-- ✓ smtp_settings
-- ✓ subscriptions
-- ✓ support_tickets
-- ✓ ticket_messages
-- ✓ trackable_links
-- ✓ user_sessions
-- ✓ user_subscriptions
-- ✓ users
-- ✓ video_progress
-- ✓ video_tutorials
-- ✓ webhook_logs
-- ✓ whitelabel_settings

-- ============================================================================
-- TABLES MANQUANTES (8) - À CRÉER:
-- ============================================================================
-- ✗ company_settings
-- ✗ payment_gateways
-- ✗ invoices
-- ✗ activity_log
-- ✗ mlm_commissions
-- ✗ permissions (différente de permissions_settings)
-- ✗ traffic_sources
-- ✗ email_templates

-- ============================================================================
-- PARTIE 1: PARAMÈTRES ENTREPRISE
-- ============================================================================

CREATE TABLE IF NOT EXISTS company_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT NOT NULL,
    company_logo_url TEXT,
    company_email TEXT,
    company_phone TEXT,
    company_address TEXT,
    tax_id TEXT,
    currency TEXT DEFAULT 'MAD',
    timezone TEXT DEFAULT 'Africa/Casablanca',
    language TEXT DEFAULT 'fr',
    commission_model JSONB,
    default_commission_rate DECIMAL(5,2) DEFAULT 10.00,
    min_payout_amount DECIMAL(10,2) DEFAULT 50.00,
    payout_schedule TEXT CHECK (payout_schedule IN ('weekly', 'biweekly', 'monthly')) DEFAULT 'monthly',
    features_enabled JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_company_settings_created ON company_settings(created_at);

-- ============================================================================
-- PARTIE 2: GATEWAYS DE PAIEMENT (MAROC)
-- ============================================================================

CREATE TABLE IF NOT EXISTS payment_gateways (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    gateway_name TEXT NOT NULL CHECK (gateway_name IN ('cmi', 'payzen', 'sg_maroc', 'stripe', 'paypal')),
    api_key TEXT,
    secret_key TEXT,
    merchant_id_gateway TEXT,
    is_active BOOLEAN DEFAULT false,
    is_test_mode BOOLEAN DEFAULT true,
    configuration JSONB DEFAULT '{}',
    webhook_url TEXT,
    supported_currencies TEXT[] DEFAULT ARRAY['MAD', 'EUR', 'USD'],
    fees JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(merchant_id, gateway_name)
);

CREATE INDEX IF NOT EXISTS idx_payment_gateways_merchant ON payment_gateways(merchant_id);
CREATE INDEX IF NOT EXISTS idx_payment_gateways_active ON payment_gateways(is_active);
CREATE INDEX IF NOT EXISTS idx_payment_gateways_gateway_name ON payment_gateways(gateway_name);

-- ============================================================================
-- PARTIE 3: FACTURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number TEXT UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE SET NULL,
    payment_id UUID REFERENCES payments(id) ON DELETE SET NULL,
    amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'MAD',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('draft', 'pending', 'sent', 'paid', 'overdue', 'cancelled', 'refunded')),
    due_date TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    invoice_items JSONB DEFAULT '[]',
    billing_address JSONB,
    notes TEXT,
    pdf_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_merchant_id ON invoices(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at DESC);

-- ============================================================================
-- PARTIE 4: JOURNAL D'ACTIVITÉ
-- ============================================================================

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
CREATE INDEX IF NOT EXISTS idx_activity_log_action ON activity_log(action);
CREATE INDEX IF NOT EXISTS idx_activity_log_entity ON activity_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at DESC);

-- ============================================================================
-- PARTIE 5: COMMISSIONS MLM
-- ============================================================================

CREATE TABLE IF NOT EXISTS mlm_commissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    affiliate_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    downline_affiliate_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    level INTEGER NOT NULL CHECK (level >= 1 AND level <= 10),
    commission_amount DECIMAL(10,2) NOT NULL,
    commission_percentage DECIMAL(5,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')),
    paid_at TIMESTAMP WITH TIME ZONE,
    payout_id UUID REFERENCES payouts(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mlm_commissions_affiliate_id ON mlm_commissions(affiliate_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_downline ON mlm_commissions(downline_affiliate_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_sale_id ON mlm_commissions(sale_id);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_status ON mlm_commissions(status);
CREATE INDEX IF NOT EXISTS idx_mlm_commissions_level ON mlm_commissions(level);

-- ============================================================================
-- PARTIE 6: PERMISSIONS (GRANULAIRES)
-- ============================================================================

CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role TEXT NOT NULL CHECK (role IN ('admin', 'merchant', 'influencer', 'affiliate', 'moderator', 'support')),
    resource TEXT NOT NULL,
    actions TEXT[] NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role, resource)
);

CREATE INDEX IF NOT EXISTS idx_permissions_role ON permissions(role);
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);
CREATE INDEX IF NOT EXISTS idx_permissions_active ON permissions(is_active);

-- ============================================================================
-- PARTIE 7: SOURCES DE TRAFIC
-- ============================================================================

CREATE TABLE IF NOT EXISTS traffic_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('organic', 'paid', 'social', 'email', 'referral', 'direct', 'affiliate')),
    description TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    total_clicks INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    tracking_parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_traffic_sources_source_type ON traffic_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_traffic_sources_active ON traffic_sources(is_active);
CREATE INDEX IF NOT EXISTS idx_traffic_sources_utm ON traffic_sources(utm_source, utm_medium, utm_campaign);

-- ============================================================================
-- PARTIE 8: TEMPLATES D'EMAILS
-- ============================================================================

CREATE TABLE IF NOT EXISTS email_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT,
    variables JSONB DEFAULT '[]',
    category TEXT CHECK (category IN ('transactional', 'marketing', 'notification', 'system', 'welcome')),
    language TEXT DEFAULT 'fr',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_templates_template_key ON email_templates(template_key);
CREATE INDEX IF NOT EXISTS idx_email_templates_category ON email_templates(category);
CREATE INDEX IF NOT EXISTS idx_email_templates_active ON email_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_email_templates_language ON email_templates(language);

-- ============================================================================
-- PARTIE 9: FONCTION POUR TRIGGERS (SI PAS DÉJÀ EXISTANTE)
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PARTIE 10: TRIGGERS POUR LES NOUVELLES TABLES
-- ============================================================================

DROP TRIGGER IF EXISTS update_company_settings_updated_at ON company_settings;
CREATE TRIGGER update_company_settings_updated_at 
    BEFORE UPDATE ON company_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_payment_gateways_updated_at ON payment_gateways;
CREATE TRIGGER update_payment_gateways_updated_at 
    BEFORE UPDATE ON payment_gateways
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_invoices_updated_at ON invoices;
CREATE TRIGGER update_invoices_updated_at 
    BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_mlm_commissions_updated_at ON mlm_commissions;
CREATE TRIGGER update_mlm_commissions_updated_at 
    BEFORE UPDATE ON mlm_commissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_permissions_updated_at ON permissions;
CREATE TRIGGER update_permissions_updated_at 
    BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_traffic_sources_updated_at ON traffic_sources;
CREATE TRIGGER update_traffic_sources_updated_at 
    BEFORE UPDATE ON traffic_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_email_templates_updated_at ON email_templates;
CREATE TRIGGER update_email_templates_updated_at 
    BEFORE UPDATE ON email_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PARTIE 11: PERMISSIONS PAR DÉFAUT
-- ============================================================================

INSERT INTO permissions (role, resource, actions, description) VALUES
    -- ADMIN
    ('admin', 'users', ARRAY['create', 'read', 'update', 'delete'], 'Gestion complète des utilisateurs'),
    ('admin', 'merchants', ARRAY['create', 'read', 'update', 'delete'], 'Gestion complète des marchands'),
    ('admin', 'influencers', ARRAY['create', 'read', 'update', 'delete'], 'Gestion complète des influenceurs'),
    ('admin', 'products', ARRAY['create', 'read', 'update', 'delete'], 'Gestion complète des produits'),
    ('admin', 'sales', ARRAY['read', 'update', 'delete'], 'Gestion des ventes'),
    ('admin', 'commissions', ARRAY['read', 'update', 'approve', 'delete'], 'Gestion des commissions'),
    ('admin', 'settings', ARRAY['read', 'update'], 'Accès aux paramètres système'),
    ('admin', 'reports', ARRAY['read', 'export'], 'Accès à tous les rapports'),
    ('admin', 'payments', ARRAY['read', 'update', 'approve'], 'Gestion des paiements'),
    ('admin', 'invoices', ARRAY['create', 'read', 'update', 'delete'], 'Gestion des factures'),
    
    -- MERCHANT
    ('merchant', 'products', ARRAY['create', 'read', 'update', 'delete'], 'Gestion de ses propres produits'),
    ('merchant', 'sales', ARRAY['read'], 'Lecture de ses propres ventes'),
    ('merchant', 'commissions', ARRAY['read'], 'Lecture des commissions liées à ses produits'),
    ('merchant', 'campaigns', ARRAY['create', 'read', 'update', 'delete'], 'Gestion de ses campagnes'),
    ('merchant', 'influencers', ARRAY['read'], 'Lecture des influenceurs'),
    ('merchant', 'reports', ARRAY['read'], 'Rapports pour ses produits'),
    ('merchant', 'payment_gateways', ARRAY['create', 'read', 'update'], 'Configuration des gateways'),
    ('merchant', 'invoices', ARRAY['read'], 'Consultation de ses factures'),
    
    -- INFLUENCER
    ('influencer', 'trackable_links', ARRAY['create', 'read', 'update', 'delete'], 'Gestion de ses liens'),
    ('influencer', 'sales', ARRAY['read'], 'Lecture de ses ventes'),
    ('influencer', 'commissions', ARRAY['read'], 'Lecture de ses commissions'),
    ('influencer', 'products', ARRAY['read'], 'Lecture des produits disponibles'),
    ('influencer', 'campaigns', ARRAY['read'], 'Lecture des campagnes disponibles'),
    ('influencer', 'reports', ARRAY['read'], 'Ses propres statistiques'),
    ('influencer', 'payouts', ARRAY['read', 'request'], 'Demande de paiements'),
    
    -- AFFILIATE
    ('affiliate', 'trackable_links', ARRAY['create', 'read', 'update', 'delete'], 'Gestion de ses liens affiliés'),
    ('affiliate', 'sales', ARRAY['read'], 'Lecture de ses ventes'),
    ('affiliate', 'commissions', ARRAY['read'], 'Lecture de ses commissions'),
    ('affiliate', 'products', ARRAY['read'], 'Lecture des produits disponibles'),
    ('affiliate', 'payouts', ARRAY['read', 'request'], 'Demande de paiements')
ON CONFLICT (role, resource) DO NOTHING;

-- ============================================================================
-- PARTIE 12: TEMPLATES D'EMAILS PAR DÉFAUT
-- ============================================================================

INSERT INTO email_templates (template_key, name, subject, body_html, body_text, variables, category, language) VALUES
    (
        'welcome_user',
        'Email de bienvenue utilisateur',
        'Bienvenue sur ShareYourSales - {{user_name}}!',
        '<html><body><h1>Bienvenue {{user_name}}!</h1><p>Merci de vous être inscrit sur ShareYourSales.</p><p>Votre compte est maintenant actif.</p></body></html>',
        'Bienvenue {{user_name}}! Merci de vous être inscrit sur ShareYourSales. Votre compte est maintenant actif.',
        '["user_name", "user_email", "platform_name"]'::jsonb,
        'welcome',
        'fr'
    ),
    (
        'commission_earned',
        'Notification commission gagnée',
        'Nouvelle commission de {{commission_amount}} {{currency}}',
        '<html><body><h2>Félicitations!</h2><p>Vous avez gagné une commission de <strong>{{commission_amount}} {{currency}}</strong>.</p><p>Produit: {{product_name}}</p><p>Date: {{sale_date}}</p></body></html>',
        'Félicitations! Vous avez gagné une commission de {{commission_amount}} {{currency}}. Produit: {{product_name}}. Date: {{sale_date}}.',
        '["commission_amount", "currency", "product_name", "sale_date"]'::jsonb,
        'notification',
        'fr'
    ),
    (
        'payout_processed',
        'Paiement traité',
        'Votre paiement de {{payout_amount}} {{currency}} a été traité',
        '<html><body><h2>Paiement confirmé</h2><p>Votre paiement de <strong>{{payout_amount}} {{currency}}</strong> a été envoyé.</p><p>Méthode: {{payment_method}}</p><p>Date: {{payout_date}}</p></body></html>',
        'Paiement confirmé. Votre paiement de {{payout_amount}} {{currency}} a été envoyé via {{payment_method}} le {{payout_date}}.',
        '["payout_amount", "currency", "payout_date", "payment_method"]'::jsonb,
        'transactional',
        'fr'
    ),
    (
        'invoice_generated',
        'Nouvelle facture',
        'Facture {{invoice_number}} - {{total_amount}} {{currency}}',
        '<html><body><h2>Nouvelle facture</h2><p>Facture N°: <strong>{{invoice_number}}</strong></p><p>Montant: {{total_amount}} {{currency}}</p><p>Date d''échéance: {{due_date}}</p></body></html>',
        'Nouvelle facture N° {{invoice_number}}. Montant: {{total_amount}} {{currency}}. Date d''échéance: {{due_date}}.',
        '["invoice_number", "total_amount", "currency", "due_date"]'::jsonb,
        'transactional',
        'fr'
    ),
    (
        'sale_notification',
        'Notification nouvelle vente',
        'Nouvelle vente - {{product_name}}',
        '<html><body><h2>Nouvelle vente!</h2><p>Produit: <strong>{{product_name}}</strong></p><p>Montant: {{sale_amount}} {{currency}}</p><p>Commission: {{commission_amount}} {{currency}}</p></body></html>',
        'Nouvelle vente! Produit: {{product_name}}. Montant: {{sale_amount}} {{currency}}. Commission: {{commission_amount}} {{currency}}.',
        '["product_name", "sale_amount", "commission_amount", "currency"]'::jsonb,
        'notification',
        'fr'
    )
ON CONFLICT (template_key) DO NOTHING;

-- ============================================================================
-- PARTIE 13: VÉRIFICATION FINALE
-- ============================================================================

DO $$
DECLARE
    table_count INTEGER;
    new_table_count INTEGER;
BEGIN
    -- Compter toutes les tables
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    
    -- Compter les nouvelles tables créées
    SELECT COUNT(*) INTO new_table_count
    FROM information_schema.tables
    WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name IN (
            'company_settings', 
            'payment_gateways', 
            'invoices', 
            'activity_log',
            'mlm_commissions',
            'permissions',
            'traffic_sources',
            'email_templates'
        );
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'MIGRATION TERMINÉE AVEC SUCCÈS!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables totales dans la base: %', table_count;
    RAISE NOTICE 'Nouvelles tables créées: %', new_table_count;
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'TABLES AJOUTÉES:';
    RAISE NOTICE '  1. company_settings';
    RAISE NOTICE '  2. payment_gateways';
    RAISE NOTICE '  3. invoices';
    RAISE NOTICE '  4. activity_log';
    RAISE NOTICE '  5. mlm_commissions';
    RAISE NOTICE '  6. permissions';
    RAISE NOTICE '  7. traffic_sources';
    RAISE NOTICE '  8. email_templates';
    RAISE NOTICE '========================================';
END $$;

-- Afficher les compteurs pour chaque nouvelle table
SELECT 
    'company_settings' as table_name, 
    COUNT(*) as row_count 
FROM company_settings
UNION ALL
SELECT 'payment_gateways', COUNT(*) FROM payment_gateways
UNION ALL
SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL
SELECT 'activity_log', COUNT(*) FROM activity_log
UNION ALL
SELECT 'mlm_commissions', COUNT(*) FROM mlm_commissions
UNION ALL
SELECT 'permissions', COUNT(*) FROM permissions
UNION ALL
SELECT 'traffic_sources', COUNT(*) FROM traffic_sources
UNION ALL
SELECT 'email_templates', COUNT(*) FROM email_templates;

-- ============================================================================
-- FIN DE LA MIGRATION
-- ============================================================================
-- Total: 8 nouvelles tables créées
-- Permissions: 30 entrées par défaut
-- Templates emails: 5 entrées par défaut
-- ============================================================================
