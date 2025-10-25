# 💰 COMMENT LES INFLUENCEURS SONT PAYÉS

## 📋 Résumé Rapide

**Les influenceurs ont 2 sources de revenus:**
1. 🎯 **Commissions sur ventes** (10-20% par vente)
2. 📱 **Accès marketplace** via abonnement (99 MAD/mois)

---

## 💳 PLAN D'ABONNEMENT INFLUENCEUR

### Plan MARKETPLACE - 99 MAD/mois

```
┌─────────────────────────────────────────┐
│   PLAN INFLUENCEUR MARKETPLACE          │
├─────────────────────────────────────────┤
│                                         │
│  Prix: 99 MAD / mois                   │
│  (environ 9€ / mois)                   │
│                                         │
│  ✅ Accès complet marketplace          │
│  ✅ Profil influenceur visible         │
│  ✅ Génération liens affiliés          │
│  ✅ Statistiques en temps réel         │
│  ✅ Paiements automatiques commissions │
│                                         │
└─────────────────────────────────────────┘
```

**Pourquoi payer 99 MAD?**
- Accès aux produits/services à promouvoir
- Outils de tracking et analytics
- Paiements sécurisés des commissions
- Support technique

---

## 💸 COMMISSIONS SUR VENTES

### Comment ça marche?

```
┌──────────────────────────────────────────────────┐
│  EXEMPLE DE VENTE                                │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. Client achète via lien influenceur          │
│     Montant: 1000 MAD                           │
│                                                  │
│  2. Système calcule les commissions:            │
│     • Influenceur: 10% = 100 MAD               │
│     • Plateforme: 5% = 50 MAD                  │
│     • Marchand: 85% = 850 MAD                  │
│                                                  │
│  3. Commission ajoutée au solde influenceur    │
│     Status: "pending" (14 jours)               │
│                                                  │
│  4. Après 14 jours sans retour:                │
│     Status: "completed"                        │
│     Solde disponible pour retrait             │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Taux de Commission par Catégorie

| Catégorie | Commission Influenceur | Commission Plateforme |
|-----------|------------------------|----------------------|
| **Beauté** | 15-20% | 5% |
| **Mode** | 12-18% | 5% |
| **Tech** | 8-12% | 5% |
| **Food** | 10-15% | 5% |
| **Services** | 10-15% | 5% |

---

## 🔄 PROCESSUS DE PAIEMENT

### Étapes Complètes

```
┌────────────────────────────────────────────┐
│  JOUR 0: VENTE                             │
├────────────────────────────────────────────┤
│  Client achète: 1000 MAD                   │
│  Commission influenceur: 100 MAD           │
│  Status: "pending"                         │
│  Solde visible mais non disponible        │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│  JOUR 1-14: PÉRIODE VALIDATION             │
├────────────────────────────────────────────┤
│  ⏳ Délai de rétractation légal (14j)      │
│  ⏳ Vérification livraison                 │
│  ⏳ Pas de retour marchandise              │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│  JOUR 14+: VALIDATION                      │
├────────────────────────────────────────────┤
│  ✅ Status: "pending" → "completed"        │
│  ✅ Commission ajoutée au solde disponible │
│  ✅ Solde actuel: 450 MAD                  │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│  QUAND SOLDE ≥ 500 MAD (50€)               │
├────────────────────────────────────────────┤
│  🎉 PAIEMENT AUTOMATIQUE                   │
│  💰 Virement bancaire automatique          │
│  📧 Email de confirmation                   │
│  🧾 Reçu de paiement                       │
└────────────────────────────────────────────┘
```

---

## 💰 SYSTÈME DE PAIEMENT AUTOMATIQUE

### Seuil Minimum: 500 MAD (50€)

**Pourquoi 500 MAD minimum?**
- Réduit les frais bancaires
- Paiements plus significatifs
- Moins de transactions administratives

### Comment ça marche?

```python
# Automatique - RIEN À FAIRE!

if solde_disponible >= 500:
    # 1. Création paiement automatique
    paiement = {
        "montant": solde_disponible,
        "methode": "virement_bancaire",
        "status": "processing"
    }

    # 2. Virement bancaire
    virement_vers_iban_influenceur()

    # 3. Email confirmation
    envoyer_email_confirmation()

    # 4. Reset solde
    solde_disponible = 0
