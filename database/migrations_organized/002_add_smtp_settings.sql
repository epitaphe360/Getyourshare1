-- =============================================================================
-- Migration 002: Configuration SMTP
-- Description: Ajoute la table smtp_settings pour la configuration email
-- Date: 2025-10-27
-- =============================================================================

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

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_smtp_settings_user_id ON smtp_settings(user_id);

-- Commentaire
COMMENT ON TABLE smtp_settings IS 'Configuration SMTP pour l''envoi d''emails par utilisateur';

-- =============================================================================
-- Fin de la migration 002
-- =============================================================================
