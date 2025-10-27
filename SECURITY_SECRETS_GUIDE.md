# 🔒 Guide de Sécurité et Gestion des Secrets

## 📋 Vue d'ensemble

Ce guide explique comment gérer correctement les variables d'environnement et les secrets dans le projet ShareYourSales.

## 🔑 Types de secrets

### 1. **Secrets Backend** (`.env`)
Fichiers de configuration sensibles côté serveur :

**Localisation** : `backend/.env`

**Secrets critiques** :
- `SUPABASE_SERVICE_KEY` : Clé service Supabase (accès admin DB)
- `JWT_SECRET` : Secret pour signer les tokens JWT
- `DATABASE_URL` : URL connexion PostgreSQL directe
- `STRIPE_SECRET_KEY` : Clé secrète Stripe
- `STRIPE_WEBHOOK_SECRET` : Secret webhook Stripe
- `AWS_SECRET_ACCESS_KEY` : Clé AWS pour S3
- `SMTP_PASSWORD` : Mot de passe email SMTP
- `SESSION_SECRET` : Secret pour sessions utilisateur

**⚠️ NE JAMAIS COMMIT ces fichiers dans Git !**

---

### 2. **Secrets Frontend** (`.env.local`)
Variables d'environnement React :

**Localisation** : `frontend/.env.local`

**Variables publiques** (préfixe `REACT_APP_`) :
- `REACT_APP_API_URL` : URL de l'API backend
- `REACT_APP_SUPABASE_URL` : URL publique Supabase
- `REACT_APP_SUPABASE_ANON_KEY` : Clé anonyme Supabase (sûre côté client)
- `REACT_APP_STRIPE_PUBLISHABLE_KEY` : Clé publique Stripe

**Note** : Les variables React sont intégrées au build et visibles côté client.

---

## 🛠️ Configuration initiale

### Étape 1 : Copier les fichiers d'exemple

#### Backend
```powershell
cd backend
Copy-Item .env.example .env
```

#### Frontend
```powershell
cd frontend
Copy-Item .env.example .env.local
```

### Étape 2 : Remplir les valeurs réelles

Éditer `backend/.env` et `frontend/.env.local` avec vos vraies clés :

```bash
# backend/.env
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=$(openssl rand -hex 32)
```

```bash
# frontend/.env.local
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🚀 Déploiement Production

### GitHub Actions Secrets

Pour le pipeline CI/CD, ajouter ces secrets dans **GitHub Settings** :

**Repository → Settings → Secrets and Variables → Actions → New repository secret**

| Secret Name | Description | Exemple |
|-------------|-------------|---------|
| `SUPABASE_URL` | URL projet Supabase | `https://xxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Clé service Supabase | `eyJhbGci...` |
| `JWT_SECRET` | Secret JWT | `openssl rand -hex 32` |
| `STRIPE_SECRET_KEY` | Clé secrète Stripe | `sk_live_...` |
| `CODECOV_TOKEN` | Token Codecov | (optionnel) |
| `DATABASE_URL` | URL PostgreSQL | `postgresql://...` |

### Utilisation dans workflows

```yaml
# .github/workflows/ci.yml
jobs:
  deploy:
    steps:
      - name: Deploy to production
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
```

---

## 🔐 Bonnes Pratiques

### ✅ À FAIRE

1. **Utiliser `.gitignore`**
   ```gitignore
   # Backend
   backend/.env
   backend/*.env
   
   # Frontend
   frontend/.env.local
   frontend/.env.*.local
   ```

2. **Générer des secrets forts**
   ```powershell
   # PowerShell - Générer secret 32 caractères
   -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
   
   # Ou utiliser OpenSSL (si installé)
   openssl rand -hex 32
   ```

3. **Rotation régulière**
   - Changer JWT_SECRET tous les 3-6 mois
   - Régénérer STRIPE_WEBHOOK_SECRET après chaque incident
   - Révoquer anciens tokens API

4. **Séparer environnements**
   - `.env.development` : Dev local
   - `.env.staging` : Environnement de test
   - `.env.production` : Production

5. **Utiliser un gestionnaire de secrets**
   - **Développement** : Fichiers `.env` locaux
   - **Production** : AWS Secrets Manager, HashiCorp Vault, ou Azure Key Vault

---

### ❌ À NE PAS FAIRE

