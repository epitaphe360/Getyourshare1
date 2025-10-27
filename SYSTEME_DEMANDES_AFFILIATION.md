# 🤝 Système de Demandes d'Affiliation

## 📋 Vue d'ensemble

Transformation du système de génération automatique de liens en un **système de demandes d'affiliation avec validation par le marchand**.

---

## 🔄 Nouveau Flux de Travail

### 1️⃣ **Influenceur : Demander un lien d'affiliation**

```
1. Dashboard Influenceur
   ↓
2. Clic "Demander un Lien d'Affiliation"
   ↓
3. Modal : Sélection du produit
   ↓
4. Formulaire de demande :
   - Produit sélectionné
   - Message au marchand (optionnel)
   - Statistiques automatiques (followers, engagement)
   ↓
5. Envoi de la demande
   ↓
6. Status : "En attente de validation"
```

### 2️⃣ **Marchand : Recevoir et traiter la demande**

```
1. Notification : "Nouvelle demande d'affiliation"
   ↓
2. Dashboard Marchand → Section "Demandes d'Affiliation"
   ↓
3. Liste des demandes en attente
   ↓
4. Consulter la demande :
   - Profil de l'influenceur
   - Statistiques (followers, engagement)
   - Message de l'influenceur
   - Produit concerné
   ↓
5. Décision :
   Option A: APPROUVER → Lien créé automatiquement
   Option B: REFUSER → Demande rejetée avec motif
```

### 3️⃣ **Système : Création automatique du lien**

```
Marchand approuve
   ↓
Trigger SQL activé
   ↓
Création automatique dans trackable_links :
   - short_code généré
   - merchant_url configuré
   - is_active = true
   ↓
Notification à l'influenceur
   ↓
Lien disponible dans "Mes Liens"
```

---

## 🗄️ Structure de la Base de Données

### Table : `affiliation_requests`

```sql
CREATE TABLE affiliation_requests (
    id UUID PRIMARY KEY,
    influencer_id UUID NOT NULL,
    product_id UUID NOT NULL,
    merchant_id UUID NOT NULL,
    
    -- Demande
    message TEXT,
    influencer_stats JSONB,
    
    -- Statut
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Réponse
    merchant_response TEXT,
    reviewed_at TIMESTAMP,
    reviewed_by UUID,
    
    -- Contraintes
    UNIQUE(influencer_id, product_id)
);
```

### Statuts possibles

| Statut | Description | Action suivante |
|--------|-------------|-----------------|
| `pending` | En attente de validation | Marchand doit répondre |
| `approved` | Approuvée par le marchand | Lien créé automatiquement |
| `rejected` | Refusée par le marchand | Influenceur peut redemander après 30j |
| `cancelled` | Annulée par l'influenceur | Archivée |

---

## 🎯 Endpoints API

### **Influenceur**

#### 1. Créer une demande
```http
POST /api/affiliation/request
Content-Type: application/json

{
  "product_id": "uuid",
  "message": "Je suis influenceur mode avec 50K followers...",
  "stats": {
    "followers": 50000,
    "engagement_rate": 4.5,
    "platforms": ["Instagram", "TikTok"]
  }
}

Response 201:
{
  "success": true,
  "request_id": "uuid",
  "status": "pending",
  "message": "Demande envoyée au marchand"
}
```

#### 2. Voir mes demandes
```http
GET /api/influencer/affiliation-requests

Response 200:
[
  {
    "id": "uuid",
    "product_name": "T-shirt Vintage",
    "merchant_company": "FashionCo",
    "status": "pending",
    "created_at": "2025-10-23T10:00:00Z",
    "commission_rate": 15
  }
]
```

#### 3. Annuler une demande
```http
DELETE /api/affiliation/request/{request_id}

Response 200:
{
  "success": true,
  "message": "Demande annulée"
}
```

---

### **Marchand**

#### 1. Voir les demandes reçues
```http
GET /api/merchant/affiliation-requests?status=pending

Response 200:
[
  {
    "id": "uuid",
    "influencer_name": "Emma Style",
    "influencer_email": "emma@example.com",
    "product_name": "T-shirt Vintage",
    "message": "Bonjour, je voudrais...",
    "stats": {
      "followers": 50000,
      "engagement_rate": 4.5
    },
    "created_at": "2025-10-23T10:00:00Z"
  }
]
```

