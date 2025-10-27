# 📁 Migrations SQL - ShareYourSales

Organisation des migrations SQL avec numérotation séquentielle pour garantir l'ordre d'exécution correct.

## 🔢 Ordre d'application des migrations

### Phase 1 : Infrastructure de Base (001-002)
1. **001_base_schema.sql** - Schéma complet (tables users, merchants, influencers, products, sales, commissions, etc.)
2. **002_add_smtp_settings.sql** - Configuration SMTP pour emails transactionnels

### Phase 2 : Configuration Utilisateurs (003-005)
3. **003_add_email_verification.sql** - Colonnes email_verified + verification_token sur users
4. **004_add_company_settings.sql** - Table company_settings (paramètres entreprise)
5. **005_add_all_settings_tables.sql** - permissions_settings, affiliate_settings, registration_settings, mlm_settings, whitelabel_settings

### Phase 3 : Support & Abonnements (006)
6. **006_create_subscription_and_support_tables.sql** - user_subscriptions, support_tickets, ticket_messages, video_tutorials, video_progress, documentation_articles

### Phase 4 : Système de Tracking (007)
7. **007_add_tracking_tables.sql** - click_logs, webhook_logs + ALTER influencers/merchants (colonnes tracking)

### Phase 5 : Affiliation v2 (008-010)
8. **008_cleanup_old_affiliation_system.sql** - DROP TABLE affiliation_requests (ancien système) ⚠️
9. **009_add_affiliation_requests.sql** - CREATE TABLE affiliation_requests + affiliation_request_history (nouveau système)
10. **010_modify_trackable_links_unified.sql** - ALTER trackable_links (colonnes influencer_message, merchant_response, status)

### Phase 6 : Paiements Avancés (011-012)
11. **011_add_payment_columns.sql** - Colonnes updated_at, approved_at + tables payouts, notifications + ALTER influencers (payment_details)
12. **012_add_payment_gateways.sql** - Gateways Maroc (CMI, PayZen, SG) + platform_invoices + ALTER merchants (gateway_config)

### Phase 7 : Sécurité (013)
13. **013_enable_2fa_for_all.sql** - UPDATE users SET two_fa_enabled = true (activation 2FA globale)

### Phase 8 : Fonctions Transactionnelles (021-022)
14. **021_add_transaction_functions.sql** - Fonctions PL/pgSQL `create_sale_transaction` et `approve_payout_transaction`
15. **022_update_transaction_functions.sql** - Correction : DROP ancienne fonction create_sale_transaction avec metadata

---

## 📋 Ordre d'exécution recommandé

### Via psql (PostgreSQL direct)
```bash
cd database/migrations_organized

# Phase 1 : Infrastructure
psql -U postgres -d shareyoursales -f 001_base_schema.sql
psql -U postgres -d shareyoursales -f 002_add_smtp_settings.sql

# Phase 2 : Configuration Utilisateurs
psql -U postgres -d shareyoursales -f 003_add_email_verification.sql
psql -U postgres -d shareyoursales -f 004_add_company_settings.sql
psql -U postgres -d shareyoursales -f 005_add_all_settings_tables.sql

# Phase 3 : Support & Abonnements
psql -U postgres -d shareyoursales -f 006_create_subscription_and_support_tables.sql

# Phase 4 : Tracking
psql -U postgres -d shareyoursales -f 007_add_tracking_tables.sql

# Phase 5 : Affiliation v2
psql -U postgres -d shareyoursales -f 008_cleanup_old_affiliation_system.sql
psql -U postgres -d shareyoursales -f 009_add_affiliation_requests.sql
psql -U postgres -d shareyoursales -f 010_modify_trackable_links_unified.sql

# Phase 6 : Paiements
psql -U postgres -d shareyoursales -f 011_add_payment_columns.sql
psql -U postgres -d shareyoursales -f 012_add_payment_gateways.sql

# Phase 7 : Sécurité
psql -U postgres -d shareyoursales -f 013_enable_2fa_for_all.sql

# Phase 8 : Fonctions Transactionnelles
psql -U postgres -d shareyoursales -f 021_add_transaction_functions.sql
psql -U postgres -d shareyoursales -f 022_update_transaction_functions.sql
```

### Via Supabase CLI
```bash
cd database/migrations_organized

# Appliquer toutes les migrations séquentiellement
supabase db execute --db-url "postgresql://..." -f 001_base_schema.sql
supabase db execute --db-url "postgresql://..." -f 002_add_smtp_settings.sql
supabase db execute --db-url "postgresql://..." -f 003_add_email_verification.sql
supabase db execute --db-url "postgresql://..." -f 004_add_company_settings.sql
supabase db execute --db-url "postgresql://..." -f 005_add_all_settings_tables.sql
supabase db execute --db-url "postgresql://..." -f 006_create_subscription_and_support_tables.sql
supabase db execute --db-url "postgresql://..." -f 007_add_tracking_tables.sql
supabase db execute --db-url "postgresql://..." -f 008_cleanup_old_affiliation_system.sql
supabase db execute --db-url "postgresql://..." -f 009_add_affiliation_requests.sql
supabase db execute --db-url "postgresql://..." -f 010_modify_trackable_links_unified.sql
supabase db execute --db-url "postgresql://..." -f 011_add_payment_columns.sql
supabase db execute --db-url "postgresql://..." -f 012_add_payment_gateways.sql
supabase db execute --db-url "postgresql://..." -f 013_enable_2fa_for_all.sql
supabase db execute --db-url "postgresql://..." -f 021_add_transaction_functions.sql
supabase db execute --db-url "postgresql://..." -f 022_update_transaction_functions.sql
```

