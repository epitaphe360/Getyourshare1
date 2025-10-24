"""
Fixtures pytest communes pour tous les tests

Fournit:
- Clients de test FastAPI
- Données de test (users, products, etc.)
- Mocks pour APIs externes
- DB transactions
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
from datetime import datetime, timedelta

# Mock environment variables pour tests
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/shareyoursales_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["JWT_SECRET"] = "test-secret-key-change-in-production"


# ============================================
# CONFIGURATION ASYNCIO
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================
# CLIENTS HTTP
# ============================================

@pytest.fixture
def client() -> Generator:
    """
    Client de test FastAPI synchrone

    Usage:
        def test_endpoint(client):
            response = client.get("/api/users")
            assert response.status_code == 200
    """
    from server import app  # Import ici pour éviter circular import

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator:
    """
    Client de test FastAPI asynchrone

    Usage:
        async def test_endpoint(async_client):
            response = await async_client.get("/api/users")
            assert response.status_code == 200
    """
    from server import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================
# DONNÉES DE TEST - USERS
# ============================================

@pytest.fixture
def test_influencer():
    """Influenceur de test"""
    return {
        "id": "test-influencer-123",
        "email": "influencer@test.com",
        "full_name": "Test Influencer",
        "role": "influencer",
        "is_verified": True,
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def test_merchant():
    """Marchand de test"""
    return {
        "id": "test-merchant-456",
        "email": "merchant@test.com",
        "full_name": "Test Merchant",
        "role": "merchant",
        "company_name": "Test Company",
        "is_verified": True,
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def test_admin():
    """Admin de test"""
    return {
        "id": "test-admin-789",
        "email": "admin@test.com",
        "full_name": "Test Admin",
        "role": "admin",
        "is_verified": True,
        "created_at": datetime.utcnow()
    }


# ============================================
# TOKENS JWT
# ============================================

@pytest.fixture
def influencer_token(test_influencer):
    """JWT token pour influenceur"""
    from auth import create_access_token
    return create_access_token(data={"sub": test_influencer["id"], "role": test_influencer["role"]})


@pytest.fixture
def merchant_token(test_merchant):
    """JWT token pour marchand"""
    from auth import create_access_token
    return create_access_token(data={"sub": test_merchant["id"], "role": test_merchant["role"]})


@pytest.fixture
def admin_token(test_admin):
    """JWT token pour admin"""
    from auth import create_access_token
    return create_access_token(data={"sub": test_admin["id"], "role": test_admin["role"]})


# ============================================
# HEADERS HTTP
# ============================================

@pytest.fixture
def influencer_headers(influencer_token):
    """Headers HTTP avec token influenceur"""
    return {"Authorization": f"Bearer {influencer_token}"}


@pytest.fixture
def merchant_headers(merchant_token):
    """Headers HTTP avec token marchand"""
    return {"Authorization": f"Bearer {merchant_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Headers HTTP avec token admin"""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================
# DONNÉES DE TEST - SOCIAL MEDIA
# ============================================

@pytest.fixture
def test_instagram_connection():
    """Connexion Instagram de test"""
    return {
        "id": "conn-instagram-123",
        "user_id": "test-influencer-123",
        "platform": "instagram",
        "platform_user_id": "17841400000000",
        "platform_username": "test_influencer",
        "access_token_encrypted": "encrypted_token_here",
        "connection_status": "active",
        "token_expires_at": datetime.utcnow() + timedelta(days=60),
        "connected_at": datetime.utcnow(),
        "last_synced_at": datetime.utcnow()
    }


@pytest.fixture
def test_social_stats():
    """Statistiques sociales de test"""
    return {
        "connection_id": "conn-instagram-123",
        "user_id": "test-influencer-123",
        "platform": "instagram",
        "followers_count": 25000,
        "following_count": 1500,
        "total_posts": 150,
        "engagement_rate": 4.2,
        "average_likes_per_post": 1050.5,
        "average_comments_per_post": 85.3,
        "followers_growth": 250,
        "synced_at": datetime.utcnow()
    }


# ============================================
# DONNÉES DE TEST - AFFILIATION
# ============================================

@pytest.fixture
def test_product():
    """Produit de test"""
    return {
        "id": "product-123",
        "merchant_id": "test-merchant-456",
        "name": "Test Product",
        "description": "A test product",
        "price": 299.99,
        "commission_rate": 15.0,
        "is_active": True,
        "category": "electronics",
        "image_url": "https://example.com/product.jpg"
    }


