-- ============================================
-- SCRIPT COMPLET - CRÉATION DE COMPTES TEST
-- ============================================
-- Application: GetYourShare / TrackNow.io
-- Date: 2025-11-02
-- Description: Crée 7 comptes de test avec profils et abonnements
-- 
-- Mot de passe pour TOUS les comptes: Test123!
-- Hash bcrypt (cost=12): $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC6FNzb9HZom
--
-- COMPTES CRÉÉS:
-- - 4 Merchants: free, starter, pro, enterprise
-- - 3 Influencers: free, pro, elite
-- ============================================

-- ============================================
-- ÉTAPE 1: NETTOYAGE (OPTIONNEL)
-- ============================================
-- Décommentez cette section si vous voulez supprimer les anciens comptes test

/*
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
*/

-- ============================================
-- ÉTAPE 2: CRÉATION DES UTILISATEURS
-- ============================================

-- MERCHANT 1: Freemium (0 MAD/mois)
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
    email_verified = EXCLUDED.email_verified,
    is_active = EXCLUDED.is_active;

-- MERCHANT 2: Standard (299 MAD/mois)
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
    email_verified = EXCLUDED.email_verified,
    is_active = EXCLUDED.is_active;

-- MERCHANT 3: Premium (799 MAD/mois)
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
    email_verified = EXCLUDED.email_verified,
    is_active = EXCLUDED.is_active;

-- MERCHANT 4: Enterprise (1999 MAD/mois)
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
    email_verified = EXCLUDED.email_verified,
    is_active = EXCLUDED.is_active;

-- INFLUENCER 1: Free (0 MAD/mois)
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
    email_verified = EXCLUDED.email_verified,
    is_active = EXCLUDED.is_active;

-- INFLUENCER 2: Pro (99 MAD/mois)
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
    email_verified = EXCLUDED.email_verified,
    is_active = EXCLUDED.is_active;

-- INFLUENCER 3: Elite (299 MAD/mois)
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
    email_verified = EXCLUDED.email_verified,
    is_active = EXCLUDED.is_active;

-- ============================================
-- ÉTAPE 3: CRÉATION DES PROFILS MERCHANTS
-- ============================================

