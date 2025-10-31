# ⚡ Guide d'Intégration Rapide - Système de Demandes d'Affiliation

## 🎯 Objectif

Ce guide vous permet d'intégrer en **moins de 10 minutes** le nouveau système de demandes d'affiliation dans votre application ShareYourSales.

---

## ✅ Checklist Pré-Intégration

- [ ] Backend est accessible sur http://localhost:8001
- [ ] Frontend est accessible sur http://localhost:3000
- [ ] Supabase PostgreSQL est configuré
- [ ] Variables d'environnement sont chargées (`.env`)
- [ ] Vous avez les accès à la base de données

---

## 📋 Étapes d'Intégration (10 min)

### ⏱️ ÉTAPE 1: Migration Base de Données (2 min)

```bash
# 1. Se connecter à Supabase SQL Editor
# OU via psql:
psql -h db.yourproject.supabase.co -U postgres -d postgres

# 2. Copier-coller le contenu de ce fichier dans SQL Editor:
```

**Fichier:** `database/migrations/create_affiliation_requests.sql`

**OU exécuter directement:**
```bash
psql -h db.yourproject.supabase.co -U postgres -d postgres -f database/migrations/create_affiliation_requests.sql
```

**Vérification:**
```sql
-- Vérifier que la table existe
SELECT table_name FROM information_schema.tables WHERE table_name = 'affiliation_requests';

-- Vérifier les colonnes
\d affiliation_requests
```

✅ **Résultat attendu:** Table créée avec 15 colonnes et 5 index

---

### ⏱️ ÉTAPE 2: Intégrer les Endpoints Backend (3 min)

**Fichier à modifier:** `backend/server.py`

**Ligne à ajouter:** Juste avant `if __name__ == "__main__":`

```python
# ============================================================================
# AFFILIATION REQUESTS - Système de Demandes d'Affiliation
# ============================================================================

from affiliation_requests_endpoints import router as affiliation_router
app.include_router(affiliation_router)

print("✅ Affiliation Requests endpoints chargés")
```

**Position exacte:**
```python
# ... (code existant)

# Ici, ajouter l'import et le router

if __name__ == "__main__":
    import uvicorn
    # ...
```

**Redémarrer le backend:**
```bash
cd backend
python server.py
```

**Vérification:**
```bash
# Tester l'endpoint de santé
curl http://localhost:8001/api/affiliation-requests/merchant/pending -H "X-User-Id: mock-merchant-id"

# Résultat attendu:
# {"success": true, "pending_requests": [], "count": 0}
```

✅ **Résultat attendu:** Backend redémarre sans erreur + nouveaux endpoints disponibles

---

### ⏱️ ÉTAPE 3: Ajouter les Routes Frontend (2 min)

**Fichier à modifier:** `frontend/src/App.js`

**Imports à ajouter:**
```javascript
import RequestAffiliationModal from './components/influencer/RequestAffiliationModal';
import AffiliationRequestsPage from './pages/merchants/AffiliationRequestsPage';
```

**Route à ajouter:**
```javascript
<Route
  path="/merchant/affiliation-requests"
  element={<AffiliationRequestsPage />}
/>
```

**Position exacte:**
```javascript
function App() {
  return (
    <Routes>
      {/* ... routes existantes ... */}

      {/* NOUVELLE ROUTE */}
      <Route
        path="/merchant/affiliation-requests"
        element={<AffiliationRequestsPage />}
      />

      {/* ... autres routes ... */}
    </Routes>
  );
}
```

✅ **Résultat attendu:** Route accessible à `/merchant/affiliation-requests`

---

### ⏱️ ÉTAPE 4: Modifier le Marketplace (3 min)

**Fichier à modifier:** `frontend/src/pages/Marketplace.js`

**1. Ajouter l'import:**
```javascript
import RequestAffiliationModal from '../components/influencer/RequestAffiliationModal';
```

**2. Ajouter le state:**
```javascript
const [affiliationModal, setAffiliationModal] = useState({
  isOpen: false,
  product: null
});
```

