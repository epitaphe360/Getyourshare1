-- ============================================
-- SCRIPT DE CRÉATION DE COMPTES TEST - VERSION CORRIGÉE
-- ============================================
-- Ce script crée 7 comptes de test avec leurs profils
-- Password pour tous les comptes: Test123!
-- Hash bcrypt: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom

-- ============================================
-- NETTOYAGE (optionnel - commentez si vous ne voulez pas supprimer les anciens comptes)
-- ============================================
-- DELETE FROM merchants WHERE user_id IN (
--   SELECT id FROM users WHERE email LIKE '%@test.com'
-- );
-- DELETE FROM influencers WHERE user_id IN (
--   SELECT id FROM users WHERE email LIKE '%@test.com'
-- );
-- DELETE FROM users WHERE email LIKE '%@test.com';

-- ============================================
-- COMPTES ENTREPRISES (MERCHANTS)
-- ============================================

-- 1. Merchant Freemium (0 MAD/mois)
INSERT INTO users (id, email, password_hash, role, is_active, two_fa_enabled, created_at)
VALUES (
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  'merchant_free@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'merchant',
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;

INSERT INTO merchants (user_id, company_name, description, industry, category, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  'Test Merchant Free',
  'Compte test pour plan Freemium',
  'E-commerce',
  'E-commerce',
  'https://test-free.com',
  'free',
  'active',
  5.00,
  0.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status;

-- 2. Merchant Standard (299 MAD/mois)
INSERT INTO users (id, email, password_hash, role, is_active, two_fa_enabled, created_at)
VALUES (
  'a1b2c3d4-e5f6-4789-a012-3456789abcde',
  'merchant_starter@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'merchant',
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;

INSERT INTO merchants (user_id, company_name, description, industry, category, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'a1b2c3d4-e5f6-4789-a012-3456789abcde',
  'Test Merchant Starter',
  'Compte test pour plan Standard',
  'Mode & Beauté',
  'Mode et lifestyle',
  'https://test-starter.com',
  'starter',
  'active',
  4.00,
  299.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status;

-- 3. Merchant Premium (799 MAD/mois)
INSERT INTO users (id, email, password_hash, role, is_active, two_fa_enabled, created_at)
VALUES (
  'b2c3d4e5-f6a7-4890-b123-456789abcdef',
  'merchant_pro@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'merchant',
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;

INSERT INTO merchants (user_id, company_name, description, industry, category, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'b2c3d4e5-f6a7-4890-b123-456789abcdef',
  'Test Merchant Pro',
  'Compte test pour plan Premium',
  'Technologie',
  'Technologie',
  'https://test-pro.com',
  'pro',
  'active',
  3.00,
  799.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status;

-- 4. Merchant Enterprise (1999 MAD/mois)
INSERT INTO users (id, email, password_hash, role, is_active, two_fa_enabled, created_at)
VALUES (
  'c3d4e5f6-a7b8-4901-c234-56789abcdef0',
  'merchant_enterprise@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'merchant',
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;

INSERT INTO merchants (user_id, company_name, description, industry, category, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'c3d4e5f6-a7b8-4901-c234-56789abcdef0',
  'Test Merchant Enterprise',
  'Compte test pour plan Enterprise',
  'Grande Distribution',
  'E-commerce',
  'https://test-enterprise.com',
  'enterprise',
  'active',
  2.00,
  1999.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status;

-- ============================================
-- COMPTES INFLUENCEURS
-- ============================================

-- 1. Influencer Free (0 MAD/mois)
INSERT INTO users (id, email, password_hash, role, is_active, two_fa_enabled, created_at)
VALUES (
  'd4e5f6a7-b8c9-4012-d345-6789abcdef01',
  'influencer_free@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'influencer',
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;

INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'd4e5f6a7-b8c9-4012-d345-6789abcdef01',
  'test_influencer_free',
  'Test Influencer Free',
  'Influenceur test plan gratuit',
  'Lifestyle',
  'nano',
  5000,
  3.50,
  'starter',
  'active',
  5.00,
  0.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status;

-- 2. Influencer Pro (99 MAD/mois)
INSERT INTO users (id, email, password_hash, role, is_active, two_fa_enabled, created_at)
VALUES (
  'e5f6a7b8-c9d0-4123-e456-789abcdef012',
  'influencer_pro@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'influencer',
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;

INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'e5f6a7b8-c9d0-4123-e456-789abcdef012',
  'test_influencer_pro',
  'Test Influencer Pro',
  'Influenceur test plan Pro',
  'Mode & Beauté',
  'micro',
  50000,
  5.20,
  'pro',
  'active',
  3.00,
  99.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status;

-- 3. Influencer Elite (299 MAD/mois)
INSERT INTO users (id, email, password_hash, role, is_active, two_fa_enabled, created_at)
VALUES (
  'f6a7b8c9-d0e1-4234-f567-89abcdef0123',
  'influencer_elite@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'influencer',
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;

INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'f6a7b8c9-d0e1-4234-f567-89abcdef0123',
  'test_influencer_elite',
  'Test Influencer Elite',
  'Influenceur test plan Elite',
  'Tech & Innovation',
  'macro',
  500000,
  7.80,
  'pro',
  'active',
  2.00,
  299.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status;

-- ============================================
-- VÉRIFICATION
-- ============================================

-- Afficher tous les comptes créés avec leurs abonnements
SELECT 
  u.email,
  u.role,
  CASE 
    WHEN u.role = 'merchant' THEN m.subscription_plan
    WHEN u.role = 'influencer' THEN i.subscription_plan
  END as plan,
  CASE 
    WHEN u.role = 'merchant' THEN m.monthly_fee
    WHEN u.role = 'influencer' THEN i.monthly_fee
  END as monthly_fee,
  COALESCE(m.company_name, i.full_name) as profile_name,
  u.is_active
FROM users u
LEFT JOIN merchants m ON u.id = m.user_id
LEFT JOIN influencers i ON u.id = i.user_id
WHERE u.email LIKE '%@test.com'
ORDER BY u.role, 
  CASE 
    WHEN u.role = 'merchant' THEN m.monthly_fee
    WHEN u.role = 'influencer' THEN i.monthly_fee
  END;
