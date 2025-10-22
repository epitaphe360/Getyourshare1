# 📊 DOCUMENTATION BASE DE DONNÉES - SHAREYOURSALES

## Vue d'ensemble

Cette base de données PostgreSQL/Supabase gère l'intégralité de la plateforme ShareYourSales avec **15 tables principales** et **3 vues** pour les rapports.

---

## 🗂️ TABLES PRINCIPALES

### 1. **users** - Utilisateurs
Gère tous les utilisateurs de la plateforme (admins, merchants, influencers).

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| email | VARCHAR(255) | Email unique |
| password_hash | VARCHAR(255) | Mot de passe haché (bcrypt) |
| role | VARCHAR(50) | Rôle: 'admin', 'merchant', 'influencer' |
| phone | VARCHAR(20) | Numéro de téléphone |
| phone_verified | BOOLEAN | Téléphone vérifié |
| **two_fa_enabled** | BOOLEAN | 2FA activé (par défaut TRUE) |
| **two_fa_code** | VARCHAR(6) | Code 2FA temporaire |
| **two_fa_expires_at** | TIMESTAMP | Expiration du code 2FA |
| last_login | TIMESTAMP | Dernière connexion |
| is_active | BOOLEAN | Compte actif |
| created_at | TIMESTAMP | Date de création |
| updated_at | TIMESTAMP | Dernière mise à jour |

**Relations:**
- 1 user → 1 merchant (user_id)
- 1 user → 1 influencer (user_id)

---

### 2. **user_sessions** - Sessions de connexion
Gère les sessions JWT pour la sécurité.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| user_id | UUID | Référence vers users |
| session_token | VARCHAR(500) | Token JWT |
| ip_address | INET | Adresse IP |
| user_agent | TEXT | Navigateur/Device |
| expires_at | TIMESTAMP | Expiration du token |

---

### 3. **merchants** - Entreprises/Compagnies
Profils des entreprises qui proposent des produits.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| user_id | UUID | Référence vers users |
| company_name | VARCHAR(255) | Nom de l'entreprise |
| industry | VARCHAR(100) | Secteur d'activité |
| **category** | VARCHAR(100) | 15 catégories disponibles* |
| address | TEXT | Adresse physique |
| tax_id | VARCHAR(50) | Numéro TVA/SIRET |
| website | VARCHAR(255) | Site web |
| logo_url | TEXT | URL du logo |
| **subscription_plan** | VARCHAR(50) | 'free', 'starter', 'pro', 'enterprise' |
| **commission_rate** | DECIMAL(5,2) | Frais plateforme (%) |
| **monthly_fee** | DECIMAL(10,2) | Abonnement mensuel |
| total_sales | DECIMAL(15,2) | Total des ventes |
| total_commission_paid | DECIMAL(15,2) | Total commissions versées |

***15 Catégories d'entreprises:**
1. E-commerce
2. Services en ligne
3. Voyage et tourisme
4. Mode et lifestyle
5. Beauté et bien-être
6. Technologie
7. Finance et assurance
8. Santé et bien-être
9. Alimentation et boissons
10. Divertissement et médias
11. Automobile
12. Immobilier
13. Sport et fitness
14. Éducation
15. Bricolage et décoration

---

### 4. **influencers** - Influenceurs
Profils des influenceurs/affiliés.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| user_id | UUID | Référence vers users |
| username | VARCHAR(100) | Pseudonyme unique |
| full_name | VARCHAR(255) | Nom complet |
| bio | TEXT | Biographie |
| profile_picture_url | TEXT | Photo de profil |
| category | VARCHAR(100) | Niche (Mode, Beauté, etc.) |
| **influencer_type** | VARCHAR(50) | 'nano', 'micro', 'macro', 'mega' |
| **audience_size** | INTEGER | Nombre d'abonnés |
| **engagement_rate** | DECIMAL(5,2) | Taux d'engagement (%) |
| **subscription_plan** | VARCHAR(50) | 'starter', 'pro' |
| **platform_fee_rate** | DECIMAL(5,2) | Frais plateforme (%) |
| **monthly_fee** | DECIMAL(10,2) | Abonnement mensuel |
| **social_links** | JSONB | {instagram, youtube, tiktok, etc.} |
| total_clicks | INTEGER | Total clics générés |
| total_sales | INTEGER | Total ventes générées |
| **total_earnings** | DECIMAL(15,2) | Total gagné |
| **balance** | DECIMAL(15,2) | Solde disponible |
| payment_method | VARCHAR(50) | PayPal, Bank, Crypto |
| payment_details | JSONB | Détails de paiement sécurisés |

