# 💰 SYSTÈME DE PAIEMENT AUTOMATIQUE

## 📋 Vue d'Ensemble

Le système de paiement automatique permet aux influenceurs de recevoir automatiquement leurs commissions dès que leur solde atteint **50€**, sans avoir à faire de demande manuelle.

---

## 🔄 Fonctionnement Complet

### **ÉTAPE 1 : Vente d'un Produit**

```
Client achète via lien d'affiliation
      ↓
Vente créée avec statut: "pending"
Commission calculée: 15% (exemple)
      ↓
⏳ Période d'attente: 14 jours
```

**Exemple :**
- Produit: 100€
- Commission influenceur: 15€
- Statut: `pending` (en attente de validation)

---

### **ÉTAPE 2 : Validation Automatique (J+14)**

**🤖 Tâche automatique quotidienne (2h du matin)**

```python
# Le système vérifie toutes les ventes de plus de 14 jours
Vérification:
✅ Pas de retour client
✅ Pas de remboursement demandé
✅ Produit livré

Si tout OK:
  - Statut passe à "completed"
  - Commission ajoutée au solde de l'influenceur
  - Notification envoyée
```

**Exemple :**
```
Vente du 1er novembre
    ↓
15 novembre (J+14) - Validation automatique
    ↓
Solde influenceur: 35€ → 50€
```

---

### **ÉTAPE 3 : Paiement Automatique (Chaque Vendredi)**

**🤖 Tâche automatique hebdomadaire (Vendredi 10h)**

```python
Le système cherche tous les influenceurs avec:
✅ Solde ≥ 50€
✅ Méthode de paiement configurée
✅ Pas de paiement en cours

Pour chacun:
  1. Crée un ordre de paiement
  2. Traite le paiement (PayPal ou Virement)
  3. Débite le solde
  4. Envoie notification + email
```

**Exemple :**
```
Vendredi 22 novembre - 10h00
    ↓
Influenceur "Marie" : 75€ disponibles
Méthode: PayPal (marie@email.com)
    ↓
💸 Paiement automatique: 75€
    ↓
Email: "Votre paiement de 75€ a été traité !"
Solde nouveau: 0€
```

---

## 🎛️ Configuration pour l'Influenceur

### **Étape 1 : Configurer la Méthode de Paiement**

Page: `/settings/payment-settings`

#### **Option A : PayPal (Recommandé)**
```
Avantages:
✅ Paiement instantané
✅ Pas de frais bancaires
✅ Simple et rapide

Informations requises:
- Email PayPal
```

#### **Option B : Virement Bancaire (SEPA)**
```
Avantages:
✅ Pas de compte PayPal nécessaire
✅ Direct sur compte bancaire

Informations requises:
- IBAN
- Nom du titulaire
- BIC/SWIFT (optionnel)

Délai: 1-2 jours ouvrés
```

### **Étape 2 : Suivre son Solde**

**Dashboard Influenceur** affiche en temps réel :

```
┌─────────────────────────────────────┐
│ 💰 Solde Disponible : 75.50€       │
│ ⏳ En attente validation : 45.00€   │
│ 📅 Prochain paiement : Vendredi 29 │
└─────────────────────────────────────┘
```

---

## 🛡️ Règles de Sécurité

### **1. Délai de Validation (14 jours)**

**Pourquoi ?**
- Délai légal de rétractation en France
- Protection contre les retours frauduleux
- Temps de vérification de la livraison

**Statuts possibles :**
```
pending    → En attente (< 14 jours)
completed  → Validé (≥ 14 jours, pas de retour)
refunded   → Remboursé (client retourne le produit)
cancelled  → Annulé (erreur ou fraude)
```

### **2. Seuil Minimum (50€)**

**Pourquoi ?**
- Réduire les frais de transaction
- PayPal facture par transaction
- Éviter trop de micro-paiements

**Règle :**
```javascript
if (solde >= 50€ && méthode_configurée) {
  paiement_automatique = true
} else {
  continuer_accumulation
}
```

### **3. Gestion des Retours**

**Scénario : Client retourne le produit**

```
1. Marchand signale le retour
   ↓
2. API: POST /api/sales/{sale_id}/refund
   ↓
3. Statut vente: "refunded"
   ↓
4. Commission annulée
   ↓
5. Si déjà créditée: Solde débité
   ↓
6. Notification influenceur
```

**Exemple :**
```
Vente initiale: +15€
Client retourne après 5 jours
Commission annulée: -15€
Solde: Inchangé (ou débité si déjà validé)
```

---

## 📊 Méthodes de Paiement

### **PayPal (Automatique)**

**Implémentation :**
```python
import paypalrestsdk

paypalrestsdk.configure({
  "mode": "live",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_SECRET"
})

payout = paypalrestsdk.Payout({
  "sender_batch_header": {
    "sender_batch_id": f"batch_{timestamp}",
    "email_subject": "Commission ShareYourSales"
  },
  "items": [{
    "recipient_type": "EMAIL",
    "amount": {"value": "75.50", "currency": "EUR"},
    "receiver": "influencer@email.com",
    "note": "Commission affiliation octobre 2025"
  }]
})

if payout.create():
  print(f"✅ Paiement envoyé: {payout.batch_header.payout_batch_id}")
```

**Frais :**
- Envoyer de l'argent: Gratuit si solde PayPal
- Recevoir: Gratuit
- Retrait vers banque: 1€ fixe

### **Virement SEPA (Semi-Automatique)**

