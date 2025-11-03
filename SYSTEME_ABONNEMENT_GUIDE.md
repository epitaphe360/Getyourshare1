# 💎 Guide du Système d'Abonnement - ShareYourSales

## 📋 Vue d'Ensemble

Le système d'abonnement permet de monétiser la plateforme en proposant différents plans avec des limites et avantages variés.

---

## 🎯 Plans Disponibles

### 👔 Plans Merchant (Entreprises)

| Plan | Prix/Mois | Produits | Campagnes | Affiliés | Frais Commission | Support |
|------|-----------|----------|-----------|----------|------------------|---------|
| **Freemium** | 0€ | 5 | 1 | 10 | 0% | Email |
| **Standard** | 49€ | 50 | 10 | 100 | 0% | Email + Chat |
| **Premium** | 149€ | 200 | 50 | 500 | 0% | Prioritaire |
| **Enterprise** | 499€ | ∞ | ∞ | ∞ | 0% | Dédié |
| **Custom** | Sur demande | ∞ | ∞ | ∞ | Négociable | VIP |

### 🌟 Plans Influenceur

| Plan | Prix/Mois | Commission | Campagnes/Mois | Paiement Instantané | Analytics |
|------|-----------|------------|----------------|---------------------|-----------|
| **Free** | 0€ | 5% | 5 | ✗ | Basic |
| **Pro** | 29€ | 3% | 25 | ✓ | Advanced |
| **Elite** | 99€ | 1% | ∞ | ✓ | Premium |

---

## 🔄 Affichage dans les Dashboards

### Dashboard Merchant

```javascript
// La carte d'abonnement affiche :
- Nom du plan (badge coloré)
- Statut (Actif/Inactif)
- Bouton "Améliorer mon Plan"
- Compteurs de limites :
  * Produits : X / Y avec barre de progression
  * Campagnes : X / Y avec barre de progression
  * Affiliés : X / Y avec barre de progression
```

**Emplacement :** Après les cartes de statistiques principales

**Code :** `frontend/src/pages/dashboards/MerchantDashboard.js` (lignes 207-285)

### Dashboard Influenceur

```javascript
// La carte d'abonnement affiche :
- Nom du plan (badge coloré)
- Statut (Actif/Inactif)
- Bouton "Passer à Pro" ou "Améliorer mon Plan"
- Avantages du plan :
  * Taux de commission (5% → 3% → 1%)
  * Campagnes par mois
  * Paiement instantané (✓/✗)
  * Niveau d'analytics
```

**Emplacement :** Entre les stats et la carte de solde

**Code :** `frontend/src/pages/dashboards/InfluencerDashboard.js` (lignes 314-380)

---

## 🛠️ Endpoints API

### 1. Obtenir l'Abonnement Actuel

```bash
GET /api/subscriptions/current
```

**Réponse Merchant:**
```json
{
  "subscription_id": "sub_123",
  "user_id": "user_456",
  "plan_name": "Standard",
  "max_products": 50,
  "max_campaigns": 10,
  "max_affiliates": 100,
  "commission_fee": 0,
  "status": "active",
  "start_date": "2025-11-01",
  "end_date": "2025-12-01"
}
```

**Réponse Influenceur:**
```json
{
  "subscription_id": "sub_789",
  "user_id": "user_101",
  "plan_name": "Pro",
  "commission_rate": 3,
  "max_campaigns": 25,
  "instant_payout": true,
  "analytics_level": "advanced",
  "status": "active",
  "start_date": "2025-11-01",
  "end_date": "2025-12-01"
}
```

### 2. Obtenir Tous les Plans

```bash
GET /api/subscriptions/plans
```

**Réponse:**
```json
{
  "merchant_plans": [
    {
      "plan_id": "plan_freemium",
      "name": "Freemium",
      "price": 0,
      "max_products": 5,
      "max_campaigns": 1,
      "max_affiliates": 10
    },
    // ... autres plans
  ],
  "influencer_plans": [
    {
      "plan_id": "plan_free",
      "name": "Free",
      "price": 0,
      "commission_rate": 5,
      "max_campaigns": 5
    },
    // ... autres plans
  ]
}
```

### 3. Créer un Abonnement

```bash
POST /api/subscriptions
Content-Type: application/json

{
  "plan_id": "plan_standard",
  "payment_method": "stripe",
  "payment_token": "tok_visa"
}
```

### 4. Annuler un Abonnement

```bash
DELETE /api/subscriptions/{subscription_id}
```

---

## 🎨 Styles et Couleurs

### Badges de Plans Merchant

```javascript
// Freemium
bg-gray-100 text-gray-800

// Standard
bg-blue-100 text-blue-800

// Premium
bg-indigo-100 text-indigo-800

// Enterprise
bg-purple-100 text-purple-800
```

### Badges de Plans Influenceur

```javascript
// Free
bg-gray-100 text-gray-800

// Pro
bg-indigo-100 text-indigo-800

// Elite
bg-purple-100 text-purple-800
```

