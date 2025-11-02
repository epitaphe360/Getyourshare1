-- ============================================
-- SCRIPT DE CRÉATION DE COMPTES TEST
-- ============================================
-- Ce script crée 7 comptes de test avec leurs profils et abonnements
-- Password pour tous les comptes: Test123!
-- Hash bcrypt: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom

-- Note: Vous devrez peut-être ajuster les colonnes selon votre schéma exact
-- Vérifiez d'abord avec: DESCRIBE users; ou \d users dans PostgreSQL

-- ============================================
-- NETTOYAGE (optionnel - commentez si vous ne voulez pas supprimer les anciens comptes)
-- ============================================
DELETE FROM user_subscriptions WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@test.com'
);
DELETE FROM merchants WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@test.com'
);
DELETE FROM influencers WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@test.com'
);
DELETE FROM users WHERE email LIKE '%@test.com';

-- ============================================
-- COMPTES ENTREPRISES (MERCHANTS)
-- ============================================

-- 1. Merchant Freemium (0 MAD/mois)
INSERT INTO users (id, email, password_hash, role, email_verified, is_active, two_fa_enabled, created_at)
VALUES (
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  'merchant_free@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'merchant',
  true,
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    email_verified = EXCLUDED.email_verified;

INSERT INTO merchants (user_id, company_name, company_description, industry, website, created_at)
VALUES (
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  'Test Merchant Free',
  'Compte test pour plan Freemium',
  'E-commerce',
  'https://test-free.com',
  NOW()
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_subscriptions (user_id, plan_id, status, started_at, current_period_start, current_period_end)
SELECT 
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  id,
  'active',
  NOW(),
  NOW(),
  NOW() + INTERVAL '1 month'
FROM subscription_plans 
WHERE name = 'Freemium' AND user_type = 'merchant'
ON CONFLICT (user_id) DO UPDATE SET plan_id = EXCLUDED.plan_id;

-- 2. Merchant Standard (299 MAD/mois)
INSERT INTO users (id, email, password_hash, role, email_verified, is_active, two_fa_enabled, created_at)
VALUES (
  'a1b2c3d4-e5f6-4789-a012-3456789abcde',
  'merchant_starter@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'merchant',
  true,
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    email_verified = EXCLUDED.email_verified;

INSERT INTO merchants (user_id, company_name, company_description, industry, website, created_at)
VALUES (
  'a1b2c3d4-e5f6-4789-a012-3456789abcde',
  'Test Merchant Starter',
  'Compte test pour plan Standard',
  'Mode & Beauté',
  'https://test-starter.com',
  NOW()
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_subscriptions (user_id, plan_id, status, started_at, current_period_start, current_period_end)
SELECT 
  'a1b2c3d4-e5f6-4789-a012-3456789abcde',
  id,
  'active',
  NOW(),
  NOW(),
  NOW() + INTERVAL '1 month'
FROM subscription_plans 
WHERE name = 'Standard' AND user_type = 'merchant'
ON CONFLICT (user_id) DO UPDATE SET plan_id = EXCLUDED.plan_id;

-- 3. Merchant Premium (799 MAD/mois)
INSERT INTO users (id, email, password_hash, role, email_verified, is_active, two_fa_enabled, created_at)
VALUES (
  'b2c3d4e5-f6a7-4890-b123-456789abcdef',
  'merchant_pro@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'merchant',
  true,
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    email_verified = EXCLUDED.email_verified;

INSERT INTO merchants (user_id, company_name, company_description, industry, website, created_at)
VALUES (
  'b2c3d4e5-f6a7-4890-b123-456789abcdef',
  'Test Merchant Pro',
  'Compte test pour plan Premium',
  'Technologie',
  'https://test-pro.com',
  NOW()
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_subscriptions (user_id, plan_id, status, started_at, current_period_start, current_period_end)
SELECT 
  'b2c3d4e5-f6a7-4890-b123-456789abcdef',
  id,
  'active',
  NOW(),
  NOW(),
  NOW() + INTERVAL '1 month'
FROM subscription_plans 
WHERE name = 'Premium' AND user_type = 'merchant'
ON CONFLICT (user_id) DO UPDATE SET plan_id = EXCLUDED.plan_id;

-- 4. Merchant Enterprise (1999 MAD/mois)
INSERT INTO users (id, email, password_hash, role, email_verified, is_active, two_fa_enabled, created_at)
VALUES (
  'c3d4e5f6-a7b8-4901-c234-56789abcdef0',
  'merchant_enterprise@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'merchant',
  true,
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    email_verified = EXCLUDED.email_verified;

INSERT INTO merchants (user_id, company_name, company_description, industry, website, created_at)
VALUES (
  'c3d4e5f6-a7b8-4901-c234-56789abcdef0',
  'Test Merchant Enterprise',
  'Compte test pour plan Enterprise',
  'Grande Distribution',
  'https://test-enterprise.com',
  NOW()
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_subscriptions (user_id, plan_id, status, started_at, current_period_start, current_period_end)
SELECT 
  'c3d4e5f6-a7b8-4901-c234-56789abcdef0',
  id,
  'active',
  NOW(),
  NOW(),
  NOW() + INTERVAL '1 month'
FROM subscription_plans 
WHERE name = 'Enterprise' AND user_type = 'merchant'
ON CONFLICT (user_id) DO UPDATE SET plan_id = EXCLUDED.plan_id;

-- ============================================
-- COMPTES INFLUENCEURS
-- ============================================

-- 1. Influencer Free (0 MAD/mois)
INSERT INTO users (id, email, password_hash, role, email_verified, is_active, two_fa_enabled, created_at)
VALUES (
  'd4e5f6a7-b8c9-4012-d345-6789abcdef01',
  'influencer_free@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'influencer',
  true,
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    email_verified = EXCLUDED.email_verified;

INSERT INTO influencers (user_id, display_name, bio, niche, total_followers, created_at)
VALUES (
  'd4e5f6a7-b8c9-4012-d345-6789abcdef01',
  'Test Influencer Free',
  'Influenceur test plan gratuit',
  'Lifestyle',
  5000,
  NOW()
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_subscriptions (user_id, plan_id, status, started_at, current_period_start, current_period_end)
SELECT 
  'd4e5f6a7-b8c9-4012-d345-6789abcdef01',
  id,
  'active',
  NOW(),
  NOW(),
  NOW() + INTERVAL '1 month'
FROM subscription_plans 
WHERE name = 'Free' AND user_type = 'influencer'
ON CONFLICT (user_id) DO UPDATE SET plan_id = EXCLUDED.plan_id;

-- 2. Influencer Pro (99 MAD/mois)
INSERT INTO users (id, email, password_hash, role, email_verified, is_active, two_fa_enabled, created_at)
VALUES (
  'e5f6a7b8-c9d0-4123-e456-789abcdef012',
  'influencer_pro@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'influencer',
  true,
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    email_verified = EXCLUDED.email_verified;

INSERT INTO influencers (user_id, display_name, bio, niche, total_followers, created_at)
VALUES (
  'e5f6a7b8-c9d0-4123-e456-789abcdef012',
  'Test Influencer Pro',
  'Influenceur test plan Pro',
  'Mode & Beauté',
  50000,
  NOW()
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_subscriptions (user_id, plan_id, status, started_at, current_period_start, current_period_end)
SELECT 
  'e5f6a7b8-c9d0-4123-e456-789abcdef012',
  id,
  'active',
  NOW(),
  NOW(),
  NOW() + INTERVAL '1 month'
FROM subscription_plans 
WHERE name = 'Pro' AND user_type = 'influencer'
ON CONFLICT (user_id) DO UPDATE SET plan_id = EXCLUDED.plan_id;

-- 3. Influencer Elite (299 MAD/mois)
INSERT INTO users (id, email, password_hash, role, email_verified, is_active, two_fa_enabled, created_at)
VALUES (
  'f6a7b8c9-d0e1-4234-f567-89abcdef0123',
  'influencer_elite@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom',
  'influencer',
  true,
  true,
  false,
  NOW()
) ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    email_verified = EXCLUDED.email_verified;

INSERT INTO influencers (user_id, display_name, bio, niche, total_followers, created_at)
VALUES (
  'f6a7b8c9-d0e1-4234-f567-89abcdef0123',
  'Test Influencer Elite',
  'Influenceur test plan Elite',
  'Tech & Innovation',
  500000,
  NOW()
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_subscriptions (user_id, plan_id, status, started_at, current_period_start, current_period_end)
SELECT 
  'f6a7b8c9-d0e1-4234-f567-89abcdef0123',
  id,
  'active',
  NOW(),
  NOW(),
  NOW() + INTERVAL '1 month'
FROM subscription_plans 
WHERE name = 'Elite' AND user_type = 'influencer'
ON CONFLICT (user_id) DO UPDATE SET plan_id = EXCLUDED.plan_id;

-- ============================================
-- VÉRIFICATION
-- ============================================

-- Afficher tous les comptes créés avec leurs abonnements
SELECT 
  u.email,
  u.role,
  sp.name as plan_name,
  sp.price,
  us.status,
  COALESCE(m.company_name, i.display_name) as profile_name
FROM users u
LEFT JOIN user_subscriptions us ON u.id = us.user_id
LEFT JOIN subscription_plans sp ON us.plan_id = sp.id
LEFT JOIN merchants m ON u.id = m.user_id
LEFT JOIN influencers i ON u.id = i.user_id
WHERE u.email LIKE '%@test.com'
ORDER BY u.role, sp.price;
