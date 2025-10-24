# 🧪 Tests ShareYourSales

Suite de tests complète pour assurer la qualité et la sécurité de la plateforme.

## 📊 Coverage Actuel

| Catégorie | Coverage | Statut |
|-----------|----------|--------|
| Backend Services | 80%+ | ✅ |
| API Endpoints | 75%+ | ✅ |
| Sécurité | 90%+ | ✅ |
| Frontend | 0% | ⏳ TODO |
| E2E | 0% | ⏳ TODO |

## 🚀 Installation

```bash
# Installer les dépendances de test
pip install -r requirements-dev.txt

# Installer les dépendances principales
pip install -r requirements.txt
```

## 🏃 Exécution des Tests

### Tous les tests

```bash
pytest
```

### Tests unitaires uniquement

```bash
pytest -m unit
```

### Tests d'intégration

```bash
pytest -m integration
```

### Tests de sécurité

```bash
pytest -m security
```

### Tests lents (exclure)

```bash
pytest -m "not slow"
```

### Avec coverage

```bash
pytest --cov=backend --cov-report=html
# Ouvrir htmlcov/index.html pour voir le rapport
```

### Tests parallèles (plus rapide)

```bash
pytest -n auto  # Utilise tous les CPU
pytest -n 4     # Utilise 4 workers
```

### Tests spécifiques

```bash
# Un fichier
pytest tests/test_social_media_service.py

# Une fonction
pytest tests/test_social_media_service.py::test_connect_instagram_success

# Par pattern
pytest -k "instagram"
```

### Mode verbose

```bash
pytest -v  # Verbose
pytest -vv # Très verbose
pytest -s  # Afficher les prints
```

## 📝 Structure des Tests

```
tests/
├── conftest.py                          # Fixtures communes
├── test_social_media_service.py         # Tests unitaires services
├── test_social_media_endpoints.py       # Tests intégration API
├── test_ai_bot_service.py               # Tests bot IA
├── test_security.py                     # Tests sécurité
├── test_affiliation_requests.py         # Tests affiliation
├── test_tracking_service.py             # Tests tracking
└── README.md                            # Ce fichier
```

## 🎯 Types de Tests

### 1. Tests Unitaires (`@pytest.mark.unit`)

Testent des fonctions/méthodes individuelles en isolation.

```python
@pytest.mark.unit
async def test_connect_instagram_success(mock_instagram_api):
    service = SocialMediaService()
    result = await service.connect_instagram(...)
    assert result is not None
```

### 2. Tests d'Intégration (`@pytest.mark.integration`)

Testent l'interaction entre composants (API + Service + DB).

```python
@pytest.mark.integration
def test_connect_instagram_endpoint(client, influencer_headers):
    response = client.post("/api/social-media/connect/instagram", ...)
    assert response.status_code == 201
```

### 3. Tests de Sécurité (`@pytest.mark.security`)

Vérifient la sécurité (authentification, autorisation, injections, etc.).

```python
@pytest.mark.security
def test_sql_injection_prevention(client):
    malicious = "'; DROP TABLE users; --"
    response = client.get(f"/api/users?name={malicious}")
    assert response.status_code in [200, 422]
```

### 4. Tests E2E (`@pytest.mark.e2e`)

Testent des workflows complets du point de vue utilisateur.

```python
@pytest.mark.e2e
def test_complete_affiliation_workflow(client):
    # 1. Influencer requests affiliation
    # 2. Merchant approves
    # 3. Link is generated
    # 4. Click is tracked
    # 5. Sale is recorded
    # 6. Commission is calculated
```

## 🔧 Configuration

### pytest.ini

Fichier de configuration principal. Définit:
- Chemins de tests
- Markers personnalisés
- Options par défaut
- Coverage settings

### Fixtures

Définies dans `conftest.py`:
- `client` - Client HTTP synchrone
- `async_client` - Client HTTP asynchrone
- `influencer_headers` - Headers avec token influenceur
- `merchant_headers` - Headers avec token marchand
- `mock_instagram_api` - Mock Instagram API
- `mock_tiktok_api` - Mock TikTok API
- Et bien d'autres...

## 📊 Générer un Rapport de Coverage

```bash
# Générer rapport HTML
pytest --cov=backend --cov-report=html

# Ouvrir dans le navigateur
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Rapport dans le terminal
pytest --cov=backend --cov-report=term-missing

# Échouer si coverage < 80%
pytest --cov=backend --cov-fail-under=80
```

## 🐛 Debugging Tests

### Utiliser pdb

```python
def test_something():
    import pdb; pdb.set_trace()
    # Code de test
```

### Utiliser pytest -s

```bash
pytest -s  # Affiche les prints
```

### Exécuter un seul test

```bash
pytest tests/test_file.py::test_function -v
```

## 🚦 CI/CD

Les tests sont exécutés automatiquement sur chaque push via GitHub Actions.

Voir `.github/workflows/tests.yml`

## ✅ Checklist avant commit

- [ ] Tous les tests passent : `pytest`
- [ ] Coverage > 80% : `pytest --cov --cov-fail-under=80`
- [ ] Pas de warnings : `pytest --strict-warnings`
- [ ] Code formaté : `black backend/`
- [ ] Imports triés : `isort backend/`
- [ ] Linting : `flake8 backend/`
- [ ] Type checking : `mypy backend/`
- [ ] Security check : `bandit -r backend/`

## 📚 Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

## 🎓 Bonnes Pratiques

### 1. Nommer les tests clairement

```python
# ✅ Bon
def test_connect_instagram_with_invalid_token_raises_error():
    ...

# ❌ Mauvais
def test_instagram():
    ...
```

### 2. Un test = une assertion principale

```python
# ✅ Bon
def test_user_creation():
    user = create_user(...)
    assert user.id is not None

def test_user_email_validation():
    with pytest.raises(ValueError):
        create_user(email="invalid")

# ❌ Mauvais (trop d'assertions)
def test_user():
    user = create_user(...)
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_active == True
    # ...
```

### 3. Utiliser fixtures pour DRY

```python
@pytest.fixture
def sample_user():
    return {"email": "test@example.com", "name": "Test"}

def test_user_creation(sample_user):
    user = create_user(**sample_user)
    assert user.email == sample_user["email"]
```

### 4. Mock les APIs externes

```python
@pytest.fixture
def mock_instagram_api(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(200, {"followers": 1000})

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
```

### 5. Tester les edge cases

```python
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_empty_list():
    assert process_list([]) == []

def test_very_large_number():
    assert process(10**100) == expected_value
```

## 🔐 Tests de Sécurité

Vérifications critiques:

✅ SQL Injection
✅ XSS
✅ CSRF
✅ Authentication
✅ Authorization (RBAC)
✅ Rate Limiting
✅ Encryption
✅ Input Validation
✅ File Upload Security
✅ Security Headers

## 🤝 Contribution

Pour ajouter de nouveaux tests:

1. Créer un fichier `test_*.py`
2. Importer fixtures depuis `conftest.py`
3. Ajouter markers appropriés (`@pytest.mark.unit`, etc.)
4. Exécuter : `pytest tests/test_new_file.py`
5. Vérifier coverage : `pytest --cov`

## 📞 Support

Questions sur les tests? Contacter l'équipe technique.
