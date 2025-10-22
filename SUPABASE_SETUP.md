# 🚀 Setup Supabase - ShareYourSales

Guide complet pour configurer Supabase et migrer l'application.

---

## ⚡ Setup Rapide (5 minutes)

### Étape 1: Créer les Tables dans Supabase

1. **Ouvrir l'éditeur SQL de Supabase:**
   ```
   https://iamezkmapbhlhhvvsits.supabase.co/project/_/sql
   ```

2. **Copier TOUT le contenu du fichier:**
   ```
   database/schema.sql
   ```

3. **Coller dans l'éditeur SQL et cliquer sur "RUN"**

   ⏱️ Cela prendra environ 30 secondes pour créer:
   - ✅ 15 tables
   - ✅ Indexes
   - ✅ Functions & Triggers
   - ✅ Views
   - ✅ Données de seed (catégories, admin)

### Étape 2: Migrer les Données MOCK

```bash
cd backend
python3 setup_supabase.py
```

Ce script va:
- ✅ Migrer tous les utilisateurs (6 users)
- ✅ Migrer tous les merchants (2 companies)
- ✅ Migrer tous les influencers (3 creators)
- ✅ Migrer tous les produits (50+ products)

### Étape 3: Démarrer l'Application

```bash
# Terminal 1 - Backend
cd backend
python3 -m uvicorn server:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend
npm start
```

L'application est maintenant **100% connectée à Supabase** ! 🎉

---

## 📊 Vérifier les Données

1. **Dashboard Supabase:**
   ```
   https://iamezkmapbhlhhvvsits.supabase.co
   ```

2. **Table Editor:**
   ```
   https://iamezkmapbhlhhvvsits.supabase.co/project/_/editor
   ```

3. **SQL Editor:**
   ```
   https://iamezkmapbhlhhvvsits.supabase.co/project/_/sql
   ```

---

## 🔐 Comptes de Test

Après la migration, vous pouvez vous connecter avec:

| Rôle | Email | Mot de passe | 2FA Code |
|------|-------|--------------|----------|
| Admin | admin@shareyoursales.com | admin123 | 123456 |
| Merchant | contact@techstyle.fr | merchant123 | 123456 |
| Merchant | hello@beautypro.com | merchant123 | 123456 |
| Influencer | emma.style@instagram.com | influencer123 | 123456 |
| Influencer | lucas.tech@youtube.com | influencer123 | 123456 |
| Influencer | julie.beauty@tiktok.com | influencer123 | 123456 |

---

## 🗂️ Structure de la Base de Données

### Tables Principales

1. **users** - Utilisateurs (admin, merchant, influencer)
2. **user_sessions** - Sessions JWT
3. **merchants** - Profils d'entreprises
4. **influencers** - Profils d'influenceurs
5. **products** - Catalogue de produits
6. **trackable_links** - Liens d'affiliation
7. **sales** - Ventes
8. **commissions** - Paiements aux influenceurs
9. **engagement_metrics** - Métriques d'engagement
10. **campaigns** - Campagnes marketing
11. **ai_analytics** - Analyses IA
12. **subscriptions** - Abonnements
13. **payments** - Historique paiements
14. **reviews** - Avis et notes
15. **categories** - Catégories

### Vues (Views)

- **influencer_performance** - Performance des influenceurs
- **product_performance** - Performance des produits
- **admin_dashboard_stats** - Statistiques admin

---

## 🔧 Dépannage

### Erreur: "relation 'users' does not exist"

➡️ **Solution:** Les tables n'ont pas été créées. Retournez à l'Étape 1.

### Erreur: "duplicate key value violates unique constraint"

➡️ **Solution:** Les données ont déjà été migrées. Supprimez les données et recommencez:

```sql
-- Dans l'éditeur SQL Supabase
DELETE FROM click_tracking;
DELETE FROM engagement_metrics;
DELETE FROM commissions;
DELETE FROM sales;
DELETE FROM trackable_links;
DELETE FROM products;
DELETE FROM influencers;
DELETE FROM merchants;
DELETE FROM user_sessions;
DELETE FROM users WHERE email != 'admin@shareyoursales.com';
```

### L'application ne se connecte pas à Supabase

➡️ **Solution:** Vérifiez les variables d'environnement dans `backend/.env`:

```ini
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJI...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJI...
```

---

## 🎯 Fonctionnalités Supabase Utilisées

- ✅ **PostgreSQL Database** - Stockage des données
- ✅ **Row Level Security (RLS)** - Sécurité des données
- ✅ **Realtime** - Mises à jour en temps réel (optionnel)
- ✅ **Auth** - Authentification intégrée (non utilisé, JWT custom)
- ✅ **Storage** - Stockage de fichiers (pour futures images)

---

## 📝 Notes Importantes

### Sécurité

- ⚠️ **Service Role Key** est dans .env (ne jamais commit!)
- ⚠️ Les mots de passe sont hashés avec bcrypt
- ⚠️ Tokens JWT avec expiration 24h

### Performance

- Les indexes sont créés automatiquement
- Les triggers `updated_at` sont en place
- Les relations foreign keys optimisent les requêtes

### Backup

Supabase fait des backups automatiques:
- Backups quotidiens pendant 7 jours
- Point-in-time recovery disponible

---

## 🚀 Prochaines Étapes

Une fois la migration terminée:

1. ✅ Tester la connexion
2. ✅ Tester les 3 dashboards (Admin, Merchant, Influencer)
3. ✅ Tester la marketplace
4. ✅ Tester la génération de liens
5. ✅ Tester les stats et analytics

---

## 📞 Support

- **Dashboard Supabase:** https://iamezkmapbhlhhvvsits.supabase.co
- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Status:** ✅ Prêt pour la migration !