@pytest.fixture
def test_affiliation_request():
    """Demande d'affiliation de test"""
    return {
        "id": "request-123",
        "influencer_id": "test-influencer-123",
        "product_id": "product-123",
        "merchant_id": "test-merchant-456",
        "status": "pending",
        "influencer_message": "Je souhaite promouvoir ce produit",
        "influencer_followers": 25000,
        "influencer_engagement_rate": 4.2,
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def test_trackable_link():
    """Lien trackable de test"""
    return {
        "id": "link-123",
        "unique_code": "ABC123XYZ",
        "influencer_id": "test-influencer-123",
        "product_id": "product-123",
        "merchant_id": "test-merchant-456",
        "short_url": "shareyoursales.ma/r/ABC123XYZ",
        "clicks": 150,
        "conversions": 12,
        "revenue": 3599.88,
        "commission": 539.98,
        "is_active": True,
        "created_at": datetime.utcnow()
    }


# ============================================
# MOCKS - APIS EXTERNES
# ============================================

@pytest.fixture
def mock_instagram_api(monkeypatch):
    """Mock Instagram Graph API"""
    import httpx

    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            def json(self):
                url = args[0] if args else kwargs.get('url', '')

                # Mock access token exchange
                if 'oauth/access_token' in url:
                    return {
                        "access_token": "long_lived_token_mock",
                        "token_type": "bearer",
                        "expires_in": 5184000  # 60 days
                    }

                # Mock user info
                if '/me' in url or 'instagram_user_id' in url:
                    return {
                        "id": "17841400000000",
                        "username": "test_influencer",
                        "account_type": "BUSINESS",
                        "followers_count": 25000
                    }

                # Mock insights
                if '/insights' in url:
                    return {
                        "data": [
                            {"name": "follower_count", "values": [{"value": 25000}]},
                            {"name": "reach", "values": [{"value": 15000}]},
                            {"name": "impressions", "values": [{"value": 30000}]}
                        ]
                    }

                # Mock media
                if '/media' in url:
                    return {
                        "data": [
                            {
                                "id": "post123",
                                "like_count": 1050,
                                "comments_count": 85,
                                "media_type": "IMAGE"
                            }
                        ]
                    }

                return {}

        return MockResponse()

    async def mock_post(*args, **kwargs):
        return await mock_get(*args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)


@pytest.fixture
def mock_tiktok_api(monkeypatch):
    """Mock TikTok Creator API"""
    import httpx

    async def mock_post(*args, **kwargs):
        class MockResponse:
            status_code = 200

            def json(self):
                url = args[0] if args else kwargs.get('url', '')

                # Mock token exchange
                if 'oauth/access_token' in url:
                    return {
                        "access_token": "tiktok_access_token_mock",
                        "open_id": "tiktok_user_123",
                        "expires_in": 86400
                    }

                # Mock user info
                if 'user/info' in url:
                    return {
                        "data": {
                            "user": {
                                "open_id": "tiktok_user_123",
                                "union_id": "union_123",
                                "display_name": "Test TikToker",
                                "avatar_url": "https://example.com/avatar.jpg",
                                "follower_count": 50000,
                                "following_count": 500,
                                "likes_count": 500000,
                                "video_count": 100
                            }
                        }
                    }

                # Mock videos
                if 'video/list' in url:
                    return {
                        "data": {
                            "videos": [
                                {
                                    "id": "video123",
                                    "like_count": 5000,
                                    "comment_count": 500,
                                    "share_count": 200,
                                    "view_count": 100000
                                }
                            ]
                        }
                    }

                return {}

        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)


# ============================================
# DATABASE FIXTURES
# ============================================

@pytest.fixture(scope="function")
def db_session():
    """
    Session de base de données pour tests

    Utilise une transaction qui est rollback à la fin de chaque test
    """
    # TODO: Implémenter avec SQLAlchemy ou asyncpg
    # Pour l'instant, retourner None
    yield None


@pytest.fixture(autouse=True)
def reset_db(db_session):
    """
    Réinitialise la DB avant chaque test

    Utilise transactions pour isolation
    """
    # TODO: Implémenter reset
    yield
    # Rollback transaction


# ============================================
# REDIS FIXTURES
# ============================================

@pytest.fixture
def redis_client():
    """Client Redis pour tests"""
    import redis
    client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

    yield client

    # Nettoyer après le test
    client.flushdb()


# ============================================
# HELPERS
# ============================================

@pytest.fixture
def assert_valid_uuid():
    """Helper pour valider les UUIDs"""
    import uuid

    def _assert_valid_uuid(uuid_string):
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False

    return _assert_valid_uuid


@pytest.fixture
def assert_valid_iso_datetime():
    """Helper pour valider les dates ISO"""
    from datetime import datetime

    def _assert_valid_iso_datetime(datetime_string):
        try:
            datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False

    return _assert_valid_iso_datetime