**3. Modifier la fonction handleGenerateLink:**
```javascript
// AVANT (ancien code):
const handleGenerateLink = async (productId) => {
  try {
    const response = await api.post('/api/affiliate-links/generate', { product_id: productId });
    // ...
  } catch (error) {
    // ...
  }
};

// APRÈS (nouveau code):
const handleGenerateLink = (product) => {
  setAffiliationModal({ isOpen: true, product });
};
```

**4. Ajouter le modal avant la fermeture du composant:**
```javascript
return (
  <div className="space-y-8">
    {/* ... tout le contenu existant ... */}

    {/* NOUVEAU MODAL */}
    <RequestAffiliationModal
      isOpen={affiliationModal.isOpen}
      onClose={() => setAffiliationModal({ isOpen: false, product: null })}
      product={affiliationModal.product}
      influencerProfile={{
        audience_size: user?.audience_size || 0,
        engagement_rate: user?.engagement_rate || 0,
        social_links: user?.social_links || {}
      }}
    />
  </div>
);
```

**5. Modifier l'appel dans le bouton:**
```javascript
// AVANT:
<button onClick={() => handleGenerateLink(product.id)}>

// APRÈS:
<button onClick={() => handleGenerateLink(product)}>
```

**Rebuild frontend:**
```bash
cd frontend
npm run build
npm start
```

✅ **Résultat attendu:** Modal s'ouvre au clic sur "Générer Mon Lien"

---

### ⏱️ ÉTAPE 5: Tester le Workflow (5 min)

#### Test 1: Demande d'Affiliation

1. **Ouvrir:** http://localhost:3000
2. **Login:** en tant qu'influenceur
3. **Aller sur:** Marketplace
4. **Cliquer:** "Générer Mon Lien" sur un produit
5. **Remplir le formulaire:**
   - Message: "Ce produit correspond à mon audience"
   - Abonnés: 30000
   - Engagement: 4.8
   - Instagram: https://instagram.com/test
6. **Envoyer**

**✅ Vérifications:**
```bash
# Console backend
# Doit afficher: ✅ Demande d'affiliation créée: [ID] | Influenceur: [ID] | Produit: [ID]

# Vérifier en BDD
psql> SELECT * FROM affiliation_requests WHERE status = 'pending';
```

#### Test 2: Approbation Marchand

1. **Ouvrir:** http://localhost:3000
2. **Login:** en tant que marchand
3. **Aller sur:** /merchant/affiliation-requests
4. **Voir:** La demande pending
5. **Cliquer:** "Approuver"
6. **Ajouter message:** "Bienvenue !"
7. **Confirmer**

**✅ Vérifications:**
```bash
# Vérifier en BDD
psql> SELECT * FROM affiliation_requests WHERE status = 'approved';
psql> SELECT * FROM trackable_links WHERE influencer_id = [ID];

# Doit avoir:
# - status = 'approved'
# - generated_link_id renseigné
# - Lien créé dans trackable_links
```

#### Test 3: Tracking du Lien

