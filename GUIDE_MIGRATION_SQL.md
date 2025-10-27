# 🗄️ GUIDE MIGRATION SQL - TABLES MANQUANTES

**Date:** 26 octobre 2025  
**Fichier:** `database/migrations/add_only_missing_tables.sql`  
**Statut:** ⏳ **EN ATTENTE D'EXÉCUTION**

---

## 📋 TABLES À CRÉER (8)

### 1. **company_settings** - Paramètres entreprise
- Nom de l'entreprise, logo, email, téléphone
- Configuration commissions (modèle, taux par défaut)
- Montant minimum de paiement
- Planning des paiements (hebdomadaire/mensuel)
- Devise, timezone, langue

### 2. **payment_gateways** - Gateways de paiement Maroc
- CMI, PayZen, Société Générale Maroc
- Configuration par marchand
- Clés API (chiffrées)
- Mode test/production
- Devises supportées
- Frais de transaction

### 3. **invoices** - Facturation
- Numéro de facture unique
- Montant TTC/HT
- Statut (pending, paid, overdue, cancelled)
- Date d'échéance
- Ligne de facturation (JSONB)
- URL du PDF

### 4. **activity_log** - Journal d'activité
- Logs des actions utilisateurs
- Type d'entité modifiée
- Anciennes/nouvelles valeurs (JSONB)
- IP address
- User agent
- Timestamp

