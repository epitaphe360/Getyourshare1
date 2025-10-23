-- Migration: Ajout de la table company_settings pour les paramètres d'entreprise
-- Date: 2025-10-23
-- Description: Permet aux merchants de configurer les informations de leur entreprise

-- Créer la table company_settings
CREATE TABLE IF NOT EXISTS company_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    email VARCHAR(255),
    address TEXT,
    tax_id VARCHAR(50),
    currency VARCHAR(3) DEFAULT 'MAD',
    phone VARCHAR(20),
    website VARCHAR(255),
    logo_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Un seul paramètre par utilisateur
    UNIQUE(user_id)
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_company_settings_user_id ON company_settings(user_id);

-- Commentaires
COMMENT ON TABLE company_settings IS 'Paramètres de l''entreprise pour chaque merchant';
COMMENT ON COLUMN company_settings.user_id IS 'ID de l''utilisateur (merchant)';
COMMENT ON COLUMN company_settings.name IS 'Nom de l''entreprise';
COMMENT ON COLUMN company_settings.email IS 'Email de contact de l''entreprise';
COMMENT ON COLUMN company_settings.address IS 'Adresse complète de l''entreprise';
COMMENT ON COLUMN company_settings.tax_id IS 'Numéro de TVA ou identifiant fiscal';
COMMENT ON COLUMN company_settings.currency IS 'Devise par défaut (EUR, USD, GBP, MAD)';
COMMENT ON COLUMN company_settings.phone IS 'Numéro de téléphone de l''entreprise';
COMMENT ON COLUMN company_settings.website IS 'Site web de l''entreprise';
COMMENT ON COLUMN company_settings.logo_url IS 'URL du logo de l''entreprise';
