-- ============================================================================
-- SCRIPT DE VÉRIFICATION - TABLES EXISTANTES DANS SUPABASE
-- ============================================================================
-- Exécutez ce script dans Supabase pour voir quelles tables existent déjà
-- ============================================================================

SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
ORDER BY table_name;