```

### Notifications

L'influenceur reçoit:
- 📧 **Email**: Paiement en cours
- 🔔 **Notification plateforme**: Virement initié
- 📄 **Reçu PDF**: Détails du paiement

---

## 📊 TABLEAU DE BORD INFLUENCEUR

### Vue d'Ensemble

```
┌──────────────────────────────────────────────────┐
│   DASHBOARD INFLUENCEUR                          │
├──────────────────────────────────────────────────┤
│                                                  │
│  💰 Solde Disponible                            │
│  ┌────────────────┐                             │
│  │   450 MAD      │  ← Prêt pour retrait       │
│  └────────────────┘    (seuil: 500 MAD)        │
│                                                  │
│  ⏳ Commissions en attente                      │
│  ┌────────────────┐                             │
│  │   280 MAD      │  ← Validation en cours      │
│  └────────────────┘    (14 jours)              │
│                                                  │
│  📊 Ce mois                                     │
│  • Ventes: 23                                   │
│  • Clics: 1,482                                 │
│  • Taux conversion: 1.6%                        │
│  • Gains totaux: 730 MAD                        │
│                                                  │
│  📈 Graphique gains 7 derniers jours            │
│  ┌──────────────────────────────────┐           │
│  │ ▂▅▇█▅▃▆                          │           │
│  └──────────────────────────────────┘           │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 💼 EXEMPLE CONCRET

### Parcours Influenceur: @sarah_beauty

#### Mois 1

```
1️⃣ Abonnement Marketplace: -99 MAD
   → Accès à 500+ produits beauté

2️⃣ Promotion de 15 produits
   → Création de 15 liens affiliés

3️⃣ Ventes réalisées:
   • 25 oct: 800 MAD → Commission: 120 MAD (15%)
   • 27 oct: 1,200 MAD → Commission: 180 MAD (15%)
   • 30 oct: 600 MAD → Commission: 90 MAD (15%)
   • 2 nov: 1,500 MAD → Commission: 225 MAD (15%)

   Total commissions: 615 MAD

4️⃣ Après validation (14 jours):
   • Solde disponible: 615 MAD
   • Seuil atteint (≥500 MAD) ✅

5️⃣ Paiement automatique: +615 MAD
   → Virement bancaire sous 2-3 jours
```

**Bilan Mois 1:**
- Investissement: -99 MAD (abonnement)
- Gains: +615 MAD (commissions)
- **Net: +516 MAD** (environ 49€)
- ROI: 521% 🎉

---

## 🏦 MÉTHODES DE PAIEMENT

### Pour Recevoir les Commissions

1. **Virement Bancaire** (Recommandé)
   - IBAN marocain
   - Délai: 2-3 jours ouvrés
   - Frais: Gratuit

2. **Compte Mobile Money**
   - Orange Money / inwi Money
   - Délai: Instantané
   - Frais: 1% (plafonné 20 MAD)

3. **PayPal** (International)
   - Pour influenceurs hors Maroc
   - Délai: 1 jour
   - Frais: 2.9% + 0.30€

---

## 📱 ACCÈS MARKETPLACE

### Qu'est-ce que l'influenceur peut promouvoir?

#### 1. PRODUITS (Onglet 1)
```
254 produits disponibles
• Mode & Accessoires
• Beauté & Cosmétiques
• Tech & Gadgets
• Maison & Décoration
• Sport & Fitness

Commission: 10-20% selon catégorie
```

#### 2. SERVICES (Onglet 2)
```
43 services disponibles
• Développement Web
• Design Graphique
• Shooting Photo
• Marketing Digital
• Consultation Business

Commission: 10-15% par contrat
```

#### 3. COMMERCIAUX (Onglet 3)
```
78 commerciaux actifs
• Collaboration B2B
• Partage de leads
• Commission sur ventes closes

Commission: Variable selon deal
```

#### 4. AUTRES INFLUENCEURS (Onglet 4)
```
124 influenceurs actifs
• Collaborations croisées
• Partenariats de marque
• Échange de visibilité

Pas de commission directe
```

---

## ⚖️ CONDITIONS LÉGALES

### Délai de Validation: 14 Jours

**Pourquoi 14 jours?**
- ✅ Délai légal de rétractation (France/UE)
- ✅ Temps de livraison + vérification
- ✅ Protection contre fraudes
- ✅ Gestion des retours produits

### Statuts de Commission

