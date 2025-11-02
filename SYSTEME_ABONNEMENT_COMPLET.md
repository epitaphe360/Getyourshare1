# 🎯 SYSTÈME D'ABONNEMENT COMPLET - GUIDE D'INSTALLATION

## ✅ Ce qui a été développé

### 1. **Backend - Base de données**

#### `CREATE_SUBSCRIPTION_PLANS_TABLE.sql`
- **Table `subscription_plans`**: Plans d'abonnement centralisés
  - 4 plans merchants: Free, Starter, Pro, Enterprise
  - 3 plans influencers: Starter, Pro, Elite
  - Prix, limites, features, commission rates
- **Index et triggers** pour performance et updated_at automatique

#### `CREATE_SUBSCRIPTIONS_TABLE.sql`
- **Table `subscriptions`**: Historique et abonnements actifs
  - Statuts: active, trialing, past_due, canceled, expired
  - Périodes de facturation
  - Intégration Stripe/CMI
  - Utilisation actuelle (products, campaigns, affiliates, etc.)
- **Vue `v_active_subscriptions`**: JOIN avec subscription_plans pour accès rapide
- **Fonctions PostgreSQL**:
  - `check_subscription_limit(user_id, limit_type)`: Vérifie si limite atteinte
  - `increment_subscription_usage(user_id, type, amount)`: Incrémente utilisation
  - `decrement_subscription_usage(user_id, type, amount)`: Décrémente utilisation

### 2. **Backend - API Endpoints**

#### `subscription_endpoints_simple.py`
- **GET `/api/subscriptions/current`**: Abonnement actuel de l'utilisateur
  - Récupère depuis merchants/influencers tables existantes
  - Retourne plan, limites, usage, features
- **GET `/api/subscriptions/plans`**: Liste tous les plans disponibles
- **GET `/api/subscriptions/usage`**: Statistiques d'utilisation détaillées
- **POST `/api/subscriptions/check-limit`**: Vérifie une limite spécifique
- **POST `/api/subscriptions/upgrade`**: Changer de plan (placeholder)
- **POST `/api/subscriptions/cancel`**: Annuler abonnement (placeholder)

#### `subscription_limits_middleware.py`
Middleware pour vérifier les limites avant actions:
- `check_product_limit()`: Vérifie avant création produit
- `check_campaign_limit()`: Vérifie avant création campagne
- `check_affiliate_limit()`: Vérifie avant ajout affilié
- `check_link_limit()`: Vérifie avant création lien tracking
- `has_feature(feature_name)`: Vérifie accès à une feature
- `require_feature(feature_name)`: Bloque si feature non disponible

**Exemple d'utilisation**:
```python
@app.post("/api/products")
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(SubscriptionLimits.check_product_limit)
):
    # Créer le produit
    pass
```

### 3. **Backend - Intégration**

#### Modifications dans `server_complete.py`
- Import du router d'abonnements
- Montage du router: `app.include_router(subscription_router)`
- Message de confirmation au démarrage

### 4. **Frontend - Pages**

#### `SubscriptionManagement.js`
Page complète de gestion d'abonnement:
- **Vue d'ensemble**: Plan actuel, prix, statut
- **Statistiques d'utilisation**: Produits, campagnes, affiliés avec barres de progression
- **Liste des features**: Toutes les fonctionnalités incluses
- **Comparaison des plans**: Grille des plans disponibles
- **Upgrade/Downgrade**: Boutons pour changer de plan
- **Annulation**: Modal avec formulaire de feedback
- **Design**: Tailwind CSS avec animations et icônes Lucide

#### Modifications dans `App.js`
- Import de `SubscriptionManagement`
- Route ajoutée: `/subscription/manage`

### 5. **Configuration des Plans**

#### Plans Merchants
| Plan | Prix | Commission | Produits | Campagnes | Affiliés |
|------|------|------------|----------|-----------|----------|
| Free | 0 MAD | 5% | 10 | 5 | 50 |
| Starter | 299 MAD | 4% | 50 | 20 | 200 |
| Pro | 799 MAD | 3% | 200 | 100 | 1000 |
| Enterprise | 1999 MAD | 2% | ∞ | ∞ | ∞ |

