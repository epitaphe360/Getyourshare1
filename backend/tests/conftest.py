"""
Fixtures et configuration communes pour les tests pytest
"""
import pytest
from unittest.mock import MagicMock, Mock
from datetime import datetime, timedelta
from uuid import uuid4


# ============================================================================
# FIXTURES SUPABASE
# ============================================================================

@pytest.fixture
def mock_supabase():
    """Mock complet du client Supabase"""
    mock = MagicMock()
    
    # Mock RPC calls
    mock.rpc.return_value.execute.return_value.data = {}
    
    # Mock table queries
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.eq.return_value = mock
    mock.insert.return_value = mock
    mock.update.return_value = mock
    mock.delete.return_value = mock
    mock.execute.return_value.data = []
    
    return mock


@pytest.fixture
def mock_supabase_response():
    """Factory pour créer des réponses Supabase mockées"""
    def _create_response(data=None, error=None, count=None):
        response = Mock()
        response.data = data
        response.error = error
        response.count = count
        return response
    return _create_response


# ============================================================================
# FIXTURES DONNÉES DE TEST - USERS
# ============================================================================

@pytest.fixture
def sample_user_id():
    """ID utilisateur de test"""
    return str(uuid4())


@pytest.fixture
def sample_influencer_user(sample_user_id):
    """Données utilisateur influenceur"""
    return {
        "id": sample_user_id,
        "email": "influencer@test.com",
        "username": "testinfluencer",
        "role": "influencer",
        "created_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_merchant_user():
    """Données utilisateur merchant"""
    merchant_id = str(uuid4())
    return {
        "id": merchant_id,
        "email": "merchant@test.com",
        "username": "testmerchant",
        "role": "merchant",
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# FIXTURES DONNÉES DE TEST - INFLUENCERS
# ============================================================================

@pytest.fixture
def sample_influencer_id():
    """ID influenceur de test"""
    return str(uuid4())


@pytest.fixture
def sample_influencer(sample_influencer_id, sample_user_id):
    """Données influenceur complètes"""
    return {
        "id": sample_influencer_id,
        "user_id": sample_user_id,
        "username": "testinfluencer",
        "balance": 150.50,
        "total_earnings": 500.00,
        "total_sales": 25,
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# FIXTURES DONNÉES DE TEST - MERCHANTS
# ============================================================================

@pytest.fixture
def sample_merchant_id():
    """ID merchant de test"""
    return str(uuid4())


@pytest.fixture
def sample_merchant(sample_merchant_id):
    """Données merchant complètes"""
    return {
        "id": sample_merchant_id,
        "user_id": str(uuid4()),
        "business_name": "Test Store",
        "commission_rate": 10.0,
        "total_sales": 100,
        "total_commission_paid": 250.00,
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# FIXTURES DONNÉES DE TEST - PRODUCTS
# ============================================================================

@pytest.fixture
def sample_product_id():
    """ID produit de test"""
    return str(uuid4())


@pytest.fixture
def sample_product(sample_product_id, sample_merchant_id):
    """Données produit complètes"""
    return {
        "id": sample_product_id,
        "merchant_id": sample_merchant_id,
        "name": "Test Product",
        "price": 99.99,
        "commission_rate": 15.0,
        "stock": 100,
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# FIXTURES DONNÉES DE TEST - TRACKABLE LINKS
# ============================================================================

@pytest.fixture
def sample_link_id():
    """ID lien trackable de test"""
    return str(uuid4())


@pytest.fixture
def sample_trackable_link(sample_link_id, sample_influencer_id, sample_product_id):
    """Données lien trackable complet"""
    return {
        "id": sample_link_id,
        "influencer_id": sample_influencer_id,
        "product_id": sample_product_id,
        "short_code": "ABC123",
        "original_url": "https://example.com/product/123",
        "clicks": 50,
        "conversions": 5,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# FIXTURES DONNÉES DE TEST - SALES
# ============================================================================

@pytest.fixture
def sample_sale_id():
    """ID vente de test"""
    return str(uuid4())


@pytest.fixture
def sample_sale(sample_sale_id, sample_link_id, sample_influencer_id, sample_merchant_id, sample_product_id):
    """Données vente complète"""
    return {
        "id": sample_sale_id,
        "link_id": sample_link_id,
        "influencer_id": sample_influencer_id,
        "merchant_id": sample_merchant_id,
        "product_id": sample_product_id,
        "amount": 99.99,
        "influencer_commission": 14.99,
        "platform_commission": 5.00,
        "merchant_net_amount": 80.00,
        "currency": "EUR",
        "status": "completed",
        "customer_email": "customer@test.com",
        "order_id": "ORDER-123",
        "created_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_sale_request():
    """Requête de création de vente"""
    return {
        "link_id": str(uuid4()),
        "amount": 99.99,
        "currency": "EUR",
        "customer_email": "customer@test.com",
        "order_id": "ORDER-123",
        "customer_name": "John Doe",
        "customer_phone": "+33612345678"
    }


# ============================================================================
# FIXTURES DONNÉES DE TEST - COMMISSIONS
# ============================================================================

@pytest.fixture
def sample_commission_id():
    """ID commission de test"""
    return str(uuid4())


@pytest.fixture
def sample_commission(sample_commission_id, sample_sale_id, sample_influencer_id):
    """Données commission complète"""
    return {
        "id": sample_commission_id,
        "sale_id": sample_sale_id,
        "influencer_id": sample_influencer_id,
        "amount": 14.99,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_at": None
    }


@pytest.fixture
def sample_commission_approved(sample_commission):
    """Commission approuvée"""
    commission = sample_commission.copy()
    commission["status"] = "approved"
    commission["approved_at"] = datetime.now().isoformat()
    return commission


@pytest.fixture
def sample_commission_paid(sample_commission_approved):
    """Commission payée"""
    commission = sample_commission_approved.copy()
    commission["status"] = "paid"
    commission["paid_at"] = datetime.now().isoformat()
    return commission


# ============================================================================
# FIXTURES UTILITAIRES
# ============================================================================

@pytest.fixture
def mock_datetime():
    """Mock pour datetime.now()"""
    return datetime(2025, 10, 27, 12, 0, 0)


@pytest.fixture
def sample_uuid():
    """UUID de test fixe"""
    return "12345678-1234-5678-1234-567812345678"


@pytest.fixture
def mock_postgres_error():
    """Factory pour créer des erreurs PostgreSQL mockées"""
    def _create_error(code, message, details=None):
        error = Mock()
        error.code = code
        error.message = message
        error.details = details
        return error
    return _create_error


# ============================================================================
# FIXTURES PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture(autouse=True)
def reset_mocks():
    """Réinitialise tous les mocks après chaque test"""
    yield
    # Cleanup automatique par pytest


@pytest.fixture
def caplog_info(caplog):
    """Capture les logs de niveau INFO et supérieur"""
    import logging
    caplog.set_level(logging.INFO)
    return caplog