### Script automatisé (PowerShell)
```powershell
# Voir apply_migrations.ps1
.\apply_migrations.ps1 -DatabaseUrl "postgresql://user:pass@host:5432/dbname"
```

---

## ⚠️ Notes importantes

### Ordre critique
- **001_base_schema.sql** doit TOUJOURS être exécuté en premier
- **021_add_transaction_functions.sql** dépend du schéma de base (tables sales, commissions)
- Les migrations de nettoyage (031+) doivent être exécutées en dernier

### Idempotence
Les migrations doivent être **idempotentes** (peuvent être exécutées plusieurs fois sans erreur) :
```sql
-- Exemple : utiliser IF NOT EXISTS
CREATE TABLE IF NOT EXISTS ma_table (...);

-- Exemple : utiliser CREATE OR REPLACE pour les fonctions
CREATE OR REPLACE FUNCTION ma_fonction(...) RETURNS ... AS $$ ... $$ LANGUAGE plpgsql;
```

### Rollback
Pour annuler une migration, créer un fichier de rollback correspondant :
- `001_base_schema.sql` → `001_base_schema_rollback.sql`
- `021_add_transaction_functions.sql` → `021_add_transaction_functions_rollback.sql`

Exemple de rollback :
```sql
-- 021_add_transaction_functions_rollback.sql
DROP FUNCTION IF EXISTS create_sale_transaction(...);
DROP FUNCTION IF EXISTS approve_payout_transaction(...);
```

---

## 🧪 Validation des migrations

Après chaque migration, vérifier :
```sql
-- Lister les tables créées
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Lister les fonctions
SELECT proname FROM pg_proc WHERE pronamespace = 'public'::regnamespace ORDER BY proname;

-- Vérifier les contraintes
SELECT conname, contype FROM pg_constraint WHERE connamespace = 'public'::regnamespace;
```

---

## 📝 Convention de nommage

Format : `<numéro>_<description_courte>.sql`

- **Numéro** : 3 chiffres avec zéros devant (001, 002, 010, 021, etc.)
- **Description** : snake_case, courte et descriptive
- **Extension** : `.sql`

Exemples :
- ✅ `001_base_schema.sql`
- ✅ `021_add_transaction_functions.sql`
- ❌ `migration-base.sql`
- ❌ `1_schema.sql` (manque zéros)

---

## 🔄 Workflow pour ajouter une nouvelle migration

1. **Créer le fichier** avec le prochain numéro disponible
   ```bash
   # Si la dernière migration est 031, créer 032
   touch database/migrations_organized/032_add_new_feature.sql
   ```

2. **Écrire la migration** avec `CREATE OR REPLACE` / `IF NOT EXISTS`
   ```sql
   -- 032_add_new_feature.sql
   CREATE TABLE IF NOT EXISTS ma_nouvelle_table (...);
   CREATE OR REPLACE FUNCTION ma_nouvelle_fonction(...) RETURNS ... AS $$ ... $$;
   ```

3. **Tester localement** avec rollback
   ```bash
   psql -d shareyoursales_dev -f 032_add_new_feature.sql
   # Vérifier
   psql -d shareyoursales_dev -c "\dt"
   # Rollback si besoin
   psql -d shareyoursales_dev -f 032_add_new_feature_rollback.sql
   ```

4. **Mettre à jour ce README** avec la nouvelle migration dans la section "Ordre d'application"

5. **Commit** avec message clair
   ```bash
   git add database/migrations_organized/032_add_new_feature.sql
   git commit -m "feat(db): add new feature migration (032)"
   ```

---

## 🗂️ Structure actuelle

```
database/
├── migrations/                    # ⚠️ Ancien dossier non organisé
│   └── *.sql                     # Migrations en vrac (à migrer)
├── migrations_organized/          # ✅ Nouveau dossier organisé
│   ├── README.md                 # Ce fichier
│   ├── apply_migrations.ps1      # Script d'application automatique
│   ├── 001_base_schema.sql
│   ├── 002_add_smtp_settings.sql
│   ├── ...
│   └── 031_cleanup_old_affiliation.sql
└── tests/
    └── test_transaction_functions.sql
```

---

**Dernière mise à jour** : Octobre 2025  
**Migrations actives** : 14  
**Version DB** : 1.1
