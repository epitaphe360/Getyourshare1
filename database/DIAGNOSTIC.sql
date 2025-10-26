-- ============================================
-- SCRIPT DE DIAGNOSTIC SUPABASE
-- Copiez ce fichier dans SQL Editor et exécutez-le
-- Il va afficher TOUTES les informations nécessaires
-- ============================================

-- 1. LISTER TOUTES LES TABLES EXISTANTES
SELECT
    '📊 TABLES EXISTANTES:' as info,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. STRUCTURE DE LA TABLE USERS (si elle existe)
SELECT
    '👤 STRUCTURE TABLE users:' as info,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'users'
ORDER BY ordinal_position;

-- 3. STRUCTURE DE LA TABLE CAMPAIGNS (si elle existe)
SELECT
    '📈 STRUCTURE TABLE campaigns:' as info,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'campaigns'
ORDER BY ordinal_position;

-- 4. VÉRIFIER SI NOS NOUVELLES TABLES EXISTENT DÉJÀ
SELECT
    '🔍 NOUVELLES TABLES (existent-elles?):' as info,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'trust_scores')
        THEN '✅ trust_scores existe'
        ELSE '❌ trust_scores MANQUANTE'
    END as trust_scores,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'payouts')
        THEN '✅ payouts existe'
        ELSE '❌ payouts MANQUANTE'
    END as payouts,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'payment_accounts')
        THEN '✅ payment_accounts existe'
        ELSE '❌ payment_accounts MANQUANTE'
    END as payment_accounts,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_content_history')
        THEN '✅ ai_content_history existe'
        ELSE '❌ ai_content_history MANQUANTE'
    END as ai_content_history,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'smart_matches')
        THEN '✅ smart_matches existe'
        ELSE '❌ smart_matches MANQUANTE'
    END as smart_matches,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'achievements')
        THEN '✅ achievements existe'
        ELSE '❌ achievements MANQUANTE'
    END as achievements,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_levels')
        THEN '✅ user_levels existe'
        ELSE '❌ user_levels MANQUANTE'
    END as user_levels,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'notification_subscriptions')
        THEN '✅ notification_subscriptions existe'
        ELSE '❌ notification_subscriptions MANQUANTE'
    END as notification_subscriptions;

-- 5. LISTER TOUS LES TRIGGERS (qui peuvent causer des erreurs)
SELECT
    '⚙️  TRIGGERS EXISTANTS:' as info,
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- 6. AFFICHER UN MESSAGE FINAL
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ DIAGNOSTIC TERMINÉ !';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '📋 INSTRUCTIONS:';
    RAISE NOTICE '1. Regardez les résultats ci-dessus';
    RAISE NOTICE '2. Notez la structure de la table users (colonne id ou user_id?)';
    RAISE NOTICE '3. Notez quelles tables manquent';
    RAISE NOTICE '4. Copiez TOUS les résultats et envoyez-les moi';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