#### Plans Influencers
| Plan | Prix | Frais Plateforme | Campagnes | Liens |
|------|------|------------------|-----------|-------|
| Starter | 0 MAD | 5% | 5 | 10 |
| Pro | 99 MAD | 3% | 50 | 100 |
| Elite | 299 MAD | 2% | ∞ | ∞ |

---

## 🚀 INSTALLATION ÉTAPE PAR ÉTAPE

### Étape 1: Créer les tables dans Supabase

1. Ouvrez **Supabase Dashboard** → SQL Editor
2. Exécutez dans l'ordre:
   ```sql
   -- 1. Créer les plans
   -- Copiez-collez le contenu de CREATE_SUBSCRIPTION_PLANS_TABLE.sql
   
   -- 2. Créer la table subscriptions
   -- Copiez-collez le contenu de CREATE_SUBSCRIPTIONS_TABLE.sql
   ```

3. Vérifiez que les tables existent:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name IN ('subscription_plans', 'subscriptions');
   ```

4. Vérifiez les 7 plans:
   ```sql
   SELECT name, code, type, price_mad FROM subscription_plans ORDER BY display_order;
   ```

### Étape 2: Tester les endpoints Backend

1. Démarrez le serveur:
   ```bash
   cd backend
   python server_complete.py
   ```

2. Vérifiez les logs:
   ```
   ✅ Subscription endpoints mounted at /api/subscriptions
   ```

3. Testez dans le navigateur ou Postman:
   ```
   GET http://localhost:8000/api/subscriptions/plans
   GET http://localhost:8000/api/subscriptions/current (avec token)
   GET http://localhost:8000/api/subscriptions/usage (avec token)
   ```

### Étape 3: Tester le Frontend

1. Démarrez l'app React:
   ```bash
   cd frontend
   npm start
   ```

2. Connectez-vous avec un compte test:
   - Email: `merchant_starter@test.com`
   - Password: `Test123!`

3. Accédez à:
   - **Dashboard**: `http://localhost:3000/merchant-dashboard`
     - ✅ Carte d'abonnement devrait s'afficher
   - **Gestion**: `http://localhost:3000/subscription/manage`
     - ✅ Page complète de gestion

### Étape 4: Créer des abonnements réels (optionnel)

Si vous voulez migrer les données existantes vers la nouvelle table `subscriptions`:

```sql
-- Créer abonnements pour tous les merchants existants
INSERT INTO subscriptions (
    user_id, 
    plan_id, 
    status, 
    current_period_start, 
    current_period_end,
    current_products,
    current_campaigns,
    current_affiliates
)
SELECT 
    m.user_id,
    sp.id as plan_id,
    m.subscription_status,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '1 month',
    3, -- mock data
    1,
    8
FROM merchants m
JOIN subscription_plans sp ON sp.code = 'merchant_' || m.subscription_plan
WHERE NOT EXISTS (
    SELECT 1 FROM subscriptions WHERE user_id = m.user_id
);

-- Pareil pour influencers
INSERT INTO subscriptions (
    user_id, 
    plan_id, 
    status, 
    current_period_start, 
    current_period_end,
    current_campaigns
)
SELECT 
    i.user_id,
    sp.id as plan_id,
    i.subscription_status,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '1 month',
    5
FROM influencers i
JOIN subscription_plans sp ON sp.code = 'influencer_' || i.subscription_plan
WHERE NOT EXISTS (
    SELECT 1 FROM subscriptions WHERE user_id = i.user_id
);
```

---

## 🔧 UTILISATION DANS VOTRE CODE

### 1. Vérifier les limites avant création

#### Dans un endpoint de création de produit:
```python
from subscription_limits_middleware import SubscriptionLimits
from auth import get_current_user

@app.post("/api/products")
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(SubscriptionLimits.check_product_limit)
):
    # Si on arrive ici, la limite n'est pas atteinte
    # Créer le produit...
    
    # Incrémenter l'utilisation
    await increment_subscription_usage(current_user["id"], "products", 1)
    
    return {"success": True}
```

