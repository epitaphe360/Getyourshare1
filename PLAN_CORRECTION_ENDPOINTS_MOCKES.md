# 📋 Plan de Correction des Endpoints Mockés

## 🎯 Objectif
Remplacer tous les endpoints qui retournent des données statiques par des requêtes réelles vers la base de données Supabase.

## 📊 Liste des Endpoints Mockés à Corriger

### 1. **Paiements & Historique**
- ❌ `GET /api/payments/history` (ligne ~2042)
  - **Mock**: Retourne 2 paiements statiques
  - **Table DB**: `commissions` + `payouts` (à vérifier)
  - **Action**: Récupérer l'historique réel des commissions payées

### 2. **Analytics Merchant**
- ❌ `GET /api/analytics/merchant/sales-chart` (ligne ~2074)
  - **Mock**: Retourne 7 jours de données générées
  - **Table DB**: `sales` ou `orders`
  - **Action**: Agréger les ventes réelles par jour

- ❌ `GET /api/analytics/merchant/products-performance` (ligne ~?)
  - **Mock**: Top 5 produits statiques
  - **Table DB**: `products` + `sales`
  - **Action**: GROUP BY product_id avec SUM(sales)

- ❌ `GET /api/analytics/merchant/affiliates-leaderboard` (ligne ~?)
  - **Mock**: Top affiliés statiques
  - **Table DB**: `users` (influencers) + `commissions`
  - **Action**: Classement par total commissions

### 3. **Analytics Influencer**
- ❌ `GET /api/analytics/influencer/earnings-chart` (ligne ~?)
  - **Mock**: 4 semaines de gains statiques
  - **Table DB**: `commissions`
  - **Action**: Agréger par semaine

- ❌ `GET /api/analytics/overview` (ligne ~?)
  - **Mock**: Stats statiques (clics, conversions, balance)
  - **Tables DB**: `clicks`, `conversions`, `commissions`
  - **Action**: Compter/sommer les vraies données

### 4. **Liens d'Affiliation**
- ❌ `GET /api/affiliate-links` (ligne ~?)
  - **Mock**: Liste de liens statiques
  - **Table DB**: `affiliate_links`
  - **Action**: SELECT avec user_id

- ❌ `POST /api/affiliate-links/generate` (ligne ~?)
  - **Mock**: Génère ID aléatoire
  - **Table DB**: `affiliate_links`
  - **Action**: INSERT avec code unique

### 5. **Campagnes**
- ❌ `GET /api/campaigns` (ligne ~?)
  - **Mock**: Liste de campagnes statiques
  - **Table DB**: `campaigns`
  - **Action**: SELECT * FROM campaigns WHERE user_id = ...

- ❌ `POST /api/campaigns` (ligne ~?)
  - **Mock**: Crée campagne avec ID random
  - **Table DB**: `campaigns`
  - **Action**: INSERT INTO campaigns

### 6. **Produits**
- ❌ `GET /api/products` (ligne ~?)
  - **Mock**: Liste produits statiques
  - **Table DB**: `products`
  - **Action**: SELECT avec filtres merchant_id

- ❌ `GET /api/products/my-products` (ligne ~3378)
  - **Mock**: 1 produit statique
  - **Table DB**: `products`
  - **Action**: SELECT WHERE merchant_id = user.id

### 7. **Liens Compagnie**
- ❌ `GET /api/company/links/my-company-links` (ligne ~3374)
  - **Mock**: 1 lien statique
  - **Table DB**: `company_links`
  - **Action**: SELECT WHERE company_id = user.company_id

- ❌ `POST /api/company/links/generate` (ligne ~3386)
  - **Mock**: Génère lien avec random ID
  - **Table DB**: `company_links`
  - **Action**: INSERT avec tracking

### 8. **Équipe**
- ❌ `GET /api/team/members` (ligne ~3382)
  - **Mock**: 1 membre statique
  - **Table DB**: `team_members`
  - **Action**: SELECT WHERE company_id = ...

