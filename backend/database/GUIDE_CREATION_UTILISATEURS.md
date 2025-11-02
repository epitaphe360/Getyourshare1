# 🎯 Guide de Création des Comptes Test

## ⚠️ IMPORTANT
Le script SQL `CREATE_ALL_TEST_ACCOUNTS.sql` a besoin que les utilisateurs existent d'abord dans Supabase Auth avant de créer leurs profils.

## 📋 Étape 1: Créer les 7 Utilisateurs (5 minutes)

### Instructions Précises:

1. **Ouvrez votre Supabase Dashboard**
   - URL: https://supabase.com/dashboard
   - Sélectionnez votre projet

2. **Allez dans Authentication → Users**
   - Cliquez sur le menu "Authentication" dans la barre latérale gauche
   - Cliquez sur "Users"
   - Cliquez sur le bouton "Add User" (en haut à droite)

3. **Créez les 4 Merchants:**

   **Merchant 1 - Free:**
   - Email: `merchant_free@test.com`
   - Password: `Test123!`
   - ✅ Cochez "Auto Confirm User"
   - Cliquez "Create User"

   **Merchant 2 - Starter:**
   - Email: `merchant_starter@test.com`
   - Password: `Test123!`
   - ✅ Cochez "Auto Confirm User"
   - Cliquez "Create User"

   **Merchant 3 - Pro:**
   - Email: `merchant_pro@test.com`
   - Password: `Test123!`
   - ✅ Cochez "Auto Confirm User"
   - Cliquez "Create User"

   **Merchant 4 - Enterprise:**
   - Email: `merchant_enterprise@test.com`
   - Password: `Test123!`
   - ✅ Cochez "Auto Confirm User"
   - Cliquez "Create User"

4. **Créez les 3 Influencers:**

   **Influencer 1 - Starter:**
   - Email: `influencer_starter@test.com`
   - Password: `Test123!`
   - ✅ Cochez "Auto Confirm User"
   - Cliquez "Create User"

   **Influencer 2 - Pro:**
   - Email: `influencer_pro@test.com`
   - Password: `Test123!`
   - ✅ Cochez "Auto Confirm User"
   - Cliquez "Create User"

   **Influencer 3 - Elite:**
   - Email: `influencer_elite@test.com`
   - Password: `Test123!`
   - ✅ Cochez "Auto Confirm User"
   - Cliquez "Create User"

## 📋 Étape 2: Vérifier la Création (30 secondes)

Vous devriez maintenant voir **7 utilisateurs** dans la liste Authentication → Users avec les emails `@test.com`

## 📋 Étape 3: Créer les Profils (30 secondes)

1. **Ouvrez le SQL Editor**
   - Cliquez sur "SQL Editor" dans la barre latérale gauche
   
2. **Exécutez le script**
   - Ouvrez le fichier `backend/database/CREATE_ALL_TEST_ACCOUNTS.sql`
   - Copiez TOUT le contenu
   - Collez-le dans le SQL Editor de Supabase
   - Cliquez sur "Run"

3. **Vérifiez le résultat**
   - Vous devriez voir:
     - `total_profiles_created: 7`
     - Un tableau avec 7 lignes affichant tous les comptes

## ✅ Résultat Attendu

```
status: ✅ PROFILS CRÉÉS
total_profiles_created: 7

email                           | name                    | plan       | monthly_fee_mad | commission_rate | type
--------------------------------|-------------------------|------------|-----------------|-----------------|----------
influencer_elite@test.com       | test_influencer_elite   | pro        | 299.00          | 2.00            | influencer
influencer_pro@test.com         | test_influencer_pro     | pro        | 99.00           | 3.00            | influencer
influencer_starter@test.com     | test_influencer_starter | starter    | 0.00            | 5.00            | influencer
merchant_enterprise@test.com    | Test Merchant Enterprise| enterprise | 1999.00         | 2.00            | merchant
merchant_free@test.com          | Test Merchant Free      | free       | 0.00            | 5.00            | merchant
merchant_pro@test.com           | Test Merchant Pro       | pro        | 799.00          | 3.00            | merchant
merchant_starter@test.com       | Test Merchant Starter   | starter    | 299.00          | 4.00            | merchant
```

## 🔐 Informations de Connexion

Tous les comptes utilisent le même mot de passe: **Test123!**

### Comptes Merchants:
- merchant_free@test.com (Plan Free - 0 MAD/mois)
- merchant_starter@test.com (Plan Starter - 299 MAD/mois)
- merchant_pro@test.com (Plan Pro - 799 MAD/mois)
- merchant_enterprise@test.com (Plan Enterprise - 1999 MAD/mois)

### Comptes Influencers:
- influencer_starter@test.com (Plan Starter - 0 MAD/mois)
- influencer_pro@test.com (Plan Pro - 99 MAD/mois)
- influencer_elite@test.com (Plan Pro Elite - 299 MAD/mois)

## 🚨 Troubleshooting

**Si `total_profiles_created: 0`:**
- Vous n'avez pas créé les utilisateurs dans Supabase Auth
- Retournez à l'Étape 1

**Si certains profils manquent:**
- Vérifiez que tous les 7 emails sont bien dans Authentication → Users
- Réexécutez le script SQL (il utilise ON CONFLICT DO NOTHING, donc sans danger)

**Si vous voyez "NO PROFILE" dans la colonne type:**
- Le script SQL n'a pas pu trouver l'utilisateur correspondant
- Vérifiez l'orthographe exacte des emails dans Auth → Users
