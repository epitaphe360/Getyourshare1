# Rapport d'Audit Logique - Projet Getyourshare1

**Date de l'audit :** 30 Octobre 2025
**Auteur :** Manus AI

Ce rapport présente les résultats de l'audit logique du code source du dépôt `epitaphe360/Getyourshare1`, réalisé après la correction des bugs statiques et des vulnérabilités de dépendances. L'objectif est d'identifier les failles de sécurité et les bugs fonctionnels qui ne sont pas détectés par les outils d'analyse statique.

---

## 1. Résumé des Vulnérabilités Logiques

L'audit logique a identifié trois domaines de vulnérabilité potentielle, principalement liés à l'**autorisation** et à la **validation des données** dans le backend.

| Domaine | Type de Vulnérabilité | Sévérité Estimée | Description |
| :--- | :--- | :--- | :--- |
| **Backend (Python)** | **Bypass d'Autorisation (IDOR/Escalade de Privilèges)** | **Élevée** | Risque que les utilisateurs non-administrateurs ou non-propriétaires puissent modifier des paramètres critiques (`company_settings`, `smtp_settings`, etc.) ou accéder à des données sensibles sans vérification de rôle adéquate. |
| **Backend (Python)** | **Injection SQL (via RPC)** | **Moyenne** | Le code utilise des fonctions RPC (`.rpc()`) qui exécutent du SQL côté base de données. Si l'implémentation de ces fonctions n'est pas sécurisée, une injection SQL est possible. |
| **Frontend (React)** | **Validation Côté Client Uniquement** | **Moyenne** | L'absence de schémas de validation clairs côté serveur pour les entrées utilisateur (ex: `CreateCampaign`, `CreateProduct`) pourrait permettre l'insertion de données malformées ou dangereuses. |

---

## 2. Analyse Détaillée du Backend (Python/FastAPI)

Le backend utilise FastAPI et le client Python pour Supabase, qui interagit avec la base de données via PostgREST.

### 2.1. Vulnérabilité d'Autorisation (Escalade de Privilèges / IDOR)

Le point le plus critique concerne la gestion des rôles et des permissions.

**Problème :**
Plusieurs endpoints de modification de paramètres critiques (ex: `/api/settings/company`, `/api/settings/affiliate`) utilisent la fonction `get_current_user(request)` pour identifier l'utilisateur. Cette fonction récupère l'ID de l'utilisateur à partir du jeton JWT.

*   **Exemple :** L'endpoint `update_company_settings` dans `server.py` utilise l'ID de l'utilisateur pour mettre à jour les paramètres de l'entreprise :
    ```python
    user_id = get_current_user(request).get("id")
    # ...
    check_response = supabase.table("company_settings").select("id").eq("user_id", user_id).execute()
    # ...
    ```
    Si un utilisateur avec le rôle `influencer` peut appeler cet endpoint, il pourrait potentiellement modifier des paramètres qui ne devraient être accessibles qu'aux `merchant` ou `admin`. Bien que la requête Supabase filtre par `user_id`, l'absence de vérification explicite du rôle expose l'application à des **failles logiques d'autorisation**.

**Recommandation :**
Chaque endpoint d'écriture ou d'accès à des données sensibles doit implémenter une vérification de rôle stricte. Par exemple, pour les paramètres d'entreprise, l'utilisateur doit avoir le rôle `merchant` ou `admin`.

### 2.2. Vulnérabilité d'Injection SQL (via Fonctions RPC)

Le code utilise des appels de fonctions stockées (RPC) pour des opérations complexes.

| Fonction RPC | Fichier d'Appel | Description | Risque |
| :--- | :--- | :--- | :--- |
| `create_sale_transaction` | `advanced_helpers.py`, `services/sales/service.py` | Crée une vente et les commissions associées. | **Moyen** : Si les paramètres d'entrée (`p_link_id`, `p_product_id`, etc.) ne sont pas utilisés comme variables de fonction sécurisées dans le SQL de la fonction stockée, une injection est possible. |
| `approve_payout_transaction` | `advanced_helpers.py`, `services/payments/service.py` | Approuve un paiement. | **Moyen** : Même risque que ci-dessus. |
| `exec_sql` | `create_smtp_table.py` | Exécute une requête SQL brute. | **Faible** : Utilisé uniquement avec une chaîne SQL statique. |

**Recommandation :**
Bien que les appels soient sécurisés au niveau de l'API Supabase, l'implémentation des fonctions stockées côté base de données doit être auditée pour s'assurer qu'elles utilisent le mécanisme de **requête paramétrée** et non la concaténation de chaînes de caractères.

---

## 3. Analyse Détaillée du Frontend (React/JavaScript)

Le frontend est construit avec React.

### 3.1. Cross-Site Scripting (XSS) et CSRF

*   **XSS :** Aucune utilisation de `dangerouslySetInnerHTML` ou de manipulation directe du DOM avec `.innerHTML` n'a été trouvée. React offre une protection native contre le XSS. **(Non Vulnérable)**
*   **CSRF :** Le backend utilise des jetons JWT dans l'en-tête `Authorization` (Bearer Token), ce qui est la méthode recommandée pour les API sans état et protège efficacement contre le CSRF. **(Non Vulnérable)**

### 3.2. Bugs Logiques Fonctionnels (Validation des Données)

**Problème :**
Le frontend permet la saisie de données utilisateur pour la création et la modification de ressources (campagnes, produits, etc.).

*   **Exemple :** Dans `CreateProduct.js`, les données sont envoyées au backend via `api.post('/api/products', {...})`.
    ```javascript
    // Frontend
    const response = await api.post('/api/products', {
      ...formData,
      price: parseFloat(formData.price),
      stock: parseInt(formData.stock),
      commission_rate: parseFloat(formData.commission_rate)
    });
    ```
    Si la validation des types de données (ex: `price` doit être un nombre positif) est effectuée uniquement côté client (JavaScript), un attaquant peut facilement contourner cette validation et envoyer des valeurs invalides (ex: chaînes de caractères, nombres négatifs) directement à l'API.

**Recommandation :**
Le backend utilise des schémas Pydantic pour la validation des données d'entrée. Il est impératif de s'assurer que ces schémas sont correctement définis pour **tous** les endpoints d'écriture (`POST`, `PUT`) et qu'ils incluent des contraintes de type, de format et de valeur (ex: `Field(..., gt=0)` pour les nombres positifs).

---

## 4. Conclusion et Prochaines Étapes

L'audit logique confirme que les problèmes les plus critiques concernent l'**Autorisation**.

**Prochaines Étapes Recommandées :**

1.  **Implémentation d'un Décorateur de Rôle :** Développer un décorateur FastAPI pour vérifier le rôle de l'utilisateur (`@require_role("merchant")`) et l'appliquer à tous les endpoints sensibles dans `server.py` et les autres routeurs.
2.  **Audit des Fonctions RPC :** Vérifier l'implémentation SQL des fonctions stockées `create_sale_transaction` et `approve_payout_transaction` pour confirmer l'utilisation de requêtes paramétrées.
3.  **Vérification des Schémas Pydantic :** S'assurer que tous les modèles Pydantic d'entrée (`schemas.py` ou définis dans les endpoints) appliquent des contraintes de validation strictes pour prévenir l'insertion de données invalides.
