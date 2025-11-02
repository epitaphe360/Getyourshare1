-- ============================================
-- CRÉATION AUTOMATIQUE DES PROFILS TEST
-- ============================================
-- Ce script récupère automatiquement les UUIDs depuis auth.users
-- et crée les profils merchants/influencers correspondants

-- PRÉREQUIS: Vous devez avoir créé les 7 utilisateurs via Supabase Auth UI:
-- 1. merchant_free@test.com
-- 2. merchant_starter@test.com  
-- 3. merchant_pro@test.com
-- 4. merchant_enterprise@test.com
-- 5. influencer_starter@test.com
-- 6. influencer_pro@test.com
-- 7. influencer_elite@test.com

-- ============================================
-- INSERTION DES MERCHANTS (récupération auto des UUIDs)
-- ============================================

-- Merchant 1: Plan FREE
INSERT INTO merchants (user_id, company_name, industry, subscription_plan, subscription_status, commission_rate, monthly_fee, total_sales, total_commission_paid)
SELECT 
    id,
    'Test Merchant Free',
    'E-commerce',
    'free',
    'active',
    5.00,
    0.00,
    0.00,
    0.00
FROM auth.users
WHERE email = 'merchant_free@test.com';

-- Merchant 2: Plan STARTER
INSERT INTO merchants (user_id, company_name, industry, subscription_plan, subscription_status, commission_rate, monthly_fee, total_sales, total_commission_paid)
SELECT 
    id,
    'Test Merchant Starter',
    'Mode & Vêtements',
    'starter',
    'active',
    4.00,
    299.00,
    15000.00,
    600.00
FROM auth.users
WHERE email = 'merchant_starter@test.com';

-- Merchant 3: Plan PRO
INSERT INTO merchants (user_id, company_name, industry, subscription_plan, subscription_status, commission_rate, monthly_fee, total_sales, total_commission_paid)
SELECT 
    id,
    'Test Merchant Pro',
    'Cosmétiques & Beauté',
    'pro',
    'active',
    3.00,
    799.00,
    45000.00,
    1350.00
FROM auth.users
WHERE email = 'merchant_pro@test.com';

-- Merchant 4: Plan ENTERPRISE
INSERT INTO merchants (user_id, company_name, industry, subscription_plan, subscription_status, commission_rate, monthly_fee, total_sales, total_commission_paid)
SELECT 
    id,
    'Test Merchant Enterprise',
    'Électronique & Tech',
    'enterprise',
    'active',
    2.00,
    1999.00,
    150000.00,
    3000.00
FROM auth.users
WHERE email = 'merchant_enterprise@test.com';

-- ============================================
-- INSERTION DES INFLUENCERS (récupération auto des UUIDs)
-- ============================================

-- Influencer 1: Plan STARTER
INSERT INTO influencers (user_id, username, full_name, bio, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, total_clicks, total_sales, total_earnings, balance, social_links)
SELECT 
    id,
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
FROM auth.users
WHERE email = 'influencer_starter@test.com';

-- Influencer 2: Plan PRO
INSERT INTO influencers (user_id, username, full_name, bio, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, total_clicks, total_sales, total_earnings, balance, social_links)
SELECT 
    id,
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
FROM auth.users
WHERE email = 'influencer_pro@test.com';

-- Influencer 3: Plan PRO ELITE
INSERT INTO influencers (user_id, username, full_name, bio, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, total_clicks, total_sales, total_earnings, balance, social_links)
SELECT 
    id,
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
FROM auth.users
WHERE email = 'influencer_elite@test.com';

-- ============================================
-- VÉRIFICATION FINALE
-- ============================================
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