**Types d'influenceurs:**
- **Nano**: < 10K abonnés
- **Micro**: 10K - 100K abonnés
- **Macro**: 100K - 1M abonnés
- **Mega**: > 1M abonnés

---

### 5. **products** - Produits
Catalogue de produits des merchants.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| merchant_id | UUID | Référence vers merchants |
| name | VARCHAR(255) | Nom du produit |
| description | TEXT | Description détaillée |
| **category** | VARCHAR(100) | Mode, Beauté, Tech, etc. |
| price | DECIMAL(10,2) | Prix du produit |
| currency | VARCHAR(3) | EUR, USD, etc. |
| **commission_rate** | DECIMAL(5,2) | Commission pour affiliés (%) |
| **commission_type** | VARCHAR(20) | 'percentage' ou 'fixed' |
| **images** | JSONB | Array d'URLs d'images |
| **videos** | JSONB | Array d'URLs de vidéos |
| **specifications** | JSONB | Caractéristiques techniques |
| stock_quantity | INTEGER | Stock disponible |
| is_available | BOOLEAN | Disponible à la vente |
| slug | VARCHAR(255) | URL-friendly name |
| total_views | INTEGER | Nombre de vues |
| total_clicks | INTEGER | Clics sur liens affiliés |
| total_sales | INTEGER | Nombre de ventes |

**Catégories de produits:**
Mode, Beauté, Technologie, Alimentation, Artisanat, Sport, Santé, Maison, Autre

**Taux de commission par catégorie (recommandés):**
- Mode: 15-20%
- Beauté: 18-22%
- Technologie: 12-18%
- Alimentation: 10-15%
- Artisanat: 20-25%

---

### 6. **trackable_links** - Liens d'affiliation
Liens de tracking uniques pour chaque influenceur/produit.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| product_id | UUID | Référence vers products |
| influencer_id | UUID | Référence vers influencers |
| **unique_code** | VARCHAR(50) | Code unique crypté |
| **full_url** | TEXT | URL complète du lien |
| **short_url** | TEXT | URL raccourcie |
| **has_discount** | BOOLEAN | Offre de rabais active |
| **discount_code** | VARCHAR(50) | Code promo |
| **discount_percentage** | DECIMAL(5,2) | Pourcentage de réduction |
| clicks | INTEGER | Nombre de clics |
| unique_clicks | INTEGER | Clics uniques (IP tracking) |
| sales | INTEGER | Nombre de ventes |
| **conversion_rate** | DECIMAL(5,2) | Taux de conversion (%) |
| **total_revenue** | DECIMAL(15,2) | Revenus générés |
| **total_commission** | DECIMAL(15,2) | Commissions gagnées |
| is_active | BOOLEAN | Lien actif |
| expires_at | TIMESTAMP | Date d'expiration |

**Contrainte:** UNIQUE(product_id, influencer_id)

---

