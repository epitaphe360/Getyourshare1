-- ============================================
-- VÉRIFICATION ULTRA SIMPLE
-- ============================================
-- Exécutez SEULEMENT CETTE requête dans Supabase SQL Editor

SELECT 
    schemaname,
    tablename
FROM pg_tables
WHERE schemaname IN ('public', 'auth')
ORDER BY schemaname, tablename;

-- Cette requête va lister TOUTES les tables qui existent vraiment dans votre base
