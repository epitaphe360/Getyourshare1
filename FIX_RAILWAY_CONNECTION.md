# 🐛 Résolution du Problème ERR_CONNECTION_REFUSED sur Railway

## 📋 Problème Identifié

Lorsque vous lancez l'application depuis Railway, vous obtenez ces erreurs :

```
localhost:8001/api/subscription-plans:1 Failed to load resource: net::ERR_CONNECTION_REFUSED
localhost:8001/api/auth/login:1 Failed to load resource: net::ERR_CONNECTION_REFUSED
WebSocketClient.js:13 WebSocket connection to 'wss://considerate-luck-production.up.railway.app:8001/ws' failed
```

## 🔍 Cause Racine

Le frontend déployé sur Railway essaie de se connecter à `localhost:8001` au lieu de l'URL Railway du backend.

### Pourquoi ?

1. **Variable d'environnement manquante** : `REACT_APP_BACKEND_URL` n'est pas configurée sur Railway
2. **Valeur par défaut** : Le code utilise `http://localhost:8001` comme fallback
3. **Build statique** : Les variables d'environnement doivent être définies **AVANT** le build React

## ✅ Solution

### Étape 1 : Configurer la variable d'environnement sur Railway

1. Allez dans votre service **Frontend** sur Railway
2. Ouvrez l'onglet **Variables**
3. Ajoutez cette variable :

```bash
REACT_APP_BACKEND_URL=https://[VOTRE-BACKEND-URL].up.railway.app
```

**⚠️ Important :**
- Remplacez `[VOTRE-BACKEND-URL]` par l'URL réelle de votre backend Railway
- **PAS de slash final** : `https://backend.railway.app` ✅ (pas `https://backend.railway.app/` ❌)
- **PAS de /api** : Le code ajoute `/api` automatiquement

### Étape 2 : Redéployer le frontend

Une fois la variable ajoutée, Railway va automatiquement redéployer. Si ce n'est pas le cas :

1. Allez dans l'onglet **Deployments**
2. Cliquez sur **Redeploy** pour le dernier déploiement

### Étape 3 : Vérifier CORS sur le backend

Assurez-vous que l'URL frontend est dans les origines CORS du backend :

1. Allez dans votre service **Backend** sur Railway
2. Ouvrez l'onglet **Variables**
3. Vérifiez/Ajoutez `CORS_ORIGINS` :

```bash
CORS_ORIGINS=https://[VOTRE-FRONTEND-URL].railway.app,http://localhost:3000
```

4. Redéployez le backend si vous avez modifié cette variable

## 🔧 Fichiers Modifiés

### `frontend/src/utils/api.js`

```javascript
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
```

Cette ligne lit la variable d'environnement `REACT_APP_BACKEND_URL`. Si elle n'existe pas, elle utilise `localhost:8001` (développement local).

### `frontend/src/context/WebSocketContext.js`

```javascript
const getWebSocketUrl = () => {
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
  const wsBase = backendUrl.replace(/^https?:\/\//, '');
  return `${wsProtocol}://${wsBase}/ws`;
};
```

Cette fonction construit l'URL WebSocket à partir de `REACT_APP_BACKEND_URL` :
- `http://localhost:8001` → `ws://localhost:8001/ws`
- `https://backend.railway.app` → `wss://backend.railway.app/ws`

### `frontend/.env.production`

```bash
DISABLE_ESLINT_PLUGIN=true
REACT_APP_BACKEND_URL=https://shareyoursales-backend-production.up.railway.app
```

Ce fichier définit la valeur par défaut pour production, mais **Railway peut l'overrider** avec ses propres variables d'environnement.

## 📊 Test de Validation

Après avoir configuré `REACT_APP_BACKEND_URL` et redéployé :

1. **Ouvrez la console browser** (F12)
2. **Rechargez la page**
3. **Vérifiez les requêtes réseau** :
   - ✅ `https://[backend-url]/api/auth/login` (pas `localhost:8001`)
   - ✅ `wss://[backend-url]/ws` pour WebSocket

4. **Testez le login** :
   - Email : `admin@shareyoursales.com`
   - Password : `admin123`
   - 2FA : `123456`
   - Devrait fonctionner sans erreur

## 🎯 Checklist Finale

- [ ] `REACT_APP_BACKEND_URL` configurée dans Railway Frontend
- [ ] Valeur = URL backend Railway (sans slash final, sans /api)
- [ ] Frontend redéployé
- [ ] `CORS_ORIGINS` configuré dans Railway Backend avec URL frontend
- [ ] Backend redéployé (si CORS modifié)
- [ ] Console browser ne montre plus `ERR_CONNECTION_REFUSED`
- [ ] Login fonctionne
- [ ] WebSocket se connecte (ou timeout si backend n'a pas de handler)

## 📝 Notes Importantes

### Variables d'environnement React

Les variables React **doivent** commencer par `REACT_APP_` :
- ✅ `REACT_APP_BACKEND_URL`
- ❌ `BACKEND_URL` (ne sera pas accessible dans le code)

### Timing du Build

Les variables d'environnement sont **injectées au moment du build** :
- Si vous changez une variable, vous **devez** redéployer
- Le build crée un bundle statique avec les valeurs "hardcodées"
- C'est pourquoi on ne peut pas changer les variables après le build

### WebSocket avec Railway

Railway supporte les WebSockets nativement :
- Utilisez `wss://` pour HTTPS
- Utilisez `ws://` pour HTTP
- Pas besoin de configuration spéciale

## 🚀 Résultat Attendu

Après avoir suivi ces étapes, votre application devrait :

1. ✅ Se connecter au backend Railway (pas localhost)
2. ✅ Afficher la landing page sans erreurs
3. ✅ Permettre la connexion des utilisateurs
4. ✅ WebSocket tente de se connecter à la bonne URL
5. ✅ Aucune erreur `ERR_CONNECTION_REFUSED` dans la console

---

## 🆘 Toujours des Problèmes ?

### Erreur persiste après redéploiement

1. **Vider le cache browser** : Ctrl + Shift + R
2. **Mode incognito** : Tester dans une fenêtre privée
3. **Vérifier les logs Railway** : Backend et Frontend
4. **Tester le backend directement** : `https://[backend-url]/health`

### WebSocket timeout

C'est **normal** si vous n'avez pas implémenté le handler WebSocket côté backend. Le frontend va réessayer automatiquement.

### CORS error

Assurez-vous que :
- L'URL frontend est exactement celle dans `CORS_ORIGINS` backend
- Pas d'espace dans la liste des origines
- Format : `https://url1.com,https://url2.com` (virgule sans espace)

---

## 📞 Documents de Référence

- `RAILWAY_DEPLOYMENT.md` : Guide complet de déploiement Railway
- `RAILWAY_ENV_VARIABLES.md` : Liste complète des variables d'environnement
- `README.md` : Documentation générale du projet

---

✅ **Problème résolu !** Votre application devrait maintenant fonctionner correctement sur Railway.
