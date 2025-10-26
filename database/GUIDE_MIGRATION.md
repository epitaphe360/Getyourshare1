# 📚 Guide de Migration Supabase

## ✅ Étapes Rapides (5 minutes)

### 1. Ouvrir Supabase SQL Editor

1. Allez sur https://app.supabase.com
2. Sélectionnez votre projet
3. Cliquez sur **SQL Editor** dans le menu de gauche
4. Cliquez sur **New Query**

### 2. Copier-Coller le SQL

1. Ouvrez le fichier: `database/migrations/create_new_features_tables.sql`
2. Copiez TOUT le contenu (Ctrl+A, Ctrl+C)
3. Collez dans SQL Editor (Ctrl+V)

### 3. Exécuter

1. Cliquez sur le bouton **RUN** (ou Ctrl+Enter)
2. Attendez 5-10 secondes
3. Vous devriez voir: ✅ Success

### 4. Vérifier

Allez dans **Table Editor** et vous devriez voir ces 8 nouvelles tables:

- ✅ `trust_scores`
- ✅ `payouts`
- ✅ `payment_accounts`
- ✅ `ai_content_history`
- ✅ `smart_matches`
- ✅ `achievements`
- ✅ `user_levels`
- ✅ `notification_subscriptions`

---

## 📊 Ce qui a été créé

### Tables Créées (8)

| Table | Description | Lignes estimées |
|-------|-------------|-----------------|
| `trust_scores` | Score de confiance 0-100 pour chaque utilisateur | 1 par user |
| `payouts` | Historique des paiements mobiles | Illimité |
| `payment_accounts` | Comptes de paiement enregistrés | ~2-3 par user |
| `ai_content_history` | Contenus générés par IA | Illimité |
| `smart_matches` | Cache des résultats de matching | ~100-1000 |
| `achievements` | Badges et achievements | ~10 par user |
| `user_levels` | Niveaux et XP gamification | 1 par user |
| `notification_subscriptions` | Push notifications PWA | ~2 par user |

### Colonnes Ajoutées

**Table `users`:**
- `avg_response_time_hours` → Temps de réponse moyen
- `balance` → Solde disponible pour payouts
- `email_verified` → Email vérifié
- `phone_verified` → Téléphone vérifié
- `kyc_verified` → KYC complété
- `subscription_plan` → Plan d'abonnement (free, starter, pro, enterprise)
- `subscription_status` → Statut (active, cancelled, past_due)

**Table `campaigns`:**
- `clicks` → Nombre de clics
- `conversions` → Nombre de conversions
- `revenue` → Revenus générés
- `content_quality_rating` → Note qualité (1-5)
- `merchant_rating` → Note marchand (1-5)
- `bounce_rate` → Taux de rebond
- `avg_session_duration` → Durée moyenne de session

### Indexes Créés (20+)

Tous les indexes nécessaires pour performance optimale sont créés automatiquement.

### Politiques RLS (Row Level Security)

Toutes les tables ont des politiques de sécurité:
- ✅ Chaque utilisateur ne voit que ses propres données
- ✅ Les Trust Scores sont publics (visible par tous)
- ✅ Les Smart Matches actifs sont publics

### Fonctions Utilitaires

**`calculate_trust_score(user_id)`**
- Calcule automatiquement le Trust Score d'un utilisateur
- Basé sur nombre de campagnes, KYC, etc.

**`add_xp(user_id, xp_amount)`**
- Ajoute de l'XP à un utilisateur
- Gère automatiquement les level ups
- Utilisé pour gamification

**Trigger Automatique:**
- Quand une campagne passe à `completed` → +100 XP automatiquement

---

## 🔥 Données Initiales (Seed)

Le script initialise automatiquement:
- **Trust Score** = 50 pour tous les utilisateurs existants
- **Niveau** = 1 avec 0 XP pour tous
- **Achievements** = Prêts à être débloqués

---

## 🧪 Tester la Migration

### 1. Vérifier les Tables

```sql
-- Voir toutes les nouvelles tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'trust_scores',
  'payouts',
  'payment_accounts',
  'ai_content_history',
  'smart_matches',
  'achievements',
  'user_levels',
  'notification_subscriptions'
);
```

### 2. Vérifier les Données Initiales

```sql
-- Voir les trust scores initialisés
SELECT * FROM trust_scores LIMIT 10;

-- Voir les niveaux initialisés
SELECT * FROM user_levels LIMIT 10;
```

### 3. Tester une Fonction

```sql
-- Calculer le trust score d'un utilisateur
SELECT calculate_trust_score('user_id_here');

-- Ajouter de l'XP
SELECT add_xp('user_id_here', 500);
```

---

## ⚠️ En cas d'erreur

### Erreur: "relation already exists"
→ Normal, c'est que la table existe déjà. Continuez.

### Erreur: "column already exists"
→ Normal, c'est que la colonne existe déjà. Continuez.

### Erreur: "auth.uid() does not exist"
→ Vous utilisez un token Service Role. Les politiques RLS ne s'appliqueront qu'aux requêtes authentifiées.

### Erreur: Foreign key constraint
→ Vérifiez que votre table `users` existe avec une colonne `id`.

---

## 🚀 Après la Migration

### 1. Redémarrer le Backend

```bash
cd backend
uvicorn server:app --reload
```

### 2. Tester les Endpoints

```bash
# Test Trust Score
curl http://localhost:8000/api/trust-score/my-score \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test Mobile Payments
curl http://localhost:8000/api/mobile-payments/providers \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test AI Content
curl http://localhost:8000/api/ai-content/templates?platform=tiktok \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test Dashboard
curl http://localhost:8000/api/dashboard/predictive \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test Smart Match
curl http://localhost:8000/api/smart-match/my-compatibility/brand_123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Vérifier dans Supabase

Allez dans **Table Editor** et regardez les nouvelles données se remplir en temps réel !

---

## 📈 Prochaines Étapes

1. ✅ Migration SQL → **FAIT**
2. ⏳ Intégrer les routers dans `server.py` → **À FAIRE**
3. ⏳ Créer les composants frontend React → **À FAIRE**
4. ⏳ Générer les icônes PWA → **À FAIRE**
5. ⏳ Configurer les clés API (OpenAI, CashPlus, etc.) → **À FAIRE**

---

## 💡 Besoin d'aide ?

Si vous rencontrez un problème:
1. Vérifiez que votre table `users` existe
2. Vérifiez que vous avez les permissions admin
3. Essayez d'exécuter le SQL par petits blocs
4. Consultez les logs Supabase

---

## ✅ Checklist

- [ ] SQL exécuté sans erreurs
- [ ] 8 nouvelles tables visibles dans Table Editor
- [ ] Colonnes ajoutées à `users` et `campaigns`
- [ ] Données initiales créées (trust_scores, user_levels)
- [ ] Politiques RLS activées
- [ ] Fonctions utilitaires créées
- [ ] Tests des endpoints backend

---

**Bonne migration ! 🚀**
