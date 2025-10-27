# 🗂️ Structure des Migrations - Vue d'Ensemble

```
database/migrations_organized/
│
├── 📚 DOCUMENTATION
│   ├── README.md                    # Guide d'utilisation complet
│   ├── MIGRATION_PLAN.md            # Analyse et stratégie d'organisation
│   └── COMPLETION_REPORT.md         # Rapport de fin de phase
│
├── 🤖 AUTOMATISATION
│   └── apply_migrations.ps1         # Script PowerShell (testé ✅)
│
└── 📜 MIGRATIONS SQL (15 fichiers)
    │
    ├── 🏗️ PHASE 1 : Infrastructure de Base
    │   ├── 001_base_schema.sql                          [Base complète]
    │   └── 002_add_smtp_settings.sql                    [Config email]
    │
    ├── ⚙️ PHASE 2 : Configuration Utilisateurs
    │   ├── 003_add_email_verification.sql               [Colonnes users]
    │   ├── 004_add_company_settings.sql                 [Table settings]
    │   └── 005_add_all_settings_tables.sql              [Tous settings]
    │
    ├── 🎫 PHASE 3 : Support & Abonnements
    │   └── 006_create_subscription_and_support_tables.sql [6 tables]
    │
    ├── 📊 PHASE 4 : Système de Tracking
    │   └── 007_add_tracking_tables.sql                  [Logs + ALTER]
    │
    ├── 🤝 PHASE 5 : Affiliation v2
    │   ├── 008_cleanup_old_affiliation_system.sql       [DROP ancien]
    │   ├── 009_add_affiliation_requests.sql             [CREATE nouveau]
    │   └── 010_modify_trackable_links_unified.sql       [ALTER links]
    │
    ├── 💳 PHASE 6 : Paiements Avancés
    │   ├── 011_add_payment_columns.sql                  [Colonnes + tables]
    │   └── 012_add_payment_gateways.sql                 [Gateways Maroc]
    │
    ├── 🔐 PHASE 7 : Sécurité
    │   └── 013_enable_2fa_for_all.sql                   [UPDATE 2FA]
    │
    └── ⚡ PHASE 8 : Fonctions Transactionnelles
        ├── 021_add_transaction_functions.sql            [CREATE functions]
        └── 022_update_transaction_functions.sql         [DROP/CREATE fix]
```

---

## 📈 Flux d'Exécution

```
START
  │
  ├──> 001 (Base)
  │      └──> Crée: users, merchants, influencers, products, sales, commissions, etc.
  │
  ├──> 002 (SMTP)
  │      └──> Crée: smtp_settings
  │
  ├──> 003 (Email Verification)
  │      └──> ALTER: users (email_verified, verification_token)
  │
  ├──> 004 (Company Settings)
  │      └──> Crée: company_settings
  │
  ├──> 005 (All Settings)
  │      └──> Crée: permissions_settings, affiliate_settings, mlm_settings, etc.
  │
  ├──> 006 (Support)
  │      └──> Crée: user_subscriptions, support_tickets, video_tutorials, etc.
  │
  ├──> 007 (Tracking)
  │      ├──> Crée: click_logs, webhook_logs
  │      └──> ALTER: influencers, merchants (colonnes tracking)
  │
  ├──> 008 (Cleanup Affiliation) ⚠️ IMPORTANT: Ordre critique
  │      └──> DROP: affiliation_requests (ancien)
  │
  ├──> 009 (New Affiliation)
  │      └──> Crée: affiliation_requests, affiliation_request_history (nouveau)
  │
  ├──> 010 (Modify Links)
  │      └──> ALTER: trackable_links (status, influencer_message, etc.)
  │
  ├──> 011 (Payment Columns)
  │      ├──> ALTER: sales (updated_at), commissions (approved_at), influencers (payment_details)
  │      └──> Crée: payouts, notifications
  │
  ├──> 012 (Payment Gateways)
  │      ├──> ALTER: merchants (payment_gateway, gateway_config)
  │      └──> Crée: platform_invoices
  │
  ├──> 013 (Enable 2FA)
  │      └──> UPDATE: users (two_fa_enabled = true)
  │
  ├──> 021 (Transaction Functions)
  │      └──> Crée: create_sale_transaction(), approve_payout_transaction()
  │
  └──> 022 (Fix Functions)
         └──> DROP/CREATE: create_sale_transaction (sans metadata)
  │
END (✅ Base de données complète)
```

---

## 🔗 Dépendances Critiques

### Tables de Base (001)
```
users ──┬──> influencers
        ├──> merchants
        └──> admin (implicite)

merchants ──> products ──> trackable_links ──┬──> sales ──> commissions
                                              └──> click_logs

influencers ──> trackable_links
```

### Dépendances des Migrations

| Migration | Dépend de | Crée/Modifie |
|-----------|-----------|--------------|
| 001 | - | Toutes les tables de base |
| 002 | - | smtp_settings |
| 003 | 001 (users) | ALTER users |
| 004 | 001 (users) | company_settings |
| 005 | 001 (users) | 5 tables settings |
| 006 | 001 (users) | 6 tables support/abonnements |
| 007 | 001 (influencers, merchants, trackable_links) | click_logs, webhook_logs + ALTER |
| 008 | 001 (affiliation_requests si existe) | DROP affiliation_requests |
| 009 | 001 (influencers, merchants, products, users) | affiliation_requests, affiliation_request_history |
| 010 | 001 (trackable_links), 009 (logique) | ALTER trackable_links |
| 011 | 001 (sales, commissions, influencers) | ALTER + payouts, notifications |
| 012 | 001 (merchants) | ALTER merchants + platform_invoices |
| 013 | 001 (users) | UPDATE users |
| 021 | 001-012 (toutes tables métier) | Fonctions PL/pgSQL |
| 022 | 021 | DROP/CREATE fonction |

---

## 🎯 Checklist de Validation

### Avant Exécution
- [x] Script PowerShell testé en DRY RUN
- [x] 15 migrations détectées dans l'ordre
- [x] Documentation complète (README, PLAN, REPORT)
- [x] Aucune erreur VS Code

### Après Exécution (À faire en production)
- [ ] Vérifier nombre de tables créées (~40)
- [ ] Tester fonction `create_sale_transaction`
- [ ] Tester fonction `approve_payout_transaction`
- [ ] Valider toutes les contraintes FOREIGN KEY
- [ ] Vérifier index créés (pg_indexes)
- [ ] Tester quelques requêtes métier

### Commandes de Validation Post-Migration
```sql
-- Compter les tables
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';

-- Vérifier les fonctions
SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public';

-- Lister les contraintes
SELECT constraint_name, table_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_schema = 'public';

-- Vérifier les index
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public';
```

---

## 📚 Liens Rapides

- [README.md](README.md) → Guide utilisateur
- [MIGRATION_PLAN.md](MIGRATION_PLAN.md) → Stratégie détaillée
- [COMPLETION_REPORT.md](COMPLETION_REPORT.md) → Rapport complet
- [apply_migrations.ps1](apply_migrations.ps1) → Script automatisé
- [../schema.sql](../schema.sql) → Schéma de référence
- [../DATABASE_DOCUMENTATION.md](../DATABASE_DOCUMENTATION.md) → Doc technique

---

**Dernière mise à jour** : 27 octobre 2025  
**Statut** : ✅ Production-Ready  
**Version** : 1.0
