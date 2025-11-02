# 🚀 INITIALISATION COMPLÈTE DE VOTRE SUPABASE

## ⚠️ PROBLÈME IDENTIFIÉ
Votre base de données Supabase est **VIDE**. Aucune table n'existe (merchants, influencers, products, etc.).

---

## 📋 SOLUTION EN 3 ÉTAPES (20 minutes)

### ÉTAPE 1 : Créer toutes les tables ⏱️ 5 min

1. **Ouvrez Supabase Dashboard** → https://supabase.com/dashboard
2. **Allez dans** : `SQL Editor` → `New Query`
3. **Copiez TOUT le contenu** du fichier : `INIT_SUPABASE_COMPLET.sql`
4. **Cliquez sur** : `RUN` ▶️

**Ce script va créer** :
- ✅ Table `merchants` (entreprises)
- ✅ Table `influencers` (influenceurs)
- ✅ Table `products` (produits)
- ✅ Table `campaigns` (campagnes)
- ✅ Table `affiliations` (liens affiliation)
- ✅ Table `trackable_links` (tracking)
- ✅ Table `clicks` (statistiques)
- ✅ Table `transactions` (ventes)

---

### ÉTAPE 2 : Créer les 7 comptes test ⏱️ 10 min

#### A) Créer les users dans Supabase Auth

1. **Allez dans** : `Authentication` → `Users` → `Add User`
2. **Créez ces 7 comptes** (cochez "Auto Confirm User") :

```
✅ merchant_free@test.com         → Test123!
✅ merchant_starter@test.com      → Test123!
✅ merchant_pro@test.com          → Test123!
✅ merchant_enterprise@test.com   → Test123!
✅ influencer_free@test.com       → Test123!
✅ influencer_pro@test.com        → Test123!
✅ influencer_elite@test.com      → Test123!
```

#### B) Récupérer les UUIDs

Exécutez dans `SQL Editor` :
```sql
SELECT id, email
FROM auth.users
WHERE email LIKE '%@test.com'
ORDER BY email;
```

**Notez les 7 UUIDs** quelque part.

#### C) Créer les profils

Copiez ce script, **REMPLACEZ LES UUIDs** par les vrais, puis exécutez :

```sql
-- MERCHANTS
INSERT INTO merchants (user_id, company_name, description, category, subscription_plan, subscription_status, commission_rate, monthly_fee)
VALUES
  ('UUID_merchant_enterprise', 'Test Merchant Enterprise', 'Compte test plan Enterprise', 'E-commerce', 'enterprise', 'active', 2.00, 1999.00),
  ('UUID_merchant_free', 'Test Merchant Free', 'Compte test plan Freemium', 'E-commerce', 'free', 'active', 5.00, 0.00),
  ('UUID_merchant_pro', 'Test Merchant Pro', 'Compte test plan Premium', 'Technologie', 'pro', 'active', 3.00, 799.00),
  ('UUID_merchant_starter', 'Test Merchant Starter', 'Compte test plan Standard', 'Mode et lifestyle', 'starter', 'active', 4.00, 299.00);

-- INFLUENCERS
INSERT INTO influencers (user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, subscription_status, platform_fee_rate, monthly_fee)
VALUES
  ('UUID_influencer_elite', 'test_influencer_elite', 'Test Influencer Elite', 'Influenceur test plan Elite', 'Tech & Innovation', 'macro', 500000, 7.80, 'pro', 'active', 2.00, 299.00),
  ('UUID_influencer_free', 'test_influencer_free', 'Test Influencer Free', 'Influenceur test plan gratuit', 'Lifestyle', 'nano', 5000, 3.50, 'starter', 'active', 5.00, 0.00),
  ('UUID_influencer_pro', 'test_influencer_pro', 'Test Influencer Pro', 'Influenceur test plan Pro', 'Mode & Beauté', 'micro', 50000, 5.20, 'pro', 'active', 3.00, 99.00);
```

---

### ÉTAPE 3 : Vérifier que tout fonctionne ⏱️ 5 min

Exécutez cette requête :
```sql
SELECT 
    au.email,
    COALESCE(m.company_name, i.username) as nom,
    COALESCE(m.subscription_plan, i.subscription_plan) as plan,
    COALESCE(m.monthly_fee, i.monthly_fee) as prix,
    CASE 
        WHEN m.user_id IS NOT NULL THEN 'merchant'
        WHEN i.user_id IS NOT NULL THEN 'influencer'
    END as role
FROM auth.users au
LEFT JOIN merchants m ON au.id = m.user_id
LEFT JOIN influencers i ON au.id = i.user_id
WHERE au.email LIKE '%@test.com'
ORDER BY au.email;
```

**Résultat attendu** : 7 lignes avec tous les comptes !

---

## 🎯 RÉSULTAT FINAL

✅ Base de données complète avec 8 tables
✅ 7 comptes test fonctionnels
✅ Prêt pour tester l'application !

---

## 🔐 CONNEXION

**URL** : Votre application frontend
**Comptes** : Les 7 emails ci-dessus
**Mot de passe** : `Test123!` pour tous

---

## ❓ EN CAS DE PROBLÈME

Si vous avez une erreur, exécutez d'abord :
```sql
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

Cela vous dira quelles tables existent déjà.
