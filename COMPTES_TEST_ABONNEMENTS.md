# Comptes de Test - Système d'Abonnement

## 🎯 Vue d'ensemble

7 comptes de test ont été créés pour tester tous les types d'abonnements (4 marchands + 3 influenceurs).

**Mot de passe pour TOUS les comptes:** `Test123!`

---

## 👔 Comptes Entreprises (Merchants)

### 1. Plan Freemium (Gratuit)
- **Email:** `merchant_free@test.com`
- **Plan:** Freemium - 0 MAD/mois
- **Entreprise:** Test Merchant Free
- **Limites:**
  - ✅ 5 produits maximum
  - ✅ 1 campagne active
  - ✅ 10 affiliés maximum
  - ✅ Analytics basiques
  - ❌ Pas de support prioritaire
  - ❌ Pas d'outils IA

### 2. Plan Standard (Starter)
- **Email:** `merchant_starter@test.com`
- **Plan:** Standard - 299 MAD/mois
- **Entreprise:** Test Merchant Starter
- **Limites:**
  - ✅ 25 produits maximum
  - ✅ 5 campagnes actives
  - ✅ 50 affiliés maximum
  - ✅ Analytics avancés
  - ✅ Support email prioritaire
  - ✅ Rapports personnalisés

### 3. Plan Premium (Pro)
- **Email:** `merchant_pro@test.com`
- **Plan:** Premium - 799 MAD/mois
- **Entreprise:** Test Merchant Pro
- **Limites:**
  - ✅ 100 produits maximum
  - ✅ 20 campagnes actives
  - ✅ 200 affiliés maximum
  - ✅ Analytics avancés
  - ✅ Support chat 24/7
  - ✅ Outils IA inclus
  - ✅ Intégrations avancées
  - ✅ API complète

### 4. Plan Enterprise
- **Email:** `merchant_enterprise@test.com`
- **Plan:** Enterprise - 1999 MAD/mois
- **Entreprise:** Test Merchant Enterprise
- **Limites:**
  - ✅ Produits illimités
  - ✅ Campagnes illimitées
  - ✅ Affiliés illimités
  - ✅ Analytics prédictifs
  - ✅ Support dédié
  - ✅ Tous les outils IA
  - ✅ White-label
  - ✅ Domaine personnalisé
  - ✅ Formation dédiée

---

## 🌟 Comptes Influenceurs

### 1. Plan Free (Gratuit)
- **Email:** `influencer_free@test.com`
- **Plan:** Free - 0 MAD/mois
- **Nom:** Test Influencer Free
- **Niche:** Lifestyle
- **Followers:** 5,000
- **Caractéristiques:**
  - ✅ Commission: 5%
  - ✅ 5 campagnes par mois
  - ✅ Analytics basiques
  - ❌ Pas de paiements instantanés
  - ❌ Pas d'outils IA

### 2. Plan Pro
- **Email:** `influencer_pro@test.com`
- **Plan:** Pro - 99 MAD/mois
- **Nom:** Test Influencer Pro
- **Niche:** Mode & Beauté
- **Followers:** 50,000
- **Caractéristiques:**
  - ✅ Commission: 3%
  - ✅ 20 campagnes par mois
  - ✅ Analytics avancés
  - ✅ Paiements instantanés
  - ✅ Outils IA basiques
  - ✅ Badge vérifié
  - ✅ Support prioritaire

### 3. Plan Elite
- **Email:** `influencer_elite@test.com`
- **Plan:** Elite - 299 MAD/mois
- **Nom:** Test Influencer Elite
- **Niche:** Tech & Innovation
- **Followers:** 500,000
- **Caractéristiques:**
  - ✅ Commission: 2%
  - ✅ Campagnes illimitées
  - ✅ Analytics prédictifs
  - ✅ Paiements instantanés
  - ✅ Tous les outils IA
  - ✅ Badge Elite
  - ✅ Support dédié
  - ✅ Formation personnalisée
  - ✅ Placement prioritaire

---

## 📋 Installation des Comptes de Test

### Option 1: Via Supabase Dashboard (Recommandé)

