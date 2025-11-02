-- ============================================
-- DIAGNOSTIC SIMPLE - SANS ERREURS
-- ============================================
-- Copiez-collez ces requêtes UNE PAR UNE dans Supabase SQL Editor

-- ============================================
-- ÉTAPE 1: Lister toutes vos tables
-- ============================================
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- ============================================
-- ÉTAPE 2: Vérifier la structure de auth.users
-- ============================================
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'auth' 
  AND table_name = 'users'
ORDER BY ordinal_position;

-- ============================================
-- ÉTAPE 3: Vérifier si public.users existe
-- ============================================
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'users'
ORDER BY ordinal_position;

-- ============================================
-- ÉTAPE 4: Vérifier la table merchants
-- ============================================
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'merchants'
ORDER BY ordinal_position;

-- ============================================
-- ÉTAPE 5: Vérifier la table influencers
-- ============================================
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'influencers'
ORDER BY ordinal_position;

-- ============================================
-- ÉTAPE 6: Voir un exemple de merchant (si existe)
-- ============================================
SELECT *
FROM merchants
LIMIT 1;

-- ============================================
-- ÉTAPE 7: Voir un exemple d'influencer (si existe)
-- ============================================
SELECT *
FROM influencers
LIMIT 1;

-- ============================================
-- ÉTAPE 8: Compter les users existants
-- ============================================
SELECT COUNT(*) as total_users
FROM auth.users;