**Implémentation :**
```python
# Génération fichier SEPA XML
import sepaxml

sepa = sepaxml.SepaTransfer({
  "name": "ShareYourSales",
  "IBAN": "FR76...",
  "BIC": "BNPAFRPP"
})

sepa.add_payment({
  "name": "Marie Influenceuse",
  "IBAN": "FR76...",
  "amount": 7550,  # En centimes
  "description": "Commission octobre 2025"
})

# Export fichier pour banque
sepa.export_to_file("virements_2025_11_22.xml")
```

**Process :**
1. Génération automatique du fichier XML
2. Admin télécharge le fichier
3. Import dans interface bancaire
4. Validation manuelle
5. Virement traité sous 1-2 jours

---

## 🔔 Notifications

### **Email de Paiement**

**Template :**
```
Objet: 💰 Votre paiement de 75.50€ a été traité

Bonjour Marie,

Bonne nouvelle ! Votre paiement a été traité avec succès.

💰 Montant: 75.50€
📅 Date: 22 novembre 2025
💳 Méthode: PayPal
🆔 Référence: PAYPAL_20251122105432

Vous devriez recevoir les fonds sous 24h sur votre compte PayPal.

Détails de vos gains:
- Nombre de ventes: 8
- Commission moyenne: 9.44€
- Produit le plus vendu: iPhone 15 Pro

Continuez comme ça ! 🚀

L'équipe ShareYourSales
```

### **Notifications In-App**

```javascript
Types de notifications:
- payout_completed: "Paiement de X€ effectué"
- sale_validated: "Vente validée: +X€"
- payment_setup_reminder: "Configurez votre paiement (solde ≥ 30€)"
- balance_milestone: "Félicitations ! Solde ≥ 50€"
```

---

## ⚙️ Administration

### **Endpoints Admin**

#### **1. Validation Manuelle**
```http
POST /api/admin/validate-sales
Authorization: Bearer {admin_token}

Response:
{
  "validated_sales": 12,
  "total_commission": 180.50,
  "influencers_updated": 7
}
```

#### **2. Paiements Manuels**
```http
POST /api/admin/process-payouts
Authorization: Bearer {admin_token}

Response:
{
  "processed_count": 5,
  "total_paid": 425.75,
  "failed_count": 1,
  "failed_payments": [...]
}
```

#### **3. Gérer un Retour**
```http
POST /api/sales/{sale_id}/refund
Body: {
  "reason": "customer_return"
}

Response:
{
  "success": true,
  "commission_cancelled": 15.00
}
```

---

## 📅 Planning des Tâches Automatiques

```
┌─────────────┬──────────────────┬─────────────────────────┐
│ Tâche       │ Fréquence        │ Horaire                 │
├─────────────┼──────────────────┼─────────────────────────┤
│ Validation  │ Quotidienne      │ 2h00                    │
│ Paiements   │ Hebdomadaire     │ Vendredi 10h00          │
│ Nettoyage   │ Quotidienne      │ 3h00                    │
│ Rappels     │ Hebdomadaire     │ Lundi 9h00              │
└─────────────┴──────────────────┴─────────────────────────┘
```

---

## 🧪 Tests

### **Test Manuel**

```bash
# Terminal 1: Démarrer le serveur
cd backend
python server.py

# Terminal 2: Exécuter les tests
python auto_payment_service.py

# Ou test du scheduler
python scheduler.py
```

### **Créer des Ventes de Test**

```python
# Dans seed_all_data.py
from datetime import datetime, timedelta

# Créer vente de 15 jours en arrière (sera validée)
past_date = (datetime.now() - timedelta(days=15)).isoformat()

sale = {
  "product_id": "prod_123",
  "influencer_id": "inf_456",
  "amount": 100,
  "influencer_commission": 15,
  "status": "pending",
  "created_at": past_date
}
supabase.table('sales').insert(sale).execute()
```

---

## 📈 Métriques de Performance

### **KPIs à Suivre**

```
1. Taux de validation automatique
   Objectif: 95%+ (peu de retours)

2. Délai moyen de paiement
   Objectif: < 7 jours après validation

3. Taux d'échec des paiements
   Objectif: < 2%

4. Satisfaction influenceurs
   Sondage: "Êtes-vous satisfait du système de paiement ?"
```

---

## 🚀 Installation

```bash
# 1. Installer les dépendances
cd backend
pip install -r requirements.txt

# 2. Configurer PayPal (optionnel)
# Ajouter dans .env:
PAYPAL_MODE=sandbox  # ou live
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_secret

# 3. Lancer le serveur (scheduler démarre automatiquement)
python server.py
```

---

## ✅ Checklist de Mise en Production

- [ ] Configurer PayPal en mode `live`
- [ ] Tester paiements PayPal sandbox
- [ ] Configurer SMTP pour emails
- [ ] Vérifier les tâches cron (logs)
- [ ] Backup base de données quotidien
- [ ] Monitoring des paiements échoués
- [ ] Documentation utilisateur publiée
- [ ] Support client formé

---

## 🆘 Dépannage

### **Problème : Paiement échoué**

```
1. Vérifier logs du serveur
2. Vérifier credentials PayPal
3. Vérifier solde compte PayPal
4. Contacter influenceur (email incorrect?)
```

### **Problème : Validation ne se fait pas**

```
1. Vérifier que scheduler est actif
2. Vérifier logs: python scheduler.py
3. Exécuter manuellement: POST /api/admin/validate-sales
```

---

## 📞 Contact

Questions ? Bugs ? Suggestions ?

- 📧 Email: dev@shareyoursales.com
- 📄 Documentation: docs.shareyoursales.com
- 🐛 Issues: github.com/shareyoursales/issues