### 7. **sales** - Ventes
Enregistrement de toutes les ventes.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| link_id | UUID | Lien d'affiliation utilisé |
| product_id | UUID | Produit vendu |
| influencer_id | UUID | Influenceur ayant généré la vente |
| merchant_id | UUID | Merchant du produit |
| customer_email | VARCHAR(255) | Email client |
| customer_name | VARCHAR(255) | Nom client |
| customer_ip | INET | IP du client |
| quantity | INTEGER | Quantité achetée |
| amount | DECIMAL(10,2) | Montant total |
| **influencer_commission** | DECIMAL(10,2) | Commission influenceur |
| **platform_commission** | DECIMAL(10,2) | Commission plateforme |
| **merchant_revenue** | DECIMAL(10,2) | Revenus merchant |
| **status** | VARCHAR(50) | 'pending', 'completed', 'refunded', 'cancelled' |
| **payment_status** | VARCHAR(50) | 'pending', 'paid' |
| sale_timestamp | TIMESTAMP | Date/heure de la vente |
| payment_processed_at | TIMESTAMP | Date de traitement du paiement |

---

### 8. **commissions** - Paiements aux influenceurs
Gestion des commissions à verser.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| sale_id | UUID | Vente associée |
| influencer_id | UUID | Influenceur bénéficiaire |
| amount | DECIMAL(10,2) | Montant de la commission |
| **status** | VARCHAR(50) | 'pending', 'approved', 'paid', 'cancelled' |
| **payment_method** | VARCHAR(50) | PayPal, Bank Transfer, Crypto |
| transaction_id | VARCHAR(255) | ID transaction externe |
| paid_at | TIMESTAMP | Date de paiement |

---

### 9. **engagement_metrics** - Métriques d'engagement
Statistiques détaillées par lien/produit/influenceur.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| link_id | UUID | Lien suivi |
| product_id | UUID | Produit concerné |
| influencer_id | UUID | Influenceur |
| **likes** | INTEGER | Nombre de likes |
| **comments** | INTEGER | Nombre de commentaires |
| **shares** | INTEGER | Nombre de partages |
| **saves** | INTEGER | Nombre de sauvegardes |
| impressions | INTEGER | Impressions |
| clicks | INTEGER | Clics |
| conversions | INTEGER | Conversions |
| **conversion_rate** | DECIMAL(5,2) | Taux de conversion (%) |
| **roi_percentage** | DECIMAL(10,2) | ROI (%) |
| **vep_value** | DECIMAL(15,2) | Valeur Économique Visibilité |
| **cpa** | DECIMAL(10,2) | Coût Par Acquisition |
| metric_date | DATE | Date des métriques |

**Contrainte:** UNIQUE(link_id, metric_date)

---

### 10. **campaigns** - Campagnes marketing
Campagnes marketing des merchants.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| merchant_id | UUID | Merchant organisateur |
| name | VARCHAR(255) | Nom de la campagne |
| description | TEXT | Description |
| **budget** | DECIMAL(15,2) | Budget total |
| **spent** | DECIMAL(15,2) | Dépensé |
| start_date | DATE | Date de début |
| end_date | DATE | Date de fin |
| **target_audience** | JSONB | {age_range, gender, interests, location} |
| **status** | VARCHAR(50) | 'draft', 'active', 'paused', 'completed' |
| total_clicks | INTEGER | Total clics |
| total_conversions | INTEGER | Total conversions |
| total_revenue | DECIMAL(15,2) | Revenus générés |
| **roi** | DECIMAL(10,2) | ROI de la campagne |

---

### 11. **ai_analytics** - Analyses IA
Intelligence artificielle pour recommandations.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| product_id | UUID | Produit analysé |
| merchant_id | UUID | Merchant concerné |
| **predicted_sales** | INTEGER | Ventes prédites |
| **trend_score** | DECIMAL(5,2) | Score de tendance (-100 à +100) |
| **recommended_strategy** | TEXT | Stratégie recommandée par IA |
| **recommended_budget** | DECIMAL(15,2) | Budget recommandé |
| **recommended_influencers** | JSONB | Array d'IDs d'influenceurs |
| **audience_insights** | JSONB | Insights démographiques |
| **competitor_analysis** | JSONB | Analyse concurrentielle |
| analysis_period_start | DATE | Début période d'analyse |
| analysis_period_end | DATE | Fin période d'analyse |
| **confidence_score** | DECIMAL(5,2) | Confiance (0-100%) |

