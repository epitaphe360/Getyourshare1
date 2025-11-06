# ⚠️ RÈGLE GIT OBLIGATOIRE

**Date d'application**: 2025-01-06  
**Statut**: 🔴 **OBLIGATOIRE**

---

## 📜 RÈGLE UNIQUE

### ✅ TOUS LES COMMITS DOIVENT ALLER SUR LA BRANCHE `main`

**Plus de branches multiples!**  
**Plus de merge conflicts!**  
**Plus de code dispersé!**

---

## 🎯 POURQUOI CETTE RÈGLE?

### Problème Résolu
Avant cette règle, nous avions:
- ❌ **7 branches divergentes** avec 1,539 commits non mergés
- ❌ **70+ conflits** lors des tentatives de fusion
- ❌ Code dispersé sur plusieurs branches
- ❌ Fonctionnalités perdues
- ❌ Historique Git complexe

### Solution Appliquée
Fusion complète de toutes les branches dans `main`:
- ✅ Toutes les branches consolidées
- ✅ Zéro conflit grâce à la stratégie intelligente
- ✅ Code unifié dans une seule branche
- ✅ Historique Git linéaire et propre

---

## 📋 WORKFLOW OBLIGATOIRE

### 1️⃣ Avant de Commencer à Travailler
```bash
# Toujours se placer sur main
git checkout main

# Récupérer les dernières mises à jour
git pull origin main
```

### 2️⃣ Faire des Modifications
```bash
# Modifier vos fichiers
# Tester votre code
# Vérifier qu'il n'y a pas d'erreurs
```

### 3️⃣ Commit des Changements
```bash
# Ajouter les fichiers modifiés
git add .

# Créer un commit avec un message descriptif
git commit -m "type: description claire du changement"
```

**Types de commits recommandés:**
- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `refactor:` - Refactorisation du code
- `docs:` - Documentation
- `chore:` - Tâches de maintenance
- `test:` - Ajout/modification de tests
- `style:` - Formatage du code

### 4️⃣ Push vers GitHub
```bash
# Pousser directement sur main
git push origin main
```

---

## 🚫 CE QUI EST INTERDIT

### ❌ NE JAMAIS créer de branches
```bash
# ❌ INTERDIT
git checkout -b ma-nouvelle-branche
git checkout -b feature/...
git checkout -b fix/...
```

### ❌ NE JAMAIS pousser vers une autre branche
```bash
# ❌ INTERDIT
git push origin ma-branche
git push origin feature/xyz
```

### ❌ NE JAMAIS travailler sur une autre branche
```bash
# ❌ INTERDIT
git checkout autre-branche
```

---

## ✅ CE QUI EST AUTORISÉ

### ✅ Commits fréquents sur main
```bash
git add .
git commit -m "feat: ajout de nouvelle fonctionnalité"
git push origin main
```

### ✅ Petits commits incrémentaux
Mieux vaut 10 petits commits clairs qu'1 gros commit confus:
```bash
git commit -m "feat: ajouter endpoint users"
git commit -m "feat: ajouter validation email"
git commit -m "test: ajouter tests pour users"
git commit -m "docs: documenter API users"
```

### ✅ Pull avant de push (si plusieurs personnes travaillent)
```bash
git pull origin main
git push origin main
```

---

## 🔧 EN CAS DE CONFLIT (rare)

Si vous obtenez un conflit lors du pull:

```bash
# 1. Pull les changements
git pull origin main

# 2. Si conflit, VS Code vous montrera les fichiers
# 3. Ouvrez chaque fichier et choisissez la bonne version
# 4. Après résolution:
git add .
git commit -m "merge: résolution conflit"
git push origin main
```

---

## 📊 ÉTAT ACTUEL

### Branches GitHub
- ✅ `main` - **SEULE BRANCHE ACTIVE**
- ❌ Toutes les autres branches **SUPPRIMÉES**

