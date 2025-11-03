-- ============================================
-- TABLE: translations
-- Description: Stocke toutes les traductions avec cache intelligent
-- ============================================

CREATE TABLE IF NOT EXISTS translations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Clé de traduction (ex: 'nav_dashboard', 'error_network')
    key VARCHAR(255) NOT NULL,
    
    -- Code langue ('fr', 'en', 'ar', 'darija')
    language VARCHAR(10) NOT NULL,
    
    -- Texte traduit
    value TEXT NOT NULL,
    
    -- Contexte optionnel pour améliorer la traduction
    context TEXT,
    
    -- Source de la traduction ('manual', 'openai', 'static_import')
    source VARCHAR(50) DEFAULT 'manual',
    
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    usage_count INTEGER DEFAULT 0,
    
    -- Contrainte unique sur key + language
    UNIQUE(key, language)
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_translations_key_language ON translations(key, language);
CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(language);
CREATE INDEX IF NOT EXISTS idx_translations_last_used ON translations(last_used DESC);

-- Commentaires
COMMENT ON TABLE translations IS 'Cache de traductions avec support OpenAI pour auto-traduction';
COMMENT ON COLUMN translations.key IS 'Identifiant unique de la chaîne à traduire';
COMMENT ON COLUMN translations.language IS 'Code ISO de la langue (fr, en, ar, darija)';
COMMENT ON COLUMN translations.value IS 'Texte traduit dans la langue cible';
COMMENT ON COLUMN translations.context IS 'Contexte pour aider l''IA à mieux traduire';
COMMENT ON COLUMN translations.source IS 'Origine de la traduction (manual, openai, static_import)';
COMMENT ON COLUMN translations.last_used IS 'Dernière utilisation pour nettoyer les traductions inutilisées';
COMMENT ON COLUMN translations.usage_count IS 'Compteur d''utilisation pour statistiques';

-- Fonction pour mettre à jour automatiquement usage_count
CREATE OR REPLACE FUNCTION increment_translation_usage()
RETURNS TRIGGER AS $$
BEGIN
    NEW.usage_count = COALESCE(OLD.usage_count, 0) + 1;
    NEW.last_used = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger sur UPDATE pour compter les usages
CREATE TRIGGER trigger_translation_usage
BEFORE UPDATE ON translations
FOR EACH ROW
EXECUTE FUNCTION increment_translation_usage();

-- ============================================
-- DONNÉES INITIALES (optionnel)
-- Importer les traductions statiques existantes
-- ============================================

-- Ces données seront importées automatiquement par le backend
-- via l'endpoint POST /api/translations/import

-- ============================================
-- REQUÊTES UTILES
-- ============================================

-- Trouver les traductions manquantes pour une langue
-- SELECT DISTINCT t1.key 
-- FROM translations t1
-- WHERE t1.language = 'fr'
-- AND NOT EXISTS (
--     SELECT 1 FROM translations t2 
--     WHERE t2.key = t1.key 
--     AND t2.language = 'en'
-- );

-- Statistiques par langue
-- SELECT 
--     language,
--     COUNT(*) as total_translations,
--     SUM(usage_count) as total_usages,
--     MAX(last_used) as last_activity
-- FROM translations
-- GROUP BY language
-- ORDER BY total_translations DESC;

-- Traductions les plus utilisées
-- SELECT key, language, value, usage_count, last_used
-- FROM translations
-- WHERE language = 'fr'
-- ORDER BY usage_count DESC
-- LIMIT 20;

-- Nettoyer les traductions inutilisées depuis 6 mois
-- DELETE FROM translations
-- WHERE last_used < NOW() - INTERVAL '6 months'
-- AND source = 'openai';
