# 🚨 IMPORTANT : CRÉATION DES COMPTES TEST

## Problème Détecté

Votre base de données Supabase utilise **Supabase Auth** pour gérer les utilisateurs.
La table `users` n'existe pas dans votre schéma public, ou n'a pas de colonne `password_hash`.

Supabase Auth stocke les utilisateurs dans `auth.users` (table système) et vous ne pouvez pas y insérer directement via SQL.

## ✅ SOLUTION : Créer les comptes via l'interface Supabase

### Étape 1 : Créer les utilisateurs dans Supabase Auth

1. **Allez dans Supabase Dashboard** → Authentication → Users
2. **Cliquez sur "Add User"**
3. **Créez 7 utilisateurs** avec ces emails et le mot de passe `Test123!` :

#### Merchants (4 comptes)
- ✉️ `merchant_free@test.com` - Password: `Test123!`
- ✉️ `merchant_starter@test.com` - Password: `Test123!`
- ✉️ `merchant_pro@test.com` - Password: `Test123!`
- ✉️ `merchant_enterprise@test.com` - Password: `Test123!`

#### Influencers (3 comptes)
- ✉️ `influencer_free@test.com` - Password: `Test123!`
- ✉️ `influencer_pro@test.com` - Password: `Test123!`
- ✉️ `influencer_elite@test.com` - Password: `Test123!`

### Étape 2 : Récupérer les IDs des utilisateurs

Après avoir créé les utilisateurs, exécutez cette requête dans Supabase SQL Editor :

\`\`\`sql
SELECT id, email FROM auth.users WHERE email LIKE '%@test.com' ORDER BY email;
\`\`\`

**Notez les IDs** pour chaque email.

### Étape 3 : Créer les profils Merchants et Influencers

Utilisez le script SQL suivant en **REMPLAÇANT LES UUIDs** par ceux que vous avez récupérés à l'étape 2 :

\`\`\`sql
-- ============================================
-- CRÉATION DES PROFILS MERCHANTS
-- ============================================

-- Merchant Freemium
INSERT INTO merchants (user_id, company_name, description, industry, category, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'REMPLACER_PAR_UUID_merchant_free',
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
SET subscription_plan = EXCLUDED.subscription_plan;

-- Merchant Starter
INSERT INTO merchants (user_id, company_name, description, industry, category, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'REMPLACER_PAR_UUID_merchant_starter',
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
SET subscription_plan = EXCLUDED.subscription_plan;

-- Merchant Pro
INSERT INTO merchants (user_id, company_name, description, industry, category, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'REMPLACER_PAR_UUID_merchant_pro',
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
SET subscription_plan = EXCLUDED.subscription_plan;

-- Merchant Enterprise
INSERT INTO merchants (user_id, company_name, description, industry, category, website, subscription_plan, subscription_status, commission_rate, monthly_fee, created_at)
VALUES (
  'REMPLACER_PAR_UUID_merchant_enterprise',
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
SET subscription_plan = EXCLUDED.subscription_plan;

-- ============================================
-- CRÉATION DES PROFILS INFLUENCERS
-- ============================================

-- Influencer Free/Starter
INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'REMPLACER_PAR_UUID_influencer_free',
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
SET subscription_plan = EXCLUDED.subscription_plan;

-- Influencer Pro
INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'REMPLACER_PAR_UUID_influencer_pro',
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
SET subscription_plan = EXCLUDED.subscription_plan;

-- Influencer Elite
INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee, created_at)
VALUES (
  'REMPLACER_PAR_UUID_influencer_elite',
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
SET subscription_plan = EXCLUDED.subscription_plan;
\`\`\`

### Étape 4 : Ajouter les rôles dans votre table custom (si nécessaire)

Si vous avez une table `public.users` pour stocker les rôles, créez-la d'abord :

\`\`\`sql
-- Créer une table pour les rôles utilisateurs (si elle n'existe pas)
CREATE TABLE IF NOT EXISTS public.user_roles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'merchant', 'influencer')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insérer les rôles pour les comptes test
INSERT INTO user_roles (id, role)
SELECT id, 
  CASE 
    WHEN email LIKE 'merchant%' THEN 'merchant'
    WHEN email LIKE 'influencer%' THEN 'influencer'
  END as role
FROM auth.users 
WHERE email LIKE '%@test.com'
ON CONFLICT (id) DO UPDATE SET role = EXCLUDED.role;
\`\`\`

## 📋 Résumé

✅ **7 comptes créés** :
- 4 Merchants : Free, Starter, Pro, Enterprise
- 3 Influencers : Free, Pro, Elite

🔑 **Mot de passe unique** : `Test123!`

💾 **Tables remplies** :
- `auth.users` (via interface Supabase)
- `public.merchants` (via SQL après récupération des UUIDs)
- `public.influencers` (via SQL après récupération des UUIDs)
- `public.user_roles` (optionnel, si vous gérez les rôles séparément)

## 🧪 Test de connexion

Après avoir créé les comptes, testez la connexion :
1. Allez sur votre application
2. Login avec `merchant_free@test.com` / `Test123!`
3. Vérifiez que le dashboard affiche bien le plan Freemium