1. Connectez-vous à votre Supabase Dashboard
2. Ouvrez l'éditeur SQL
3. Copiez le contenu de `backend/database/insert_test_accounts.sql`
4. Exécutez le script
5. Vérifiez que les 7 comptes ont été créés

### Option 2: Via CLI Supabase

```bash
# Si vous avez Supabase CLI installé
supabase db execute --file backend/database/insert_test_accounts.sql
```

### Option 3: Via psql

```bash
# Connexion directe à la base de données
psql "postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres" -f backend/database/insert_test_accounts.sql
```

---

## ✅ Vérification Post-Installation

Le script contient une requête de vérification à la fin qui affiche tous les comptes créés:

```sql
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
```

Vous devriez voir 7 comptes avec leurs abonnements actifs.

---

## 🧪 Tests à Effectuer

### Pour les Marchands:
1. ✅ Connexion avec chaque compte
2. ✅ Vérifier la carte d'abonnement dans le dashboard
3. ✅ Tester les limites (essayer de créer plus de produits que permis)
4. ✅ Vérifier que le bouton "Améliorer mon Plan" fonctionne
5. ✅ Tester l'upgrade vers un plan supérieur

### Pour les Influenceurs:
1. ✅ Connexion avec chaque compte
2. ✅ Vérifier la carte d'abonnement dans le dashboard
3. ✅ Vérifier le taux de commission affiché
4. ✅ Tester la création de campagnes (limites respectées)
5. ✅ Vérifier les options de paiement instantané (Pro/Elite)

---

## 🎨 Affichage dans les Dashboards

### MerchantDashboard
La carte d'abonnement affiche:
- Badge coloré selon le plan (Freemium=gris, Standard=bleu, Premium=indigo, Enterprise=purple)
- Statut de l'abonnement (Actif/Inactif)
- **3 barres de progression:**
  - Produits: X / Y utilisés
  - Campagnes: X / Y utilisées
  - Affiliés: X / Y utilisés
- Frais de commission (si applicable)
- Bouton "Améliorer mon Plan" → redirige vers `/pricing`

### InfluencerDashboard
La carte d'abonnement affiche:
- Badge coloré selon le plan (Free=gris, Pro=indigo, Elite=purple)
- Statut de l'abonnement (Actif/Inactif)
- **Informations clés:**
  - Taux de commission (5% → 3% → 2%)
  - Campagnes par mois
  - Paiement instantané (✓/✗)
  - Niveau d'analytics
- Message promotionnel pour les comptes Free
- Bouton "Passer à Pro" ou "Améliorer mon Plan"

---

## 🔧 Dépannage

### Les comptes ne se créent pas
- Vérifiez que la table `subscription_plans` existe et contient les plans
- Assurez-vous que les contraintes de clé étrangère sont satisfaites
- Vérifiez les logs Supabase pour les erreurs

### Les abonnements n'apparaissent pas dans le dashboard
- Vérifiez que l'endpoint `/api/subscriptions/current` fonctionne
- Inspectez la console navigateur pour les erreurs API
- Vérifiez que le `user_id` correspond bien

### Problème de mot de passe
- Le hash fourni est un exemple, il faudra peut-être le régénérer avec votre système
- Utilisez bcrypt pour hasher `Test123!` si nécessaire

---

## 📝 Notes Importantes

1. **Sécurité:** Ces comptes sont pour les tests uniquement, ne les utilisez JAMAIS en production
2. **Hash du mot de passe:** Le hash fourni est un exemple, vous devrez peut-être le remplacer
3. **UUIDs:** Les UUIDs sont fixés pour reproductibilité, ajustez si nécessaire
4. **Durée d'abonnement:** Les abonnements sont actifs pour 1 mois à partir de la date d'insertion
5. **Suppression:** Pour nettoyer, exécutez `DELETE FROM users WHERE email LIKE '%@test.com';`

---

## 🚀 Prochaines Étapes

1. Exécutez le script SQL pour créer les comptes
2. Testez la connexion avec chaque compte
3. Vérifiez l'affichage des abonnements dans les dashboards
4. Testez les limites de chaque plan
5. Testez le flux d'upgrade vers un plan supérieur

**Bon test ! 🎉**
