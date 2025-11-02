-- ============================================
-- ANALYSE COMPLÈTE DE LA STRUCTURE SUPABASE
-- ============================================
-- Exécutez ces requêtes dans votre Supabase SQL Editor
-- pour comprendre la structure réelle de votre base de données

-- ============================================
-- 1. VÉRIFIER LA TABLE USERS (PUBLIC SCHEMA)
-- ============================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    character_maximum_length
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'users'
ORDER BY ordinal_position;

-- ============================================
-- 2. VÉRIFIER LA TABLE AUTH.USERS (SUPABASE AUTH)
-- ============================================
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'auth' 
  AND table_name = 'users'
ORDER BY ordinal_position;

-- ============================================
-- 3. LISTER TOUTES LES TABLES DANS PUBLIC
-- ============================================
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- ============================================
-- 4. VÉRIFIER LA TABLE MERCHANTS
-- ============================================
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'merchants'
ORDER BY ordinal_position;

-- ============================================
-- 5. VÉRIFIER LA TABLE INFLUENCERS
-- ============================================
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'influencers'
ORDER BY ordinal_position;

-- ============================================
-- 6. VÉRIFIER S'IL EXISTE DES USERS DE TEST
-- ============================================
-- auth.users n'a PAS de colonne "role"
SELECT 
    id,
    email,
    created_at,
    email_confirmed_at,
    last_sign_in_at
FROM auth.users
WHERE email LIKE '%@test.com%'
LIMIT 10;

-- Alternative si public.users existe:
SELECT 
    id,
    email,
    role,
    created_at
FROM public.users
WHERE email LIKE '%@test.com%'
LIMIT 10;

-- ============================================
-- 7. VÉRIFIER LES COLONNES DE SUBSCRIPTION DANS MERCHANTS
-- ============================================
SELECT 
    user_id,
    company_name,
    subscription_plan,
    subscription_status,
    monthly_fee,
    commission_rate
FROM merchants
LIMIT 5;

-- ============================================
-- 8. VÉRIFIER LES COLONNES DE SUBSCRIPTION DANS INFLUENCERS
-- ============================================
SELECT 
    user_id,
    username,
    subscription_plan,
    subscription_status,
    monthly_fee,
    platform_fee_rate
FROM influencers
LIMIT 5;

-- ============================================
-- RÉSUMÉ DE CE QU'ON CHERCHE À COMPRENDRE:
-- ============================================
-- 1. Est-ce que la table "public.users" existe?
-- 2. Est-ce que la colonne "password_hash" existe dans users?
-- 3. Est-ce que Supabase utilise "auth.users" pour l'authentification?
-- 4. Quelle est la structure réelle des tables merchants et influencers?
-- 5. Comment sont stockés les abonnements (subscription_plan)?
