-- ============================================
-- DIAGNOSTIC TRACKABLE_LINKS
-- Exécutez ce script AVANT la migration pour voir l'état actuel
-- ============================================

-- 1. Vérifier si trackable_links est une table ou une vue
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'trackable_links'
            AND table_type = 'BASE TABLE'
        ) THEN 'TABLE'
        WHEN EXISTS (
            SELECT 1 FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name = 'trackable_links'
        ) THEN 'VIEW'
        ELSE 'N_EXISTE_PAS'
    END as trackable_links_type;

-- 2. Lister toutes les colonnes de trackable_links (table ou vue)
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'trackable_links'
ORDER BY ordinal_position;

-- 3. Vérifier si les colonnes nécessaires existent déjà
SELECT 
    'influencer_message' as colonne,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'trackable_links' AND column_name = 'influencer_message'
    ) THEN 'EXISTE' ELSE 'MANQUANTE' END as status
UNION ALL
SELECT 
    'merchant_response',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'trackable_links' AND column_name = 'merchant_response'
    ) THEN 'EXISTE' ELSE 'MANQUANTE' END
UNION ALL
SELECT 
    'reviewed_at',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'trackable_links' AND column_name = 'reviewed_at'
    ) THEN 'EXISTE' ELSE 'MANQUANTE' END
UNION ALL
SELECT 
    'reviewed_by',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'trackable_links' AND column_name = 'reviewed_by'
    ) THEN 'EXISTE' ELSE 'MANQUANTE' END
UNION ALL
SELECT 
    'status',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'trackable_links' AND column_name = 'status'
    ) THEN 'EXISTE' ELSE 'MANQUANTE' END;

-- 4. Lister toutes les vues qui dépendent de trackable_links
SELECT 
    view_name,
    view_definition
FROM information_schema.views
WHERE table_schema = 'public'
AND view_definition ILIKE '%trackable_links%'
ORDER BY view_name;

-- 5. Vérifier si les fonctions nécessaires existent
SELECT 
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('approve_affiliation_request', 'reject_affiliation_request');

-- 6. Compter les enregistrements dans trackable_links
SELECT 
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE status = 'pending_approval') as pending,
    COUNT(*) FILTER (WHERE status = 'active') as active,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected
FROM trackable_links;
