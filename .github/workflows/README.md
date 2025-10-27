# 🚀 Pipeline CI/CD - ShareYourSales

[![CI/CD Pipeline](https://github.com/[USERNAME]/[REPO]/actions/workflows/ci.yml/badge.svg)](https://github.com/[USERNAME]/[REPO]/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/[USERNAME]/[REPO]/branch/main/graph/badge.svg)](https://codecov.io/gh/[USERNAME]/[REPO])

## 📋 Vue d'ensemble

Ce pipeline automatise l'intégration et la livraison continues pour le projet ShareYourSales. Il s'exécute automatiquement sur chaque **push** et **pull request** vers les branches `main` et `develop`.

## 🔄 Jobs du Pipeline

### 1. **Lint Backend** 🐍
**Objectif** : Vérifier la qualité du code Python selon les standards du projet

**Outils utilisés** :
- **Ruff** : Linter Python moderne et rapide (~40 règles activées)
- **Black** : Formatter Python (line-length=100)
- **isort** : Tri automatique des imports
- **mypy** : Vérification des types statiques

**Configuration** : `backend/.ruff.toml`, `backend/pyproject.toml`

**Commandes** :
```bash
cd backend
pip install -r requirements-dev.txt
ruff check .
black --check .
isort --check-only .
mypy . --ignore-missing-imports
```

**Note** : Les warnings de lint ne bloquent pas le pipeline (`continue-on-error: true`)

---

### 2. **Test Backend** ✅
**Objectif** : Exécuter les tests unitaires avec coverage minimum 80%

**Framework** : Pytest 7.4.3 avec pytest-cov

**Tests inclus** :
- `tests/test_sales.py` : 25+ tests module Sales
- `tests/test_payments.py` : 30+ tests module Payments
- Fixtures : 25+ fixtures dans `conftest.py`

**Configuration** : `backend/pytest.ini`

**Commandes** :
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest --cov=services --cov-report=xml --cov-report=term-missing
```

**Artifacts** :
- Coverage XML uploadé sur **Codecov**
- Rapport terminal avec lignes non couvertes

**Critère de succès** : Tous les tests passent (failure bloquant)

---

### 3. **Lint Frontend** 💅
**Objectif** : Vérifier la qualité du code JavaScript/React

**Outils utilisés** :
- **ESLint** : Linter JavaScript (react-hooks, best practices)
- **Prettier** : Formatter de code (singleQuote, tabWidth=2)

**Configuration** : `frontend/.eslintrc.json`, `frontend/.prettierrc`

**Commandes** :
```bash
cd frontend
npm ci
npm run lint
npm run format:check
```

**Note** : Les warnings de lint ne bloquent pas le pipeline

---

### 4. **Build Frontend** 🏗️
**Objectif** : Compiler l'application React pour production

**Build tool** : Create React App (react-scripts 5.0.1)

**Commandes** :
```bash
cd frontend
npm ci
npm run build
```

**Artifacts** :
- Build production uploadé dans **frontend-build**
- Rétention : 7 jours
- Utilisation : Déploiement manuel ou automatique

---

### 5. **Security Scan** 🔒
**Objectif** : Scanner les vulnérabilités de sécurité

**Outil** : **Trivy** (scanner de vulnérabilités)

**Cibles** :
- Dépendances Python (`backend/requirements.txt`)
- Dépendances JavaScript (`frontend/package.json`)
- Images Docker (si applicable)

**Commandes** :
```bash
trivy fs --severity HIGH,CRITICAL backend/
trivy fs --severity HIGH,CRITICAL frontend/
```

**Sévérités bloquantes** : HIGH, CRITICAL

---

### 6. **Status Check** ✔️
**Objectif** : Validation globale du pipeline

**Dépendances** : Nécessite succès de tous les jobs précédents

**Résultat** : Badge de statut vert ✅ ou rouge ❌

---

## 🛠️ Tester localement

### Backend

```powershell
# Installer les dépendances
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Linters
ruff check .
black --check .
isort --check-only .
mypy . --ignore-missing-imports

# Tests
pytest --cov=services --cov-report=term-missing

# OU utiliser le script PowerShell
.\run_tests.ps1
```

### Frontend

```powershell
# Installer les dépendances
cd frontend
npm ci

# Linters
npm run lint
npm run format:check

# Build
npm run build

# Tests
npm test
```

---

## 📊 Badges de statut

Ajouter ces badges dans votre `README.md` principal :

```markdown
[![CI/CD Pipeline](https://github.com/[USERNAME]/[REPO]/actions/workflows/ci.yml/badge.svg)](https://github.com/[USERNAME]/[REPO]/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/[USERNAME]/[REPO]/branch/main/graph/badge.svg)](https://codecov.io/gh/[USERNAME]/[REPO])
```

**Remplacer** `[USERNAME]` et `[REPO]` par vos valeurs GitHub.

---

## 🔧 Configuration requise

### Secrets GitHub (Settings → Secrets and Variables → Actions)

- **`CODECOV_TOKEN`** : Token Codecov pour upload coverage (optionnel mais recommandé)

### Variables d'environnement (optionnelles)

- **`PYTHON_VERSION`** : Version Python (défaut: 3.11)
- **`NODE_VERSION`** : Version Node.js (défaut: 18)

---

## 📂 Structure des fichiers de configuration

```
.github/
  workflows/
    ci.yml               # Pipeline principal
    README.md            # Cette documentation

backend/
  .ruff.toml            # Config Ruff linter
  pyproject.toml        # Config Black + isort
  pytest.ini            # Config Pytest
  requirements-dev.txt  # Dépendances dev

frontend/
  .eslintrc.json        # Config ESLint
  .prettierrc           # Config Prettier
  .eslintignore         # Fichiers ignorés
  .prettierignore       # Fichiers ignorés
  package.json          # Scripts lint/format
```

---

## 🚨 Résolution de problèmes

### ❌ Lint Backend échoue

**Problème** : Ruff ou Black trouve des erreurs

**Solution** :
```bash
cd backend
ruff check . --fix         # Auto-fix Ruff
black .                    # Auto-format Black
isort .                    # Auto-sort imports
```

---

### ❌ Tests Backend échouent

**Problème** : Coverage < 80% ou tests failing

**Solution** :
```bash
cd backend
pytest -v --cov=services --cov-report=term-missing
# Ajouter tests pour lignes non couvertes
```

---

### ❌ Lint Frontend échoue

**Problème** : ESLint ou Prettier trouve des erreurs

**Solution** :
```bash
cd frontend
npm run lint:fix           # Auto-fix ESLint
npm run format             # Auto-format Prettier
```

---

### ❌ Build Frontend échoue

**Problème** : Erreurs de compilation React

**Solution** :
```bash
cd frontend
npm ci                     # Réinstaller dépendances
npm start                  # Tester en dev
# Corriger erreurs TypeScript/ESLint
```

---

### ❌ Security Scan trouve des vulnérabilités

**Problème** : Trivy détecte vulnérabilités HIGH/CRITICAL

**Solution** :
```bash
# Backend
cd backend
pip install --upgrade <package>

# Frontend
cd frontend
npm audit fix
npm audit fix --force  # Si nécessaire
```

---

## 📈 Métriques et monitoring

### Coverage Report

- **Backend** : Disponible sur [Codecov](https://codecov.io)
- **Objectif** : Minimum 80% coverage
- **Rapport local** : `pytest --cov=services --cov-report=html` → ouvrir `htmlcov/index.html`

### Historique du pipeline

- **GitHub Actions** : [https://github.com/[USERNAME]/[REPO]/actions](https://github.com/[USERNAME]/[REPO]/actions)
- **Durée moyenne** : ~5-7 minutes
- **Succès rate** : Suivre sur dashboard GitHub

---

## 🔄 Workflow de développement

1. **Créer une branche** : `git checkout -b feature/ma-feature`
2. **Développer** : Coder + tester localement
3. **Lint local** : Exécuter linters avant commit
4. **Commit** : `git commit -m "feat: nouvelle fonctionnalité"`
5. **Push** : `git push origin feature/ma-feature`
6. **Pull Request** : Ouvrir PR vers `develop`
7. **CI/CD s'exécute** : Vérifier statut des checks
8. **Review** : Correction si nécessaire
9. **Merge** : Si tous les checks passent ✅

---

## 📝 Changelog

### v1.0.0 (2024-01-XX)
- ✅ Création pipeline CI/CD complet
- ✅ 6 jobs parallèles (lint, test, build, security)
- ✅ Configuration Ruff + Black + isort pour Python
- ✅ Configuration ESLint + Prettier pour JavaScript
- ✅ Intégration Codecov pour coverage
- ✅ Scanner Trivy pour sécurité

---

## 🤝 Contribution

Pour contribuer au pipeline CI/CD :

1. Modifier `.github/workflows/ci.yml`
2. Tester localement avec **act** (optionnel) :
   ```bash
   act -j lint-backend --secret-file .secrets
   ```
3. Ouvrir PR avec description détaillée des changements

---

## 📚 Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [ESLint Documentation](https://eslint.org/docs/latest/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

---

**Dernière mise à jour** : 2024-01-XX  
**Auteur** : ShareYourSales Team  
**License** : MIT