---

### 12. **subscriptions** - Abonnements
Gestion des abonnements utilisateurs.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| user_id | UUID | Utilisateur |
| **plan_type** | VARCHAR(50) | Type de plan* |
| **monthly_fee** | DECIMAL(10,2) | Tarif mensuel |
| **commission_rate** | DECIMAL(5,2) | Frais plateforme (%) |
| max_products | INTEGER | Limite produits |
| max_links | INTEGER | Limite liens |
| max_users | INTEGER | Limite utilisateurs |
| **features** | JSONB | Array de features |
| start_date | DATE | Début |
| end_date | DATE | Fin |
| next_billing_date | DATE | Prochaine facturation |
| **status** | VARCHAR(50) | 'active', 'cancelled', 'expired', 'trial' |
| payment_method | VARCHAR(50) | Méthode de paiement |

**Plans disponibles:**
- **Merchants**: free, starter, pro, enterprise
- **Influencers**: influencer_starter, influencer_pro

**Grille tarifaire:**

| Plan Merchant | Prix/mois | Commission | Limites |
|---------------|-----------|------------|---------|
| Free | 0€ | 7% | 1 compte, 10 liens |
| Starter | 49€ | 5% | 5 comptes, 100 liens |
| Pro | 199€ | 3% | 20 comptes, 500 liens, IA |
| Enterprise | Sur devis | 1-2% | Illimité |

| Plan Influencer | Prix/mois | Frais plateforme |
|-----------------|-----------|------------------|
| Starter | 9,90€ | 5% |
| Pro | 29,90€ | 3% |

---

### 13. **payments** - Historique paiements
Tous les paiements de la plateforme.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| user_id | UUID | Utilisateur |
| subscription_id | UUID | Abonnement associé |
| amount | DECIMAL(10,2) | Montant |
| **payment_type** | VARCHAR(50) | 'subscription', 'commission', 'refund' |
| **payment_method** | VARCHAR(50) | 'credit_card', 'paypal', 'bank_transfer', 'crypto' |
| transaction_id | VARCHAR(255) | ID transaction unique |
| gateway_response | JSONB | Réponse gateway |
| **status** | VARCHAR(50) | 'pending', 'completed', 'failed', 'refunded' |
| transaction_date | TIMESTAMP | Date transaction |

---

### 14. **reviews** - Avis & Notes
Système de notation des produits.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| product_id | UUID | Produit noté |
| user_id | UUID | Utilisateur |
| **rating** | INTEGER | Note 1-5 |
| title | VARCHAR(255) | Titre de l'avis |
| comment | TEXT | Commentaire |
| is_verified_purchase | BOOLEAN | Achat vérifié |
| is_approved | BOOLEAN | Modéré/approuvé |
| helpful_count | INTEGER | Nombre de "utile" |

---

### 15. **categories** - Catégories
Catégories de produits hiérarchiques.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| name | VARCHAR(100) | Nom de la catégorie |
| slug | VARCHAR(100) | URL-friendly |
| description | TEXT | Description |
| parent_id | UUID | Catégorie parente |
| icon_url | TEXT | URL icône |
| display_order | INTEGER | Ordre d'affichage |
| is_active | BOOLEAN | Active |

---

### 16. **click_tracking** - Suivi détaillé des clics
Tracking granulaire de chaque clic.

| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| link_id | UUID | Lien cliqué |
| **ip_address** | INET | IP du visiteur |
| **user_agent** | TEXT | Navigateur/Device |
| **referrer** | TEXT | Source du clic |
| **country** | VARCHAR(2) | Pays (code ISO) |
| **city** | VARCHAR(100) | Ville |
| **device_type** | VARCHAR(50) | Mobile, Desktop, Tablet |
| **os** | VARCHAR(50) | Système d'exploitation |
| **browser** | VARCHAR(50) | Navigateur |
| session_id | VARCHAR(255) | ID session |
| is_unique_visitor | BOOLEAN | Premier clic de l'IP |
| clicked_at | TIMESTAMP | Date/heure du clic |

