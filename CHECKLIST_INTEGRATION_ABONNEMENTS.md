# ✅ CHECKLIST INTÉGRATION - SYSTÈME D'ABONNEMENTS

## 📋 À FAIRE POUR FINALISER

Cochez au fur et à mesure ✓

---

## 🔧 PHASE 1: INTÉGRATION CODE (15 min)

### Frontend - Routes
```jsx
// Fichier: frontend/src/App.js

[ ] Ajouter imports:
    import SubscriptionPlans from './pages/subscription/SubscriptionPlans';
    import BillingHistory from './pages/subscription/BillingHistory';
    import CancelSubscription from './pages/subscription/CancelSubscription';
    import SubscriptionCancelled from './pages/subscription/SubscriptionCancelled';

[ ] Ajouter routes dans <Routes>:
    <Route path="/subscription/plans" element={<SubscriptionPlans />} />
    <Route path="/subscription/billing" element={<BillingHistory />} />
    <Route path="/subscription/cancel" element={<CancelSubscription />} />
    <Route path="/subscription/cancelled" element={<SubscriptionCancelled />} />
```

### Frontend - Alertes Dashboard
```jsx
// Fichier: frontend/src/components/MerchantDashboard.js

[ ] Ajouter import:
    import SubscriptionLimitAlert from './subscription/SubscriptionLimitAlert';

[ ] Ajouter composant dans JSX (ligne 1):
    <SubscriptionLimitAlert />

// Fichier: frontend/src/components/InfluencerDashboard.js

[ ] Faire pareil pour influenceur
```

### Frontend - Menu Sidebar
```jsx
// Fichier: frontend/src/components/Sidebar.js

[ ] Ajouter section menu:
    <Link to="/subscription/plans">📊 Plans & Tarifs</Link>
    <Link to="/subscription/billing">📄 Mes Factures</Link>
    <Link to="/subscription/cancel">⏸️ Annuler</Link>
```

---

## 🔑 PHASE 2: CONFIGURATION STRIPE (30 min)

### Créer compte Stripe
```
[ ] Aller sur https://stripe.com
[ ] Créer compte (si pas déjà fait)
[ ] Activer mode "Test" (activé par défaut)
```

### Obtenir clés API
```
[ ] Aller sur https://dashboard.stripe.com/test/apikeys
[ ] Copier "Secret key" (sk_test_...)
[ ] Copier "Publishable key" (pk_test_...)
```

### Configurer .env
```bash
# Fichier: backend/.env

[ ] Ajouter (ou modifier):
    STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxxxxxxxxxx
    STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxxxxxxxxxx
    STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx  # À faire plus tard
```

### Créer produits Stripe
```
[ ] Dashboard Stripe → Products → New product

Créer ces 7 produits:

[ ] MERCHANT_FREEMIUM
    Nom: Merchant Freemium
    Prix mensuel: 0€
    Prix annuel: 0€

[ ] MERCHANT_STANDARD
    Nom: Merchant Standard
    Prix mensuel: 49€
    Prix annuel: 470€

[ ] MERCHANT_PREMIUM
    Nom: Merchant Premium
    Prix mensuel: 99€
    Prix annuel: 950€

[ ] MERCHANT_PRO
    Nom: Merchant Pro
    Prix mensuel: 199€
    Prix annuel: 1910€

[ ] MERCHANT_ENTERPRISE
    Nom: Merchant Enterprise
    Prix mensuel: 499€
    Prix annuel: 4790€

[ ] INFLUENCER_FREEMIUM
    Nom: Influencer Freemium
    Prix mensuel: 0€
    Prix annuel: 0€

[ ] INFLUENCER_PRO
    Nom: Influencer Pro
    Prix mensuel: 79€
    Prix annuel: 760€
```

### Mettre à jour base de données
```sql
-- Fichier: Supabase SQL Editor

[ ] Pour chaque produit, copier Price ID et exécuter:

UPDATE subscription_plans 
SET 
  stripe_price_id_monthly = 'price_XXXXX',  -- Remplacer
  stripe_price_id_yearly = 'price_YYYYY'    -- Remplacer
WHERE code = 'merchant_standard';

[ ] Répéter pour les 7 plans
```

---

## 🧪 PHASE 3: TESTS (30 min)

### Test 1: Routes fonctionnent
```
[ ] npm start
[ ] Aller sur http://localhost:3000/subscription/plans
[ ] Page affiche 7 plans avec prix ✓
[ ] Toggle Mensuel/Annuel fonctionne ✓
```

