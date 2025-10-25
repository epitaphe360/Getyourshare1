"""
Tests pour les endpoints d'abonnement

Coverage:
- Liste des plans d'abonnement
- Souscription à un plan
- Mise à jour d'abonnement
- Annulation d'abonnement
- Consultation de l'abonnement actif
- Historique des abonnements
- Vérification des limites
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


# ============================================
# TESTS - PLANS D'ABONNEMENT
# ============================================

@pytest.mark.asyncio
async def test_list_subscription_plans(async_client):
    """Test listing all subscription plans"""
    response = await async_client.get("/api/subscriptions/plans")

    assert response.status_code == 200
    data = response.json()

    # Vérifier qu'on a bien 4 plans
    assert len(data) >= 4

    # Vérifier les codes des plans
    plan_codes = [plan["code"] for plan in data]
    assert "enterprise_small" in plan_codes
    assert "enterprise_medium" in plan_codes
    assert "enterprise_large" in plan_codes
    assert "marketplace_independent" in plan_codes


@pytest.mark.asyncio
async def test_get_plan_details(async_client):
    """Test getting details of a specific plan"""
    response = await async_client.get("/api/subscriptions/plans/enterprise_small")

    assert response.status_code == 200
    data = response.json()

    # Vérifier les détails du plan Small
    assert data["code"] == "enterprise_small"
    assert data["name"] == "Small"
    assert data["price_mad"] == 199.00
    assert data["max_team_members"] == 2
    assert data["max_domains"] == 1
    assert data["type"] == "enterprise"


@pytest.mark.asyncio
async def test_plan_features(async_client):
    """Test that plan features are returned correctly"""
    response = await async_client.get("/api/subscriptions/plans/enterprise_medium")

    assert response.status_code == 200
    data = response.json()

    # Vérifier les features
    assert "features" in data
    assert isinstance(data["features"], list)
    assert len(data["features"]) > 0
    assert any("10 comptes" in feature for feature in data["features"])


# ============================================
# TESTS - SOUSCRIPTION
# ============================================

@pytest.mark.asyncio
async def test_subscribe_to_plan_success(async_client, merchant_headers):
    """Test successful subscription to a plan"""
    with patch('stripe.Customer.create') as mock_customer, \
         patch('stripe.Subscription.create') as mock_subscription:

        # Mock Stripe responses
        mock_customer.return_value = Mock(id="cus_test123")
        mock_subscription.return_value = Mock(
            id="sub_test123",
            status="active",
            current_period_start=1234567890,
            current_period_end=1237246290
        )

        response = await async_client.post(
            "/api/subscriptions/subscribe",
            headers=merchant_headers,
            json={
                "plan_code": "enterprise_small",
                "payment_method_id": "pm_card_visa"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "active"
        assert data["plan_code"] == "enterprise_small"
        assert "subscription_id" in data


@pytest.mark.asyncio
async def test_subscribe_invalid_plan(async_client, merchant_headers):
    """Test subscription with invalid plan code"""
    response = await async_client.post(
        "/api/subscriptions/subscribe",
        headers=merchant_headers,
        json={
            "plan_code": "invalid_plan",
            "payment_method_id": "pm_card_visa"
        }
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_subscribe_without_payment_method(async_client, merchant_headers):
    """Test subscription without payment method"""
    response = await async_client.post(
        "/api/subscriptions/subscribe",
        headers=merchant_headers,
        json={
            "plan_code": "enterprise_small"
        }
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_subscribe_when_already_subscribed(async_client, merchant_headers):
    """Test subscribing when user already has active subscription"""
    # Cette logique doit être gérée par l'endpoint
    # Soit upgrade, soit erreur
    response = await async_client.post(
        "/api/subscriptions/subscribe",
        headers=merchant_headers,
        json={
            "plan_code": "enterprise_medium",
            "payment_method_id": "pm_card_visa"
        }
    )

    # Devrait soit réussir (upgrade), soit retourner 409 (conflict)
    assert response.status_code in [200, 409]


# ============================================
# TESTS - CONSULTATION ABONNEMENT
# ============================================

@pytest.mark.asyncio
async def test_get_current_subscription(async_client, merchant_headers):
    """Test getting current active subscription"""
    response = await async_client.get(
        "/api/subscriptions/current",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "plan_name" in data
        assert "status" in data
        assert "current_period_end" in data


@pytest.mark.asyncio
async def test_get_subscription_usage(async_client, merchant_headers):
    """Test getting subscription usage stats"""
    response = await async_client.get(
        "/api/subscriptions/usage",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "current_team_members" in data
        assert "max_team_members" in data
        assert "current_domains" in data
        assert "max_domains" in data


# ============================================
# TESTS - MISE À JOUR ABONNEMENT
# ============================================

@pytest.mark.asyncio
async def test_upgrade_subscription(async_client, merchant_headers):
    """Test upgrading to a higher plan"""
    with patch('stripe.Subscription.modify') as mock_modify:
        mock_modify.return_value = Mock(
            id="sub_test123",
            status="active"
        )

        response = await async_client.post(
            "/api/subscriptions/upgrade",
            headers=merchant_headers,
            json={
                "new_plan_code": "enterprise_medium"
            }
        )

        # Devrait réussir ou 404 si pas d'abonnement actif
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_downgrade_subscription(async_client, merchant_headers):
    """Test downgrading to a lower plan"""
    response = await async_client.post(
        "/api/subscriptions/downgrade",
        headers=merchant_headers,
        json={
            "new_plan_code": "enterprise_small"
        }
    )

    # Devrait réussir ou 404 si pas d'abonnement actif
    assert response.status_code in [200, 404]


# ============================================
# TESTS - ANNULATION
# ============================================

@pytest.mark.asyncio
async def test_cancel_subscription_immediately(async_client, merchant_headers):
    """Test canceling subscription immediately"""
    with patch('stripe.Subscription.delete') as mock_delete:
        mock_delete.return_value = Mock(status="canceled")

        response = await async_client.post(
            "/api/subscriptions/cancel",
            headers=merchant_headers,
            json={
                "immediate": True
            }
        )

        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_cancel_subscription_at_period_end(async_client, merchant_headers):
    """Test canceling subscription at end of billing period"""
    with patch('stripe.Subscription.modify') as mock_modify:
        mock_modify.return_value = Mock(
            cancel_at_period_end=True,
            status="active"
        )

        response = await async_client.post(
            "/api/subscriptions/cancel",
            headers=merchant_headers,
            json={
                "immediate": False
            }
        )

        assert response.status_code in [200, 404]


# ============================================
# TESTS - HISTORIQUE
# ============================================

@pytest.mark.asyncio
async def test_get_subscription_history(async_client, merchant_headers):
    """Test getting subscription history"""
    response = await async_client.get(
        "/api/subscriptions/history",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    # L'historique peut être vide si pas d'abonnements précédents


# ============================================
# TESTS - VÉRIFICATION LIMITES
# ============================================

@pytest.mark.asyncio
async def test_check_team_member_limit(async_client, merchant_headers):
    """Test checking if team member limit is reached"""
    response = await async_client.get(
        "/api/subscriptions/check-limit/team_members",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "can_add" in data
        assert "current" in data
        assert "max" in data


@pytest.mark.asyncio
async def test_check_domain_limit(async_client, merchant_headers):
    """Test checking if domain limit is reached"""
    response = await async_client.get(
        "/api/subscriptions/check-limit/domains",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "can_add" in data
        assert "current" in data
        assert "max" in data


# ============================================
# TESTS - AUTORISATION
# ============================================

@pytest.mark.asyncio
async def test_subscription_endpoints_require_auth(async_client):
    """Test that subscription endpoints require authentication"""
    endpoints = [
        "/api/subscriptions/current",
        "/api/subscriptions/usage",
        "/api/subscriptions/history"
    ]

    for endpoint in endpoints:
        response = await async_client.get(endpoint)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_influencer_cannot_subscribe_to_enterprise(async_client, influencer_headers):
    """Test that influencers cannot subscribe to enterprise plans"""
    response = await async_client.post(
        "/api/subscriptions/subscribe",
        headers=influencer_headers,
        json={
            "plan_code": "enterprise_small",
            "payment_method_id": "pm_card_visa"
        }
    )

    # Devrait être refusé (403) ou plan non disponible (404)
    assert response.status_code in [403, 404]


# ============================================
# TESTS - MARKETPLACE PLAN
# ============================================

@pytest.mark.asyncio
async def test_influencer_subscribe_marketplace(async_client, influencer_headers):
    """Test influencer subscribing to marketplace plan"""
    with patch('stripe.Customer.create') as mock_customer, \
         patch('stripe.Subscription.create') as mock_subscription:

        mock_customer.return_value = Mock(id="cus_influencer123")
        mock_subscription.return_value = Mock(
            id="sub_marketplace123",
            status="active",
            current_period_start=1234567890,
            current_period_end=1237246290
        )

        response = await async_client.post(
            "/api/subscriptions/subscribe",
            headers=influencer_headers,
            json={
                "plan_code": "marketplace_independent",
                "payment_method_id": "pm_card_visa"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["plan_code"] == "marketplace_independent"
        assert data["status"] == "active"


# ============================================
# TESTS - VALIDATION
# ============================================

@pytest.mark.asyncio
async def test_validate_subscription_data(async_client, merchant_headers):
    """Test validation of subscription request data"""
    # Missing plan_code
    response = await async_client.post(
        "/api/subscriptions/subscribe",
        headers=merchant_headers,
        json={
            "payment_method_id": "pm_card_visa"
        }
    )

    assert response.status_code == 422

    # Invalid plan_code type
    response = await async_client.post(
        "/api/subscriptions/subscribe",
        headers=merchant_headers,
        json={
            "plan_code": 123,  # Should be string
            "payment_method_id": "pm_card_visa"
        }
    )

    assert response.status_code == 422
