# 🛡️ SYSTÈME DE MODÉRATION IA - GUIDE COMPLET

**Date**: 2 Novembre 2025  
**Version**: 1.0  
**Status**: ✅ Prêt pour déploiement

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Workflow](#workflow)
5. [API Endpoints](#api-endpoints)
6. [Dashboard Admin](#dashboard-admin)
7. [Configuration IA](#configuration-ia)
8. [Tests](#tests)

---

## 🎯 VUE D'ENSEMBLE

### Objectif
Protéger la plateforme contre les produits/services:
- ❌ Contenu sexuel/adulte (+18)
- ❌ Armes et explosifs
- ❌ Drogues et substances illicites
- ❌ Produits contrefaits
- ❌ Services illégaux
- ❌ Contenus violents/haineux
- ❌ Et 10+ autres catégories interdites

### Comment ça marche
1. **Merchant crée produit** → 2. **IA analyse** → 3. **Décision automatique OU queue admin** → 4. **Admin valide** → 5. **Produit publié**

### Technologies
- **IA**: OpenAI GPT-4o-mini (rapide & économique)
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL (Supabase)
- **Frontend**: React + Tailwind CSS

---

## 🏗️ ARCHITECTURE

### Composants

#### 1. **moderation_service.py** (Backend)
```python
# Service IA pour analyser produits
await moderate_product(
    product_name="iPhone 13",
    description="Smartphone neuf",
    category="Électronique",
    price=5000.00
)
# Returns: {approved, confidence, risk_level, flags, reason}
```

**Fonctionnalités**:
- ✅ Analyse IA via OpenAI
- ✅ Détection mots-clés (fallback)
- ✅ 15 catégories interdites
- ✅ Scoring de confiance (0-1)
- ✅ Niveaux de risque (low/medium/high/critical)

#### 2. **CREATE_MODERATION_TABLES.sql** (Database)
```sql
-- Table principale
moderation_queue
├── product_id
├── ai_decision (approved/rejected)
├── ai_confidence (0.00-1.00)
├── ai_risk_level
├── ai_flags (JSONB array)
├── admin_decision
└── status (pending/approved/rejected)

-- Historique
moderation_history
├── action (submitted, approved, rejected)
├── performed_by (admin_user_id)
└── metadata (JSONB)
```

#### 3. **moderation_endpoints.py** (API)
```python
GET  /api/admin/moderation/pending      # Liste produits en attente
GET  /api/admin/moderation/stats        # Statistiques
POST /api/admin/moderation/review       # Approuver/Rejeter
POST /api/admin/moderation/test         # Tester l'IA
GET  /api/admin/moderation/{id}         # Détails
```

#### 4. **Dashboard Admin** (Frontend - à créer)
- Liste des produits en attente
- Filtres par risque
- Détails IA (flags, raison, confidence)
- Boutons Approuver/Rejeter
- Historique merchant

---

## ⚙️ INSTALLATION

### 1. Configurer OpenAI

```bash
# .env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

**Obtenir une clé**:
1. Aller sur https://platform.openai.com/api-keys
2. Créer un nouveau projet "GetYourShare Moderation"
3. Générer clé API
4. Ajouter 5-10$ de crédit (0.01$ par modération environ)

### 2. Créer les tables SQL

```bash
# Dans Supabase SQL Editor
cd backend/database
# Copier/coller CREATE_MODERATION_TABLES.sql
# Exécuter
```

**Vérification**:
```sql
SELECT * FROM moderation_queue LIMIT 1;
SELECT * FROM v_pending_moderation LIMIT 1;
```

### 3. Installer dépendances Python

```bash
cd backend
pip install openai
```

Vérifier:
```bash
python -c "from moderation_service import moderate_product; print('✅ OK')"
```

### 4. Démarrer le serveur

```bash
cd backend
python server_complete.py
```

Vous devriez voir:
```
✅ Moderation endpoints loaded successfully
✅ Moderation endpoints mounted at /api/admin/moderation
```

---

## 🔄 WORKFLOW DÉTAILLÉ

### Scénario 1: Produit Approuvé par IA (80%+ confiance)

```
1. Merchant POST /api/products
   {
     "name": "Ordinateur Dell XPS 13",
     "description": "Laptop neuf sous garantie",
     "price": 12000
   }

2. Backend appelle moderate_product()
   → IA analyse
   → Result: {approved: true, confidence: 0.95, risk_level: "low"}

3. Produit créé directement
   → Visible immédiatement
   → Pas de queue admin

4. Log dans moderation_queue pour audit
   status = 'approved'
```

### Scénario 2: Produit Rejeté par IA (confidence > 0.7)

```
1. Merchant POST /api/products
   {
     "name": "Pilules minceur miracle",
     "description": "Perdez 10kg en 1 semaine garanti",
     "price": 299
   }

2. Backend appelle moderate_product()
   → IA détecte: medical_fraud
   → Result: {
       approved: false,
       confidence: 0.92,
       risk_level: "high",
       flags: ["medical_fraud"],
       reason: "Fausses promesses médicales non autorisées"
     }

3. Produit REJETÉ immédiatement
   → Merchant reçoit erreur 403
   → Message: "Produit rejeté - Fausses promesses médicales"

4. Log dans moderation_queue
   status = 'rejected'
   admin_decision = NULL (pas besoin de review)
```

### Scénario 3: Produit Incertain (confidence < 0.8)

```
1. Merchant POST /api/products
   {
     "name": "Montre Rolex Submariner",
     "description": "Montre de luxe état neuf",
     "price": 2500
   }

2. Backend appelle moderate_product()
   → IA suspicieuse: prix trop bas pour Rolex
   → Result: {
       approved: false,
       confidence: 0.65,
       risk_level: "medium",
       flags: ["counterfeit"],
       reason: "Prix suspect - possible contrefaçon"
     }

3. Produit AJOUTÉ à moderation_queue
   status = 'pending'
   
4. Admin reçoit notification
   → Visite dashboard modération
   → Voit détails + analyse IA
   → Décide: Approuver OU Rejeter

5a. Si Admin approuve:
    → Produit créé et publié
    → Merchant notifié

5b. Si Admin rejette:
    → Merchant notifié avec raison
    → Peut soumettre à nouveau avec corrections
```

---

## 📡 API ENDPOINTS

### Admin - Liste Produits en Attente

```http
GET /api/admin/moderation/pending?limit=50&risk_level=high
Authorization: Bearer {admin_token}
```

**Response**:
```json
{
  "data": [
    {
      "id": "uuid",
      "product_name": "Montre Rolex",
      "product_description": "...",
      "merchant_name": "TechStore",
      "ai_risk_level": "medium",
      "ai_confidence": 0.65,
      "ai_flags": ["counterfeit"],
      "ai_reason": "Prix suspect - possible contrefaçon",
      "hours_pending": 2.5,
      "created_at": "2025-11-02T10:00:00Z"
    }
  ],
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

### Admin - Statistiques

```http
GET /api/admin/moderation/stats?period=today
Authorization: Bearer {admin_token}
```

**Response**:
```json
{
  "period": "today",
  "total": 127,
  "pending": 15,
  "approved": 95,
  "rejected": 17,
  "approval_rate": 0.75,
  "by_risk_level": {
    "low": 80,
    "medium": 30,
    "high": 12,
    "critical": 5
  },
  "avg_ai_confidence": 0.82,
  "needs_review": 15
}
```

### Admin - Approuver Produit

```http
POST /api/admin/moderation/review
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "moderation_id": "uuid-du-produit",
  "decision": "approve",
  "comment": "Vérifié - produit authentique"
}
```

**Response**:
```json
{
  "success": true,
  "decision": "approved",
  "message": "Produit approuvé avec succès"
}
```

### Admin - Rejeter Produit

```http
POST /api/admin/moderation/review
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "moderation_id": "uuid-du-produit",
  "decision": "reject",
  "comment": "Produit contrefait confirmé"
}
```

### Admin - Tester l'IA

```http
POST /api/admin/moderation/test-moderation
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "product_name": "Test Produit",
  "description": "Description à tester"
}
```

**Response**:
```json
{
  "test_result": {
    "approved": true,
    "confidence": 0.95,
    "risk_level": "low",
    "flags": [],
    "reason": "",
    "moderation_method": "ai"
  },
  "message": "Test de modération effectué avec succès"
}
```

### Merchant - Mes Produits en Attente

```http
GET /api/admin/moderation/my-pending
Authorization: Bearer {merchant_token}
```

**Response**:
```json
{
  "pending_products": [
    {
      "id": "uuid",
      "product_name": "Mon Produit",
      "status": "pending",
      "ai_risk_level": "medium",
      "ai_reason": "En cours de révision par l'équipe",
      "created_at": "2025-11-02T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

## 🎨 DASHBOARD ADMIN (À DÉVELOPPER)

### Composant React Recommandé

```jsx
// frontend/src/pages/admin/ModerationDashboard.js
import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const ModerationDashboard = () => {
  const [pending, setPending] = useState([]);
  const [stats, setStats] = useState({});
  const [filter, setFilter] = useState('all'); // all, high, medium, low
  
  useEffect(() => {
    fetchPending();
    fetchStats();
  }, [filter]);
  
  const fetchPending = async () => {
    const params = filter !== 'all' ? `?risk_level=${filter}` : '';
    const res = await api.get(`/api/admin/moderation/pending${params}`);
    setPending(res.data.data);
  };
  
  const fetchStats = async () => {
    const res = await api.get('/api/admin/moderation/stats?period=today');
    setStats(res.data);
  };
  
  const handleReview = async (moderationId, decision, comment) => {
    try {
      await api.post('/api/admin/moderation/review', {
        moderation_id: moderationId,
        decision,
        comment
      });
      alert(`Produit ${decision === 'approve' ? 'approuvé' : 'rejeté'}`);
      fetchPending();
      fetchStats();
    } catch (err) {
      alert('Erreur: ' + err.response?.data?.detail);
    }
  };
  
  return (
    <div className="p-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard title="En attente" value={stats.pending} color="yellow" />
        <StatCard title="Approuvés" value={stats.approved} color="green" />
        <StatCard title="Rejetés" value={stats.rejected} color="red" />
        <StatCard title="Taux approbation" value={`${(stats.approval_rate*100).toFixed(0)}%`} />
      </div>
      
      {/* Filters */}
      <div className="mb-4">
        <button onClick={() => setFilter('all')}>Tous</button>
        <button onClick={() => setFilter('critical')}>🔴 Critical</button>
        <button onClick={() => setFilter('high')}>🟠 High</button>
        <button onClick={() => setFilter('medium')}>🟡 Medium</button>
        <button onClick={() => setFilter('low')}>🟢 Low</button>
      </div>
      
      {/* Pending List */}
      {pending.map(item => (
        <ModerationCard 
          key={item.id}
          item={item}
          onApprove={(comment) => handleReview(item.id, 'approve', comment)}
          onReject={(comment) => handleReview(item.id, 'reject', comment)}
        />
      ))}
    </div>
  );
};
```

### Features du Dashboard
- ✅ Stats en temps réel
- ✅ Filtres par niveau de risque
- ✅ Détails complets produit
- ✅ Analyse IA visible
- ✅ Boutons Approuver/Rejeter
- ✅ Champ commentaire admin
- ✅ Historique merchant
- ✅ Badge de priorité
- ✅ Temps d'attente
- ✅ Images produit preview

---

## 🤖 CONFIGURATION IA

### Modèles OpenAI Disponibles

| Modèle | Vitesse | Coût | Qualité | Recommandé |
|--------|---------|------|---------|------------|
| **gpt-4o-mini** | ⚡ Très rapide | 💰 0.01$ | 🌟🌟🌟🌟 | ✅ OUI |
| gpt-4o | 🐢 Lent | 💰💰💰 0.05$ | 🌟🌟🌟🌟🌟 | Pour cas complexes |
| gpt-3.5-turbo | ⚡⚡ Ultra rapide | 💰 0.001$ | 🌟🌟🌟 | Fallback |

**Recommandation**: Utiliser **gpt-4o-mini** (déjà configuré)
- Balance parfaite qualité/prix/vitesse
- 0.01$ par modération
- Temps de réponse < 2 secondes

### Optimiser les Coûts

**Budget moyen**:
- 100 produits/jour = 1$ /jour = 30$/mois
- 500 produits/jour = 5$/jour = 150$/mois
- 1000 produits/jour = 10$/jour = 300$/mois

**Stratégies d'économie**:

1. **Filtrage pré-IA par mots-clés**:
```python
# Si mots interdits évidents, rejeter sans IA
if quick_check_prohibited_keywords(product_name + description):
    return {"approved": False, "reason": "Contenu interdit détecté"}
# Sinon, appeler IA
```

2. **Cache des résultats similaires**:
```python
# Si produit similaire déjà analysé, réutiliser résultat
hash_key = hashlib.md5(f"{product_name}{description}".encode()).hexdigest()
if hash_key in redis_cache:
    return redis_cache[hash_key]
```

3. **Auto-approval pour merchants fiables**:
```python
# Si merchant a 95%+ approval rate et 50+ produits
if merchant.approval_rate > 0.95 and merchant.total_products > 50:
    # Approuver directement sans IA
    return {"approved": True, "confidence": 0.99}
```

---

## 🧪 TESTS

### Test 1: Produit Normal (doit être approuvé)

```bash
curl -X POST http://localhost:8000/api/admin/moderation/test-moderation \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "MacBook Pro M3",
    "description": "Ordinateur portable Apple neuf, garantie 1 an"
  }'
```

**Résultat attendu**:
```json
{
  "test_result": {
    "approved": true,
    "confidence": 0.95,
    "risk_level": "low",
    "flags": [],
    "reason": ""
  }
}
```

### Test 2: Contenu Adulte (doit être rejeté)

```bash
curl -X POST http://localhost:8000/api/admin/moderation/test-moderation \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Contenu XXX",
    "description": "Vidéos adultes premium"
  }'
```

**Résultat attendu**:
```json
{
  "test_result": {
    "approved": false,
    "confidence": 0.98,
    "risk_level": "critical",
    "flags": ["adult_content"],
    "reason": "Contenu sexuel/adulte (+18) détecté"
  }
}
```

### Test 3: Produit Suspect (doit aller en queue)

```bash
curl -X POST http://localhost:8000/api/admin/moderation/test-moderation \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 14 Pro Max",
    "description": "Neuf, prix cassé seulement 500 MAD"
  }'
```

**Résultat attendu**:
```json
{
  "test_result": {
    "approved": false,
    "confidence": 0.72,
    "risk_level": "high",
    "flags": ["counterfeit"],
    "reason": "Prix anormalement bas pour un iPhone neuf - risque de contrefaçon"
  }
}
```

---

## 📊 MONITORING & ANALYTICS

### Métriques Importantes

1. **Taux d'approbation IA**: Devrait être 70-85%
2. **Faux positifs**: IA rejette produit légitime (< 5%)
3. **Faux négatifs**: IA approuve produit interdit (< 1%)
4. **Temps de review admin**: < 24h idéalement
5. **Backlog queue**: < 50 produits en attente

### Dashboard Analytics

```sql
-- Requête pour dashboard analytics
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE ai_decision = 'approved') as ai_approved,
    COUNT(*) FILTER (WHERE ai_decision = 'rejected') as ai_rejected,
    AVG(ai_confidence) as avg_confidence
FROM moderation_queue
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 🚀 DÉPLOIEMENT PRODUCTION

### Checklist

- [ ] Clé OpenAI configurée et créditée (10$+)
- [ ] Tables SQL créées dans Supabase
- [ ] Endpoints montés dans server_complete.py
- [ ] Dashboard admin développé et testé
- [ ] Tests passés (3 scénarios)
- [ ] Monitoring configuré
- [ ] Documentation admin rédigée
- [ ] Webhook notifications configuré (optionnel)
- [ ] Rate limiting sur endpoints IA
- [ ] Logs structurés activés

### Variables d'environnement

```bash
# .env.production
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxxxxxxxxxxxx
MODERATION_CONFIDENCE_THRESHOLD=0.8  # Seuil pour queue admin
MODERATION_AUTO_APPROVE_THRESHOLD=0.95  # Seuil pour auto-approve
```

---

## 🆘 SUPPORT & TROUBLESHOOTING

### Problème: "OpenAI API key not configured"

**Solution**: Ajouter `OPENAI_API_KEY` dans .env

### Problème: "IA retourne toujours approved=True"

**Solution**: Vérifier le prompt, augmenter la température à 0.2

### Problème: "Trop de faux positifs"

**Solution**: Baisser confidence_threshold de 0.8 à 0.7

### Problème: "Trop lent (> 5 secondes)"

**Solution**: 
1. Vérifier connexion OpenAI
2. Réduire max_tokens de 500 à 300
3. Utiliser gpt-3.5-turbo au lieu de gpt-4o-mini

---

## 📚 RESSOURCES

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Supabase Functions](https://supabase.com/docs/guides/database/functions)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

---

**Développeur**: GitHub Copilot  
**Client**: GetYourShare  
**Version**: 1.0  
**License**: Propriétaire
