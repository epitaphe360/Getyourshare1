# ⚡ INSTALLATION AUTOMATIQUE - 2 COMMANDES

Guide ultra-rapide pour déployer **GetYourShare** en production.

---

## 🎯 Installation en 3 Étapes (10 minutes)

### ✅ ÉTAPE 1: Créer les Tables Supabase (3 min)

Votre Supabase est déjà configuré! Il faut juste créer les tables:

1. **Ouvrez:** https://app.supabase.com/project/iamezkmapbhlhhvvsits/editor

2. **Cliquez sur:** "New Query"

3. **Copiez le fichier SQL:**
   ```bash
   cat backend/create_subscription_tables.sql
   ```

4. **Collez** le contenu dans l'éditeur Supabase

5. **Cliquez sur:** "Run" (bouton vert)

6. **Vérifiez:** Vous devriez voir "Success. No rows returned"

✅ **Tables créées!**

---

### ✅ ÉTAPE 2: Déployer sur Railway (5 min)

**Une seule commande:**

```bash
./auto_deploy.sh
```

Le script va automatiquement:
- ✅ Installer Railway CLI
- ✅ Vous connecter à Railway
- ✅ Créer le projet
- ✅ Déployer le Backend
- ✅ Déployer le Frontend
- ✅ Configurer toutes les variables
- ✅ Générer les URLs
- ✅ Configurer CORS

**Choisissez l'option 1:** Installation complète automatique

---

### ✅ ÉTAPE 3: Tester (2 min)

Le script affichera vos URLs à la fin:

```
Backend:  https://backend-xxx.up.railway.app
Frontend: https://frontend-xxx.up.railway.app
```

**Testez:**
```bash
# Backend
curl https://votre-backend-url/health

# Frontend (ouvrez dans le navigateur)
https://votre-frontend-url
```

---

## 🎊 C'est Tout!

Votre application est **DÉPLOYÉE ET FONCTIONNELLE** ! 🚀

---

## 📋 Configuration Avancée (Optionnel)

### Stripe (Paiements)

1. Créez un compte: https://dashboard.stripe.com
2. Obtenez vos clés API
3. Dans Railway → Backend → Variables:
   ```
   STRIPE_SECRET_KEY=sk_test_votre_cle
   STRIPE_PUBLISHABLE_KEY=pk_test_votre_cle
   ```
4. Dans Railway → Frontend → Variables:
   ```
   REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_votre_cle
   ```

### Email SMTP (Gmail)

1. Gmail → Sécurité → Validation en 2 étapes (activer)
2. Mots de passe d'application → Mail → Générer
3. Dans Railway → Backend → Variables:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=votre@gmail.com
   SMTP_PASSWORD=mot_de_passe_app_16_caracteres
   ```

### Domaine Personnalisé

1. Railway → Service → Settings → Custom Domain
2. Entrez: `api.votredomaine.com` (backend)
3. Chez votre registrar (GoDaddy, Namecheap, etc.):
   ```
   Type: CNAME
   Name: api
   Value: backend-xxx.up.railway.app
   ```
4. Répétez pour le frontend: `app.votredomaine.com`

---

## 🐛 Dépannage Express

### Le script ne fonctionne pas

```bash
# Donnez les permissions d'exécution
chmod +x auto_deploy.sh

# Relancez
./auto_deploy.sh
```

### Railway CLI ne s'installe pas

**Installation manuelle:**

```bash
# Linux/macOS
curl -fsSL https://railway.app/install.sh | sh

# macOS avec Homebrew
brew install railway
```

### Les tables Supabase ne se créent pas

**Vérifiez:**
- Vous êtes bien sur le bon projet Supabase
- Vous avez cliqué sur "Run" après avoir collé le SQL
- Pas de messages d'erreur en rouge

**Solution:** Réessayez en supprimant d'abord les tables existantes:
```sql
DROP TABLE IF EXISTS subscription_events CASCADE;
DROP TABLE IF EXISTS subscription_usage CASCADE;
DROP TABLE IF EXISTS subscription_coupons CASCADE;
DROP TABLE IF EXISTS payment_transactions CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS payment_methods CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS subscription_plans CASCADE;
```

Puis relancez le script de création.

### Backend/Frontend ne démarre pas

**Attendez 2-3 minutes** (cold start Railway)

**Consultez les logs:**
```bash
cd backend
railway logs

# ou
cd frontend
railway logs
```

### Erreur CORS

Dans Railway → Backend → Variables, vérifiez:
```
ALLOWED_ORIGINS=https://votre-frontend-url
```

---

## 📊 Vos Informations

Toutes vos credentials sont déjà dans `.env.production`:

```env
✅ SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
✅ SUPABASE_KEY=ey... (configuré)
✅ JWT_SECRET_KEY=bFe... (configuré)
```

**Le script utilise automatiquement ces informations!**

---

## 🔧 Commandes Utiles

```bash
# Déployer uniquement le backend
cd backend
railway up

# Déployer uniquement le frontend
cd frontend
railway up

# Voir les logs
railway logs

# Voir les variables
railway variables

# Ouvrir le dashboard Railway
railway open
```

---

## 📚 Documentation Complète

Si vous voulez plus de détails:

- **Guide Complet:** `DEPLOY_RAILWAY.md`
- **Guide Rapide:** `QUICKSTART.md`
- **Système d'Abonnement:** `SUBSCRIPTION_SYSTEM.md`

---

## ✨ Résumé de l'Installation

```
AVANT:
- Supabase configuré ✅
- Code sur GitHub ✅

EXÉCUTER:
1. Créer tables Supabase (SQL Editor)
2. ./auto_deploy.sh
3. Tester les URLs

APRÈS:
- Backend déployé ✅
- Frontend déployé ✅
- Base de données opérationnelle ✅
- HTTPS activé ✅
- Application en production ✅
```

---

## 🎯 URLs Importantes

**Votre Projet:**
- Supabase: https://app.supabase.com/project/iamezkmapbhlhhvvsits
- Railway: https://railway.app/dashboard

**Documentation Externe:**
- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs

---

## 🆘 Besoin d'Aide?

1. **Consultez les logs Railway**
2. **Vérifiez le status:** https://railway.statuspage.io
3. **Discord Railway:** https://discord.gg/railway

---

**🎊 Profitez de votre application en production! 🚀**

*⚡ Generated with [Claude Code](https://claude.com/claude-code)*