INSERT INTO merchants (user_id, company_name, company_description, industry, website, created_at)
VALUES (
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  'Test Merchant Free',
  'Boutique e-commerce de test - Plan Freemium',
  'E-commerce',
  'https://test-free.example.com',
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET company_name = EXCLUDED.company_name,
    company_description = EXCLUDED.company_description;

INSERT INTO merchants (user_id, company_name, company_description, industry, website, created_at)
VALUES (
  'a1b2c3d4-e5f6-4789-a012-3456789abcde',
  'Test Merchant Starter',
  'Boutique mode et beauté - Plan Standard',
  'Mode & Beauté',
  'https://test-starter.example.com',
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET company_name = EXCLUDED.company_name,
    company_description = EXCLUDED.company_description;

INSERT INTO merchants (user_id, company_name, company_description, industry, website, created_at)
VALUES (
  'b2c3d4e5-f6a7-4890-b123-456789abcdef',
  'Test Merchant Pro',
  'Entreprise technologique - Plan Premium',
  'Technologie',
  'https://test-pro.example.com',
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET company_name = EXCLUDED.company_name,
    company_description = EXCLUDED.company_description;

INSERT INTO merchants (user_id, company_name, company_description, industry, website, created_at)
VALUES (
  'c3d4e5f6-a7b8-4901-c234-56789abcdef0',
  'Test Merchant Enterprise',
  'Grande distribution multinationale - Plan Enterprise',
  'Grande Distribution',
  'https://test-enterprise.example.com',
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET company_name = EXCLUDED.company_name,
    company_description = EXCLUDED.company_description;

-- ============================================
-- ÉTAPE 4: CRÉATION DES PROFILS INFLUENCEURS
-- ============================================

INSERT INTO influencers (user_id, display_name, bio, niche, total_followers, created_at)
VALUES (
  'd4e5f6a7-b8c9-4012-d345-6789abcdef01',
  'Test Influencer Free',
  'Créateur de contenu lifestyle 📸 | Plan gratuit pour démarrer',
  'Lifestyle',
  5000,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET display_name = EXCLUDED.display_name,
    bio = EXCLUDED.bio,
    total_followers = EXCLUDED.total_followers;

INSERT INTO influencers (user_id, display_name, bio, niche, total_followers, created_at)
VALUES (
  'e5f6a7b8-c9d0-4123-e456-789abcdef012',
  'Test Influencer Pro',
  'Experte mode & beauté ✨ | Collaborations de marque | Plan Pro',
  'Mode & Beauté',
  50000,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET display_name = EXCLUDED.display_name,
    bio = EXCLUDED.bio,
    total_followers = EXCLUDED.total_followers;

INSERT INTO influencers (user_id, display_name, bio, niche, total_followers, created_at)
VALUES (
  'f6a7b8c9-d0e1-4234-f567-89abcdef0123',
  'Test Influencer Elite',
  'Tech reviewer 💻 | Innovation & Gadgets | 500K+ followers | Plan Elite',
  'Tech & Innovation',
  500000,
  NOW()
) ON CONFLICT (user_id) DO UPDATE 
SET display_name = EXCLUDED.display_name,
    bio = EXCLUDED.bio,
    total_followers = EXCLUDED.total_followers;

-- ============================================
-- ÉTAPE 5: ATTRIBUTION DES ABONNEMENTS
-- ============================================

-- Merchant Freemium
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
LIMIT 1
ON CONFLICT (user_id) DO UPDATE 
SET plan_id = EXCLUDED.plan_id,
    status = EXCLUDED.status,
    current_period_start = EXCLUDED.current_period_start,
    current_period_end = EXCLUDED.current_period_end;

-- Merchant Standard
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
LIMIT 1
ON CONFLICT (user_id) DO UPDATE 
SET plan_id = EXCLUDED.plan_id,
    status = EXCLUDED.status,
    current_period_start = EXCLUDED.current_period_start,
    current_period_end = EXCLUDED.current_period_end;

-- Merchant Premium
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
LIMIT 1
ON CONFLICT (user_id) DO UPDATE 
SET plan_id = EXCLUDED.plan_id,
    status = EXCLUDED.status,
    current_period_start = EXCLUDED.current_period_start,
    current_period_end = EXCLUDED.current_period_end;

-- Merchant Enterprise
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
LIMIT 1
ON CONFLICT (user_id) DO UPDATE 
SET plan_id = EXCLUDED.plan_id,
    status = EXCLUDED.status,
    current_period_start = EXCLUDED.current_period_start,
    current_period_end = EXCLUDED.current_period_end;

-- Influencer Free
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
LIMIT 1
ON CONFLICT (user_id) DO UPDATE 
SET plan_id = EXCLUDED.plan_id,
    status = EXCLUDED.status,
    current_period_start = EXCLUDED.current_period_start,
    current_period_end = EXCLUDED.current_period_end;

-- Influencer Pro
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
LIMIT 1
ON CONFLICT (user_id) DO UPDATE 
SET plan_id = EXCLUDED.plan_id,
    status = EXCLUDED.status,
    current_period_start = EXCLUDED.current_period_start,
    current_period_end = EXCLUDED.current_period_end;

-- Influencer Elite
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
LIMIT 1
ON CONFLICT (user_id) DO UPDATE 
SET plan_id = EXCLUDED.plan_id,
    status = EXCLUDED.status,
    current_period_start = EXCLUDED.current_period_start,
    current_period_end = EXCLUDED.current_period_end;

-- ============================================
-- ÉTAPE 6: VÉRIFICATION
-- ============================================

-- Afficher tous les comptes créés avec leurs abonnements
SELECT 
  u.email,
  u.role,
  u.email_verified,
  u.is_active,
  sp.name as plan_name,
  sp.price as plan_price,
  us.status as subscription_status,
  COALESCE(m.company_name, i.display_name) as profile_name,
  COALESCE(i.total_followers, 0) as followers
FROM users u
LEFT JOIN user_subscriptions us ON u.id = us.user_id
LEFT JOIN subscription_plans sp ON us.plan_id = sp.id
LEFT JOIN merchants m ON u.id = m.user_id
LEFT JOIN influencers i ON u.id = i.user_id
WHERE u.email LIKE '%@test.com'
ORDER BY u.role, sp.price;

-- ============================================
-- RÉSUMÉ
-- ============================================
-- 
-- ✅ 7 comptes créés avec succès !
--
-- MERCHANTS (4):
-- - merchant_free@test.com       | Freemium   | 0 MAD    | 5 produits, 1 campagne
-- - merchant_starter@test.com    | Standard   | 299 MAD  | 50 produits, 10 campagnes
-- - merchant_pro@test.com        | Premium    | 799 MAD  | 100 produits, 20 campagnes
-- - merchant_enterprise@test.com | Enterprise | 1999 MAD | Illimité
--
-- INFLUENCERS (3):
-- - influencer_free@test.com  | Free  | 0 MAD   | 5% commission, 5 campagnes/mois
-- - influencer_pro@test.com   | Pro   | 99 MAD  | 3% commission, 20 campagnes/mois
-- - influencer_elite@test.com | Elite | 299 MAD | 2% commission, illimité
--
-- Mot de passe pour TOUS: Test123!
--
-- PROCHAINES ÉTAPES:
-- 1. Testez la connexion avec chaque compte
-- 2. Vérifiez que les limites d'abonnement s'affichent correctement
-- 3. Testez les fonctionnalités spécifiques à chaque plan
-- ============================================
