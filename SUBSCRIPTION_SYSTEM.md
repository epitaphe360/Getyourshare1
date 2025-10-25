# 💳 Système d'Abonnement SaaS - ShareYourSales

## 📋 Vue d'ensemble

Système d'abonnement complet et moderne pour les marchands et influenceurs, avec gestion des paiements récurrents, facturation automatique et contrôle d'accès basé sur les fonctionnalités.

---

## ✨ Fonctionnalités Principales

### 1. Plans d'Abonnement Flexibles
- **Plans Merchants**: Freemium, Standard, Premium, Enterprise
- **Plans Influencers**: Free, Pro, Elite
- Tarification mensuelle et annuelle
- Période d'essai gratuite configurable
- Limites personnalisées par plan (produits, campagnes, affiliés)

### 2. Souscription Fluide
- Onboarding guidé avec choix du plan
- Essai gratuit sans carte bancaire (optionnel)
- Page "Mon Abonnement" complète
- Upgrade/Downgrade instantané avec prorata
- Annulation à tout moment

### 3. Paiements Récurrents Automatisés
- Intégration Stripe pour paiements internationaux
- Support prévu pour CMI, PayZen, SG Maroc
- Prélèvement automatique mensuel/annuel
- Gestion des échecs de paiement avec relance
- Webhooks pour synchronisation automatique

### 4. Facturation Transparente
- Génération automatique de factures PDF professionnelles
- Historique des factures dans l'espace client
- Notifications email à chaque paiement
- Numérotation automatique des factures

### 5. Gestion des Accès en Temps Réel
- Abonnement actif = accès complet aux fonctionnalités
- Abonnement expiré = mode restreint (lecture seule)
- Middleware de vérification automatique
- Blocage des fonctionnalités selon le plan

### 6. Coupons & Promotions
- Codes de réduction en pourcentage ou montant fixe
- Durée configurable (once, repeating, forever)
- Limites d'utilisation
- Réservé aux nouveaux clients (optionnel)

### 7. Sécurité & Conformité
- Données de paiement via Stripe (PCI DSS)
- Tokens JWT pour authentification
- Conformité RGPD ready
- Logs complets des événements

---

## 🏗️ Architecture

### Structure Backend

```
backend/
├── create_subscription_tables.sql      # Schéma de base de données
├── subscription_helpers.py             # Fonctions CRUD et logique métier
├── payment_service.py                  # Intégration Stripe et paiements
├── invoice_service.py                  # Génération de factures PDF
├── subscription_endpoints.py           # Endpoints API REST
├── subscription_middleware.py          # Middleware de vérification
├── apply_subscription_system.py        # Script de migration
└── server.py                           # (modifié) Intégration du système
```

### Tables de Base de Données

```sql
1. subscription_plans        # Plans d'abonnement disponibles
2. subscriptions             # Abonnements actifs des utilisateurs
3. payment_methods           # Méthodes de paiement enregistrées
4. invoices                  # Factures générées
5. payment_transactions      # Historique des transactions
6. subscription_coupons      # Codes promo et réductions
7. subscription_usage        # Suivi de l'utilisation
8. subscription_events       # Logs des événements
```

### Diagramme de Relations

```
users (existant)
  │
  ├──> subscriptions
  │       ├──> subscription_plans
  │       ├──> payment_methods
  │       └──> subscription_usage
  │
  ├──> invoices
  │       └──> payment_transactions
  │
  └──> payment_methods
```

---

## 🚀 Installation

### 1. Installer les Dépendances

```bash
cd backend
pip install -r requirements.txt
```

Nouvelles dépendances ajoutées:
- `stripe==11.2.0` - Paiements
- `reportlab==4.2.5` - Génération PDF

### 2. Configurer les Variables d'Environnement

