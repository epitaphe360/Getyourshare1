# 🧪 Guide de Test - ShareYourSales 100%

## 🚀 Test Rapide (5 minutes)

### Prérequis
- ✅ Backend running sur http://0.0.0.0:8001
- ✅ Frontend running sur http://localhost:3000
- ✅ Base de données Supabase connectée

---

## ✅ Smoke Test - Vérification Rapide

### 1. Page d'Accueil
```
URL: http://localhost:3000
✓ Page charge sans erreur
✓ Boutons "Se connecter" / "S'inscrire" visibles
✓ Navigation fonctionnelle
```

### 2. Connexion
```
URL: http://localhost:3000/login
✓ Formulaire email/password s'affiche
✓ Bouton "Connexion" cliquable
✓ Messages d'erreur si champs vides
✓ Redirection vers dashboard après login
```

### 3. Dashboard
```
URL: http://localhost:3000/dashboard
✓ Stats cards affichées (4 minimum)
✓ Graphiques chargent (Recharts)
✓ Aucune erreur console
✓ Sidebar visible à gauche
```

### 4. Recherche Globale
```
Action: Appuyer Ctrl+K
✓ Modal s'ouvre
✓ Input de recherche focus automatique
✓ Taper "test" → résultats apparaissent ou message "Aucun résultat"
✓ Escape ferme le modal
```

### 5. Notifications
```
Action: Cliquer cloche dans header
✓ Dropdown s'ouvre
✓ Liste de notifications s'affiche (ou "Aucune notification")
✓ Badge avec nombre de non-lues
✓ Click outside ferme le dropdown
```

---

## 🎯 Tests Fonctionnels Détaillés

### Test 1 : Système de Messagerie (10 min)

#### 1.1 Navigation Messages
```
Étapes:
1. Cliquer "Messages" dans sidebar
2. Vérifier URL = /messages
3. Vérifier layout split (conversations | thread)
4. Vérifier état vide si aucune conversation
```
**Résultat attendu :** Interface messagerie s'affiche correctement

#### 1.2 Créer Conversation (via API)
```
Méthode: POST /api/messages/send
Body:
{
  "recipient_id": "influencer_123",
  "recipient_type": "influencer",
  "content": "Bonjour, je souhaite discuter d'une collaboration",
  "subject": "Nouvelle collaboration"
}
```
**Résultat attendu :** 
- Status 200
- Retour JSON avec conversation_id
- Message enregistré en DB

#### 1.3 Vérifier Conversation UI
```
Étapes:
1. Rafraîchir page /messages
2. Vérifier conversation apparaît dans liste gauche
3. Cliquer conversation
4. Vérifier message s'affiche dans thread droite
5. Vérifier badge "non lu" si applicable
```
**Résultat attendu :** Conversation visible avec message

#### 1.4 Envoyer Message UI
```
Étapes:
1. Dans conversation active, taper message dans input bas
2. Appuyer Enter ou cliquer bouton "Envoyer"
3. Vérifier message apparaît immédiatement
4. Vérifier auto-scroll vers bas
5. Vérifier indicateur ✓ (envoyé)
```
**Résultat attendu :** Message envoyé et affiché instantanément

#### 1.5 Notifications
```
Étapes:
1. Cliquer cloche header
2. Vérifier notification "Nouveau message de [nom]"
3. Cliquer notification
4. Vérifier redirection vers /messages
5. Vérifier badge diminue (1 notification marquée lue)
```
**Résultat attendu :** Notification fonctionnelle avec navigation

---

### Test 2 : Gestion Produits (15 min)

#### 2.1 Liste Produits
```
Étapes:
1. Cliquer "Produits" dans sidebar
2. Vérifier URL = /products
3. Vérifier stats cards (Total, Actifs, Valeur catalogue)
4. Vérifier tableau avec colonnes: Image, Nom, Catégorie, Prix, Commission, Statut, Actions
5. Si vide: vérifier état vide avec bouton "Créer produit"
```
**Résultat attendu :** Liste produits s'affiche avec stats

#### 2.2 Recherche Produits
```
Étapes:
1. Dans input "Rechercher produits...", taper "test"
2. Vérifier filtrage instantané (nom/description/catégorie)
3. Effacer input
4. Vérifier tous produits réapparaissent
```
**Résultat attendu :** Recherche filtre résultats en temps réel

#### 2.3 Créer Produit
```
Étapes:
1. Cliquer bouton "Ajouter un produit"
2. Vérifier URL = /products/create
3. Remplir formulaire:
   - Nom: "Test Product" *
   - Description: "Ceci est un test" *
   - Prix: 49.99 *
   - Commission: 15 *
   - Catégorie: Mode *
   - Statut: active
   - SKU: TEST-001
   - Stock: 50
   - Tags: test,demo,mode
4. Upload image (JPG/PNG < 5MB)
5. Vérifier preview image apparaît
6. Cliquer "Créer le produit"
```
**Résultat attendu :**
- Validation OK (champs requis remplis)
- Redirection vers /products
- Produit apparaît dans tableau
- Notification succès