#### 2. Approuver une demande
```http
POST /api/merchant/affiliation-requests/{request_id}/approve
Content-Type: application/json

{
  "response": "Bienvenue dans notre programme d'affiliation!"
}

Response 200:
{
  "success": true,
  "message": "Demande approuvée",
  "tracking_link": {
    "id": "uuid",
    "short_code": "ABC12345",
    "url": "http://localhost:8001/r/ABC12345"
  }
}
```

#### 3. Refuser une demande
```http
POST /api/merchant/affiliation-requests/{request_id}/reject
Content-Type: application/json

{
  "response": "Merci pour votre intérêt, mais..."
}

Response 200:
{
  "success": true,
  "message": "Demande refusée"
}
```

---

## 🎨 Interface Utilisateur

### **Dashboard Influenceur**

#### Section : "Demander un Lien"

```javascript
<Button onClick={() => setShowRequestModal(true)}>
  <Plus /> Demander un Lien d'Affiliation
</Button>
```

#### Modal de Demande

```
┌─────────────────────────────────────────┐
│ 📝 Demander un Lien d'Affiliation      │
├─────────────────────────────────────────┤
│                                         │
│ Produit: [Dropdown avec recherche]     │
│                                         │
│ Votre message au marchand (optionnel): │
│ ┌─────────────────────────────────┐   │
│ │ Bonjour,                        │   │
│ │ Je suis influenceur mode...     │   │
│ └─────────────────────────────────┘   │
│                                         │
│ 📊 Vos statistiques (automatiques):    │
│ • Followers: 50,000                    │
│ • Taux d'engagement: 4.5%              │
│ • Plateformes: Instagram, TikTok       │
│                                         │
│ ℹ️  Le marchand examinera votre profil │
│    avant de valider la demande.        │
│                                         │
│ [Annuler]  [Envoyer la Demande ✅]     │
└─────────────────────────────────────────┘
```

#### Liste des Demandes

