# 🤝 Système de Collaboration Complet - Guide Technique

## 📋 Vue d'Ensemble

Le système de collaboration permet aux marchands d'inviter des influenceurs à promouvoir leurs produits, avec un processus complet incluant :
- Demandes de collaboration
- Acceptation / Refus / Contre-offres
- Signature de contrat électronique
- Génération automatique de liens d'affiliation
- Suivi des collaborations actives

---

## 🗂️ Architecture du Système

### 1. Base de Données (Supabase)

#### Tables Créées

**collaboration_requests**
```sql
CREATE TABLE collaboration_requests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  merchant_id UUID REFERENCES users(id),
  influencer_id UUID REFERENCES users(id),
  status TEXT CHECK (status IN ('pending', 'accepted', 'rejected', 'counter_offer', 'expired', 'active')),
  proposed_commission DECIMAL(5,2),
  counter_commission DECIMAL(5,2),
  message TEXT,
  contract_text TEXT,
  contract_accepted_at TIMESTAMP,
  merchant_signature TEXT,
  influencer_signature TEXT,
  affiliate_link_id UUID REFERENCES affiliate_links(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days')
);
```

**collaboration_products** (Many-to-Many)
```sql
CREATE TABLE collaboration_products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  request_id UUID REFERENCES collaboration_requests(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  created_at TIMESTAMP DEFAULT NOW()
);
```