### 9. **Statistiques Dashboard**
- ❌ `GET /api/stats` ou `/api/analytics/*`
  - **Mock**: Nombreuses stats statiques
  - **Tables DB**: Multiples (clicks, sales, commissions)
  - **Action**: Requêtes d'agrégation complexes

### 10. **Payouts**
- ❌ `GET /api/payouts` (ligne ~3837)
  - **Mock**: 1 payout statique
  - **Table DB**: `payouts`
  - **Action**: SELECT WHERE influencer_id = user.id

## 🗄️ Tables de Base de Données Nécessaires

### Tables Existantes (à vérifier)
- ✅ `users` (avec rôles: admin, merchant, influencer)
- ✅ `campaigns`
- ✅ `products`
- ✅ `affiliate_links`
- ✅ `commissions`
- ✅ `clicks` (tracking)
- ✅ `conversions` (sales)
- ✅ `platform_settings` (créée)
- ✅ `moderation_queue` (créée)

### Tables à Créer/Vérifier
- ❓ `payouts` (historique des paiements effectués)
- ❓ `company_links` (liens tracking entreprise)
- ❓ `team_members` (membres d'équipe)
- ❓ `sales` ou `orders` (commandes)
- ❓ `clicks` (tracking des clics)

## 📝 Plan d'Action Priorisé

### Phase 1: Analytics Essentiels (HAUTE PRIORITÉ)
1. **GET /api/analytics/overview** → Stats dashboard influencer
2. **GET /api/analytics/merchant/sales-chart** → Graphique ventes
3. **GET /api/affiliate-links** → Liste des liens réels
4. **GET /api/payments/history** → Historique paiements

### Phase 2: CRUD Basiques (MOYENNE PRIORITÉ)
5. **GET /api/products/my-products** → Mes produits
6. **GET /api/campaigns** → Mes campagnes
7. **POST /api/affiliate-links/generate** → Générer lien
8. **GET /api/payouts** → Liste des payouts

### Phase 3: Fonctionnalités Avancées (BASSE PRIORITÉ)
9. **GET /api/company/links/my-company-links** → Liens entreprise
10. **GET /api/team/members** → Membres équipe
11. Autres endpoints analytics

## 🛠️ Approche de Correction

Pour chaque endpoint :

1. **Identifier la table DB** correspondante
2. **Vérifier l'existence** de la table dans Supabase
3. **Créer la requête SQL** avec Supabase client
4. **Remplacer le mock** par la vraie requête
5. **Gérer les erreurs** (try/catch)
6. **Tester** avec données réelles
7. **Commit** les changements

## 📦 Helpers à Créer

```python
# backend/db_queries.py

async def get_user_affiliate_links(user_id: str):
    """Récupère tous les liens d'affiliation d'un influenceur"""
    
async def get_user_commissions_history(user_id: str):
    """Récupère l'historique des commissions"""
    
async def get_merchant_sales_stats(merchant_id: str, days: int = 7):
    """Stats de ventes pour un marchand"""
    
async def get_influencer_stats(influencer_id: str):
    """Stats globales pour influenceur (clics, conversions, balance)"""
```

## 🎯 Résultat Attendu

- ✅ Tous les endpoints retournent des données réelles de la DB
- ✅ Données cohérentes entre frontend et backend
- ✅ Statistiques dynamiques et mises à jour en temps réel
- ✅ Système de paiements fonctionnel avec historique
- ✅ Tracking réel des clics et conversions
- ✅ Dashboard analytics avec vraies données

## 📌 Notes Importantes

- **Performances**: Ajouter des index sur les colonnes fréquemment requêtées
- **Cache**: Considérer un cache Redis pour les stats fréquentes
- **Pagination**: Implémenter pour les listes longues
- **Filtres**: Ajouter des paramètres de filtrage (date range, status, etc.)
- **Agrégations**: Utiliser des fonctions SQL pour les calculs côté DB
