# Plan d'Organisation des Migrations

## 📋 Analyse des Fichiers Existants

### ✅ Fichiers à Conserver (Migrations Uniques)

1. **add_email_verification.sql** → Ajoute colonnes email_verified à users
2. **add_smtp_settings.sql** → Crée table smtp_settings (déjà copié: 002)
3. **add_company_settings.sql** → Crée table company_settings
4. **add_all_settings_tables.sql** → Crée permissions_settings, affiliate_settings, registration_settings, mlm_settings, whitelabel_settings
5. **add_tracking_tables.sql** → Crée click_logs, webhook_logs + ALTER influencers/merchants
6. **add_affiliation_requests.sql** → Crée affiliation_requests + affiliation_request_history
7. **modify_trackable_links_unified.sql** → ALTER trackable_links (ajoute colonnes affiliation)
8. **add_payment_columns.sql** → Colonnes updated_at, approved_at + tables payouts, notifications
9. **add_payment_gateways.sql** → Configuration gateways Maroc (CMI, PayZen, SG) + platform_invoices
10. **create_subscription_and_support_tables.sql** → user_subscriptions, support_tickets, ticket_messages, video_tutorials, video_progress, documentation_articles
11. **enable_2fa_for_all.sql** → UPDATE users SET two_fa_enabled = true
12. **cleanup_old_affiliation_system.sql** → DROP TABLE affiliation_requests (à placer AVANT recréation)
13. **add_transaction_functions.sql** → Fonctions PL/pgSQL (déjà copié: 021)
14. **update_transaction_functions.sql** → Correction fonction (retrait metadata)

### ❌ Fichiers Redondants (À IGNORER)

- **complete_database_setup.sql** → Ensemble massif redondant avec migrations granulaires
- **add_missing_tables_only.sql** → Redondant avec create_subscription_and_support_tables.sql
- **add_only_missing_tables.sql** → Redondant avec add_all_settings_tables.sql
- **check_2fa_merchants.sql** → Script de diagnostic, pas une migration
- **check_existing_tables.sql** → Script de diagnostic
- **diagnostic_trackable_links.sql** → Script de diagnostic
- **enable_2fa_for_all_users.sql** → Doublon de enable_2fa_for_all.sql
- **verify_2fa_config.sql** → Script de vérification

---

## 🎯 Ordre d'Application Proposé

Basé sur les dépendances entre tables et l'évolution logique du schéma :

```
001_base_schema.sql                           ✅ (déjà copié)
002_add_smtp_settings.sql                     ✅ (déjà copié)
003_add_email_verification.sql                🆕 Ajoute colonnes à users
004_add_company_settings.sql                  🆕 Table indépendante
005_add_all_settings_tables.sql               🆕 Tables settings (permissions, affiliate, mlm, etc.)
006_create_subscription_and_support_tables.sql 🆕 Support + abonnements
007_add_tracking_tables.sql                   🆕 click_logs + webhook_logs
008_cleanup_old_affiliation_system.sql        🆕 DROP ancienne table affiliation_requests
009_add_affiliation_requests.sql              🆕 Nouvelle table affiliation_requests
010_modify_trackable_links_unified.sql        🆕 ALTER trackable_links pour affiliation
011_add_payment_columns.sql                   🆕 Colonnes paiement + payouts + notifications
012_add_payment_gateways.sql                  🆕 Gateways Maroc + platform_invoices
013_enable_2fa_for_all.sql                    🆕 Active 2FA pour tous
021_add_transaction_functions.sql             ✅ (déjà copié)
022_update_transaction_functions.sql          🆕 Correction fonction (retrait metadata)
```

---

## 📝 Notes sur l'Ordre

### Phase 1 : Base (001-002)
- Schéma complet + configuration email

### Phase 2 : Configuration Utilisateurs (003-005)
- Email verification → Company settings → All settings tables
- Aucune dépendance entre elles

### Phase 3 : Support & Abonnements (006)
- Tables autonomes pour support client

### Phase 4 : Tracking (007)
- Dépend de influencers/merchants (Phase 1)

### Phase 5 : Affiliation v2 (008-010)
- Cleanup ancien système → Nouveau système → Modification trackable_links
- **IMPORTANT** : 008 avant 009 pour éviter conflit de noms

### Phase 6 : Paiements (011-012)
- Colonnes paiement → Gateways
- Dépend de sales/commissions/influencers (Phase 1)

### Phase 7 : Sécurité (013)
- Activation 2FA pour tous

### Phase 8 : Fonctions Transactionnelles (021-022)
- Fonctions PL/pgSQL → Correction metadata

---

## ⚠️ Conflits Potentiels

### affiliation_requests
- **008** : DROP TABLE affiliation_requests
- **009** : CREATE TABLE affiliation_requests
- ✅ Solution : Ordre respecté (DROP avant CREATE)

### Colonnes Dupliquées
- Plusieurs migrations utilisent `IF NOT EXISTS` → idempotent ✅
- Certaines colonnes peuvent être ajoutées plusieurs fois → vérifier avec diagnostic

### Tables Redondantes
- `complete_database_setup.sql` crée TOUT → ne pas l'utiliser
- Préférer migrations granulaires pour traçabilité

---

## 🚀 Prochaines Actions

1. ✅ Copier fichiers selon ordre (003-013, 022)
2. ✅ Mettre à jour README.md avec ordre complet
3. ✅ Tester apply_migrations.ps1 en DRY RUN
4. ✅ Vérifier absence de conflits SQL

---

**Date** : 27 octobre 2025  
**Auteur** : GitHub Copilot  
**Version** : 1.0
