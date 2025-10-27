# 📊 ANALYSE COMPLÈTE - TABLES DE LA BASE DE DONNÉES

**Date:** 26 Octobre 2025  
**Application:** ShareYourSales (Plateforme d'affiliation)  
**Base de données:** PostgreSQL via Supabase

---

## 🎯 OBJECTIF

Analyser **TOUTES** les tables existantes et identifier les tables manquantes nécessaires au bon fonctionnement de l'application.

---

## ✅ TABLES EXISTANTES (Dans schema.sql)

### 1️⃣ **AUTHENTIFICATION & UTILISATEURS**

#### `users` ✅
**Statut:** Créée  
**Colonnes:**
- `id` (UUID, PK)
- `email` (VARCHAR, UNIQUE)
- `password_hash` (VARCHAR)
- `role` (admin, merchant, influencer)
- `phone` (VARCHAR)
- `phone_verified` (BOOLEAN)
- `two_fa_enabled` (BOOLEAN) ← **Colonne 2FA présente**
- `two_fa_code` (VARCHAR)
- `two_fa_expires_at` (TIMESTAMP)
- `last_login` (TIMESTAMP)
- `is_active` (BOOLEAN)
- `created_at`, `updated_at`

**Problème identifié:** `two_fa_enabled` défini par défaut à `TRUE`, mais certains utilisateurs ont `FALSE`

#### `user_sessions` ✅
**Statut:** Créée  
**Colonnes:**
- `id`, `user_id`, `session_token`, `ip_address`, `user_agent`, `expires_at`, `created_at`

---

### 2️⃣ **PROFILS UTILISATEURS**

#### `merchants` ✅
**Statut:** Créée  
**Colonnes:**
- Infos entreprise: `company_name`, `industry`, `category`, `address`, `tax_id`, `website`, `logo_url`, `description`
- Abonnement: `subscription_plan`, `subscription_status`, `monthly_fee`
- Finances: `commission_rate`, `total_sales`, `total_commission_paid`

#### `influencers` ✅
**Statut:** Créée  
**Colonnes:**
- Profil: `username`, `full_name`, `bio`, `profile_picture_url`, `category`, `influencer_type`
- Audience: `audience_size`, `engagement_rate`
- Réseaux sociaux: `social_links` (JSONB)
- Finances: `balance`, `total_earnings`, `payment_method`, `payment_details`
- Statistiques: `total_clicks`, `total_sales`

---

### 3️⃣ **CATALOGUE PRODUITS**

#### `products` ✅
**Statut:** Créée  
**Colonnes:**
- Informations: `name`, `description`, `category`, `price`, `currency`
- Commission: `commission_rate`, `commission_type`
- Médias: `images`, `videos` (JSONB)
- Stock: `stock_quantity`, `is_available`
- SEO: `slug`, `meta_description`
- Stats: `total_views`, `total_clicks`, `total_sales`

#### `categories` ✅
**Statut:** Créée avec données initiales (Mode, Beauté, Technologie, etc.)

---

### 4️⃣ **SYSTÈME DE TRACKING**

#### `trackable_links` ✅
**Statut:** Créée  
**Colonnes:**
- Identifiants: `product_id`, `influencer_id`, `unique_code`, `full_url`, `short_url`
- Offres: `has_discount`, `discount_code`, `discount_percentage`
- Statistiques: `clicks`, `unique_clicks`, `sales`, `conversion_rate`, `total_revenue`, `total_commission`
- Status: `is_active`, `expires_at`

**Problème potentiel:** Le schéma utilise `unique_code`, mais le code backend utilise `short_code`

#### `click_tracking` ✅
**Statut:** Créée  
**Colonnes:**
- Tracking: `link_id`, `ip_address`, `user_agent`, `referrer`
- Géolocalisation: `country`, `city`
- Device: `device_type`, `os`, `browser`
- Session: `session_id`, `is_unique_visitor`

---

### 5️⃣ **VENTES & COMMISSIONS**

#### `sales` ✅
**Statut:** Créée  
**Colonnes:**
- Relations: `link_id`, `product_id`, `influencer_id`, `merchant_id`
- Client: `customer_email`, `customer_name`, `customer_ip`
- Détails: `quantity`, `amount`, `currency`
- Commissions: `influencer_commission`, `platform_commission`, `merchant_revenue`
- Status: `status`, `payment_status`

#### `commissions` ✅
**Statut:** Créée  
**Colonnes:**
- `sale_id`, `influencer_id`, `amount`, `currency`
- Status: `status` (pending, approved, paid, cancelled)
- Paiement: `payment_method`, `transaction_id`, `paid_at`

---

### 6️⃣ **ANALYTICS & MÉTRIQUES**

#### `engagement_metrics` ✅
**Statut:** Créée  
**Colonnes:**
- Engagement: `likes`, `comments`, `shares`, `saves`
- Conversion: `impressions`, `clicks`, `conversions`, `conversion_rate`
- Financier: `roi_percentage`, `vep_value`, `cpa`

#### `ai_analytics` ✅
**Statut:** Créée  
**Colonnes:**
- Prédictions: `predicted_sales`, `trend_score`
- Recommandations: `recommended_strategy`, `recommended_budget`, `recommended_influencers`
- Insights: `audience_insights`, `competitor_analysis`

---

### 7️⃣ **CAMPAGNES MARKETING**

#### `campaigns` ✅
**Statut:** Créée  
**Colonnes:**
- Infos: `merchant_id`, `name`, `description`
- Budget: `budget`, `spent`
- Période: `start_date`, `end_date`
- Ciblage: `target_audience` (JSONB)
- Performance: `total_clicks`, `total_conversions`, `total_revenue`, `roi`

---

### 8️⃣ **ABONNEMENTS & PAIEMENTS**

#### `subscriptions` ✅
**Statut:** Créée  
**Colonnes:**
- Plan: `plan_type`, `monthly_fee`, `commission_rate`
- Limites: `max_products`, `max_links`, `max_users`
- Features: `features` (JSONB)
- Période: `start_date`, `end_date`, `next_billing_date`
- Status: `status` (active, cancelled, expired, trial)

**Note:** Cette table semble redondante avec `user_subscriptions` (à créer)

#### `payments` ✅
**Statut:** Créée  
**Colonnes:**
- Relations: `user_id`, `subscription_id`
- Montant: `amount`, `currency`
- Type: `payment_type` (subscription, commission, refund)
- Méthode: `payment_method`, `transaction_id`
- Status: `status` (pending, completed, failed, refunded)

---

### 9️⃣ **AVIS & ÉVALUATIONS**

#### `reviews` ✅
**Statut:** Créée  
**Colonnes:**
- `product_id`, `user_id`, `rating` (1-5), `title`, `comment`
- Validation: `is_verified_purchase`, `is_approved`
- Social: `helpful_count`

---

### 🔟 **PARAMÈTRES**

#### `smtp_settings` ✅
**Statut:** Créée  
**Colonnes:**
- Configuration email: `host`, `port`, `username`, `password`, `from_email`, `from_name`, `encryption`

---

## ❌ TABLES MANQUANTES (Identifiées)

### 🔴 **PRIORITÉ HAUTE**

#### 1. `user_subscriptions` ❌
**Raison:** Page Subscription.js nécessite cette table  
**Colonnes requises:**
```sql
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    plan_type TEXT (free, starter, pro, enterprise, merchant_basic, etc.),
    status TEXT (active, cancelled, expired, pending),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    auto_renew BOOLEAN,
    payment_method TEXT,
    last_payment_date TIMESTAMP,
    next_billing_date TIMESTAMP
);
```

#### 2. `support_tickets` ❌
**Raison:** Page Support.js nécessite cette table  
**Colonnes requises:**
```sql
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    subject TEXT,
    category TEXT (technical, billing, account, feature_request, other),
    priority TEXT (low, medium, high, urgent),
    status TEXT (open, in_progress, waiting_response, resolved, closed),
    description TEXT,
    assigned_to UUID REFERENCES users(id),
    resolved_at TIMESTAMP
);
```

#### 3. `ticket_messages` ❌
**Raison:** Système de messages dans les tickets de support  
**Colonnes requises:**
```sql
CREATE TABLE ticket_messages (
    id UUID PRIMARY KEY,
    ticket_id UUID REFERENCES support_tickets(id),
    user_id UUID REFERENCES users(id),
    message TEXT,
    is_internal BOOLEAN,
    attachments JSONB,
    created_at TIMESTAMP
);
```

#### 4. `video_tutorials` ❌
**Raison:** Page VideoTutorials.js nécessite cette table  
**Colonnes requises:**
```sql
CREATE TABLE video_tutorials (
    id UUID PRIMARY KEY,
    title TEXT,
    description TEXT,
    video_url TEXT,
    thumbnail_url TEXT,
    duration INTEGER,
    category TEXT (getting_started, influencer, merchant, admin, advanced),
    difficulty TEXT (beginner, intermediate, advanced),
    views INTEGER,
    likes INTEGER,
    created_by UUID REFERENCES users(id),
    is_published BOOLEAN
);
```

#### 5. `video_progress` ❌
**Raison:** Suivi de progression des vidéos  
**Colonnes requises:**
```sql
CREATE TABLE video_progress (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    video_id UUID REFERENCES video_tutorials(id),
    progress_seconds INTEGER,
    completed BOOLEAN,
    last_watched_at TIMESTAMP,
    UNIQUE(user_id, video_id)
);
```

#### 6. `documentation_articles` ❌
**Raison:** Page Documentation.js nécessite cette table  
**Colonnes requises:**
```sql
CREATE TABLE documentation_articles (
    id UUID PRIMARY KEY,
    title TEXT,
    slug TEXT UNIQUE,
    content TEXT,
    category TEXT (getting_started, influencer, merchant, api, troubleshooting, faq),
    tags TEXT[],
    views INTEGER,
    is_published BOOLEAN,
    author_id UUID REFERENCES users(id)
);
```

---

### 🟡 **PRIORITÉ MOYENNE**

#### 7. `affiliation_requests` ❌
**Raison:** Page MerchantAffiliationRequests.js nécessite cette table  
**Note:** Existe dans migration `add_affiliation_requests.sql` mais pas dans schema.sql principal  
**Colonnes requises:**
```sql
CREATE TABLE affiliation_requests (
    id UUID PRIMARY KEY,
    influencer_id UUID REFERENCES influencers(id),
    merchant_id UUID REFERENCES merchants(id),
    product_id UUID REFERENCES products(id),
    status TEXT (pending, approved, rejected),
    requested_commission_rate DECIMAL,
    message TEXT,
    merchant_response TEXT,
    responded_at TIMESTAMP
);
```

#### 8. `company_settings` ❌
**Raison:** Page CompanySettings.js nécessite cette table  
**Note:** Existe dans migration `add_company_settings.sql`  
**Colonnes requises:**
```sql
CREATE TABLE company_settings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE,
    company_name TEXT,
    industry TEXT,
    website TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    postal_code TEXT,
    country TEXT,
    logo_url TEXT,
    favicon_url TEXT,
    primary_color TEXT,
    secondary_color TEXT
);
```

#### 9. `payment_gateways` ❌
**Raison:** Système de paiement Maroc (CMI, PayZen, SG)  
**Note:** Existe dans migration `add_payment_gateways.sql`  
**Colonnes requises:**
```sql
CREATE TABLE payment_gateways (
    id UUID PRIMARY KEY,
    merchant_id UUID REFERENCES merchants(id),
    gateway_name TEXT (cmi, payzen, sg_maroc),
    api_key TEXT,
    secret_key TEXT,
    merchant_id_gateway TEXT,
    is_active BOOLEAN,
    is_test_mode BOOLEAN,
    configuration JSONB
);
```

#### 10. `invoices` ❌
**Raison:** Pages AdminInvoices.js et MerchantInvoices.js  
**Colonnes requises:**
```sql
CREATE TABLE invoices (
    id UUID PRIMARY KEY,
    merchant_id UUID REFERENCES merchants(id),
    invoice_number TEXT UNIQUE,
    amount DECIMAL,
    currency TEXT,
    status TEXT (draft, sent, paid, overdue, cancelled),
    due_date DATE,
    paid_date DATE,
    items JSONB,
    pdf_url TEXT,
    notes TEXT
);
```

---

### 🟢 **PRIORITÉ BASSE (OPTIONNELLES)**

#### 11. `notifications` ❌
**Raison:** Système de notifications en temps réel  
**Colonnes requises:**
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    type TEXT (sale, commission, message, system),
    title TEXT,
    message TEXT,
    link TEXT,
    is_read BOOLEAN,
    created_at TIMESTAMP
);
```

#### 12. `activity_log` ❌
**Raison:** Audit trail des actions utilisateurs  
**Colonnes requises:**
```sql
CREATE TABLE activity_log (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action TEXT,
    entity_type TEXT,
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP
);
```

#### 13. `affiliate_settings` ❌
**Raison:** Page AffiliateSettings.js  
**Colonnes requises:**
```sql
CREATE TABLE affiliate_settings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE,
    min_payout_amount DECIMAL,
    payout_frequency TEXT (weekly, biweekly, monthly),
    auto_approve_affiliates BOOLEAN,
    default_commission_rate DECIMAL,
    cookie_duration_days INTEGER,
    require_approval BOOLEAN
);
```

#### 14. `mlm_settings` ❌
**Raison:** Page MLMSettings.js (Marketing Multi-Niveau)  
**Colonnes requises:**
```sql
CREATE TABLE mlm_settings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE,
    enabled BOOLEAN,
    max_levels INTEGER,
    level_commissions JSONB, -- {level_1: 5%, level_2: 3%, etc.}
    require_purchase BOOLEAN,
    min_referrals_per_level INTEGER
);
```

#### 15. `mlm_commissions` ❌
**Raison:** Suivi des commissions MLM par niveau  
**Colonnes requises:**
```sql
CREATE TABLE mlm_commissions (
    id UUID PRIMARY KEY,
    sale_id UUID REFERENCES sales(id),
    influencer_id UUID REFERENCES influencers(id),
    referrer_id UUID REFERENCES influencers(id),
    level INTEGER,
    amount DECIMAL,
    status TEXT (pending, paid)
);
```

#### 16. `registration_settings` ❌
**Raison:** Page RegistrationSettings.js  
**Colonnes requises:**
```sql
CREATE TABLE registration_settings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE,
    require_email_verification BOOLEAN,
    require_phone_verification BOOLEAN,
    require_admin_approval BOOLEAN,
    allowed_domains TEXT[],
    blocked_domains TEXT[],
    min_age INTEGER,
    terms_url TEXT,
    privacy_url TEXT
);
```

#### 17. `permissions` ❌
**Raison:** Page Permissions.js (Gestion des droits)  
**Colonnes requises:**
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    role TEXT,
    resource TEXT,
    action TEXT,
    allowed BOOLEAN
);
```