### 2. Vérifier l'accès à une feature

```python
@app.get("/api/analytics/advanced")
async def get_advanced_analytics(
    current_user: dict = Depends(get_current_user)
):
    # Vérifier si l'utilisateur a accès aux analytics avancées
    has_access = await SubscriptionLimits.has_feature("analytics_advanced", current_user)
    
    if not has_access:
        raise HTTPException(
            status_code=403, 
            detail="Upgrade to Pro or Enterprise for advanced analytics"
        )
    
    # Retourner les analytics...
```

### 3. Bloquer l'accès API selon le plan

```python
@app.get("/api/external/data")
async def api_endpoint(
    api_key: str,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(lambda u=Depends(get_current_user): 
                     SubscriptionLimits.require_feature("api_access", u))
):
    # Seuls les utilisateurs avec accès API peuvent arriver ici
    return {"data": "..."}
```

---

## 📊 FEATURES PAR PLAN

### Features vérifiables avec `has_feature()`

- `api_access`: Accès à l'API externe
- `white_label`: Personnalisation complète
- `analytics_advanced`: Analytics avancées/premium
- `priority_support`: Support prioritaire/24/7/dédié
- `instant_payout`: Paiement instantané
- `custom_links`: Liens personnalisés
- `account_manager`: Account manager dédié
- `unlimited`: Limites illimitées

---

## 🎨 PERSONNALISATION

### Modifier les limites d'un plan

```sql
UPDATE subscription_plans
SET 
    max_products = 100,
    max_campaigns = 50
WHERE code = 'merchant_starter';
```

### Ajouter une nouvelle feature

```sql
UPDATE subscription_plans
SET features = features || '["Nouvelle feature"]'::jsonb
WHERE code = 'merchant_pro';
```

### Changer le prix

```sql
UPDATE subscription_plans
SET price_mad = 399.00
WHERE code = 'merchant_starter';
```

---

## 🐛 DÉPANNAGE

### Les endpoints ne marchent pas
```bash
# Vérifiez que le module est importé
cd backend
python -c "from subscription_endpoints_simple import router; print('OK')"
```

### La page React crash
```bash
# Vérifiez les imports
cd frontend/src/pages/subscription
ls -la SubscriptionManagement.js

# Vérifiez la route dans App.js
grep -n "SubscriptionManagement" ../App.js
```

### Les données ne s'affichent pas
1. Vérifiez que l'utilisateur a un profil dans `merchants` ou `influencers`
2. Vérifiez le token JWT dans localStorage
3. Ouvrez la console navigateur pour voir les erreurs réseau

---

## 📈 PROCHAINES ÉTAPES

### Fonctionnalités à ajouter:

1. **Intégration paiement CMI**:
   - Endpoints pour initier paiement
   - Webhooks pour confirmer paiement
   - Mise à jour automatique du statut

2. **Factures automatiques**:
   - Génération PDF
   - Email de facturation
   - Historique des paiements

3. **Essai gratuit**:
   - 14 jours gratuits
   - Conversion automatique
   - Reminder emails

4. **Upgrade automatique**:
   - Paiement prorata
   - Confirmation email
   - Mise à jour instantanée

5. **Analytics avancées**:
   - Revenus par plan
   - Taux de conversion
   - Churn rate

---

## ✅ CHECKLIST FINALE

- [ ] Tables créées dans Supabase
- [ ] 7 plans insérés et visibles
- [ ] Backend démarre sans erreur
- [ ] Endpoints `/api/subscriptions/*` accessibles
- [ ] Frontend compile sans erreur
- [ ] Page `/subscription/manage` accessible
- [ ] Connexion avec compte test fonctionne
- [ ] Dashboard affiche la carte d'abonnement
- [ ] Les limites s'affichent correctement
- [ ] Tests avec les 7 comptes différents

---

**🎉 FÉLICITATIONS !**

Vous avez maintenant un système d'abonnement SaaS complet et fonctionnel pour votre plateforme d'affiliation marocaine !