### Vérification
```bash
# Vérifier les branches distantes
git branch -r

# Résultat attendu:
#   origin/HEAD -> origin/main
#   origin/main
```

---

## 🎯 AVANTAGES DE CETTE RÈGLE

### 1. Simplicité
- ✅ Une seule branche = zéro confusion
- ✅ Workflow simple: edit → commit → push
- ✅ Pas de merge = pas de conflits

### 2. Collaboration Efficace
- ✅ Tout le monde voit le même code
- ✅ Pas de code "caché" dans des branches
- ✅ Intégration continue naturelle

### 3. Code Toujours Déployable
- ✅ Main = production ready
- ✅ Tests automatiques sur chaque commit
- ✅ Déploiement continu possible

### 4. Historique Git Propre
- ✅ Linéaire et facile à suivre
- ✅ Chaque commit = un changement atomique
- ✅ Facile de revenir en arrière si besoin

---

## 📚 EXEMPLES DE WORKFLOW

### Exemple 1: Ajouter une Nouvelle Fonctionnalité
```bash
# 1. Se placer sur main
git checkout main
git pull origin main

# 2. Développer la fonctionnalité
# ... édition de fichiers ...

# 3. Tester localement
npm test  # ou pytest pour backend

# 4. Commit
git add .
git commit -m "feat: ajouter système de notifications push"

# 5. Push
git push origin main
```

### Exemple 2: Corriger un Bug
```bash
# 1. Se placer sur main
git checkout main
git pull origin main

# 2. Corriger le bug
# ... édition de fichiers ...

# 3. Vérifier la correction
# ... tests manuels ou automatiques ...

# 4. Commit
git add .
git commit -m "fix: corriger erreur 500 sur endpoint /api/users"

# 5. Push
git push origin main
```

### Exemple 3: Refactoring
```bash
# 1. Se placer sur main
git checkout main
git pull origin main

# 2. Refactoriser
# ... amélioration du code ...

# 3. S'assurer que tout fonctionne
npm test

# 4. Commit
git add .
git commit -m "refactor: moderniser syntaxe Pydantic v2"

# 5. Push
git push origin main
```

---

## ⚡ COMMANDES RAPIDES

### Workflow Standard Quotidien
```bash
# Matin: mise à jour
git checkout main && git pull origin main

# Pendant la journée: commits réguliers
git add . && git commit -m "description" && git push origin main

# Soir: dernier push
git push origin main
```

### Vérification Status
```bash
# Voir les modifications en cours
git status

# Voir l'historique récent
git log --oneline -10

# Voir les branches (doit être que main)
git branch -a
```

---

## 🆘 AIDE RAPIDE

### Si vous êtes sur une autre branche
```bash
# Revenir sur main
git checkout main

# Si vous avez des modifications non commitées
git stash  # sauvegarder temporairement
git checkout main
git stash pop  # récupérer les modifications
```

### Si vous avez créé une branche par erreur
```bash
# Revenir sur main
git checkout main

# Supprimer la branche locale
git branch -D nom-branche-erreur
```

### Si vous avez poussé vers une autre branche
```bash
# Contacter l'équipe pour décider:
# - Merger dans main puis supprimer
# - Ou supprimer directement si pas important
```

---

## 📞 CONTACT

En cas de doute sur cette règle:
- Consulter `FUSION_COMPLETE_RAPPORT.md` pour comprendre le contexte
- Vérifier `git log --oneline -10` pour voir l'historique
- Toujours travailler sur `main`

---

## 🎓 CONCLUSION

**UNE SEULE RÈGLE À RETENIR:**

```
TOUS LES COMMITS → MAIN
```

Simple. Efficace. Sans conflits.

---

**Créé le**: 2025-01-06  
**Mis à jour**: 2025-01-06  
**Version**: 1.0  
**Statut**: 🔴 **OBLIGATOIRE ET PERMANENT**