### Barres de Progression

```javascript
// Normal (< 80%)
bg-indigo-600

// Attention (>= 80%)
bg-red-500
```

---

## 🔧 Configuration Backend

### Fichier : `backend/subscription_endpoints.py`

**Endpoints disponibles :**
- `GET /api/subscriptions/current` - Abonnement actuel
- `GET /api/subscriptions/plans` - Liste des plans
- `POST /api/subscriptions` - Créer abonnement
- `PUT /api/subscriptions/{id}` - Modifier abonnement
- `DELETE /api/subscriptions/{id}` - Annuler abonnement
- `POST /api/subscriptions/{id}/upgrade` - Upgrade plan

### Fichier : `backend/subscription_helpers.py`

**Fonctions utiles :**
- `check_subscription_limits()` - Vérifier les limites
- `get_plan_features()` - Obtenir les fonctionnalités
- `calculate_prorated_amount()` - Calcul prorata
- `send_subscription_email()` - Email de confirmation

---

## 📊 Base de Données

### Table : `subscriptions`

```sql
CREATE TABLE subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    plan_id UUID REFERENCES subscription_plans(plan_id),
    status VARCHAR(20) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT NOW(),
    end_date TIMESTAMP,
    auto_renew BOOLEAN DEFAULT true,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Table : `subscription_plans`

```sql
CREATE TABLE subscription_plans (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    plan_type VARCHAR(20), -- 'merchant' ou 'influencer'
    price DECIMAL(10,2) NOT NULL,
    billing_period VARCHAR(20) DEFAULT 'monthly',
    max_products INTEGER,
    max_campaigns INTEGER,
    max_affiliates INTEGER,
    commission_rate DECIMAL(5,2),
    features JSONB,
    is_active BOOLEAN DEFAULT true
);
```

---

## 🧪 Tests

### 1. Tester l'Affichage

```bash
# 1. Se connecter en tant que Merchant
# 2. Vérifier que la carte "Mon Abonnement" s'affiche
# 3. Vérifier les compteurs de limites
# 4. Cliquer sur "Améliorer mon Plan"

# 5. Se connecter en tant que Influenceur
# 6. Vérifier que la carte "Mon Abonnement Influenceur" s'affiche
# 7. Vérifier le taux de commission
# 8. Vérifier les avantages du plan
```

### 2. Tester les Limites

```bash
# Merchant Freemium (5 produits max)
curl -X POST http://localhost:8000/api/products \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Produit 6", ...}'

# Devrait retourner une erreur si limite atteinte
{
  "error": "subscription_limit_reached",
  "message": "Limite de produits atteinte (5/5). Passez à Standard pour 50 produits."
}
```

### 3. Tester l'Upgrade

```bash
# 1. Se connecter en tant que Merchant Freemium
# 2. Cliquer sur "Améliorer mon Plan"
# 3. Sélectionner "Standard"
# 4. Entrer les informations de paiement
# 5. Confirmer
# 6. Vérifier que le plan a changé
# 7. Vérifier que les nouvelles limites sont appliquées
```

---

## 🐛 Dépannage

### Problème : La carte d'abonnement ne s'affiche pas

**Causes possibles :**
1. L'API `/api/subscriptions/current` retourne une erreur
2. La variable `subscription` est `null` ou `undefined`
3. Le composant est conditionnel : `{subscription && (`

**Solutions :**
```javascript
// Option 1 : Vérifier la console du navigateur
console.log('Subscription data:', subscription);

// Option 2 : Vérifier l'appel API
const response = await api.get('/api/subscriptions/current');
console.log('API response:', response);

// Option 3 : Ajouter un abonnement par défaut
if (!subscription) {
  setSubscription({
    plan_name: 'Freemium',
    max_products: 5,
    status: 'active'
  });
}
```

### Problème : Les limites ne sont pas appliquées

**Solution :**
1. Vérifier que le middleware `subscription_limits_middleware.py` est activé
2. Vérifier que les endpoints sont protégés
3. Vérifier la logique dans `subscription_helpers.py`

### Problème : L'upgrade ne fonctionne pas

**Solution :**
1. Vérifier la configuration Stripe
2. Vérifier les webhooks Stripe
3. Vérifier les logs du backend

---

## 📞 Support

- **Documentation complète :** `SYSTEME_ABONNEMENT_COMPLET.md`
- **Code backend :** `backend/subscription_endpoints.py`
- **Code frontend :** `frontend/src/pages/dashboards/`
- **Tests :** `backend/tests/test_subscriptions.py`

---

## 🚀 Améliorations Futures

1. **Essai gratuit** (14 jours)
2. **Codes promo** et réductions
3. **Abonnements annuels** (réduction)
4. **Gestion d'équipe** (multi-utilisateurs)
5. **Analytics avancés** par plan
6. **API publique** pour intégrations tierces

---

**Status :** ✅ Système d'Abonnement Complet et Fonctionnel

**Version :** 3.0.0

**Date :** Novembre 2025
