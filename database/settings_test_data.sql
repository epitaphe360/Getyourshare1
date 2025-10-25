-- ============================================
-- Settings Test Data for ShareYourSales
-- ============================================
-- This script inserts test configuration data for all settings
-- Run this after creating the settings table
-- Date: 2025-10-23
-- ============================================

-- Company Settings
-- Used by: CompanySettings.js
INSERT INTO settings (key, value, description) VALUES
('company_name', 'ShareYourSales', 'Nom de l''entreprise'),
('company_email', 'contact@shareyoursales.com', 'Email de contact'),
('company_address', '123 Rue de la Tech, 75001 Paris, France', 'Adresse de l''entreprise'),
('company_tax_id', 'FR12345678901', 'Numéro de TVA'),
('company_currency', 'EUR', 'Devise par défaut')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;

-- Affiliate Settings
-- Used by: AffiliateSettings.js
INSERT INTO settings (key, value, description) VALUES
('affiliate_min_withdrawal', '50', 'Montant minimum pour retrait (€)'),
('affiliate_auto_approval', 'false', 'Approbation automatique des affiliés'),
('affiliate_email_verification', 'true', 'Vérification email requise'),
('affiliate_payment_mode', 'on_demand', 'Mode de paiement (on_demand/automatic)'),
('affiliate_single_campaign_mode', 'false', 'Limiter à une seule campagne'),
('affiliate_default_commission', '10', 'Commission par défaut (%)'),
('affiliate_cookie_duration', '30', 'Durée du cookie (jours)')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;

-- Registration Settings
-- Used by: RegistrationSettings.js
INSERT INTO settings (key, value, description) VALUES
('registration_allow_affiliate', 'true', 'Autoriser inscription affiliés'),
('registration_allow_advertiser', 'true', 'Autoriser inscription annonceurs'),
('registration_require_invitation', 'false', 'Invitation requise (MLM)'),
('registration_require_2fa', 'false', '2FA obligatoire'),
('registration_country_required', 'true', 'Pays requis'),
('registration_company_name_required', 'true', 'Nom entreprise requis'),
('registration_enabled', 'true', 'Inscription ouverte'),
('registration_auto_approve', 'false', 'Approbation automatique'),
('registration_allowed_roles', '["influencer","merchant"]', 'Rôles autorisés')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;

-- MLM Settings
-- Used by: MLMSettings.js
INSERT INTO settings (key, value, description) VALUES
('mlm_enabled', 'true', 'MLM activé'),
('mlm_max_levels', '10', 'Nombre de niveaux MLM maximum'),
('mlm_level_1_percentage', '10', 'Commission niveau 1 (%)'),
('mlm_level_1_enabled', 'true', 'Niveau 1 activé'),
('mlm_level_2_percentage', '5', 'Commission niveau 2 (%)'),
('mlm_level_2_enabled', 'true', 'Niveau 2 activé'),
('mlm_level_3_percentage', '2.5', 'Commission niveau 3 (%)'),
('mlm_level_3_enabled', 'true', 'Niveau 3 activé'),
('mlm_level_4_percentage', '0', 'Commission niveau 4 (%)'),
('mlm_level_4_enabled', 'false', 'Niveau 4 activé'),
('mlm_level_5_percentage', '0', 'Commission niveau 5 (%)'),
('mlm_level_5_enabled', 'false', 'Niveau 5 activé'),
('mlm_level_6_percentage', '0', 'Commission niveau 6 (%)'),
('mlm_level_6_enabled', 'false', 'Niveau 6 activé'),
('mlm_level_7_percentage', '0', 'Commission niveau 7 (%)'),
('mlm_level_7_enabled', 'false', 'Niveau 7 activé'),
('mlm_level_8_percentage', '0', 'Commission niveau 8 (%)'),
('mlm_level_8_enabled', 'false', 'Niveau 8 activé'),
('mlm_level_9_percentage', '0', 'Commission niveau 9 (%)'),
('mlm_level_9_enabled', 'false', 'Niveau 9 activé'),
('mlm_level_10_percentage', '0', 'Commission niveau 10 (%)'),
('mlm_level_10_enabled', 'false', 'Niveau 10 activé')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;

-- SMTP Settings
-- Used by: SMTP.js
INSERT INTO settings (key, value, description) VALUES
('smtp_host', 'smtp.gmail.com', 'Serveur SMTP'),
('smtp_port', '587', 'Port SMTP'),
('smtp_username', '', 'Nom d''utilisateur SMTP (vide par défaut)'),
('smtp_password', '', 'Mot de passe SMTP (vide par défaut)'),
('smtp_encryption', 'tls', 'Encryption SMTP (tls/ssl/none)'),
('smtp_from_email', 'noreply@shareyoursales.com', 'Email expéditeur'),
('smtp_from_name', 'ShareYourSales', 'Nom expéditeur')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;

-- White Label Settings
-- Used by: WhiteLabel.js
INSERT INTO settings (key, value, description) VALUES
('whitelabel_logo_url', '', 'URL du logo personnalisé'),
('whitelabel_company_name', 'ShareYourSales', 'Nom de marque'),
('whitelabel_primary_color', '#3b82f6', 'Couleur primaire (hex)'),
('whitelabel_secondary_color', '#1e40af', 'Couleur secondaire (hex)'),
('whitelabel_accent_color', '#10b981', 'Couleur accent (hex)'),
('whitelabel_custom_domain', 'track.votredomaine.com', 'Domaine personnalisé'),
('whitelabel_ssl_enabled', 'true', 'SSL/HTTPS activé'),
('whitelabel_custom_email_domain', 'noreply@votredomaine.com', 'Domaine email personnalisé')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;

-- Permissions Settings
-- Used by: Permissions.js
INSERT INTO settings (key, value, description) VALUES
('permissions_visible_screens', '{"performance":true,"clicks":true,"impressions":false,"conversions":true,"leads":true,"references":true,"campaigns":true,"lost_orders":false}', 'Écrans visibles par défaut (JSON)'),
('permissions_visible_fields', '{"conversion_amount":true,"short_link":true,"conversion_order_id":true}', 'Champs visibles par défaut (JSON)'),
('permissions_authorized_actions', '{"api_access":true,"view_personal_info":true}', 'Actions autorisées par défaut (JSON)')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;

-- ============================================
-- Verification Query
-- ============================================
-- Run this to verify all settings were inserted:
-- SELECT key, value, description FROM settings ORDER BY key;

-- Count settings by category:
-- SELECT
--   CASE
--     WHEN key LIKE 'company_%' THEN 'Company'
--     WHEN key LIKE 'affiliate_%' THEN 'Affiliate'
--     WHEN key LIKE 'registration_%' THEN 'Registration'
--     WHEN key LIKE 'mlm_%' THEN 'MLM'
--     WHEN key LIKE 'smtp_%' THEN 'SMTP'
--     WHEN key LIKE 'whitelabel_%' THEN 'White Label'
--     WHEN key LIKE 'permissions_%' THEN 'Permissions'
--     ELSE 'Other'
--   END as category,
--   COUNT(*) as count
-- FROM settings
-- GROUP BY category
-- ORDER BY category;

-- ============================================
-- Expected Results:
-- Company:       5 settings
-- Affiliate:     7 settings
-- Registration:  9 settings
-- MLM:          21 settings (1 enabled + 10 levels x 2 settings each)
-- SMTP:          7 settings
-- White Label:   8 settings
-- Permissions:   3 settings
-- TOTAL:        60 settings
-- ============================================