```
┌─────────────────────────────────────────────────────────┐
│ 📋 Mes Demandes d'Affiliation                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ⏳ EN ATTENTE                                          │
│ ┌─────────────────────────────────────────────┐       │
│ │ 🛍️  T-shirt Vintage                         │       │
│ │ Marchand: FashionCo                         │       │
│ │ Commission: 15%                             │       │
│ │ Demandé le: 23 Oct 2025                     │       │
│ │ [Annuler]                                   │       │
│ └─────────────────────────────────────────────┘       │
│                                                         │
│ ✅ APPROUVÉES                                          │
│ ┌─────────────────────────────────────────────┐       │
│ │ 👔 Chemise Classic                          │       │
│ │ Lien: localhost:8001/r/XYZ789               │       │
│ │ [Copier] [Voir Stats]                       │       │
│ └─────────────────────────────────────────────┘       │
│                                                         │
│ ❌ REFUSÉES                                            │
│ ┌─────────────────────────────────────────────┐       │
│ │ 👗 Robe d'Été                               │       │
│ │ Motif: "Profil non compatible..."           │       │
│ │ Refusé le: 20 Oct 2025                      │       │
│ └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

### **Dashboard Marchand**

#### Section : "Demandes d'Affiliation"

```
┌────────────────────────────────────────────────────────┐
│ 🤝 Demandes d'Affiliation Reçues                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Filtres: [Toutes] [En attente] [Approuvées] [Refusées]│
│                                                        │
│ ⏳ NOUVELLES DEMANDES (3)                             │
│                                                        │
│ ┌──────────────────────────────────────────────┐     │
│ │ 👤 Emma Style (@emma.style)                  │     │
│ │ 📧 emma.style@instagram.com                  │     │
│ │                                               │     │
│ │ 📊 Statistiques:                             │     │
│ │ • 50K followers Instagram                    │     │
│ │ • 4.5% taux d'engagement                     │     │
│ │ • Niche: Mode & Lifestyle                    │     │
│ │                                               │     │
│ │ 🛍️  Produit demandé:                         │     │
│ │ T-shirt Vintage (Commission: 15%)            │     │
│ │                                               │     │
│ │ 💬 Message:                                  │     │
│ │ "Bonjour, je suis influenceur mode avec..."  │     │
│ │                                               │     │
│ │ 📅 Demandé le: 23 Oct 2025 - 10:30          │     │
│ │                                               │     │
│ │ [❌ Refuser] [✅ Approuver]                  │     │
│ └──────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
```

#### Modal d'Approbation

```
┌─────────────────────────────────────────┐
│ ✅ Approuver la Demande                │
├─────────────────────────────────────────┤
│                                         │
│ Influenceur: Emma Style                │
│ Produit: T-shirt Vintage                │
│                                         │
│ Message de bienvenue (optionnel):      │
│ ┌─────────────────────────────────┐   │
│ │ Bienvenue dans notre programme! │   │
│ │ Voici vos conditions...         │   │
│ └─────────────────────────────────┘   │
│                                         │
│ ✨ Un lien de tracking sera créé       │
│    automatiquement après validation    │
│                                         │
│ [Annuler]  [Confirmer l'Approbation]   │
└─────────────────────────────────────────┘
```

---

## ⚙️ Configuration Backend

### Modèles Pydantic

```python
class AffiliationRequestCreate(BaseModel):
    product_id: str
    message: Optional[str] = None
    stats: Optional[Dict] = None

class AffiliationRequestUpdate(BaseModel):
    status: str
    merchant_response: Optional[str] = None
    reviewed_by: str

class AffiliationRequestResponse(BaseModel):
    id: str
    influencer_id: str
    product_id: str
    merchant_id: str
    status: str
    message: Optional[str]
    merchant_response: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    
    # Relations
    product_name: str
    merchant_company: str
    commission_rate: float
```

---

## 🔔 Notifications

### Notifications Influenceur

1. **Demande envoyée**
   - "✅ Votre demande a été envoyée à [Marchand]"

2. **Demande approuvée**
   - "🎉 Félicitations! Votre demande pour [Produit] a été approuvée"
   - "🔗 Votre lien de tracking est prêt!"

3. **Demande refusée**
   - "❌ Votre demande pour [Produit] a été refusée"
   - Affichage du motif

### Notifications Marchand

1. **Nouvelle demande**
   - "🔔 Nouvelle demande d'affiliation de [Influenceur]"
   - Badge sur l'icône du menu

2. **Demande annulée**
   - "ℹ️ [Influenceur] a annulé sa demande pour [Produit]"

---

## 📈 Statistiques & Rapports

### Dashboard Marchand

```
┌─────────────────────────────────────────┐
│ 📊 Statistiques des Demandes           │
├─────────────────────────────────────────┤
│                                         │
│ ⏳ En attente:        12                │
│ ✅ Approuvées:        45                │
│ ❌ Refusées:          8                 │
│                                         │
│ 📈 Taux d'approbation: 84.9%           │
│ ⏱️  Temps moyen de réponse: 2.5 jours │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🚀 Migration & Déploiement

### Étape 1: Exécuter la migration SQL

```bash
# Dans Supabase SQL Editor
database/migrations/add_affiliation_requests.sql
```

### Étape 2: Mettre à jour le backend

```bash
# Redémarrer le serveur
cd backend
python server.py
```

### Étape 3: Mettre à jour le frontend

```bash
# Hot reload automatique
# Ou rafraîchir F5
```

---

## ✅ Avantages du Nouveau Système

### Pour les Marchands

✅ **Contrôle total** sur qui peut promouvoir leurs produits  
✅ **Vérification du profil** avant collaboration  
✅ **Protection de la marque** - pas de liens automatiques  
✅ **Sélection qualitative** des influenceurs  

### Pour les Influenceurs

✅ **Processus transparent** avec statut en temps réel  
✅ **Communication directe** avec les marchands  
✅ **Professionnalisme** - demande formelle  
✅ **Traçabilité** de toutes les demandes  

### Pour la Plateforme

✅ **Qualité** des partenariats  
✅ **Réduction du spam**  
✅ **Historique complet** des interactions  
✅ **Métriques** de performance  

---

## 🔐 Sécurité & Validation

### Contraintes

- ✅ Un influenceur ne peut faire qu'**une demande par produit**
- ✅ Impossible de redemander un produit **refusé avant 30 jours**
- ✅ Validation des données côté backend
- ✅ Authentification requise pour toutes les actions

### Logs & Audit

- ✅ Historique complet dans `affiliation_request_history`
- ✅ Traçabilité de tous les changements de statut
- ✅ Qui a approuvé/refusé et quand

---

## 📝 TODO Liste

- [ ] Créer les endpoints backend
- [ ] Modifier la page TrackingLinks.js
- [ ] Créer la page MerchantAffiliationRequests.js
- [ ] Ajouter les notifications en temps réel
- [ ] Créer les emails de notification
- [ ] Tests unitaires
- [ ] Documentation API complète

---

**Date de création**: 23 Octobre 2025  
**Version**: 1.0  
**Statut**: Prêt pour implémentation
