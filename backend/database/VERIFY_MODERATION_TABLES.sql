-- ============================================
-- SCRIPT DE VÉRIFICATION - TABLES DE MODÉRATION
-- Exécutez ce script pour vérifier que tout est bien créé
-- ============================================

-- 1. Vérifier que les tables existent
SELECT 
    'moderation_queue' as table_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name = 'moderation_queue'
UNION ALL
SELECT 
    'moderation_stats' as table_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name = 'moderation_stats'
UNION ALL
SELECT 
    'moderation_history' as table_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name = 'moderation_history';

-- 2. Vérifier que les vues existent
SELECT 
    table_name as view_name,
    view_definition
FROM information_schema.views 
WHERE table_name IN ('v_pending_moderation', 'v_daily_moderation_stats');

-- 3. Vérifier que les fonctions existent
SELECT 
    routine_name as function_name,
    routine_type
FROM information_schema.routines 
WHERE routine_name IN (
    'submit_product_for_moderation',
    'approve_moderation',
    'reject_moderation',
    'update_moderation_timestamp'
);

-- 4. Vérifier les index
SELECT 
    indexname,
    tablename
FROM pg_indexes 
WHERE tablename IN ('moderation_queue', 'moderation_stats', 'moderation_history')
ORDER BY tablename, indexname;

-- 5. Tester l'insertion (optionnel - décommentez pour tester)
/*
DO $$
DECLARE
    v_test_moderation_id UUID;
    v_test_merchant_id UUID;
    v_test_user_id UUID;
BEGIN
    -- Récupérer un merchant et user de test (ou créer des UUIDs fictifs)
    SELECT id INTO v_test_merchant_id FROM merchants LIMIT 1;
    SELECT id INTO v_test_user_id FROM users WHERE role = 'merchant' LIMIT 1;
    
    -- Tester la fonction submit_product_for_moderation
    v_test_moderation_id := submit_product_for_moderation(
        gen_random_uuid(), -- product_id fictif
        v_test_merchant_id,
        v_test_user_id,
        'Produit Test Modération',
        'Description de test pour vérifier le système de modération',
        'Électronique',
        99.99,
        '["https://example.com/image.jpg"]'::jsonb,
        '{
            "approved": false,
            "confidence": 0.75,
            "risk_level": "medium",
            "flags": ["test"],
            "reason": "Test du système de modération",
            "recommendation": "Manual review",
            "moderation_method": "ai"
        }'::jsonb
    );
    
    RAISE NOTICE 'Modération de test créée avec ID: %', v_test_moderation_id;
    
    -- Vérifier l'entrée
    IF EXISTS (SELECT 1 FROM moderation_queue WHERE id = v_test_moderation_id) THEN
        RAISE NOTICE '✅ Insertion réussie dans moderation_queue';
    END IF;
    
    IF EXISTS (SELECT 1 FROM moderation_history WHERE moderation_id = v_test_moderation_id) THEN
        RAISE NOTICE '✅ Log créé dans moderation_history';
    END IF;
    
    -- Nettoyer
    DELETE FROM moderation_queue WHERE id = v_test_moderation_id;
    RAISE NOTICE '✅ Test nettoyé';
    
END $$;
*/

-- 6. Afficher la structure complète de moderation_queue
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'moderation_queue'
ORDER BY ordinal_position;

-- ============================================
-- RÉSULTATS ATTENDUS
-- ============================================

/*
✅ Si tout est OK, vous devriez voir:

1. Tables:
   - moderation_queue: ~20 colonnes
   - moderation_stats: ~15 colonnes
   - moderation_history: ~8 colonnes

2. Vues:
   - v_pending_moderation
   - v_daily_moderation_stats

3. Fonctions:
   - submit_product_for_moderation
   - approve_moderation
   - reject_moderation
   - update_moderation_timestamp

4. Index (au moins 8):
   - idx_moderation_status
   - idx_moderation_merchant
   - idx_moderation_created
   - idx_moderation_priority
   - idx_moderation_risk
   - idx_moderation_stats_date
   - idx_moderation_history_mod
   - idx_moderation_history_date
*/
