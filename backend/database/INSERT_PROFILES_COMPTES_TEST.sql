-- ============================================
-- INSERTION DES PROFILS POUR LES COMPTES TEST
-- ============================================
-- IMPORTANT: Vous devez d'abord créer les 7 utilisateurs via l'interface Supabase Auth
-- puis remplacer les UUIDs ci-dessous avec les vrais UUIDs générés

-- ============================================
-- ÉTAPE 1: Créer 7 utilisateurs dans Supabase Auth Dashboard
-- ============================================
-- Allez sur: Supabase Dashboard → Authentication → Users → Add User
-- Cochez "Auto Confirm User" pour chaque compte
--
-- 1. merchant_free@test.com (password: Test123!)
-- 2. merchant_starter@test.com (password: Test123!)
-- 3. merchant_pro@test.com (password: Test123!)
-- 4. merchant_enterprise@test.com (password: Test123!)
-- 5. influencer_starter@test.com (password: Test123!)
-- 6. influencer_pro@test.com (password: Test123!)
-- 7. influencer_elite@test.com (password: Test123!)

-- ============================================
-- ÉTAPE 2: Récupérer les UUIDs des utilisateurs créés
-- ============================================
-- Exécutez cette requête pour obtenir les UUIDs:
-- SELECT id, email FROM auth.users WHERE email LIKE '%@test.com' ORDER BY email;
-- 
-- Copiez les UUIDs et remplacez-les ci-dessous

-- ============================================
-- ÉTAPE 3: Remplacer les UUIDs puis exécuter ce script
-- ============================================

-- Variables temporaires pour stocker les UUIDs (REMPLACEZ CES VALEURS!)
DO $$
DECLARE
    merchant_free_uuid UUID := 'REMPLACER_PAR_UUID_1';  -- merchant_free@test.com
    merchant_starter_uuid UUID := 'REMPLACER_PAR_UUID_2';  -- merchant_starter@test.com
    merchant_pro_uuid UUID := 'REMPLACER_PAR_UUID_3';  -- merchant_pro@test.com
    merchant_enterprise_uuid UUID := 'REMPLACER_PAR_UUID_4';  -- merchant_enterprise@test.com
    influencer_starter_uuid UUID := 'REMPLACER_PAR_UUID_5';  -- influencer_starter@test.com
    influencer_pro_uuid UUID := 'REMPLACER_PAR_UUID_6';  -- influencer_pro@test.com
    influencer_elite_uuid UUID := 'REMPLACER_PAR_UUID_7';  -- influencer_elite@test.com
