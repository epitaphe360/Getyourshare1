-- ============================================
-- TABLE PLATFORM_SETTINGS
-- Paramètres globaux de la plateforme (Admin uniquement)
-- ============================================

-- Supprimer la table si elle existe déjà
DROP TABLE IF EXISTS platform_settings CASCADE;

-- Créer la table
CREATE TABLE platform_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Paramètres de paiement
    min_payout_amount DECIMAL(10, 2) NOT NULL DEFAULT 50.00,
    payout_frequency VARCHAR(20) NOT NULL DEFAULT 'weekly',
    payout_day VARCHAR(20) DEFAULT 'friday',
    validation_delay_days INTEGER NOT NULL DEFAULT 14,
    platform_commission_rate DECIMAL(5, 2) NOT NULL DEFAULT 5.00,
    auto_payout_enabled BOOLEAN NOT NULL DEFAULT true,
    
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Contraintes
    CONSTRAINT check_min_payout_amount CHECK (min_payout_amount >= 10 AND min_payout_amount <= 1000),
    CONSTRAINT check_commission_rate CHECK (platform_commission_rate >= 0 AND platform_commission_rate <= 50),
    CONSTRAINT check_validation_delay CHECK (validation_delay_days >= 0 AND validation_delay_days <= 90),
    CONSTRAINT check_payout_frequency CHECK (payout_frequency IN ('daily', 'weekly', 'biweekly', 'monthly')),
    CONSTRAINT check_payout_day CHECK (payout_day IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'))
);

-- Index pour recherche rapide
CREATE INDEX idx_platform_settings_updated_at ON platform_settings(updated_at DESC);

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_platform_settings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour updated_at
DROP TRIGGER IF EXISTS trigger_update_platform_settings_timestamp ON platform_settings;
CREATE TRIGGER trigger_update_platform_settings_timestamp
    BEFORE UPDATE ON platform_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_platform_settings_timestamp();

-- ============================================
-- DONNÉES PAR DÉFAUT
-- ============================================

-- Insérer les paramètres par défaut (un seul enregistrement)
INSERT INTO platform_settings (
    min_payout_amount,
    payout_frequency,
    payout_day,
    validation_delay_days,
    platform_commission_rate,
    auto_payout_enabled
) VALUES (
    50.00,        -- Montant minimum de retrait recommandé
    'weekly',     -- Paiements hebdomadaires (standard industrie)
    'friday',     -- Le vendredi (fin de semaine)
    14,           -- 14 jours de délai de rétractation (légal FR)
    5.00,         -- 5% de commission plateforme
    true          -- Paiements automatiques activés
) ON CONFLICT DO NOTHING;

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE platform_settings IS 'Paramètres globaux de la plateforme (modifiables uniquement par les admins)';
COMMENT ON COLUMN platform_settings.min_payout_amount IS 'Montant minimum de retrait pour tous les influenceurs (€)';
COMMENT ON COLUMN platform_settings.payout_frequency IS 'Fréquence de traitement des paiements (daily/weekly/biweekly/monthly)';
COMMENT ON COLUMN platform_settings.payout_day IS 'Jour de la semaine pour les paiements hebdomadaires';
COMMENT ON COLUMN platform_settings.validation_delay_days IS 'Délai avant validation des ventes (délai de rétractation)';
COMMENT ON COLUMN platform_settings.platform_commission_rate IS 'Taux de commission prélevé par la plateforme (%)';
COMMENT ON COLUMN platform_settings.auto_payout_enabled IS 'Activer les paiements automatiques';
COMMENT ON COLUMN platform_settings.updated_by IS 'ID de l''admin qui a effectué la dernière modification';

-- ============================================
-- POLITIQUE DE SÉCURITÉ (RLS)
-- ============================================

-- Activer Row Level Security
ALTER TABLE platform_settings ENABLE ROW LEVEL SECURITY;

-- Politique: Seuls les admins peuvent lire
CREATE POLICY "Admins can read platform settings" ON platform_settings
    FOR SELECT
    USING (true);  -- Temporairement permissif, à sécuriser via backend

-- Politique: Seuls les admins peuvent modifier
CREATE POLICY "Admins can update platform settings" ON platform_settings
    FOR UPDATE
    USING (true);  -- Temporairement permissif, à sécuriser via backend

-- ============================================
-- VÉRIFICATION
-- ============================================

-- Afficher les paramètres créés
SELECT 
    'Platform Settings créés avec succès' as status,
    min_payout_amount,
    payout_frequency,
    payout_day,
    validation_delay_days,
    platform_commission_rate,
    auto_payout_enabled
FROM platform_settings;

-- Vérifier les contraintes
SELECT 
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'platform_settings';