### 5. **mlm_commissions** - Commissions MLM
- Commission multi-niveaux (jusqu'à 10 niveaux)
- Affilié parent/enfant
- Vente associée
- Pourcentage par niveau
- Statut paiement

### 6. **permissions** - Permissions granulaires
- Par rôle (admin, merchant, influencer, affiliate)
- Par ressource (users, products, sales, etc.)
- Actions autorisées (create, read, update, delete)
- État actif/inactif

### 7. **traffic_sources** - Sources de trafic
- Type (organic, paid, social, email, referral)
- Paramètres UTM (source, medium, campaign)
- Statistiques (clics, conversions, taux)
- Suivi des performances

### 8. **email_templates** - Templates d'emails
- Clé unique du template
- Sujet et corps (HTML + texte)
- Variables dynamiques (JSONB)
- Catégorie (transactional, marketing, notification)
- Support multilingue

---

## 🚀 PROCÉDURE D'EXÉCUTION

### ÉTAPE 1: Ouvrir Supabase Dashboard

1. **Connectez-vous à Supabase:**
   ```
   https://supabase.com/dashboard
   ```

2. **Sélectionnez votre projet:**
   - Nom: `iamezkmapbhlhhvvsits`
   - URL: `https://iamezkmapbhlhhvvsits.supabase.co`

3. **Accédez au SQL Editor:**
   - Menu latéral gauche → **SQL Editor**
   - Ou utilisez ce lien direct:
     ```
     https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits/sql
     ```

### ÉTAPE 2: Créer une nouvelle requête

1. Cliquez sur **"New query"** (bouton vert en haut à droite)

2. **NOM DE LA REQUÊTE:** `Migration - Tables manquantes (8)`

### ÉTAPE 3: Copier le SQL

1. **Ouvrez le fichier local:**
   ```
   c:\Users\Admin\Desktop\shareyoursales\Getyourshare1\database\migrations\add_only_missing_tables.sql
   ```

2. **Sélectionnez TOUT le contenu** (Ctrl+A)

3. **Copiez** (Ctrl+C)

### ÉTAPE 4: Coller dans Supabase

1. Dans l'éditeur SQL de Supabase, **collez** le contenu (Ctrl+V)

2. **Vérifiez** que le fichier est complet (490 lignes)

### ÉTAPE 5: Exécuter la migration

1. Cliquez sur **"RUN"** (bouton vert en bas à droite)

2. **Attendez l'exécution** (~10-15 secondes)

### ÉTAPE 6: Vérifier le succès

Vous devriez voir dans les **NOTICES:**

```sql
========================================
MIGRATION TERMINÉE AVEC SUCCÈS!
========================================
Tables totales dans la base: 44
Nouvelles tables créées: 8
========================================

TABLES AJOUTÉES:
  1. company_settings
  2. payment_gateways
  3. invoices
  4. activity_log
  5. mlm_commissions
  6. permissions
  7. traffic_sources
  8. email_templates
========================================
```

Et un **tableau de résultats:**

| table_name | row_count |
|------------|-----------|
| company_settings | 0 |
| payment_gateways | 0 |
| invoices | 0 |
| activity_log | 0 |
| mlm_commissions | 0 |
| permissions | 28 |
| traffic_sources | 0 |
| email_templates | 5 |

**Note:** `permissions` et `email_templates` ont déjà des données (28 permissions et 5 templates par défaut)

---

## ✅ VÉRIFICATION POST-MIGRATION

### Méthode 1: SQL Editor

Dans Supabase SQL Editor, exécutez:

```sql
-- Vérifier que toutes les tables existent
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'company_settings', 
    'payment_gateways', 
    'invoices', 
    'activity_log',
    'mlm_commissions',
    'permissions',
    'traffic_sources',
    'email_templates'
  )
ORDER BY table_name;
```

**Résultat attendu:** 8 lignes

### Méthode 2: Table Editor

1. Menu latéral → **Table Editor**
2. Vérifiez que les 8 nouvelles tables apparaissent dans la liste

### Méthode 3: Tester depuis le Backend

Une fois les tables créées, testez les endpoints:

```bash
# Test permissions
curl http://localhost:8002/api/admin/permissions

# Test email templates
curl http://localhost:8002/api/admin/email-templates

# Test company settings
curl http://localhost:8002/api/settings/company
```

---

## 📊 DONNÉES PAR DÉFAUT INSÉRÉES

### 28 Permissions créées:

**Admin (10):**
- users (create, read, update, delete)
- merchants (create, read, update, delete)
- influencers (create, read, update, delete)
- products (create, read, update, delete)
- sales (read, update, delete)
- commissions (read, update, approve, delete)
- settings (read, update)
- reports (read, export)
- payments (read, update, approve)
- invoices (create, read, update, delete)

**Merchant (8):**
- products (create, read, update, delete)
- sales (read)
- commissions (read)
- campaigns (create, read, update, delete)
- influencers (read)
- reports (read)
- payment_gateways (create, read, update)
- invoices (read)

**Influencer (7):**
- trackable_links (create, read, update, delete)
- sales (read)
- commissions (read)
- products (read)
- campaigns (read)
- reports (read)
- payouts (read, request)

**Affiliate (5):**
- trackable_links (create, read, update, delete)
- sales (read)
- commissions (read)
- products (read)
- payouts (read, request)

### 5 Templates d'emails créés:

1. **welcome_user** - Email de bienvenue
2. **commission_earned** - Notification commission gagnée
3. **payout_processed** - Paiement traité
4. **invoice_generated** - Nouvelle facture
5. **sale_notification** - Notification nouvelle vente

---

## 🔧 TRIGGERS CRÉÉS

Chaque table a un **trigger automatique** pour mettre à jour `updated_at`:

```sql
CREATE TRIGGER update_[table]_updated_at 
    BEFORE UPDATE ON [table]
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

Tables concernées:
- company_settings
- payment_gateways
- invoices
- mlm_commissions
- permissions
- traffic_sources
- email_templates

---

## 📝 INDEX CRÉÉS (Performance)

**company_settings:** 1 index
- `idx_company_settings_created` sur `created_at`

**payment_gateways:** 3 index
- `idx_payment_gateways_merchant` sur `merchant_id`
- `idx_payment_gateways_active` sur `is_active`
- `idx_payment_gateways_gateway_name` sur `gateway_name`

**invoices:** 5 index
- `idx_invoices_user_id` sur `user_id`
- `idx_invoices_merchant_id` sur `merchant_id`
- `idx_invoices_status` sur `status`
- `idx_invoices_invoice_number` sur `invoice_number`
- `idx_invoices_created_at` sur `created_at DESC`

**activity_log:** 4 index
- `idx_activity_log_user_id` sur `user_id`
- `idx_activity_log_action` sur `action`
- `idx_activity_log_entity` sur `(entity_type, entity_id)`
- `idx_activity_log_created_at` sur `created_at DESC`

**mlm_commissions:** 5 index
- `idx_mlm_commissions_affiliate_id` sur `affiliate_id`
- `idx_mlm_commissions_downline` sur `downline_affiliate_id`
- `idx_mlm_commissions_sale_id` sur `sale_id`
- `idx_mlm_commissions_status` sur `status`
- `idx_mlm_commissions_level` sur `level`

**permissions:** 3 index
- `idx_permissions_role` sur `role`
- `idx_permissions_resource` sur `resource`
- `idx_permissions_active` sur `is_active`

**traffic_sources:** 3 index
- `idx_traffic_sources_source_type` sur `source_type`
- `idx_traffic_sources_active` sur `is_active`
- `idx_traffic_sources_utm` sur `(utm_source, utm_medium, utm_campaign)`

**email_templates:** 4 index
- `idx_email_templates_template_key` sur `template_key`
- `idx_email_templates_category` sur `category`
- `idx_email_templates_active` sur `is_active`
- `idx_email_templates_language` sur `language`

**Total:** 28 index pour performance optimale

---

## ⚠️ ERREURS POSSIBLES

### Erreur 1: Table déjà existante
```
ERROR: relation "company_settings" already exists
```
**Solution:** La table existe déjà, pas besoin de la recréer. Sautez cette partie.

### Erreur 2: Référence manquante
```
ERROR: relation "merchants" does not exist
```
**Solution:** Vérifiez que la table `merchants` existe. Si non, exécutez d'abord `schema.sql`.

### Erreur 3: Fonction manquante
```
ERROR: function update_updated_at_column() does not exist
```
**Solution:** La fonction est créée dans le script (PARTIE 9). Vérifiez qu'elle s'est bien exécutée.

### Erreur 4: Permission denied
```
ERROR: permission denied for schema public
```
**Solution:** Utilisez la **Service Role Key** dans votre connexion Supabase.

---

## 🎯 APRÈS LA MIGRATION

### 1. Redémarrer le backend

```powershell
# Arrêter le backend actuel (Ctrl+C dans le terminal)

# Redémarrer
cd c:\Users\Admin\Desktop\shareyoursales\Getyourshare1\backend
python server.py
```

### 2. Tester les nouveaux endpoints

```bash
# Permissions
GET /api/admin/permissions
POST /api/admin/permissions

# Email templates
GET /api/admin/email-templates
POST /api/admin/email-templates

# Company settings
GET /api/settings/company
PUT /api/settings/company

# Payment gateways
GET /api/merchant/payment-gateways
POST /api/merchant/payment-gateways

# Invoices
GET /api/merchant/invoices
POST /api/admin/invoices/generate

# Activity log
GET /api/admin/activity-log

# Traffic sources
GET /api/admin/traffic-sources
POST /api/admin/traffic-sources
```

### 3. Vérifier les pages frontend

Les pages suivantes devraient maintenant fonctionner sans erreur:

**Admin:**
- Paramètres → Permissions
- Paramètres → Templates Emails
- Paramètres → Entreprise
- Billing → Factures
- Analytics → Sources de trafic
- Logs → Activité

**Merchant:**
- Paramètres → Gateways de paiement
- Billing → Mes factures

**Influencer:**
- MLM → Commissions multi-niveaux

---

## 📚 DOCUMENTATION COMPLÉMENTAIRE

**Fichiers liés:**
- `database/schema.sql` - Schéma complet de la base
- `database/DATABASE_DOCUMENTATION.md` - Documentation des tables
- `backend/server.py` - Endpoints API utilisant ces tables

**Commits GitHub:**
- `SESSION_COMPLETE_RATE_LIMITING_PAGINATION.md` - Documentation session
- `RATE_LIMITING_PAGINATION.md` - Documentation features

---

## ✅ CHECKLIST FINALE

Après l'exécution de la migration, cochez:

- [ ] Les 8 tables apparaissent dans Supabase Table Editor
- [ ] La requête SQL retourne 8 lignes (vérification)
- [ ] 28 permissions insérées (table `permissions`)
- [ ] 5 email templates insérés (table `email_templates`)
- [ ] Backend redémarré sans erreur
- [ ] Endpoints API testés et fonctionnels
- [ ] Pages frontend accessibles sans erreur 500

---

**🎉 Une fois cette migration terminée, votre base de données sera complète et toutes les fonctionnalités seront opérationnelles !**

---

## 🔗 LIEN DIRECT

**Supabase SQL Editor:**
```
https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits/sql
```

**Durée estimée:** 2-3 minutes

**Difficulté:** ⭐ Facile (copier-coller)

---
