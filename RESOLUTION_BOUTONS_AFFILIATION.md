# 🔧 RÉSOLUTION : Boutons Accepter/Rejeter Inactifs

## 📋 **Diagnostic**

Les boutons "Accepter" et "Rejeter" dans **Demandes d'Affiliation** ne réagissent pas.

### **Causes possibles :**

1. ✅ **Frontend fonctionnel** : Les fonctions `handleApprove()` et `handleReject()` existent
2. ✅ **Endpoints backend OK** : `/api/merchant/affiliation-requests/{id}/approve` et `/reject`
3. ❓ **Fonctions SQL manquantes** : `approve_affiliation_request()` et `reject_affiliation_request()`
4. ❓ **Migration SQL non exécutée** : `modify_trackable_links_unified.sql`

---

## 🚀 **SOLUTION RAPIDE**

### **Étape 1 : Vérifier la console du navigateur**

1. Ouvrez l'application : `http://localhost:3000`
2. Connectez-vous en tant que **Merchant** :
   - Email : `contact@techstyle.fr`
   - Password : `merchant123`
   - Code 2FA : `123456`
3. Allez dans **Demandes d'Affiliation**
4. Appuyez sur `F12` → Onglet **Console**
5. Cliquez sur "Accepter" ou "Rejeter"
6. **Observez les erreurs**

### **Erreurs courantes et solutions :**

#### ❌ **Erreur : "function approve_affiliation_request does not exist"**

**Solution :** Exécutez la migration SQL

1. Ouvrez : https://supabase.com/dashboard
2. Projet : `iamezkmapbhlhhvvsits`
3. SQL Editor → New query
4. Copiez le contenu de :
   ```
   database/migrations/modify_trackable_links_unified.sql
   ```
5. Cliquez **RUN**

#### ❌ **Erreur : "column influencer_message does not exist"**

**Solution :** La migration n'a pas été exécutée (même solution qu'au-dessus)

#### ❌ **Erreur 403 : "Marchands uniquement"**

**Solution :** Vous n'êtes pas connecté en tant que marchand. Vérifiez votre rôle.

#### ❌ **Erreur 404 : "Demande non trouvée"**

**Solution :** L'ID de la demande est incorrect ou la demande a déjà été traitée.

---

## 🔍 **VÉRIFICATION MANUELLE**

### **Option 1 : Test Backend Direct**

```powershell
# Terminal 1 - Backend doit être actif
cd c:\Users\Admin\Desktop\shareyoursales\Getyourshare1\backend
python server.py

# Terminal 2 - Test avec curl (remplacez TOKEN et REQUEST_ID)
curl -X POST "http://localhost:8001/api/merchant/affiliation-requests/REQUEST_ID/approve" `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"merchant_response": "Bienvenue!"}'
```

### **Option 2 : Vérifier la base de données**

Exécutez dans Supabase SQL Editor :

```sql
-- 1. Vérifier si les fonctions existent
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_name LIKE '%affiliation%';

-- 2. Vérifier les colonnes de trackable_links
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'trackable_links';

-- 3. Vérifier les demandes en attente
SELECT id, influencer_id, product_id, status, influencer_message, created_at
FROM trackable_links
WHERE status = 'pending_approval';

-- 4. Test manuel d'approbation (remplacez les IDs)
SELECT approve_affiliation_request(
  'REQUEST_ID'::uuid,
  'Test approbation'::text,
  'MERCHANT_USER_ID'::uuid
);
```

---

## 📝 **MIGRATION SQL COMPLÈTE**

**Fichier :** `database/migrations/modify_trackable_links_unified.sql`

Cette migration :
- ✅ Ajoute les colonnes nécessaires à `trackable_links`
- ✅ Crée les fonctions SQL `approve_affiliation_request()` et `reject_affiliation_request()`
- ✅ Crée les vues `merchant_affiliation_requests` et `affiliation_requests_stats`
- ✅ Configure les contraintes de statut

---

## 🎯 **APRÈS LA MIGRATION**

1. **Redémarrez le backend** (Ctrl+C puis relancez)
2. **Rafraîchissez le frontend** (F5)
3. **Testez les boutons** :
   - Cliquez "Accepter" → Modal s'ouvre
   - Écrivez un message (optionnel)
   - Cliquez "Confirmer l'Approbation"
   - ✅ Toast de succès : "Demande approuvée !"
   - Le statut passe à "Approuvée" (badge vert)

4. **Vérifiez le lien de tracking** :
   - Allez dans **Liens de Tracking**
   - Le nouveau lien apparaît avec status "Active"
   - Le `short_code` est généré automatiquement

---

## 🐛 **DEBUGGING AVANCÉ**

### **Activer les logs backend**

Ajoutez dans `server.py` ligne 3650 :

```python
@app.post("/api/merchant/affiliation-requests/{request_id}/approve")
async def approve_affiliation_request(...):
    try:
        print(f"[DEBUG] Approve request ID: {request_id}")
        print(f"[DEBUG] User: {user}")
        print(f"[DEBUG] Response: {response_data.merchant_response}")
        
        # ... reste du code
```

### **Vérifier les requêtes réseau**

1. F12 → Onglet **Network**
2. Cliquez "Accepter"
3. Cherchez la requête `approve`
4. Vérifiez :
   - Status Code : doit être 200
   - Response : `{"success": true, ...}`
   - Si 500 : regardez la console backend

---

## ✅ **CHECKLIST FINALE**

- [ ] Migration SQL exécutée dans Supabase
- [ ] Fonctions SQL créées (`approve_affiliation_request`, `reject_affiliation_request`)
- [ ] Colonnes ajoutées à `trackable_links` (`influencer_message`, `merchant_response`, etc.)
- [ ] Backend redémarré
- [ ] Frontend rafraîchi
- [ ] Connecté en tant que **Merchant**
- [ ] Demandes d'affiliation visible (au moins une demande `pending_approval`)
- [ ] Bouton "Accepter" ouvre le modal
- [ ] Bouton "Confirmer l'Approbation" fonctionne
- [ ] Toast de succès affiché
- [ ] Statut mis à jour dans la liste

---

## 📞 **BESOIN D'AIDE ?**

Si après ces étapes les boutons ne fonctionnent toujours pas :

1. **Copiez les erreurs de la console** (F12 → Console)
2. **Copiez les logs du backend** (terminal où server.py tourne)
3. **Vérifiez que la migration SQL a bien été exécutée**

Le problème vient très certainement de la **migration SQL non exécutée**.
