# 🚀 GUIDE RAPIDE : CRÉER 7 COMPTES TEST SUR SUPABASE

## ⚠️ IMPORTANT
Supabase utilise **Supabase Auth** pour gérer les utilisateurs.
**Vous ne pouvez PAS créer des users avec SQL directement.**

## 📋 MÉTHODE RAPIDE (15 minutes)

### ÉTAPE 1 : Créer les 7 users dans Supabase Dashboard

1. **Ouvrez votre projet Supabase** → https://supabase.com/dashboard
2. **Allez dans** : `Authentication` → `Users` → `Add User`
3. **Créez ces 7 comptes UN PAR UN** :

#### 🏢 Merchants (4 comptes)
```
1. Email: merchant_free@test.com
   Password: Test123!
   
2. Email: merchant_starter@test.com
   Password: Test123!
   
3. Email: merchant_pro@test.com
   Password: Test123!
   
4. Email: merchant_enterprise@test.com
   Password: Test123!
```

#### 👤 Influencers (3 comptes)
```
5. Email: influencer_free@test.com
   Password: Test123!
   
6. Email: influencer_pro@test.com
   Password: Test123!
   
7. Email: influencer_elite@test.com
   Password: Test123!
```

**Important** : Cochez "Auto Confirm User" pour chaque compte !

---

### ÉTAPE 2 : Récupérer les UUIDs

Exécutez cette requête dans **Supabase SQL Editor** :

```sql
SELECT id, email
FROM auth.users
WHERE email LIKE '%@test.com'
ORDER BY email;
```

**Copiez les 7 UUIDs** quelque part (Notepad).

---

### ÉTAPE 3 : Créer les profils merchants et influencers

Ouvrez le fichier `insert_test_profiles.sql` que je vais créer maintenant.

**Remplacez les UUIDs** par ceux que vous avez copiés, puis **exécutez le script**.

---

## 🎯 RÉSULTAT FINAL

Vous aurez 7 comptes fonctionnels :
- ✅ 4 merchants (free, starter, pro, enterprise)
- ✅ 3 influencers (free, pro, elite)
- ✅ Tous avec le mot de passe : `Test123!`

---

## 🔍 VÉRIFICATION

```sql
-- Vérifier que tout fonctionne
SELECT 
    au.email,
    COALESCE(m.company_name, i.username) as nom,
    COALESCE(m.subscription_plan, i.subscription_plan) as plan,
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

Vous devriez voir les 7 comptes avec leurs profils !