| Statut | Description | Action |
|--------|-------------|--------|
| `pending` | Vente récente (<14j) | Attente validation |
| `completed` | Vente validée (≥14j) | Ajout au solde |
| `cancelled` | Retour marchandise | Commission annulée |
| `refunded` | Remboursement client | Commission retirée |

---

## 🔍 SUIVI EN TEMPS RÉEL

### Analytics Disponibles

```
📊 Statistiques Influenceur
━━━━━━━━━━━━━━━━━━━━━━━━

Vue d'ensemble
├─ Clics totaux: 3,482
├─ Ventes générées: 67
├─ Taux conversion: 1.9%
└─ Gains ce mois: 1,245 MAD

Performance par lien
├─ Lien #1 (Robe été): 450 clics → 8 ventes
├─ Lien #2 (Maquillage): 380 clics → 12 ventes
└─ Lien #3 (Parfum): 290 clics → 4 ventes

Meilleurs produits
├─ 1. Maquillage Pro Kit: 12 ventes (1,800 MAD)
├─ 2. Robe été 2025: 8 ventes (1,200 MAD)
└─ 3. Sneakers mode: 6 ventes (900 MAD)
```

---

## 🎯 COMMENT MAXIMISER SES GAINS?

### Stratégies Recommandées

1. **Choisir les bons produits**
   - Alignés avec votre audience
   - Commission élevée (15-20%)
   - Produits tendance/populaires

2. **Créer du contenu de qualité**
   - Photos/vidéos authentiques
   - Reviews honnêtes
   - Storytelling engageant

3. **Analyser les performances**
   - Suivre le taux de conversion
   - Identifier les meilleurs produits
   - Optimiser les liens faibles

4. **Diversifier les promotions**
   - Mix produits/services
   - Différentes gammes de prix
   - Plusieurs catégories

---

## ❓ FAQ

### 1. Dois-je payer 99 MAD chaque mois?
**Oui**, tant que vous voulez accès au marketplace. Si vous annulez:
- ❌ Accès marketplace perdu
- ❌ Impossibilité créer nouveaux liens
- ✅ Liens existants continuent de fonctionner
- ✅ Commissions en cours validées normalement

### 2. Quand vais-je recevoir mes commissions?
**Automatiquement** dès que:
1. Ventes validées (≥14 jours)
2. Solde ≥ 500 MAD (50€)

Sinon, vous pouvez attendre d'atteindre le seuil.

### 3. Puis-je demander un paiement avant 500 MAD?
**Non**, le seuil minimum est de 500 MAD pour:
- Réduire les frais bancaires
- Éviter les micro-paiements
- Optimiser les coûts

### 4. Que se passe-t-il en cas de retour produit?
Si client retourne le produit dans les 14 jours:
- ❌ Commission annulée
- 📧 Notification envoyée
- 📊 Solde ajusté

### 5. Comment je reçois mes paiements?
**Automatiquement** par virement bancaire vers votre IBAN enregistré.
Délai: 2-3 jours ouvrés après déclenchement.

### 6. Puis-je promouvoir plusieurs marchands?
**Oui**, vous avez accès à:
- 254 produits de différents marchands
- 43 services de différents prestataires
- Commissions variables selon chaque marchand

### 7. Y a-t-il une limite de gains?
**Non**, vous pouvez gagner:
- ∞ Commissions illimitées
- ∞ Nombre de liens illimités
- ∞ Nombre de ventes illimité

---

## 📞 SUPPORT

### Besoin d'aide?

**Email**: support@shareyoursales.com
**WhatsApp**: +212 6XX XX XX XX
**FAQ**: https://shareyoursales.com/faq

**Temps de réponse**:
- Plan Marketplace: 24-48h
- Urgent: Utiliser WhatsApp

---

```
╔═══════════════════════════════════════════════════╗
║                                                   ║
║  💰 RÉSUMÉ SIMPLE                                 ║
║                                                   ║
║  1. Payer 99 MAD/mois pour accès marketplace    ║
║  2. Promouvoir produits/services                 ║
║  3. Gagner 10-20% commission par vente           ║
║  4. Recevoir paiement auto à 500 MAD             ║
║                                                   ║
║  ROI moyen: 5x l'investissement mensuel          ║
║  (99 MAD → 500+ MAD de gains)                    ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

**Date**: 25 Octobre 2025
**Version**: 1.0
**Statut**: ✅ Système Actif