#### 2.4 Éditer Produit
```
Étapes:
1. Dans tableau produits, cliquer icône Edit (Pen)
2. Vérifier URL = /products/{id}/edit
3. Vérifier formulaire pré-rempli avec données produit
4. Modifier prix: 59.99
5. Cliquer "Modifier le produit"
```
**Résultat attendu :**
- Formulaire pré-rempli correctement
- Update réussit
- Redirection vers /products
- Prix modifié visible dans tableau

#### 2.5 Supprimer Produit
```
Étapes:
1. Cliquer icône Trash sur un produit
2. Vérifier modal confirmation s'ouvre
3. Vérifier message "Êtes-vous sûr..."
4. Cliquer "Supprimer"
```
**Résultat attendu :**
- Modal confirmation apparaît
- Produit supprimé après confirmation
- Disparaît du tableau
- Notification succès

#### 2.6 Validation Formulaire
```
Étapes:
1. Aller sur /products/create
2. Laisser champs vides
3. Cliquer "Créer le produit"
4. Vérifier messages erreur rouges sous champs requis
5. Entrer prix négatif (-10)
6. Vérifier erreur "Le prix doit être positif"
7. Entrer commission 150%
8. Vérifier erreur "Commission entre 0 et 100"
9. Upload image > 5MB
10. Vérifier erreur "Taille maximale 5MB"
```
**Résultat attendu :** Tous validations bloquent submit avec messages clairs

---

### Test 3 : Gestion Campagnes (10 min)

#### 3.1 Liste Campagnes
```
Étapes:
1. Naviguer vers /campaigns
2. Vérifier tableau campagnes s'affiche
3. Vérifier colonnes: Nom, Catégorie, Statut, Budget, Dates, Actions
4. Vérifier badges statut colorés:
   - Active = vert
   - Paused = jaune
   - Archived = gris
   - Draft = bleu
```
**Résultat attendu :** Liste avec badges colorés selon statut

#### 3.2 Pause Campagne
```
Étapes:
1. Trouver campagne avec statut "Active"
2. Cliquer bouton "Pause" (icône jaune)
3. Vérifier modal confirmation s'ouvre
4. Vérifier message "Mettre en pause cette campagne ?"
5. Cliquer "Confirmer"
```
**Résultat attendu :**
- Modal confirmation apparaît
- Après confirmation: badge passe à "En pause" (jaune)
- Bouton "Pause" disparaît, bouton "Play" apparaît
- Notification succès

#### 3.3 Reprendre Campagne
```
Étapes:
1. Trouver campagne avec statut "Paused"
2. Cliquer bouton "Play" (icône verte)
3. Confirmer dans modal
```
**Résultat attendu :**
- Badge passe à "Actif" (vert)
- Bouton "Play" disparaît, bouton "Pause" réapparaît

#### 3.4 Archiver Campagne
```
Étapes:
1. Trouver campagne avec statut "Active" ou "Paused"
2. Cliquer bouton "Archive" (icône grise)
3. Vérifier modal avec WARNING rouge
4. Vérifier message "Cette action est irréversible"
5. Cliquer "Confirmer"
```
**Résultat attendu :**
- Warning rouge dans modal
- Badge passe à "Archivé" (gris)
- Boutons Pause/Play/Archive disparaissent
- Campagne non modifiable

#### 3.5 Permissions
```
Étapes (si role merchant):
1. Tenter modifier campagne d'un autre merchant
2. Vérifier erreur 403 Forbidden

Étapes (si role admin):
1. Modifier n'importe quelle campagne
2. Vérifier modification réussit
```
**Résultat attendu :** Permissions respectées (owner ou admin seulement)

---

### Test 4 : Profil Influenceur (8 min)

#### 4.1 Navigation Profil
```
Étapes:
1. Naviguer vers /influencers (liste)
2. Cliquer nom d'un influenceur
3. Vérifier URL = /influencers/{id}
4. Vérifier page charge sans erreur
```
**Résultat attendu :** Page profil s'affiche

#### 4.2 Vérifier Sections
```
Vérifications visuelles:
✓ Header: Avatar, Nom, Badge vérifié (si applicable), Bio
✓ Contact Info: Email, Téléphone, Localisation, Date inscription
✓ Social Links: Instagram (rose), Twitter (bleu), Facebook, Website
✓ Stats Cards (4): Followers, Clicks, Sales (€), Conversion %
✓ Catégories: Badges colorés
✓ Campagnes: Nombre complétées
✓ Description: Texte bio complet
```
**Résultat attendu :** Toutes sections visibles et formatées

