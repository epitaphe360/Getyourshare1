-- ============================================
-- MIGRATION: Ajout table smtp_settings
-- Date: 2025-10-23
-- Description: Configuration SMTP par utilisateur
-- ============================================

-- Créer la table smtp_settings
CREATE TABLE IF NOT EXISTS smtp_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    host VARCHAR(255) NOT NULL DEFAULT 'smtp.gmail.com',
    port INTEGER NOT NULL DEFAULT 587,
    username VARCHAR(255),
    password VARCHAR(255),
    from_email VARCHAR(255) NOT NULL DEFAULT 'noreply@shareyoursales.com',
    from_name VARCHAR(255) NOT NULL DEFAULT 'Share Your Sales',
    encryption VARCHAR(10) CHECK (encryption IN ('tls', 'ssl', 'none')) DEFAULT 'tls',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer un index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_smtp_settings_user_id ON smtp_settings(user_id);

-- Ajouter un trigger pour mettre à jour automatiquement updated_at
CREATE TRIGGER update_smtp_settings_updated_at 
    BEFORE UPDATE ON smtp_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Vérification
SELECT 'Table smtp_settings créée avec succès!' as status;