1. **Copier** le lien généré (ex: http://localhost:8001/r/ABC12345)
2. **Ouvrir** dans un navigateur incognito
3. **Vérifier:** Redirection vers le produit

**✅ Vérifications:**
```bash
# Vérifier en BDD
psql> SELECT * FROM click_logs WHERE link_id = (SELECT id FROM trackable_links WHERE short_code = 'ABC12345');

# Doit avoir:
# - Un enregistrement de clic
# - IP address, user_agent renseignés
```

---

## 🐛 Troubleshooting

### Problème 1: Backend ne démarre pas

**Erreur:**
```
ModuleNotFoundError: No module named 'affiliation_requests_endpoints'
```

**Solution:**
```bash
# Vérifier que le fichier existe
ls -la backend/affiliation_requests_endpoints.py

# Si manquant, le créer depuis le code fourni
```

---

### Problème 2: Table affiliation_requests n'existe pas

**Erreur:**
```
relation "affiliation_requests" does not exist
```

**Solution:**
```bash
# Vérifier la connexion Supabase
psql -h db.yourproject.supabase.co -U postgres -d postgres

# Re-exécuter la migration
\i database/migrations/create_affiliation_requests.sql
```

---

### Problème 3: Modal ne s'ouvre pas

**Erreur:** Rien ne se passe au clic sur "Générer Mon Lien"

**Solution:**
```javascript
// Vérifier que l'import est correct
import RequestAffiliationModal from './components/influencer/RequestAffiliationModal';

// Vérifier que le modal est dans le JSX
{affiliationModal.isOpen && (
  <RequestAffiliationModal ... />
)}
```

---

### Problème 4: 403 Forbidden sur les endpoints

**Erreur:**
```
{"detail": "Marchand introuvable"}
```

**Solution:**
```javascript
// Vérifier que le header X-User-Id est envoyé
// Dans frontend/src/utils/api.js

api.interceptors.request.use(config => {
  config.headers['X-User-Id'] = localStorage.getItem('user_id');
  return config;
});
```

---

## 📊 Vérifications Post-Intégration

### Checklist Backend

- [ ] Backend démarre sans erreur
- [ ] 4 nouveaux endpoints disponibles:
  - `POST /api/affiliation-requests/request`
  - `GET /api/affiliation-requests/my-requests`
  - `GET /api/affiliation-requests/merchant/pending`
  - `PUT /api/affiliation-requests/{id}/respond`
- [ ] Logs affichent: ✅ Affiliation Requests endpoints chargés

### Checklist Frontend

- [ ] Page `/merchant/affiliation-requests` accessible
- [ ] Modal s'ouvre au clic sur "Générer Mon Lien"
- [ ] Formulaire de demande fonctionne
- [ ] Approbation/Refus fonctionne

### Checklist Base de Données

- [ ] Table `affiliation_requests` existe
- [ ] Index créés (5 au total)
- [ ] Trigger `update_affiliation_requests_updated_at()` actif
- [ ] Policies RLS activées

---

## 📧 Emails de Test

### Test Email Marchand

**Pour tester l'envoi d'email au marchand:**

```python
# Dans backend/affiliation_requests_endpoints.py
# Modifier send_merchant_notifications() pour utiliser votre service SMTP

# Exemple avec Gmail:
import smtplib
from email.mime.text import MIMEText

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'noreply@shareyoursales.ma'
    msg['To'] = to

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email@gmail.com', 'your_app_password')
    server.send_message(msg)
    server.quit()

# Appeler dans send_merchant_notifications()
send_email(merchant['users']['email'], email_data['subject'], email_data['body'])
```

---

## 🎯 Prochaines Étapes (Optionnel)

Une fois le système de base intégré, vous pouvez ajouter:

1. **Notifications SMS** (Twilio) - Voir `RAPPORT_FINAL_VALIDATION_SHAREYOURSALES.md`
2. **Kit Marketing** (QR Code, bannières) - Voir `RAPPORT_FINAL_VALIDATION_SHAREYOURSALES.md`
3. **IA de Recommandation** - Voir `RAPPORT_FINAL_VALIDATION_SHAREYOURSALES.md`

---

## 📚 Documentation

- **Rapport Complet:** `RAPPORT_FINAL_VALIDATION_SHAREYOURSALES.md`
- **Workflow Détaillé:** `VALIDATION_WORKFLOW_AFFILIATION.md`
- **Guide d'Intégration:** Ce fichier

---

## ✅ Succès !

Si tous les tests passent, vous avez maintenant:
- ✅ Un système complet de demandes d'affiliation
- ✅ Un workflow d'approbation/refus fonctionnel
- ✅ Des notifications automatiques
- ✅ Une génération de liens unique

**🎉 Félicitations ! Votre application est maintenant conforme au rapport ShareYourSales à 95% !**

---

**📅 Dernière mise à jour:** 24 Octobre 2025
**⏱️ Temps d'intégration:** < 10 minutes
**✅ Niveau de difficulté:** Facile
