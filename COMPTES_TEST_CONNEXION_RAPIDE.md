# 🔐 Comptes de Test - Connexion Rapide

## 📋 Tous les Comptes Test Disponibles

Mot de passe pour tous les comptes: **Test123!**

---

## 👔 Comptes Merchants (4 comptes)

### 1. Merchant Free (Plan Gratuit)
- **Email**: `merchant_free@test.com`
- **Password**: `Test123!`
- **Plan**: Free
- **Frais mensuels**: 0 MAD
- **Commission**: 5%

### 2. Merchant Starter
- **Email**: `merchant_starter@test.com`
- **Password**: `Test123!`
- **Plan**: Starter
- **Frais mensuels**: 299 MAD
- **Commission**: 4%
- **Ventes totales**: 15,000 MAD

### 3. Merchant Pro
- **Email**: `merchant_pro@test.com`
- **Password**: `Test123!`
- **Plan**: Pro
- **Frais mensuels**: 799 MAD
- **Commission**: 3%
- **Ventes totales**: 45,000 MAD

### 4. Merchant Enterprise
- **Email**: `merchant_enterprise@test.com`
- **Password**: `Test123!`
- **Plan**: Enterprise
- **Frais mensuels**: 1999 MAD
- **Commission**: 2%
- **Ventes totales**: 150,000 MAD

---

## 📱 Comptes Influencers (3 comptes)

### 1. Influencer Starter (Nano)
- **Email**: `influencer_starter@test.com`
- **Password**: `Test123!`
- **Plan**: Starter
- **Frais mensuels**: 0 MAD
- **Commission**: 5%
- **Audience**: 5,000 followers
- **Engagement**: 3.5%
- **Revenus**: 500 MAD

### 2. Influencer Pro (Micro)
- **Email**: `influencer_pro@test.com`
- **Password**: `Test123!`
- **Plan**: Pro
- **Frais mensuels**: 99 MAD
- **Commission**: 3%
- **Audience**: 25,000 followers
- **Engagement**: 5.2%
- **Revenus**: 3,500 MAD

### 3. Influencer Elite (Macro)
- **Email**: `influencer_elite@test.com`
- **Password**: `Test123!`
- **Plan**: Pro Elite
- **Frais mensuels**: 299 MAD
- **Commission**: 2%
- **Audience**: 100,000 followers
- **Engagement**: 6.8%
- **Revenus**: 12,000 MAD

---

## 🚀 Connexion Rapide (Copier-Coller)

### Merchants
```
merchant_free@test.com
Test123!

merchant_starter@test.com
Test123!

merchant_pro@test.com
Test123!

merchant_enterprise@test.com
Test123!
```

### Influencers
```
influencer_starter@test.com
Test123!

influencer_pro@test.com
Test123!

influencer_elite@test.com
Test123!
```

---

## 📊 Tableau Récapitulatif

| Email | Type | Plan | Frais/mois | Commission |
|-------|------|------|------------|------------|
| merchant_free@test.com | Merchant | Free | 0 MAD | 5% |
| merchant_starter@test.com | Merchant | Starter | 299 MAD | 4% |
| merchant_pro@test.com | Merchant | Pro | 799 MAD | 3% |
| merchant_enterprise@test.com | Merchant | Enterprise | 1999 MAD | 2% |
| influencer_starter@test.com | Influencer | Starter | 0 MAD | 5% |
| influencer_pro@test.com | Influencer | Pro | 99 MAD | 3% |
| influencer_elite@test.com | Influencer | Elite | 299 MAD | 2% |

---

## 🎯 Scénarios de Test Recommandés

### Test 1: Vérifier les Dashboards
1. Connectez-vous avec `merchant_free@test.com`
2. Vérifiez que la carte d'abonnement affiche "Plan Free"
3. Testez le bouton "Améliorer mon Plan"

### Test 2: Comparer les Plans
1. Connectez-vous avec différents comptes
2. Observez les différences de commissions
3. Vérifiez les limites de chaque plan

### Test 3: Test Influencer
1. Connectez-vous avec `influencer_elite@test.com`
2. Vérifiez les stats (100K followers, 6.8% engagement)
3. Testez les fonctionnalités pro

---

## ⚠️ Notes Importantes

- Tous les comptes utilisent le même mot de passe: `Test123!`
- Les données sont des données de test (factices)
- Ces comptes sont pour le développement/test uniquement
- Ne pas utiliser en production

---

## 🔄 Pour Réinitialiser les Comptes

Si vous devez recréer les comptes:

1. Supprimez les utilisateurs dans Supabase Auth Dashboard
2. Exécutez `backend/database/CREATE_ALL_TEST_ACCOUNTS.sql`
3. Tous les profils seront recréés avec les mêmes données