#### 4.3 Vérifier Stats Réelles
```
Étapes:
1. Noter stats affichées (ex: 15,234€ sales)
2. Vérifier DevTools Network → /api/influencers/{id}/stats
3. Comparer response JSON avec UI
4. Vérifier calculs:
   - total_sales = somme(sales.amount)
   - total_clicks = somme(tracking_links.clicks)
   - conversion_rate = (sales/clicks) * 100
   - campaigns_completed = count(WHERE status='completed')
```
**Résultat attendu :** Stats affichées = données API (pas hardcodées)

#### 4.4 Bouton Contacter
```
Étapes:
1. Cliquer bouton "Contacter"
2. Vérifier redirection vers /messages
3. Vérifier state passé (recipient = influencer)
4. Vérifier conversation peut être créée
```
**Résultat attendu :** Navigation vers messagerie avec context

#### 4.5 Social Links
```
Étapes:
1. Vérifier liens sociaux cliquables
2. Cliquer Instagram → ouvre nouvel onglet (si lien valide)
3. Vérifier couleurs icônes:
   - Instagram = rose (#E1306C)
   - Twitter = bleu (#1DA1F2)
   - Facebook = bleu foncé (#1877F2)
   - Website = gris (#6B7280)
```
**Résultat attendu :** Liens fonctionnels avec design cohérent

---

### Test 5 : Analytics Admin (5 min)

#### 5.1 Dashboard Admin
```
Étapes (role admin requis):
1. Login avec compte admin
2. Naviguer vers /dashboard
3. Vérifier graphique catégories (PieChart)
4. Noter distribution (ex: Mode 35%, Tech 25%, Beauté 20%...)
```
**Résultat attendu :** Graphique s'affiche avec vraies données

#### 5.2 Vérifier Données Réelles
```
Étapes:
1. Ouvrir DevTools Network
2. Chercher appel /api/analytics/admin/categories
3. Vérifier response JSON:
   [
     {"category": "Mode", "count": 12},
     {"category": "Tech", "count": 8},
     ...
   ]
4. Comparer avec graphique UI
5. Rafraîchir page plusieurs fois
6. Vérifier valeurs IDENTIQUES (pas aléatoires)
```
**Résultat attendu :** 
- Données proviennent de vraie requête SQL GROUP BY
- Valeurs stables (non Math.random())
- Cohérence UI/API

#### 5.3 Validation Base de Données
```
SQL Query (optionnel):
SELECT category, COUNT(*) as count
FROM campaigns
GROUP BY category
ORDER BY count DESC;

Comparer résultat avec API response
```
**Résultat attendu :** Données API = données DB

---

### Test 6 : Recherche Globale (5 min)

#### 6.1 Ouvrir Recherche
```
Étapes:
1. Depuis n'importe quelle page, appuyer Ctrl+K (Cmd+K sur Mac)
2. Vérifier modal s'ouvre full-screen
3. Vérifier overlay noir semi-transparent
4. Vérifier input auto-focus
```
**Résultat attendu :** Modal recherche s'ouvre instantanément

#### 6.2 Recherche Multi-Entités
```
Étapes:
1. Taper "a" (1 caractère)
2. Vérifier message "Tapez au moins 2 caractères"
3. Taper "test" (4 caractères)
4. Vérifier sections apparaissent:
   - Campagnes (icône Target, couleur indigo)
   - Produits (icône Package, couleur verte)
   - Influenceurs (icône TrendingUp, couleur violette)
   - Marchands (icône Users, couleur bleue)
5. Vérifier limite 3 résultats par section
6. Vérifier compteur total en bas (ex: "8 résultats")
```
**Résultat attendu :** Recherche filtre 4 types d'entités

#### 6.3 Navigation Résultats
```
Étapes:
1. Rechercher "mode"
2. Cliquer résultat "Campagne Mode Hiver"
3. Vérifier navigation vers /campaigns
4. Vérifier modal se ferme
5. Vérifier query input se vide

Répéter pour:
- Produit → /products/{id}/edit
- Influenceur → /influencers/{id}
- Marchand → /merchants
```
**Résultat attendu :** Navigation correcte selon type

#### 6.4 Fermeture Modal
```
Tester 3 méthodes:
1. Appuyer Escape → modal ferme
2. Cliquer icône X en haut → modal ferme
3. Cliquer en dehors du modal (zone noire) → modal ferme
```
**Résultat attendu :** 3 méthodes fonctionnent

