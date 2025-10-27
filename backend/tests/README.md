# 🧪 Tests Unitaires - ShareYourSales Backend

Infrastructure de tests complète pour les modules backend avec pytest.

---

## 📁 Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Fixtures communes (mocks, données de test)
├── test_sales.py            # Tests module Sales (25+ tests)
└── test_payments.py         # Tests module Payments (30+ tests)
```

---

## 🚀 Installation

### Installer les dépendances de test
```bash
cd backend
pip install -r requirements-dev.txt
```

---

## ▶️ Exécution des Tests

### Tous les tests
```bash
pytest
```

### Tests d'un module spécifique
```bash
# Tests Sales seulement
pytest tests/test_sales.py

# Tests Payments seulement
pytest tests/test_payments.py
```

### Tests avec marqueurs
```bash
# Tests unitaires seulement
pytest -m unit

# Tests Sales
pytest -m sales

# Tests Payments
pytest -m payments
```

### Coverage
```bash
# Rapport coverage dans le terminal
pytest --cov=services --cov-report=term-missing

# Rapport HTML
pytest --cov=services --cov-report=html
# Ouvrir htmlcov/index.html dans le navigateur
```

### Mode verbeux
```bash
pytest -v
```

### Tests spécifiques
```bash
# Test unique par nom
pytest tests/test_sales.py::test_create_sale_success

# Tests contenant un pattern
pytest -k "create_sale"
```

---

## 📊 Configuration Coverage

Objectif : **80% de couverture minimum**

Configuration dans `pytest.ini` :
```ini
[pytest]
addopts = 
    --cov=services
    --cov-report=term-missing
    --cov-fail-under=80
```

Le build échouera si la couverture descend sous 80%.

---

## 🧩 Fixtures Disponibles

### Fixtures Supabase
- `mock_supabase` : Mock complet du client Supabase
- `mock_supabase_response` : Factory pour réponses mockées
- `mock_postgres_error` : Factory pour erreurs PostgreSQL

### Fixtures Données de Test

#### Users
- `sample_user_id`
- `sample_influencer_user`
- `sample_merchant_user`

#### Influencers
- `sample_influencer_id`
- `sample_influencer`

#### Merchants
- `sample_merchant_id`
- `sample_merchant`

#### Products
- `sample_product_id`
- `sample_product`

#### Trackable Links
- `sample_link_id`
- `sample_trackable_link`

#### Sales
- `sample_sale_id`
- `sample_sale`
- `sample_sale_request`

#### Commissions
- `sample_commission_id`
- `sample_commission`
- `sample_commission_approved`
- `sample_commission_paid`

### Fixtures Utilitaires
- `mock_datetime` : Date fixe pour tests
- `sample_uuid` : UUID fixe

---

## ✅ Tests Implémentés

### test_sales.py (25+ tests)

#### SalesService.create_sale
- ✅ Création réussie
- ✅ Lien invalide
- ✅ Montant négatif
- ✅ Paramètres manquants
- ✅ Erreur base de données
- ✅ Tous paramètres optionnels

#### SalesService.get_sale_by_id
- ✅ Récupération réussie
- ✅ Vente non trouvée
- ✅ UUID invalide

#### SalesService.get_sales_by_influencer
- ✅ Liste complète
- ✅ Filtrage par statut
- ✅ Résultat vide
- ✅ Grand dataset (100+ résultats)

#### SalesService.get_sales_by_merchant
- ✅ Liste complète
- ✅ Pagination

#### SalesService.update_sale_status
- ✅ Mise à jour réussie
- ✅ Statut invalide
- ✅ Vente non trouvée

#### Edge Cases
- ✅ Création concurrente
- ✅ Large dataset

---

### test_payments.py (30+ tests)

#### PaymentsService.approve_commission
- ✅ Approbation réussie
- ✅ Déjà approuvée
- ✅ Commission inexistante
- ✅ UUID invalide

#### PaymentsService.pay_commission
- ✅ Paiement réussi
- ✅ Non approuvée (erreur)

#### PaymentsService.reject_commission
- ✅ Rejet réussi
- ✅ Déjà payée (erreur)

#### PaymentsService.get_commission_by_id
- ✅ Récupération réussie
- ✅ Commission non trouvée

#### PaymentsService.get_commissions_by_status
- ✅ Liste complète
- ✅ Résultat vide
- ✅ Statut invalide

#### PaymentsService.get_commissions_by_influencer
- ✅ Liste complète
- ✅ Filtrage par statut

#### PaymentsService.get_pending_commissions_total
- ✅ Total calculé
- ✅ Total zéro

#### PaymentsService.get_approved_commissions_total
- ✅ Total calculé

#### PaymentsService.batch_approve_commissions
- ✅ Approbation en lot réussie
- ✅ Échecs partiels
- ✅ Liste vide
- ✅ Grand lot (100+ commissions)

#### Edge Cases
- ✅ Transitions de statut
- ✅ Mises à jour concurrentes
- ✅ Résumé complet

---

## 🎯 Bonnes Pratiques

### 1. Utiliser les fixtures
```python
def test_create_sale(mock_supabase, sample_sale_request):
    service = SalesService(mock_supabase)
    result = service.create_sale(**sample_sale_request)
    assert result is not None
```

### 2. Mocker les appels Supabase
```python
mock_supabase.rpc.return_value.execute.return_value.data = {"id": "123"}
```

### 3. Tester les cas d'erreur
```python
with pytest.raises(ValueError, match="Invalid link"):
    service.create_sale(invalid_data)
```

### 4. Utiliser les marqueurs
```python
@pytest.mark.unit
@pytest.mark.sales
def test_something():
    pass
```

### 5. Assertions claires
```python
assert result == expected_value
assert len(results) == 5
assert result["status"] == "approved"
```

---

## 🐛 Debugging

### Afficher les prints
```bash
pytest -s
```

### Mode verbeux avec traceback complet
```bash
pytest -vv --tb=long
```

### Arrêter au premier échec
```bash
pytest -x
```

### Ré-exécuter les tests échoués
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

### Profiling
```bash
pytest --durations=10  # Top 10 tests les plus lents
```

---

## 📈 Métriques Actuelles

| Métrique | Valeur |
|----------|--------|
| Tests totaux | 55+ |
| Coverage | > 80% |
| Modules testés | Sales, Payments |
| Fixtures | 25+ |
| Marqueurs | 6 |

---

## 🔄 CI/CD Integration

Les tests sont automatiquement exécutés dans le pipeline CI/CD :

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: pytest --cov=services --cov-report=xml
```

---

## 📚 Ressources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)

---

## 🚧 Prochaines Étapes

- [ ] Tests du module `affiliation`
- [ ] Tests d'intégration avec Supabase réel
- [ ] Tests de performance
- [ ] Tests E2E avec frontend

---

**Auteur** : GitHub Copilot  
**Date** : 27 octobre 2025  
**Version** : 1.0
