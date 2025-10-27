# Architecture & Stratégie — GetYourShare

Date: 2025-10-27

But: professionnaliser l'application (fiabilité, maintenabilité, sécurité, observabilité, expérience produit).

## 1. Résumé de l'état actuel
- Backend: FastAPI monolithique dans `backend/server.py`. Logique métier dispersée.
- DB: Supabase Postgres avec procédures stockées (`database/migrations/*.sql`).
- Frontend: React + Tailwind dans `frontend/`.
- Intégrations: webhooks, gateways paiement, notifications (polling coté client).

## 2. Principaux objectifs
- Modulariser le backend par domaines (affiliation, sales, payments, notifications).
- Mettre en place tests automatiques (unit + intégration pour procédures SQL).
- CI/CD: lint + tests + build + déploiement staging.
- Observabilité: logging structuré, Sentry, health checks.
- Temps réel notifications (Supabase Realtime ou WebSockets).
- Sécurité: gestion centralisée des secrets, hardening JWT/RBAC, rotation clés.

## 3. Contrat des modules (proposition rapide)
- backend/services/affiliation
  - fonctions: create_request, approve_request, reject_request, list_requests
  - inputs/outputs validés par Pydantic
- backend/services/sales
  - wrappers autour des procédures SQL (`create_sale_transaction`, `approve_payout_transaction`)
  - tests pour calculs commissions
- backend/services/notifications
  - queue d'envoi (db-backed) + realtime push

## 4. Stratégie de migration progressive
1. Cartographie endpoints & tests manquants (1 jour)
2. Extraire module `affiliation` (2-3 jours) — petit pas, garantir compatibilité
3. Ajouter tests unitaires pour `affiliation` et CI (1-2 jours)
4. Itérer sur `sales` (incl. tests SQL) (3-4 jours)
5. Implémenter notifications realtime et améliorer frontend hooks (2-3 jours)

## 5. Priorités immédiates (this week)
1. Produire ADRs (modularisation + migrations) — actionnalise décisions architecturales.
2. Mettre en place CI minimal (lint + tests) pour empêcher régressions.
3. Extraire le module `affiliation` depuis `server.py` (pas de rupture API).

## 6. Prochaines actions que je peux lancer maintenant
- Créer ADRs et document d'architecture (fait — voir ce fichier)
- Configurer skeleton de module `backend/services/affiliation` et y déplacer un premier router
- Ajouter job GitHub Actions CI (lint + tests stub)

---

Si tu me confirmes, je commence immédiatement par extraire le module `affiliation` depuis `backend/server.py` :
- créer `backend/services/affiliation/router.py` et `backend/services/affiliation/service.py`
- déplacer les endpoints d'affiliation (création / approbation / rejet / stats)
- ajouter tests unitaires simples

Dis-moi si tu veux que je commence par ça, ou préfères-tu une autre priorité (ex: CI, tests SQL, notifications).