**collaboration_messages**
```sql
CREATE TABLE collaboration_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  request_id UUID REFERENCES collaboration_requests(id) ON DELETE CASCADE,
  sender_id UUID REFERENCES users(id),
  message TEXT,
  is_counter_offer BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### Fonctions SQL

**1. get_user_received_requests(p_user_id UUID)**
- Retourne toutes les demandes reçues par un influenceur
- Inclut les infos du marchand et la liste des produits

**2. get_user_sent_requests(p_user_id UUID)**
- Retourne toutes les demandes envoyées par un marchand
- Inclut les infos de l'influenceur et statut

**3. respond_to_request(p_request_id, p_response, p_counter_commission, p_message)**
- Gère les réponses (accept/reject/counter_offer)
- Met à jour le statut et crée les messages

**4. accept_contract(p_request_id, p_user_id, p_user_role, p_signature)**
- Enregistre la signature électronique
- Finalise le contrat

**5. generate_affiliate_link_from_collaboration(p_request_id)**
- Crée automatiquement les liens d'affiliation
- Appelé après signature du contrat

---

## 🔌 API Endpoints (Backend)

### Base URL: `/api/collaborations`

#### 1. **POST /requests**
Créer une nouvelle demande de collaboration

**Body:**
```json
{
  "influencer_id": "uuid",
  "product_ids": ["uuid1", "uuid2"],
  "commission": 15.5,
  "message": "Message personnalisé"
}
```

**Response:**
```json
{
  "success": true,
  "request_id": "uuid",
  "message": "Demande envoyée"
}
```

---

#### 2. **GET /requests/received**
Demandes reçues (pour influenceurs)

**Response:**
```json
{
  "success": true,
  "requests": [
    {
      "id": "uuid",
      "merchant_id": "uuid",
      "merchant_name": "Boutique X",
      "status": "pending",
      "proposed_commission": 15,
      "message": "...",
      "products": [
        {
          "id": "uuid",
          "name": "Produit A",
          "price": 299.99,
          "image_url": "..."
        }
      ],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### 3. **GET /requests/sent**
Demandes envoyées (pour marchands)

**Response:** (même structure que received)

---

#### 4. **PUT /requests/{request_id}/accept**
Accepter une demande (influenceur)

**Response:**
```json
{
  "success": true,
  "message": "Demande acceptée, veuillez signer le contrat"
}
```

---

#### 5. **PUT /requests/{request_id}/reject**
Refuser une demande

**Body:**
```json
{
  "message": "Raison du refus"
}
```

---

#### 6. **PUT /requests/{request_id}/counter-offer**
Faire une contre-proposition

**Body:**
```json
{
  "counter_commission": 20,
  "message": "Justification"
}
```

---

#### 7. **POST /requests/{request_id}/sign-contract**
Signer le contrat électroniquement

**Body:**
```json
{
  "signature": "hash_signature"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Contrat signé ! Votre lien d'affiliation a été généré.",
  "affiliate_link_id": "uuid"
}
```

---

#### 8. **GET /requests/{request_id}**
Détails d'une demande spécifique

---

#### 9. **GET /contract-terms**
Termes du contrat standard

**Response:**
```json
{
  "success": true,
  "contract": {
    "version": "v1.0",
    "terms": [
      {
        "title": "1. Respect Éthique",
        "content": "..."
      },
      ...
    ]
  }
}
```

---

## 🎨 Composants Frontend

### 1. **CollaborationRequestModal.js**
Modal pour le marchand pour créer une demande

**Props:**
- `isOpen`: Boolean
- `onClose`: Function
- `products`: Array<Product>
- `influencerId`: String
- `influencerName`: String

**Fonctionnalités:**
- Multi-sélection de produits
- Slider de commission (5-50%)
- Message optionnel
- Validation avant envoi

---

### 2. **CollaborationResponseModal.js**
Modal pour l'influenceur pour répondre

**Props:**
- `isOpen`: Boolean
- `onClose`: Function
- `request`: Object (la demande)
- `onRespond`: Function (callback)

**Actions possibles:**
- ✅ **Accepter** → Ouvre ContractModal
- ❌ **Refuser** → Demande une raison
- 🔄 **Contre-offre** → Propose nouvelle commission

---

### 3. **ContractModal.js**
Modal de signature de contrat

**Props:**
- `isOpen`: Boolean
- `onClose`: Function
- `requestId`: String
- `userRole`: 'merchant' | 'influencer'
- `onSigned`: Function

**Fonctionnalités:**
- Affichage des termes du contrat
- Code de conduite éthique
- Checkbox d'acceptation
- Signature électronique (nom complet)
- Validation et envoi

---

## 🔄 Workflow Complet

### Étape 1 : Création de la demande (Marchand)
1. Marchand va sur le profil d'un influenceur
2. Clique sur "Collaborer Maintenant"
3. Sélectionne les produits
4. Définit la commission
5. Ajoute un message (optionnel)
6. Envoie la demande
7. **Status:** `pending`

---

### Étape 2 : Réception (Influenceur)
1. Influenceur voit la demande dans son dashboard
2. Section "Demandes de Collaboration"
3. Badge indiquant le nombre de demandes en attente

---

### Étape 3a : Acceptation
1. Influenceur clique sur "Répondre"
2. Voit les détails (produits, commission, message)
3. Clique sur "Accepter la collaboration"
4. **Modal de contrat s'ouvre**
5. Lit les termes et conditions
6. Coche "J'accepte les termes"
7. Signe électroniquement (tape son nom)
8. Clique sur "Signer le contrat"
9. **Backend:**
   - Enregistre la signature
   - Change status → `active`
   - Génère automatiquement les liens d'affiliation
   - Retourne le lien généré
10. **Status:** `active`

---

### Étape 3b : Refus
1. Influenceur clique sur "Refuser"
2. Écrit une raison (obligatoire)
3. Confirme le refus
4. **Status:** `rejected`
5. Marchand est notifié

---

### Étape 3c : Contre-offre
1. Influenceur clique sur "Faire une contre-proposition"
2. Ajuste la commission (slider)
3. Justifie sa proposition
4. Envoie la contre-offre
5. **Status:** `counter_offer`
6. **Marchand peut:**
   - Accepter la nouvelle commission → Retour à Étape 3a
   - Refuser → Status `rejected`
   - Négocier à nouveau

---

## 📊 Statuts Possibles

| Status | Description | Qui peut agir |
|--------|-------------|---------------|
| `pending` | Demande envoyée, en attente | Influenceur |
| `accepted` | Accepté, en attente de signature | Influenceur (signer) |
| `rejected` | Refusé par l'influenceur | Personne (fin) |
| `counter_offer` | Contre-offre faite | Marchand |
| `expired` | Expirée après 7 jours | Personne (fin) |
| `active` | Contrat signé, collaboration active | Les deux (analytics) |

---

## 🔒 Sécurité

### Authentification
- Tous les endpoints nécessitent un token JWT
- Vérification du rôle utilisateur (merchant/influencer)
- Validation des IDs (pas d'accès aux demandes d'autres users)

### Validation
- Commission entre 5% et 50%
- Produits doivent appartenir au marchand
- Influenceur ne peut répondre qu'à ses propres demandes
- Signature électronique hashée avec timestamp

### Intégrité des données
- Foreign keys avec CASCADE
- Contraintes CHECK sur status
- Triggers pour auto-expiration (7 jours)

---

## 📈 Dashboards

### Dashboard Influenceur
**Section:** "Demandes de Collaboration"

**Affichage:**
- Carte avec badge du nombre de demandes
- Liste des demandes avec:
  - Nom du marchand
  - Nombre de produits
  - Commission proposée
  - Status (badge coloré)
  - Bouton "Répondre" (si pending)

**Actions:**
- Cliquer sur "Répondre" → Ouvre CollaborationResponseModal
- Voir les détails de la demande
- Accepter/Refuser/Contre-offre

---

### Dashboard Marchand
**Section:** "Demandes Envoyées" (À implémenter)

**Affichage:**
- Liste des demandes envoyées
- Nom de l'influenceur
- Produits inclus
- Status
- Date d'envoi

**Actions:**
- Voir les réponses
- Accepter/Refuser les contre-offres

---

## 🎯 Prochaines Étapes (Améliorations)

### Court Terme
- [ ] Dashboard marchand - Section demandes envoyées
- [ ] Notifications en temps réel (WebSocket)
- [ ] Historique des messages de négociation
- [ ] Export PDF du contrat signé

### Moyen Terme
- [ ] Système de notation après collaboration
- [ ] Templates de contrats personnalisables
- [ ] Renouvellement automatique des contrats
- [ ] Analytics de performance par collaboration

### Long Terme
- [ ] Messagerie intégrée marchand-influenceur
- [ ] Système de dispute/médiation
- [ ] Programme de fidélité (bonus pour collaborations répétées)
- [ ] IA pour recommander les meilleurs influenceurs

---

## 🐛 Tests Manuels

### Test 1 : Création de demande
1. Login en tant que marchand
2. Aller sur marketplace → Profil influenceur
3. Cliquer "Collaborer Maintenant"
4. Sélectionner 2 produits
5. Mettre 20% commission
6. Ajouter un message
7. Envoyer
8. ✅ Vérifier: Demande apparaît dans dashboard marchand (quand implémenté)

### Test 2 : Acceptation + Signature
1. Login en tant qu'influenceur
2. Dashboard → Section "Demandes de Collaboration"
3. Cliquer "Répondre" sur une demande pending
4. Cliquer "Accepter la collaboration"
5. Lire le contrat
6. Cocher "J'accepte"
7. Taper nom complet dans signature
8. Cliquer "Signer le contrat"
9. ✅ Vérifier: 
   - Message de succès
   - Lien d'affiliation généré
   - Status passe à "active"
   - Badge de demande disparaît

### Test 3 : Contre-offre
1. Influenceur répond à une demande
2. Cliquer "Faire une contre-proposition"
3. Ajuster commission à 25%
4. Écrire justification
5. Envoyer
6. ✅ Vérifier:
   - Status passe à "counter_offer"
   - Marchand reçoit notification (quand implémenté)

### Test 4 : Refus
1. Influenceur répond à une demande
2. Cliquer "Refuser la demande"
3. Écrire une raison
4. Confirmer
5. ✅ Vérifier:
   - Status passe à "rejected"
   - Demande reste visible avec badge rouge

---

## 📝 Code Snippets Utiles

### Récupérer les demandes reçues (Frontend)
```javascript
const fetchCollaborationRequests = async () => {
  try {
    const response = await api.get('/api/collaborations/requests/received');
    setCollaborationRequests(response.data.requests || []);
  } catch (error) {
    console.error('Error fetching collaboration requests:', error);
  }
};
```

### Accepter et signer (Frontend)
```javascript
const handleAccept = async (requestId, signature) => {
  try {
    const response = await api.post(
      `/api/collaborations/requests/${requestId}/sign-contract`,
      { signature }
    );
    
    if (response.data.success) {
      toast.success('Collaboration activée ! Lien d\'affiliation généré.');
      // Rafraîchir les données
      fetchCollaborationRequests();
    }
  } catch (error) {
    toast.error('Erreur lors de la signature');
  }
};
```

---

## 🔗 Fichiers Modifiés/Créés

### Backend
- ✅ `backend/migrations/003_affiliate_links.sql`
- ✅ `backend/migrations/005_collaboration_system.sql`
- ✅ `backend/server_complete.py` (ajout des 9 endpoints)

### Frontend
- ✅ `frontend/src/components/modals/CollaborationRequestModal.js` (NOUVEAU)
- ✅ `frontend/src/components/modals/CollaborationResponseModal.js` (NOUVEAU)
- ✅ `frontend/src/components/modals/ContractModal.js` (NOUVEAU)
- ✅ `frontend/src/pages/dashboards/InfluencerDashboard.js` (modifié)
- ⏳ `frontend/src/pages/dashboards/MerchantDashboard.js` (à modifier)
- ⏳ `frontend/src/pages/MarketplaceGroupon.js` (à intégrer le bouton)

---

## ✅ Checklist d'Implémentation

### Base de Données
- [x] Migration 003_affiliate_links.sql
- [x] Migration 005_collaboration_system.sql
- [x] Fonctions SQL (get_received, get_sent, respond, accept_contract, generate_link)
- [x] Triggers (auto_expire, create_affiliate_link)

### Backend
- [x] POST /requests (créer demande)
- [x] GET /requests/received (influenceur)
- [x] GET /requests/sent (marchand)
- [x] PUT /requests/{id}/accept
- [x] PUT /requests/{id}/reject
- [x] PUT /requests/{id}/counter-offer
- [x] POST /requests/{id}/sign-contract
- [x] GET /requests/{id} (détails)
- [x] GET /contract-terms

### Frontend - Modals
- [x] CollaborationRequestModal (marchand crée demande)
- [x] CollaborationResponseModal (influenceur répond)
- [x] ContractModal (signature électronique)

### Frontend - Dashboards
- [x] InfluencerDashboard : Section demandes reçues
- [ ] MerchantDashboard : Section demandes envoyées
- [ ] Intégration bouton "Collaborer" dans MarketplaceGroupon

### Tests
- [ ] Test création demande
- [ ] Test acceptation + signature
- [ ] Test refus avec raison
- [ ] Test contre-offre
- [ ] Test expiration automatique (7 jours)
- [ ] Test génération lien affiliation

---

## 🎉 Résumé

**Ce système offre:**
✅ Workflow complet de collaboration marchand-influenceur
✅ Négociation avec contre-offres
✅ Contrat électronique légal avec signature
✅ Génération automatique de liens d'affiliation
✅ Code de conduite éthique intégré
✅ Suivi des statuts en temps réel
✅ Expiration automatique des demandes obsolètes
✅ Interface utilisateur intuitive et moderne

**Stack technique:**
- Backend: FastAPI + Supabase (PostgreSQL)
- Frontend: React + Tailwind CSS + Lucide Icons
- Authentification: JWT
- État: React Hooks + Context API

---

**Version:** 1.0  
**Dernière mise à jour:** 2024  
**Statut:** 90% complet (reste dashboard marchand)
