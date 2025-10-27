-- ============================================
-- MIGRATION: Ajout tables de settings
-- Date: 2025-10-23
-- Description: Tables pour tous les paramètres d'application
-- ============================================

-- Table permissions_settings
CREATE TABLE IF NOT EXISTS permissions_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    visible_screens JSONB DEFAULT '{"performance": true, "clicks": true, "impressions": false, "conversions": true, "leads": true, "references": true, "campaigns": true, "lost_orders": false}'::jsonb,
    visible_fields JSONB DEFAULT '{"conversion_amount": true, "short_link": true, "conversion_order_id": true}'::jsonb,
    authorized_actions JSONB DEFAULT '{"api_access": true, "view_personal_info": true}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table affiliate_settings
CREATE TABLE IF NOT EXISTS affiliate_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    min_withdrawal DECIMAL(10,2) DEFAULT 50.00,
    auto_approval BOOLEAN DEFAULT FALSE,
    email_verification BOOLEAN DEFAULT TRUE,
    payment_mode VARCHAR(20) CHECK (payment_mode IN ('on_demand', 'automatic')) DEFAULT 'on_demand',
    single_campaign_mode BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table registration_settings
CREATE TABLE IF NOT EXISTS registration_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    allow_affiliate_registration BOOLEAN DEFAULT TRUE,
    allow_advertiser_registration BOOLEAN DEFAULT TRUE,
    require_invitation BOOLEAN DEFAULT FALSE,
    require_2fa BOOLEAN DEFAULT FALSE,
    country_required BOOLEAN DEFAULT TRUE,
    company_name_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table mlm_settings
CREATE TABLE IF NOT EXISTS mlm_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    mlm_enabled BOOLEAN DEFAULT TRUE,
    levels JSONB DEFAULT '[
        {"level": 1, "percentage": 10, "enabled": true},
        {"level": 2, "percentage": 5, "enabled": true},
        {"level": 3, "percentage": 2.5, "enabled": true},
        {"level": 4, "percentage": 0, "enabled": false},
        {"level": 5, "percentage": 0, "enabled": false},
        {"level": 6, "percentage": 0, "enabled": false},
        {"level": 7, "percentage": 0, "enabled": false},
        {"level": 8, "percentage": 0, "enabled": false},
        {"level": 9, "percentage": 0, "enabled": false},
        {"level": 10, "percentage": 0, "enabled": false}
    ]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table whitelabel_settings
CREATE TABLE IF NOT EXISTS whitelabel_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#3b82f6',
    secondary_color VARCHAR(7) DEFAULT '#1e40af',
    accent_color VARCHAR(7) DEFAULT '#10b981',
    company_name VARCHAR(255) DEFAULT 'Share Your Sales Platform',
    custom_domain VARCHAR(255) DEFAULT 'track.votredomaine.com',
    ssl_enabled BOOLEAN DEFAULT TRUE,
    custom_email_domain VARCHAR(255) DEFAULT 'noreply@votredomaine.com',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer les index
CREATE INDEX IF NOT EXISTS idx_permissions_settings_user_id ON permissions_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_affiliate_settings_user_id ON affiliate_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_registration_settings_user_id ON registration_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_mlm_settings_user_id ON mlm_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_whitelabel_settings_user_id ON whitelabel_settings(user_id);

-- Ajouter les triggers pour updated_at (avec DROP IF EXISTS pour éviter les erreurs)
DROP TRIGGER IF EXISTS update_permissions_settings_updated_at ON permissions_settings;
CREATE TRIGGER update_permissions_settings_updated_at 
    BEFORE UPDATE ON permissions_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_affiliate_settings_updated_at ON affiliate_settings;
CREATE TRIGGER update_affiliate_settings_updated_at 
    BEFORE UPDATE ON affiliate_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_registration_settings_updated_at ON registration_settings;
CREATE TRIGGER update_registration_settings_updated_at 
    BEFORE UPDATE ON registration_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_mlm_settings_updated_at ON mlm_settings;
CREATE TRIGGER update_mlm_settings_updated_at 
    BEFORE UPDATE ON mlm_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_whitelabel_settings_updated_at ON whitelabel_settings;
CREATE TRIGGER update_whitelabel_settings_updated_at 
    BEFORE UPDATE ON whitelabel_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Vérification
SELECT 'Toutes les tables de settings créées avec succès!' as status;