#### 6.5 Keyboard Shortcuts
```
Vérifier footer affiche:
✓ ↑↓ Naviguer
✓ Enter Sélectionner
✓ Esc Fermer

Note: Navigation ↑↓ non implémentée (amélioration future)
```
**Résultat attendu :** Instructions visibles

---

## 🐛 Cas d'Erreur à Tester

### Backend Offline
```
Étapes:
1. Arrêter serveur backend (Ctrl+C)
2. Tenter actions frontend (login, fetch data)
3. Vérifier messages erreur réseau
4. Vérifier pas de crash app
```
**Résultat attendu :** Erreurs gérées gracieusement

### Données Invalides
```
Tests:
1. Créer produit prix = "abc" → erreur validation
2. Message vide → bouton disabled ou erreur
3. Upload fichier .exe → refusé (images seulement)
4. Commission 200% → erreur "Max 100%"
```
**Résultat attendu :** Validation côté client + serveur

### Permissions Insuffisantes
```
Tests (merchant):
1. Accéder /admin → redirect ou 403
2. Modifier campagne autre merchant → 403
3. Voir stats globales → 403
```
**Résultat attendu :** Accès refusé proprement

### Ressources Inexistantes
```
Tests:
1. Naviguer /products/999999 → 404
2. GET /api/influencers/fake_id → 404
3. Modifier conversation inexistante → erreur
```
**Résultat attendu :** 404 avec message clair

---

## 📊 Performance

### Temps de Chargement
```
Mesures (DevTools Network):
✓ Page initiale < 2 sec
✓ API calls < 500 ms
✓ Images < 1 sec
✓ Total page load < 3 sec
```

### Responsive
```
Tester résolutions:
✓ Mobile 375px (iPhone SE)
✓ Tablet 768px (iPad)
✓ Desktop 1920px (Full HD)

Vérifier:
- Sidebar collapse sur mobile
- Tables scrollables horizontal
- Modals adaptés
- Buttons cliquables (min 44px)
```

---

## ✅ Checklist Finale

### Fonctionnalités Core
- [ ] Login/Logout fonctionnent
- [ ] Dashboards s'affichent (Admin/Merchant/Influencer)
- [ ] Campagnes CRUD complet
- [ ] Produits CRUD complet + upload image
- [ ] Messagerie conversations + notifications
- [ ] Profils influenceurs stats réelles
- [ ] Analytics catégories vraies données
- [ ] Recherche globale Ctrl+K
- [ ] Sidebar navigation complète

### UX/UI
- [ ] Aucune erreur console critique
- [ ] Design cohérent (Tailwind)
- [ ] Icônes Lucide affichées
- [ ] Badges colorés corrects
- [ ] Modals confirmations
- [ ] États vides messages
- [ ] Loading spinners
- [ ] Success/error notifications
- [ ] Responsive mobile/desktop

### Technique
- [ ] Backend port 8001 opérationnel
- [ ] Frontend port 3000 compilé
- [ ] Supabase DB connectée
- [ ] 66 endpoints API chargés
- [ ] Aucune erreur 500
- [ ] Logs serveur propres
- [ ] Webpack warnings non-critiques

---

## 🎯 Critères de Succès

**Test RÉUSSI si :**
- ✅ Tous tests fonctionnels passent (90%+)
- ✅ Aucune erreur bloquante
- ✅ Performance acceptable (< 3 sec load)
- ✅ Design cohérent sur toutes pages
- ✅ Données réelles (pas hardcodées)

**Test ÉCHOUÉ si :**
- ❌ Erreur 500 fréquente
- ❌ Page blanche (crash React)
- ❌ Fonctionnalité core cassée (login, dashboard)
- ❌ Données perdues (DB corruption)
- ❌ Performance > 10 sec

---

## 📝 Rapport de Test

**Template à remplir:**

```
Date: ___________
Testeur: ___________
Environnement: [ ] Local  [ ] Staging  [ ] Production

SMOKE TEST (5 min)
[ ] Accueil charge
[ ] Login fonctionne
[ ] Dashboard s'affiche
[ ] Recherche Ctrl+K OK
[ ] Notifications OK

TESTS FONCTIONNELS
[ ] Messagerie (10 min) - ___/5 OK
[ ] Produits (15 min) - ___/6 OK
[ ] Campagnes (10 min) - ___/5 OK
[ ] Profils (8 min) - ___/5 OK
[ ] Analytics (5 min) - ___/3 OK
[ ] Recherche (5 min) - ___/5 OK

ERREURS TROUVÉES:
1. _________________________
2. _________________________
3. _________________________

RECOMMANDATIONS:
_________________________
_________________________

CONCLUSION: [ ] APPROUVÉ  [ ] REFUSÉ  [ ] À CORRIGER
```

---

**🎉 Bon testing ! Si tous les tests passent, l'application est 100% opérationnelle ! 🎉**