#### 18. `white_label_settings` ❌
**Raison:** Page WhiteLabel.js (Marque blanche)  
**Colonnes requises:**
```sql
CREATE TABLE white_label_settings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE,
    domain TEXT,
    brand_name TEXT,
    logo_url TEXT,
    favicon_url TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    custom_css TEXT,
    custom_js TEXT,
    meta_title TEXT,
    meta_description TEXT
);
```

#### 19. `traffic_sources` ❌
**Raison:** Page TrafficSources.js (Suivi des sources de trafic)  
**Colonnes requises:**
```sql
CREATE TABLE traffic_sources (
    id UUID PRIMARY KEY,
    name TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    total_clicks INTEGER,
    total_conversions INTEGER,
    conversion_rate DECIMAL,
    is_active BOOLEAN
);
```

#### 20. `email_templates` ❌
**Raison:** Page Emails.js (Gestion des templates d'emails)  
**Colonnes requises:**
```sql
CREATE TABLE email_templates (
    id UUID PRIMARY KEY,
    name TEXT,
    subject TEXT,
    body_html TEXT,
    body_text TEXT,
    variables JSONB,
    category TEXT,
    is_active BOOLEAN
);
```

---

## 🔧 PROBLÈMES IDENTIFIÉS

### ⚠️ Incohérence: `unique_code` vs `short_code`

**Dans schema.sql:**
```sql
trackable_links.unique_code VARCHAR(50)
```

**Dans backend/server.py:**
```python
link = {"short_code": "ABC123", ...}
```

**Solution:** Renommer `unique_code` → `short_code` ou ajouter alias

---

### ⚠️ Table `subscriptions` dupliquée

**Problème:** 
- `subscriptions` dans schema.sql (structure générique)
- `user_subscriptions` nécessaire (structure spécifique utilisateur)

**Solution:** Utiliser uniquement `user_subscriptions` ou fusionner

---

### ⚠️ Migrations éparpillées

**Problème:** Migrations SQL dans `database/migrations/` non appliquées

**Fichiers existants mais non exécutés:**
- `add_affiliation_requests.sql`
- `add_company_settings.sql`
- `add_payment_gateways.sql`
- `add_all_settings_tables.sql`

**Solution:** Consolider et exécuter toutes les migrations

---

## 📋 PLAN D'ACTION

### Phase 1: Tables critiques 2FA ✅
- ✅ Créer migration `enable_2fa_for_all_users.sql`
- ⏳ Exécuter dans Supabase

### Phase 2: Tables Support & Abonnements (PRIORITÉ HAUTE)
- ✅ Créer migration `create_subscription_and_support_tables.sql`
- ⏳ Exécuter dans Supabase

### Phase 3: Tables Settings (PRIORITÉ MOYENNE)
- ⏳ Consolider `add_all_settings_tables.sql`
- ⏳ Exécuter dans Supabase

### Phase 4: Tables MLM & Permissions (PRIORITÉ BASSE)
- ⏳ Créer si nécessaire
- ⏳ Exécuter dans Supabase

---

## 📊 RÉSUMÉ STATISTIQUES

| Catégorie | Créées | Manquantes | Total |
|-----------|--------|------------|-------|
| **Authentification** | 2 | 0 | 2 |
| **Profils** | 2 | 0 | 2 |
| **Produits** | 2 | 0 | 2 |
| **Tracking** | 2 | 0 | 2 |
| **Ventes** | 2 | 0 | 2 |
| **Analytics** | 2 | 0 | 2 |
| **Campagnes** | 1 | 0 | 1 |
| **Abonnements** | 2 | 1 | 3 |
| **Support** | 0 | 2 | 2 |
| **Vidéos** | 0 | 2 | 2 |
| **Documentation** | 0 | 1 | 1 |
| **Settings** | 1 | 7 | 8 |
| **Autres** | 1 | 5 | 6 |
| **TOTAL** | **17** | **18** | **35** |

---

## ✅ CONCLUSION

L'application nécessite **18 tables supplémentaires** pour être 100% fonctionnelle.

**Actions immédiates:**
1. ✅ Corriger types UUID dans `create_subscription_and_support_tables.sql`
2. ⏳ Exécuter la migration dans Supabase
3. ⏳ Tester les pages Subscription, Support, VideoTutorials, Documentation
4. ⏳ Créer migrations consolidées pour les tables Settings

**Ordre de priorité:**
1. 🔴 Support & Abonnements (nécessaires immédiatement)
2. 🟡 Settings & Affiliation (nécessaires pour production)
3. 🟢 MLM & Permissions (optimisations futures)

---

**Document généré le:** 26 Octobre 2025  
**Auteur:** GitHub Copilot  
**Version:** 1.0
