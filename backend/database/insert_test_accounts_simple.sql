-- ============================================
-- SCRIPT DE CRÉATION DE COMPTES TEST - VERSION SIMPLIFIÉE
-- ============================================
-- Ce script crée 7 comptes de test avec leurs profils
-- Password pour tous les comptes: Test123!
-- Hash bcrypt: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom
--
-- COMPTES CRÉÉS:
-- 1. merchant_free@test.com (Freemium)
-- 2. merchant_starter@test.com (Standard/Starter)
-- 3. merchant_pro@test.com (Premium/Pro)
-- 4. merchant_enterprise@test.com (Enterprise)
-- 5. influencer_free@test.com (Starter)
-- 6. influencer_pro@test.com (Pro)
-- 7. influencer_elite@test.com (Pro)
-- ============================================

-- ============================================
-- ÉTAPE 1: NETTOYAGE (optionnel)
-- ============================================
-- Décommentez si vous voulez supprimer les anciens comptes test
/*
DELETE FROM merchants WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@test.com'
);
DELETE FROM influencers WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@test.com'
);
DELETE FROM users WHERE email LIKE '%@test.com';
*/

-- ============================================
-- ÉTAPE 2: CRÉATION DES COMPTES USERS
-- ============================================

-- 1. Merchant Freemium
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

-- 2. Merchant Starter/Standard
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

-- 3. Merchant Pro/Premium
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

-- 4. Merchant Enterprise
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

-- 5. Influencer Free/Starter
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

-- 6. Influencer Pro
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

-- 7. Influencer Elite (Pro aussi)
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

-- ============================================
-- ÉTAPE 3: CRÉATION DES PROFILS MERCHANTS
-- ============================================

-- 1. Merchant Freemium (free plan)
INSERT INTO merchants (user_id, company_name, industry, category, description, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  'Test Merchant Free',
  'E-commerce',
  'E-commerce',
  'Compte test pour plan Freemium - limité à 5 produits',
  'https://test-free.com',
  'free',
  'active',
  5.00,
  0.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status,
    commission_rate = EXCLUDED.commission_rate,
    monthly_fee = EXCLUDED.monthly_fee;

-- 2. Merchant Starter (starter plan)
INSERT INTO merchants (user_id, company_name, industry, category, description, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'a1b2c3d4-e5f6-4789-a012-3456789abcde',
  'Test Merchant Starter',
  'Mode & Beauté',
  'Mode et lifestyle',
  'Compte test pour plan Standard/Starter - 30 produits',
  'https://test-starter.com',
  'starter',
  'active',
  4.00,
  299.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status,
    commission_rate = EXCLUDED.commission_rate,
    monthly_fee = EXCLUDED.monthly_fee;

-- 3. Merchant Pro (pro plan)
INSERT INTO merchants (user_id, company_name, industry, category, description, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'b2c3d4e5-f6a7-4890-b123-456789abcdef',
  'Test Merchant Pro',
  'Technologie',
  'Technologie',
  'Compte test pour plan Premium/Pro - produits illimités',
  'https://test-pro.com',
  'pro',
  'active',
  3.00,
  799.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status,
    commission_rate = EXCLUDED.commission_rate,
    monthly_fee = EXCLUDED.monthly_fee;

-- 4. Merchant Enterprise (enterprise plan)
INSERT INTO merchants (user_id, company_name, industry, category, description, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'c3d4e5f6-a7b8-4901-c234-56789abcdef0',
  'Test Merchant Enterprise',
  'Grande Distribution',
  'E-commerce',
  'Compte test pour plan Enterprise - tout illimité + support prioritaire',
  'https://test-enterprise.com',
  'enterprise',
  'active',
  2.00,
  1999.00,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET subscription_plan = EXCLUDED.subscription_plan,
    subscription_status = EXCLUDED.subscription_status,
    commission_rate = EXCLUDED.commission_rate,
    monthly_fee = EXCLUDED.monthly_fee;

-- ============================================
-- ÉTAPE 4: CRÉATION DES PROFILS INFLUENCERS
-- ============================================

-- 1. Influencer Free/Starter
INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'd4e5f6a7-b8c9-4012-d345-6789abcdef01',
  'test_influencer_free',
  'Test Influencer Free',
  'Influenceur test plan gratuit - 2 campagnes/mois',
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
    subscription_status = EXCLUDED.subscription_status,
    platform_fee_rate = EXCLUDED.platform_fee_rate,
    monthly_fee = EXCLUDED.monthly_fee;

-- 2. Influencer Pro
INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'e5f6a7b8-c9d0-4123-e456-789abcdef012',
  'test_influencer_pro',
  'Test Influencer Pro',
  'Influenceur test plan Pro - campagnes illimitées + analytics',
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
    subscription_status = EXCLUDED.subscription_status,
    platform_fee_rate = EXCLUDED.platform_fee_rate,
    monthly_fee = EXCLUDED.monthly_fee;

-- 3. Influencer Elite (Pro plan aussi)
INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'f6a7b8c9-d0e1-4234-f567-89abcdef0123',
  'test_influencer_elite',
  'Test Influencer Elite',
  'Influenceur test plan Elite/Pro - grosse audience + paiements instantanés',
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
    subscription_status = EXCLUDED.subscription_status,
    platform_fee_rate = EXCLUDED.platform_fee_rate,
    monthly_fee = EXCLUDED.monthly_fee;

-- ============================================
-- ÉTAPE 5: VÉRIFICATION
-- ============================================

-- Afficher tous les comptes créés
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

-- ============================================
-- RÉSUMÉ
-- ============================================
/*
✅ 7 COMPTES CRÉÉS AVEC SUCCÈS

MERCHANTS (4 comptes):
- merchant_free@test.com       | Plan: free       | 0 MAD/mois    | Comm: 5%
- merchant_starter@test.com    | Plan: starter    | 299 MAD/mois  | Comm: 4%
- merchant_pro@test.com        | Plan: pro        | 799 MAD/mois  | Comm: 3%
- merchant_enterprise@test.com | Plan: enterprise | 1999 MAD/mois | Comm: 2%

INFLUENCERS (3 comptes):
- influencer_free@test.com  | Plan: starter | 0 MAD/mois   | Fee: 5%
- influencer_pro@test.com   | Plan: pro     | 99 MAD/mois  | Fee: 3%
- influencer_elite@test.com | Plan: pro     | 299 MAD/mois | Fee: 2%

MOT DE PASSE POUR TOUS: Test123!

PROCHAINES ÉTAPES:
1. Testez la connexion avec chaque compte
2. Vérifiez l'affichage des dashboards avec les plans d'abonnement
3. Les API endpoints devraient maintenant afficher les bonnes données d'abonnement
*/