Ajoutez dans `backend/.env`:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Comment obtenir les clés Stripe:**
1. Créez un compte sur [stripe.com](https://stripe.com)
2. Allez dans Developers > API Keys
3. Copiez la Secret Key et Publishable Key
4. Pour le Webhook Secret: Developers > Webhooks > Add endpoint

### 3. Appliquer la Migration SQL

**Option A: Via Dashboard Supabase (Recommandé)**

1. Ouvrez [app.supabase.com](https://app.supabase.com)
2. Allez dans "SQL Editor"
3. Copiez le contenu de `create_subscription_tables.sql`
4. Exécutez le script

**Option B: Via Script Python**

```bash
cd backend
python apply_subscription_system.py
```

### 4. Redémarrer le Serveur

```bash
python server.py
```

Vous devriez voir:
```
✅ Système d'abonnement SaaS chargé avec succès
   📦 Plans d'abonnement disponibles
   💳 Paiements récurrents activés
   📄 Facturation automatique configurée
```

---

## 📡 API Endpoints

### Plans d'Abonnement

```http
GET /api/subscriptions/plans
GET /api/subscriptions/plans/{plan_id}
```

### Gestion Abonnement

```http
GET    /api/subscriptions/my-subscription
POST   /api/subscriptions/subscribe
PUT    /api/subscriptions/my-subscription
POST   /api/subscriptions/my-subscription/cancel
POST   /api/subscriptions/my-subscription/upgrade
POST   /api/subscriptions/my-subscription/downgrade
```

### Méthodes de Paiement

```http
GET    /api/subscriptions/payment-methods
POST   /api/subscriptions/payment-methods
PUT    /api/subscriptions/payment-methods/{id}/set-default
DELETE /api/subscriptions/payment-methods/{id}
```

### Factures

```http
GET /api/subscriptions/invoices
GET /api/subscriptions/invoices/{invoice_id}
GET /api/subscriptions/invoices/{invoice_id}/pdf
```

### Coupons

```http
POST /api/subscriptions/coupons/validate
```

### Usage & Limites

```http
GET /api/subscriptions/usage
GET /api/subscriptions/usage/check/{limit_type}
```

### Webhooks

```http
POST /api/subscriptions/webhooks/stripe
```

### Admin

```http
GET /api/subscriptions/admin/all
GET /api/subscriptions/admin/stats
```

---

## 💻 Utilisation du Middleware

### Vérifier l'Abonnement Actif

```python
from subscription_middleware import SubscriptionMiddleware

@router.post("/premium-feature")
async def premium_feature(
    user_id: str = Depends(SubscriptionMiddleware.require_active_subscription)
):
    # Code accessible uniquement avec abonnement actif
    return {"message": "Feature accessible"}
```

### Vérifier l'Accès à une Fonctionnalité

```python
@router.post("/generate-ai-content")
async def generate_ai_content(
    user_id: str = Depends(SubscriptionMiddleware.require_feature("ai_content_generation"))
):
    # Code accessible uniquement si le plan inclut l'IA
    return {"content": "Generated content"}
```

### Vérifier les Limites d'Usage

```python
@router.post("/products")
async def create_product(
    user_id: str = Depends(SubscriptionMiddleware.check_limit("products"))
):
    # Vérifie si l'utilisateur n'a pas atteint sa limite de produits
    # Code pour créer le produit

    # Incrémenter le compteur
    from subscription_middleware import increment_feature_usage
    increment_feature_usage(user_id, "products")

    return {"message": "Product created"}
```

### Obtenir les Infos d'Abonnement

```python
@router.get("/dashboard")
async def dashboard(
    subscription_info: dict = Depends(SubscriptionMiddleware.get_subscription_info)
):
    plan_name = subscription_info.get("plan", {}).get("name", "Free")
    has_ai = subscription_info.get("features", {}).get("ai_content_generation", False)

    return {
        "plan": plan_name,
        "can_use_ai": has_ai
    }
```

---

## 📊 Plans par Défaut

### Plans Merchants

| Plan | Prix/mois | Prix/an | Produits | Campagnes | Affiliés | Commission |
|------|-----------|---------|----------|-----------|----------|------------|
| **Freemium** | 0 MAD | 0 MAD | 5 | 1 | 10 | 15% |
| **Standard** | 299 MAD | 2,990 MAD | 50 | 10 | 100 | 10% |
| **Premium** | 799 MAD | 7,990 MAD | 200 | 50 | 500 | 7% |
| **Enterprise** | 1,999 MAD | 19,990 MAD | ∞ | ∞ | ∞ | 5% |

### Plans Influencers

| Plan | Prix/mois | Prix/an | Fonctionnalités |
|------|-----------|---------|-----------------|
| **Free** | 0 MAD | 0 MAD | Marketplace, Liens basiques |
| **Pro** | 99 MAD | 990 MAD | + Analytics, IA, Boost visibilité |
| **Elite** | 299 MAD | 2,990 MAD | + Branding, API, Account manager |

---

## 🎯 Fonctionnalités par Plan

### Toutes les Fonctionnalités

- ✅ `max_products` - Nombre maximum de produits
- ✅ `max_campaigns` - Nombre maximum de campagnes
- ✅ `max_affiliates` - Nombre maximum d'affiliés
- ✅ `ai_content_generation` - Génération de contenu IA
- ✅ `advanced_analytics` - Analytics avancés
- ✅ `priority_support` - Support prioritaire
- ✅ `custom_branding` - Branding personnalisé
- ✅ `api_access` - Accès API
- ✅ `export_data` - Export de données
- ✅ `commission_rate` - Taux de commission

---

## 🔄 Flux de Souscription

### 1. Utilisateur choisit un plan

```javascript
// Frontend
const response = await fetch('/api/subscriptions/subscribe', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    plan_id: 'plan-id-here',
    billing_cycle: 'monthly',
    payment_method_id: 'pm_stripe_id',
    coupon_code: 'LAUNCH50',
    start_trial: true
  })
});
```

### 2. Backend crée l'abonnement

- Vérifie qu'aucun abonnement actif n'existe
- Calcule les dates (essai, fin de période)
- Applique les réductions (coupons)
- Crée l'abonnement dans la DB
- Log l'événement

### 3. Traitement du paiement

- Crée une facture
- Crée une transaction
- Appelle Stripe Payment Intent
- Met à jour le statut selon la réponse

### 4. Activation

- Abonnement = `active` ou `trialing`
- Utilisateur a accès aux fonctionnalités
- Prochaine facturation programmée

---

## 🔔 Webhooks Stripe

### Configuration

1. Dans Stripe Dashboard > Webhooks
2. Ajoutez l'endpoint: `https://votredomaine.com/api/subscriptions/webhooks/stripe`
3. Sélectionnez les événements:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.deleted`

### Traitement

Les webhooks mettent automatiquement à jour:
- Statut des transactions
- Statut des factures
- Statut des abonnements
- Logs des événements

---

## 📄 Génération de Factures PDF

### Automatique

Les factures PDF sont générées automatiquement:
- À chaque paiement réussi
- Format professionnel avec logo
- Numérotation unique
- Détails complets (items, montants, TVA)

### Manuel

```python
from invoice_service import InvoiceService

# Générer et télécharger
pdf_bytes = InvoiceService.generate_invoice_pdf(invoice_id)

# Sauvegarder sur disque
InvoiceService.save_invoice_pdf(invoice_id, "/path/to/save.pdf")

# Envoyer par email
InvoiceService.send_invoice_email(invoice_id, user_email)
```

---

## 🔒 Sécurité

### Authentification
- JWT tokens avec expiration
- Vérification sur chaque requête
- Refresh tokens (à implémenter si nécessaire)

### Paiements
- Tokens Stripe (pas de données de carte stockées)
- PCI DSS compliant via Stripe
- Webhooks avec vérification de signature

### RGPD
- Accès aux données utilisateur
- Suppression de compte avec cascade
- Anonymisation des données sur demande
- Consentement pour newsletters

---

## 📈 Métriques & Analytics

### KPIs Disponibles

```python
# Via l'endpoint admin
GET /api/subscriptions/admin/stats

Response:
{
  "total_subscriptions": 150,
  "by_status": {
    "active": 120,
    "trialing": 20,
    "past_due": 5,
    "canceled": 5
  },
  "total_revenue": 125000.00,
  "mrr": 45000.00  # Monthly Recurring Revenue
}
```

### Tracking de l'Usage

- Compteurs par utilisateur/abonnement
- Historique des limites atteintes
- Alertes proactives avant dépassement

---

## 🧪 Tests

### Cartes de Test Stripe

```
Succès: 4242 4242 4242 4242
Échec:  4000 0000 0000 0002
3D Secure: 4000 0027 6000 3184
```

Date d'expiration: N'importe quelle date future
CVC: N'importe quel 3 chiffres

### Scénarios de Test

1. **Souscription avec essai**
   - Choisir un plan avec trial_days > 0
   - Vérifier status = "trialing"
   - Vérifier next_billing_date = trial_end_date

2. **Paiement réussi**
   - Utiliser carte 4242...
   - Vérifier facture = "paid"
   - Vérifier transaction = "succeeded"

3. **Paiement échoué**
   - Utiliser carte 4000 0000 0000 0002
   - Vérifier abonnement = "past_due"
   - Vérifier notification envoyée

4. **Upgrade de plan**
   - Passer de Standard à Premium
   - Vérifier calcul prorata
   - Vérifier accès aux nouvelles features

5. **Annulation**
   - Annuler immédiatement vs fin de période
   - Vérifier statut
   - Vérifier accès restreint

---

## 🐛 Dépannage

### Problème: Les endpoints ne sont pas accessibles

**Solution:**
```bash
# Vérifier que le serveur démarre sans erreur
python server.py

# Vous devriez voir:
✅ Système d'abonnement SaaS chargé avec succès
```

### Problème: Erreur "Table does not exist"

**Solution:**
```sql
-- Exécuter le SQL dans Supabase Dashboard
-- Fichier: create_subscription_tables.sql
```

### Problème: Paiement Stripe échoue

**Solution:**
1. Vérifier les clés Stripe dans .env
2. Vérifier les logs Stripe Dashboard
3. Tester avec cartes de test

### Problème: PDF ne se génère pas

**Solution:**
```bash
# Installer reportlab
pip install reportlab==4.2.5

# Vérifier les permissions d'écriture
# Le PDF est généré en mémoire par défaut
```

---

## 🔄 Paiements Récurrents

### Processus Automatique

Un script cron ou tâche planifiée doit appeler:

```python
from payment_service import PaymentService

# Pour chaque abonnement dont next_billing_date est aujourd'hui
result = PaymentService.process_recurring_payment(subscription_id)

if result["success"]:
    print("✅ Paiement réussi")
    # Facture créée automatiquement
    # Dates de l'abonnement mises à jour
else:
    print("❌ Paiement échoué")
    # Abonnement mis en "past_due"
    # Email de relance envoyé
```

### Configuration Cron (Linux)

```bash
# Exécuter tous les jours à 2h du matin
0 2 * * * cd /path/to/backend && python -c "from payment_service import process_all_recurring_payments; process_all_recurring_payments()"
```

---

## 📚 Ressources

### Documentation Stripe
- [Stripe Docs](https://stripe.com/docs)
- [Testing](https://stripe.com/docs/testing)
- [Webhooks](https://stripe.com/docs/webhooks)

### Documentation Supabase
- [Supabase Docs](https://supabase.com/docs)
- [PostgreSQL Functions](https://supabase.com/docs/guides/database/functions)

---

## 🎉 Félicitations !

Vous avez maintenant un système d'abonnement SaaS complet et professionnel !

### Prochaines Étapes Recommandées

1. **Personnaliser les plans** selon votre business model
2. **Configurer Stripe en mode production** (pas test)
3. **Implémenter le frontend React** (pages Plans & Mon Abonnement)
4. **Mettre en place les paiements récurrents** (cron job)
5. **Configurer les emails transactionnels** (SendGrid, AWS SES)
6. **Ajouter des analytics** pour suivre la croissance

---

## 📞 Support

Pour toute question ou assistance:
- 📧 Email: dev@shareyoursales.com
- 📖 Documentation complète dans ce fichier
- 🐛 Issues: GitHub Issues

---

**© 2025 ShareYourSales - Système d'Abonnement SaaS**
**Version: 1.0.0**