---

## 📊 VUES (Views)

### 1. **influencer_performance**
Vue agrégée des performances des influenceurs.

```sql
SELECT 
    id, username, full_name, influencer_type, category,
    total_links, total_clicks, total_sales, total_revenue,
    total_commission, balance, total_earnings
FROM influencers
```

### 2. **product_performance**
Vue agrégée des performances des produits.

```sql
SELECT 
    product.id, name, category, merchant_name,
    total_links, total_clicks, total_sales, total_revenue,
    average_rating, review_count
FROM products
```

### 3. **admin_dashboard_stats**
Statistiques globales pour le dashboard admin.

```sql
SELECT 
    total_influencers, total_merchants, active_products,
    total_platform_revenue, total_commissions_paid,
    total_sales, active_links
```

---

## 🔐 SÉCURITÉ

### Authentification 2FA
- **Code SMS** envoyé au numéro de téléphone
- Code de 6 chiffres valide 5 minutes
- Stocké dans `users.two_fa_code` avec `two_fa_expires_at`

### Mots de passe
- Hachés avec **bcrypt** (rounds: 12)
- Politique: min 8 caractères, 1 majuscule, 1 chiffre

### Sessions
- Tokens JWT stockés dans `user_sessions`
- Expiration: 24 heures
- Tracking IP et User-Agent

---

## 🎯 FLUX DE DONNÉES PRINCIPAUX

### 1. Inscription Influenceur
1. Création dans `users` (role: influencer)
2. Création dans `influencers`
3. Création dans `subscriptions` (plan starter par défaut)

### 2. Création Lien d'Affiliation
1. Influenceur sélectionne produit
2. Génération `unique_code` crypté
3. Insertion dans `trackable_links`
4. URLs full + short générées

### 3. Vente via Lien
1. Clic enregistré dans `click_tracking`
2. Achat → Insertion dans `sales`
3. Calcul commissions:
   - `influencer_commission` = amount × product.commission_rate
   - `platform_commission` = amount × (influencer.platform_fee_rate + merchant.commission_rate)
   - `merchant_revenue` = amount - influencer_commission - platform_commission
4. Création dans `commissions` (status: pending)
5. Mise à jour statistiques dans `engagement_metrics`

### 4. Paiement Influenceur
1. Admin approuve commission (status: approved)
2. Paiement traité (PayPal/Bank/Crypto)
3. Création dans `payments`
4. Update `commissions` (status: paid, paid_at)
5. Update `influencers.balance` et `total_earnings`

---

## 📈 CALCULS CLÉS

### ROI Marketing
```sql
ROI = ((total_revenue - total_spent) / total_spent) × 100
```

### Taux de Conversion
```sql
Conversion Rate = (conversions / clicks) × 100
```

### VEP (Valeur Économique Visibilité)
```sql
VEP = (impressions × estimated_cpm) / 1000
```

### CPA (Coût Par Acquisition)
```sql
CPA = total_spent / total_conversions
```

---

## 🔍 INDEX CRITIQUES

Performance optimisée sur:
- `users.email`, `users.role`
- `trackable_links.unique_code` (recherches rapides)
- `sales.sale_timestamp` (rapports temporels)
- `click_tracking.ip_address`, `clicked_at` (anti-fraude)

---

## 🔄 TRIGGERS AUTOMATIQUES

- **update_updated_at**: Met à jour `updated_at` sur UPDATE
- Appliqué aux tables: users, merchants, influencers, products, trackable_links

---

## 📦 DONNÉES INITIALES (Seed)

- 8 catégories de base
- 1 compte admin: `admin@shareyoursales.com` / `Admin123!`

---

**Version:** 1.0  
**Date:** Mars 2024  
**Type de Base:** PostgreSQL 14+ / Supabase  
**Total Tables:** 16  
**Total Vues:** 3
