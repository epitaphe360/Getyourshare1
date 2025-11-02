# Endpoints Ajoutés au Backend

## Date: 2 Novembre 2024

Tous les endpoints manquants identifiés dans les dashboards ont été ajoutés au fichier `backend/server_complete.py`.

---

## 📊 Merchant Dashboard Endpoints

### GET `/api/analytics/merchant/sales-chart`
- **Description**: Graphique des ventes des 7 derniers jours
- **Response**: `{data: [{date, ventes, revenus}]}`
- **Authentification**: Requise (JWT)

### GET `/api/analytics/merchant/performance`
- **Description**: Métriques de performance du marchand
- **Response**: 
  ```json
  {
    "conversion_rate": 3.8,
    "engagement_rate": 12.5,
    "satisfaction_rate": 92.0,
    "monthly_goal_progress": 68.0
  }
  ```

---

## 💰 Influencer Dashboard Endpoints

### GET `/api/affiliate-links`
- **Description**: Liste des liens d'affiliation de l'influenceur
- **Response**: `{links: [...], total: number}`
- **Mock Data**: 3 liens avec produits, clics, conversions, commissions

### GET `/api/analytics/influencer/earnings-chart`
- **Description**: Graphique des gains des 7 derniers jours
- **Response**: `{data: [{date, gains}]}`

### POST `/api/payouts/request`
- **Description**: Demander un paiement
- **Body**: `{amount, payment_method, currency}`
- **Response**: Confirmation de demande avec ID et statut

---

## 📱 Admin Social Dashboard Endpoints

### GET `/api/admin/social/posts`
- **Description**: Liste des posts sociaux de l'admin
- **Access**: Admin uniquement
- **Response**: Posts avec statut, plateformes, statistiques

### GET `/api/admin/social/templates`
- **Description**: Templates de posts pour l'admin
- **Response**: Liste de 4 templates (lancement, feature, recrutement)

### GET `/api/admin/social/analytics`
- **Description**: Analytics des posts sociaux
- **Response**: Stats globales + breakdown par plateforme

### POST `/api/admin/social/posts`
- **Description**: Créer un nouveau post social
- **Body**: `{title, caption, media_urls, campaign_type, cta_text, cta_url, hashtags}`

### POST `/api/admin/social/posts/{post_id}/publish`
- **Description**: Publier un post sur les réseaux sociaux
- **Body**: `{platforms: [], publish_now, scheduled_for}`

### DELETE `/api/admin/social/posts/{post_id}`
- **Description**: Archiver un post

---

## 💳 Subscription Dashboard Endpoints

### GET `/api/subscriptions/my-subscription`
- **Description**: Abonnement actuel de l'utilisateur
- **Response**: Détails complets (plan, limites, membres, domaines)

### GET `/api/subscriptions/usage`
- **Description**: Usage actuel de l'abonnement
- **Response**: Pourcentages d'utilisation (membres, domaines, API calls)

### POST `/api/subscriptions/cancel`
- **Description**: Annuler l'abonnement
- **Body**: `{immediate: boolean}`

### GET `/api/subscriptions/plans`
- **Description**: Liste des plans d'abonnement disponibles
- **Response**: 4 plans (Free, Starter, Business, Enterprise)

---

## 🔗 Company Links Dashboard Endpoints

### GET `/api/company/links/my-company-links`
- **Description**: Liens générés par l'entreprise
- **Response**: Liste avec produits, membres assignés, stats

### GET `/api/products/my-products`
- **Description**: Produits de l'entreprise connectée
- **Response**: Liste des produits (type="product")

### POST `/api/company/links/generate`
- **Description**: Générer un lien d'affiliation pour un produit
- **Body**: `{product_id, custom_slug?, commission_rate?, notes?}`

### POST `/api/company/links/assign`
- **Description**: Attribuer un lien à un membre d'équipe
- **Body**: `{link_id, member_id, custom_commission_rate?}`

### DELETE `/api/company/links/{link_id}`
- **Description**: Désactiver un lien

---

## 👥 Team Management Endpoints

### GET `/api/team/members`
- **Description**: Liste des membres de l'équipe
- **Query Params**: `status_filter` (optional)
- **Response**: Array de membres avec rôles et statuts

### GET `/api/team/stats`
- **Description**: Statistiques de l'équipe
- **Response**: Totaux, actifs, performances

### POST `/api/team/invite`
- **Description**: Inviter un nouveau membre
- **Body**: `{email, role, first_name?, last_name?}`

---

## ⚙️ Settings Endpoints

### GET `/api/settings`
- **Description**: Paramètres généraux de l'entreprise
- **Response**: Logo, timezone, devise, langue

### PUT `/api/settings/company`
- **Description**: Mise à jour des paramètres entreprise
- **Body**: `{settings: {...}}`

---

## 📈 Statistiques Totales

- **Endpoints Merchant**: 2
- **Endpoints Influencer**: 3
- **Endpoints Admin Social**: 6
- **Endpoints Subscription**: 4
- **Endpoints Company Links**: 5
- **Endpoints Team**: 3
- **Endpoints Settings**: 2

**Total Ajoutés**: **25 nouveaux endpoints**

---

## 🔄 Prochaines Étapes

1. ✅ Tous les dashboards ont maintenant leurs endpoints
2. ⏳ Backend à redémarrer pour appliquer les changements
3. ⏳ Tester chaque dashboard pour vérifier les appels API
4. ⏳ Migration des données mockées vers Supabase

---

## 🛠️ Changements Frontend

### Route Marketplace Corrigée

**Problème**: Deux routes `/marketplace` dans App.js
- Route 1 (ligne 126): `<MarketplaceGroupon />` ✅
- Route 2 (ligne 398): `<Marketplace />` ❌ (ancienne version)

**Solution**: Route 2 renommée en `/marketplace-old`

**Résultat**: `/marketplace` utilise maintenant uniquement la **version Groupon** avec:
- Design inspiré de Groupon.ca
- Onglets: Produits, Services, Commerciaux, Influenceurs
- Cards premium avec badges, stats, gradients
- Authentication guards avant navigation

---

## 📝 Notes Importantes

1. Tous les endpoints utilisent `verify_token` pour l'authentification
2. Les données sont actuellement mockées mais suivent la structure réelle
3. Les endpoints admin vérifient `user_role == "admin"`
4. Les endpoints retournent des structures JSON cohérentes
5. Codes d'erreur HTTP appropriés (403 pour accès refusé, 404 pour non trouvé)

---

## 🚀 Pour Démarrer

```bash
# Backend
cd backend
python server_complete.py

# Frontend (autre terminal)
cd frontend
npm start
```

L'application sera accessible sur:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