### Test 2: Alertes limites
```
[ ] Créer 4 produits (80% de limite Freemium)
[ ] Banner jaune apparaît en haut ✓
[ ] Créer 5e produit (100%)
[ ] Modal rouge bloque l'action ✓
[ ] Click "Voir les plans" → Redirection ✓
```

### Test 3: Menu sidebar
```
[ ] Ouvrir sidebar
[ ] Section "Abonnement" visible ✓
[ ] 3 liens présents ✓
[ ] Click sur liens → Navigation OK ✓
```

### Test 4: Page factures
```
[ ] Menu → "Mes Factures"
[ ] Si aucune facture: message "Aucune facture disponible" ✓
[ ] (Après paiement): Liste factures affichée ✓
```

### Test 5: Page annulation
```
[ ] Menu → "Annuler l'abonnement"
[ ] Form avec dropdown raisons ✓
[ ] Radio buttons type annulation ✓
[ ] Section "Ce que vous perdrez" ✓
[ ] Alternatives proposées ✓
```

### Test 6: Paiement Stripe (Test)
```
[ ] Page plans → Sélectionner Standard
[ ] Click "Choisir ce plan"
[ ] Redirection vers checkout.stripe.com ✓
[ ] Entrer carte test: 4242 4242 4242 4242
[ ] Date: Future (ex: 12/25)
[ ] CVC: 123
[ ] Paiement réussi ✓
[ ] Redirection vers app ✓
```

### Test 7: Vérification backend
```
[ ] Backend server en cours d'exécution
[ ] Pas d'erreurs dans terminal
[ ] Logs affichent requêtes API
```

---

## 🚀 PHASE 4: PRODUCTION (Optionnel)

### Webhook Stripe
```
[ ] Dashboard Stripe → Developers → Webhooks
[ ] Add endpoint
[ ] URL: https://votre-domaine.com/api/webhooks/stripe
[ ] Sélectionner événements:
    [ ] invoice.paid
    [ ] invoice.payment_failed
    [ ] customer.subscription.deleted
    [ ] customer.subscription.updated
    [ ] checkout.session.completed
[ ] Copier "Signing secret" (whsec_...)
[ ] Ajouter dans .env: STRIPE_WEBHOOK_SECRET=whsec_...
```

### Mode Live Stripe
```
[ ] Dashboard Stripe → Passer en mode "Live"
[ ] Obtenir nouvelles clés live (sk_live_...)
[ ] Remplacer dans .env
[ ] Créer produits en mode Live
[ ] Tester avec vraie carte
```

### SSL/HTTPS
```
[ ] Activer SSL sur domaine
[ ] URLs callback Stripe en HTTPS
[ ] Tester webhooks en production
```

---

## ✅ VÉRIFICATION FINALE

### Fonctionnalités critiques
```
[ ] ✅ User peut voir les plans
[ ] ✅ User peut upgrader (test Stripe)
[ ] ✅ Alertes apparaissent avant limite
[ ] ✅ Modal bloque à 100%
[ ] ✅ User peut voir factures
[ ] ✅ User peut annuler abonnement
[ ] ✅ Webhooks synchronisent DB
[ ] ✅ Middleware vérifie limites
[ ] ✅ Historique enregistré
```

### Performance
```
[ ] ✅ Pages chargent < 2 secondes
[ ] ✅ Pas d'erreurs console
[ ] ✅ Pas d'erreurs backend
[ ] ✅ Design responsive mobile
```

### Sécurité
```
[ ] ✅ Clés Stripe sécurisées (.env)
[ ] ✅ Webhooks signature validée
[ ] ✅ Limites vérifiées côté serveur
[ ] ✅ Authentification sur tous endpoints
```

---

## 📝 NOTES

```
Problèmes rencontrés:
_____________________________________________________
_____________________________________________________
_____________________________________________________

Solutions appliquées:
_____________________________________________________
_____________________________________________________
_____________________________________________________

Modifications faites:
_____________________________________________________
_____________________________________________________
_____________________________________________________
```

---

## 🎉 FÉLICITATIONS !

```
Si tout est coché ✅

Votre système d'abonnements est:
✨ Intégré
✨ Configuré
✨ Testé
✨ Production Ready

Prochaines étapes (optionnelles):
- Trial gratuit 14 jours
- Emails automatiques
- Dashboard analytics admin
```

---

**Date complétion:** __________________  
**Par:** __________________  
**Version:** 1.0  
**Statut:** [ ] En cours  [ ] Terminé ✅