1. ❌ Commit de fichiers `.env` dans Git
2. ❌ Partager secrets dans Slack/Email
3. ❌ Hardcoder secrets dans le code source
4. ❌ Utiliser clés de test en production
5. ❌ Exposer `SUPABASE_SERVICE_KEY` côté client
6. ❌ Réutiliser mots de passe entre services

---

## 🔍 Vérification de sécurité

### Audit des secrets exposés

```powershell
# Backend - Vérifier si .env est dans Git
cd backend
git ls-files | Select-String -Pattern "\.env$"
# Résultat attendu : Aucun fichier

# Frontend - Vérifier
cd frontend
git ls-files | Select-String -Pattern "\.env"
# Résultat attendu : Aucun fichier
```

### Scanner de vulnérabilités

```powershell
# Backend Python
cd backend
pip install safety
safety check

# Frontend JavaScript
cd frontend
npm audit
npm audit fix
```

### Détection secrets dans historique Git

```powershell
# Installer gitleaks (https://github.com/gitleaks/gitleaks)
gitleaks detect --source . --verbose
```

---

## 📂 Structure recommandée

```
backend/
  .env                  # ❌ Gitignored - Secrets production
  .env.example          # ✅ Commité - Template
  .env.development      # ❌ Gitignored - Dev local
  .env.test             # ❌ Gitignored - Tests
  .gitignore            # ✅ Commité

frontend/
  .env.local            # ❌ Gitignored - Secrets locaux
  .env.example          # ✅ Commité - Template
  .env.development      # ❌ Gitignored
  .env.production       # ❌ Gitignored
  .gitignore            # ✅ Commité
```

---

## 🚨 En cas de fuite de secrets

### 1. **Révoquer immédiatement**

**Supabase** :
- Dashboard → Settings → API → Reset service role key

**Stripe** :
- Dashboard → Developers → API keys → Roll keys

**JWT** :
- Générer nouveau secret → Redéployer → Invalider tous tokens

### 2. **Analyser l'impact**

```powershell
# Rechercher commits contenant le secret
git log -S"leaked_secret" --all
```

### 3. **Nettoyer l'historique Git**

```powershell
# Utiliser BFG Repo-Cleaner
bfg --replace-text passwords.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### 4. **Notification**

- Informer l'équipe
- Audit logs d'accès API
- Documenter incident dans CHANGELOG

---

## 📚 Ressources

### Outils recommandés

| Outil | Usage | URL |
|-------|-------|-----|
| **AWS Secrets Manager** | Gestion secrets production | [aws.amazon.com/secrets-manager](https://aws.amazon.com/secrets-manager/) |
| **HashiCorp Vault** | Gestion secrets open-source | [vaultproject.io](https://www.vaultproject.io/) |
| **dotenv-vault** | Chiffrement .env | [dotenv.org/vault](https://www.dotenv.org/vault) |
| **Gitleaks** | Scanner secrets Git | [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| **Trivy** | Scanner vulnérabilités | [aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy/) |

### Documentation officielle

- [Supabase Security](https://supabase.com/docs/guides/platform/security)
- [Stripe Security](https://stripe.com/docs/security/stripe)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## ✅ Checklist de sécurité

- [ ] Fichiers `.env` ajoutés dans `.gitignore`
- [ ] Fichiers `.env.example` créés et documentés
- [ ] Secrets GitHub Actions configurés
- [ ] JWT_SECRET généré avec 32+ caractères
- [ ] Clés Stripe test/live séparées
- [ ] CORS configuré restrictif en production
- [ ] HTTPS activé en production (`COOKIE_SECURE=true`)
- [ ] Rate limiting activé (`RATE_LIMIT_PER_MINUTE`)
- [ ] Logs sensibles masqués (passwords, tokens)
- [ ] Backup automatiques configurés
- [ ] Scanner sécurité dans CI/CD (Trivy)
- [ ] Audit régulier des dépendances (`npm audit`, `safety check`)

---

**Dernière mise à jour** : 2024-01-XX  
**Auteur** : ShareYourSales Team  
**License** : MIT

---

## 🆘 Support

En cas de problème de sécurité :
- 🔒 Email sécurisé : security@shareyoursales.com
- 📞 Hotline : +33 X XX XX XX XX
- 🐛 Issue privée GitHub : Security Advisory