BEGIN
    -- ============================================
    -- INSERTION DES MERCHANTS (4 comptes)
    -- ============================================
    
    -- Merchant 1: Plan FREE (0 MAD/mois, commission 5%)
    INSERT INTO merchants (user_id, company_name, industry, subscription_plan, subscription_status, commission_rate, monthly_fee, total_sales, total_commission_paid)
    VALUES (
        merchant_free_uuid,
        'Test Merchant Free',
        'E-commerce',
        'free',
        'active',
        5.00,
        0.00,
        0.00,
        0.00
    );
    
    -- Merchant 2: Plan STARTER (299 MAD/mois, commission 4%)
    INSERT INTO merchants (user_id, company_name, industry, subscription_plan, subscription_status, commission_rate, monthly_fee, total_sales, total_commission_paid)
    VALUES (
        merchant_starter_uuid,
        'Test Merchant Starter',
        'Mode & Vêtements',
        'starter',
        'active',
        4.00,
        299.00,
        15000.00,
        600.00
    );
    
    -- Merchant 3: Plan PRO (799 MAD/mois, commission 3%)
    INSERT INTO merchants (user_id, company_name, industry, subscription_plan, subscription_status, commission_rate, monthly_fee, total_sales, total_commission_paid)
    VALUES (
        merchant_pro_uuid,
        'Test Merchant Pro',
        'Cosmétiques & Beauté',
        'pro',
        'active',
        3.00,
        799.00,
        45000.00,
        1350.00
    );
    
    -- Merchant 4: Plan ENTERPRISE (1999 MAD/mois, commission 2%)
    INSERT INTO merchants (user_id, company_name, industry, subscription_plan, subscription_status, commission_rate, monthly_fee, total_sales, total_commission_paid)
    VALUES (
        merchant_enterprise_uuid,
        'Test Merchant Enterprise',
        'Électronique & Tech',
        'enterprise',
        'active',
        2.00,
        1999.00,
        150000.00,
        3000.00
    );
    
    -- ============================================
    -- INSERTION DES INFLUENCERS (3 comptes)
    -- ============================================
    
    -- Influencer 1: Plan STARTER (0 MAD/mois, commission 5%)
    INSERT INTO influencers (user_id, username, full_name, bio, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, total_clicks, total_sales, total_earnings, balance, social_links)
    VALUES (
        influencer_starter_uuid,
        'test_influencer_starter',
        'Test Influencer Starter',
        'Influenceur débutant - Plan Starter',
        'nano',
        5000,
        3.50,
        'starter',
        'active',
        5.00,
        0.00,
        250,
        5,
        500.00,
        500.00,
        '{"instagram": "@test_starter", "tiktok": "@test_starter"}'::jsonb
    );
    
    -- Influencer 2: Plan PRO (99 MAD/mois, commission 3%)
    INSERT INTO influencers (user_id, username, full_name, bio, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, total_clicks, total_sales, total_earnings, balance, social_links)
    VALUES (
        influencer_pro_uuid,
        'test_influencer_pro',
        'Test Influencer Pro',
        'Influenceur professionnel - Plan Pro',
        'micro',
        25000,
        5.20,
        'pro',
        'active',
        3.00,
        99.00,
        1500,
        35,
        3500.00,
        2800.00,
        '{"instagram": "@test_pro", "tiktok": "@test_pro", "youtube": "TestProChannel"}'::jsonb
    );
    
    -- Influencer 3: Plan PRO ELITE (299 MAD/mois, commission 2%)
    INSERT INTO influencers (user_id, username, full_name, bio, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, total_clicks, total_sales, total_earnings, balance, social_links)
    VALUES (
        influencer_elite_uuid,
        'test_influencer_elite',
        'Test Influencer Elite',
        'Influenceur élite - Plan Pro Premium',
        'macro',
        100000,
        6.80,
        'pro',
        'active',
        2.00,
        299.00,
        5000,
        120,
        12000.00,
        9500.00,
        '{"instagram": "@test_elite", "tiktok": "@test_elite", "youtube": "TestEliteChannel", "twitter": "@test_elite"}'::jsonb
    );
    
    RAISE NOTICE '✅ Tous les profils ont été créés avec succès!';
    RAISE NOTICE '   - 4 Merchants (free, starter, pro, enterprise)';
    RAISE NOTICE '   - 3 Influencers (starter, pro, elite)';
END $$;

-- ============================================
-- ÉTAPE 4: VÉRIFICATION DES DONNÉES INSÉRÉES
-- ============================================
-- Exécutez cette requête pour vérifier que tout est bien créé:

SELECT 
    au.email,
    COALESCE(m.company_name, i.username) as name,
    COALESCE(m.subscription_plan, i.subscription_plan) as plan,
    COALESCE(m.monthly_fee, i.monthly_fee) as monthly_fee,
    COALESCE(m.commission_rate, i.platform_fee_rate) as commission_rate,
    CASE 
        WHEN m.id IS NOT NULL THEN 'merchant'
        WHEN i.id IS NOT NULL THEN 'influencer'
    END as type
FROM auth.users au
LEFT JOIN merchants m ON au.id = m.user_id
LEFT JOIN influencers i ON au.id = i.user_id
WHERE au.email LIKE '%@test.com'
ORDER BY type, au.email;
