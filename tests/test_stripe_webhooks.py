"""
Tests pour les webhooks Stripe

Coverage:
- Validation de signature Stripe
- Événement invoice.payment_succeeded
- Événement invoice.payment_failed
- Événement customer.subscription.created
- Événement customer.subscription.updated
- Événement customer.subscription.deleted
- Gestion des erreurs
"""

import pytest
import json
import time
import hmac
import hashlib
from unittest.mock import Mock, patch


# ============================================
# HELPERS
# ============================================

def generate_stripe_signature(payload: str, secret: str) -> str:
    """Generate Stripe webhook signature for testing"""
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


# ============================================
# TESTS - VALIDATION SIGNATURE
# ============================================

@pytest.mark.asyncio
async def test_webhook_valid_signature(async_client):
    """Test webhook with valid Stripe signature"""
    payload = json.dumps({
        "id": "evt_test_123",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_test_123",
                "customer": "cus_test_123",
                "subscription": "sub_test_123"
            }
        }
    })

    secret = "whsec_test_secret"
    signature = generate_stripe_signature(payload, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        # Devrait passer la validation
        assert response.status_code in [200, 204]


@pytest.mark.asyncio
async def test_webhook_invalid_signature(async_client):
    """Test webhook with invalid signature"""
    payload = json.dumps({
        "id": "evt_test_123",
        "type": "invoice.payment_succeeded"
    })

    response = await async_client.post(
        "/api/stripe/webhook",
        content=payload,
        headers={
            "Stripe-Signature": "invalid_signature",
            "Content-Type": "application/json"
        }
    )

    # Devrait rejeter la signature invalide
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_missing_signature(async_client):
    """Test webhook without signature header"""
    payload = json.dumps({
        "id": "evt_test_123",
        "type": "invoice.payment_succeeded"
    })

    response = await async_client.post(
        "/api/stripe/webhook",
        content=payload,
        headers={"Content-Type": "application/json"}
    )

    # Devrait rejeter sans signature
    assert response.status_code == 400


# ============================================
# TESTS - PAIEMENT RÉUSSI
# ============================================

@pytest.mark.asyncio
async def test_invoice_payment_succeeded(async_client):
    """Test handling successful invoice payment"""
    payload = {
        "id": "evt_payment_succeeded_123",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_123",
                "customer": "cus_123",
                "subscription": "sub_123",
                "amount_paid": 19900,  # 199.00 MAD en cents
                "currency": "mad",
                "status": "paid"
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]


# ============================================
# TESTS - PAIEMENT ÉCHOUÉ
# ============================================

@pytest.mark.asyncio
async def test_invoice_payment_failed(async_client):
    """Test handling failed invoice payment"""
    payload = {
        "id": "evt_payment_failed_123",
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "id": "in_failed_123",
                "customer": "cus_123",
                "subscription": "sub_123",
                "amount_due": 19900,
                "attempt_count": 1,
                "next_payment_attempt": int(time.time()) + 86400
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]


# ============================================
# TESTS - ABONNEMENT CRÉÉ
# ============================================

@pytest.mark.asyncio
async def test_subscription_created(async_client):
    """Test handling subscription.created event"""
    payload = {
        "id": "evt_sub_created_123",
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_new_123",
                "customer": "cus_123",
                "status": "active",
                "plan": {
                    "id": "price_enterprise_small",
                    "amount": 19900,
                    "currency": "mad"
                },
                "current_period_start": int(time.time()),
                "current_period_end": int(time.time()) + 2592000  # +30 jours
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]


# ============================================
# TESTS - ABONNEMENT MIS À JOUR
# ============================================

@pytest.mark.asyncio
async def test_subscription_updated(async_client):
    """Test handling subscription.updated event"""
    payload = {
        "id": "evt_sub_updated_123",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "active",
                "plan": {
                    "id": "price_enterprise_medium",  # Upgrade
                    "amount": 49900,
                    "currency": "mad"
                },
                "current_period_start": int(time.time()),
                "current_period_end": int(time.time()) + 2592000
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]


# ============================================
# TESTS - ABONNEMENT ANNULÉ/SUPPRIMÉ
# ============================================

@pytest.mark.asyncio
async def test_subscription_deleted(async_client):
    """Test handling subscription.deleted event"""
    payload = {
        "id": "evt_sub_deleted_123",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "canceled",
                "canceled_at": int(time.time()),
                "ended_at": int(time.time())
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]


# ============================================
# TESTS - STATUTS D'ABONNEMENT
# ============================================

@pytest.mark.asyncio
async def test_subscription_status_past_due(async_client):
    """Test handling subscription becoming past_due"""
    payload = {
        "id": "evt_sub_past_due_123",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "past_due",  # Paiement en retard
                "current_period_start": int(time.time()) - 2592000,
                "current_period_end": int(time.time()) - 86400  # Expiré hier
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]


@pytest.mark.asyncio
async def test_subscription_status_unpaid(async_client):
    """Test handling subscription becoming unpaid"""
    payload = {
        "id": "evt_sub_unpaid_123",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "unpaid",  # Tous les paiements ont échoué
                "current_period_start": int(time.time()) - 2592000,
                "current_period_end": int(time.time()) - 86400
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]


# ============================================
# TESTS - PÉRIODE D'ESSAI
# ============================================

@pytest.mark.asyncio
async def test_subscription_trial_ending(async_client):
    """Test handling trial period ending soon"""
    payload = {
        "id": "evt_trial_ending_123",
        "type": "customer.subscription.trial_will_end",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "trialing",
                "trial_end": int(time.time()) + 259200  # Dans 3 jours
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]


# ============================================
# TESTS - ÉVÉNEMENTS INCONNUS
# ============================================

@pytest.mark.asyncio
async def test_unknown_event_type(async_client):
    """Test handling unknown event type"""
    payload = {
        "id": "evt_unknown_123",
        "type": "unknown.event.type",
        "data": {
            "object": {}
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        # Devrait accepter mais ignorer
        assert response.status_code in [200, 204]


# ============================================
# TESTS - GESTION D'ERREURS
# ============================================

@pytest.mark.asyncio
async def test_webhook_malformed_json(async_client):
    """Test webhook with malformed JSON"""
    payload = "{ invalid json"

    secret = "whsec_test_secret"
    signature = generate_stripe_signature(payload, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_missing_event_id(async_client):
    """Test webhook with missing event ID"""
    payload = {
        "type": "invoice.payment_succeeded",
        "data": {"object": {}}
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        # Devrait gérer gracieusement
        assert response.status_code in [200, 400]


# ============================================
# TESTS - IDEMPOTENCE
# ============================================

@pytest.mark.asyncio
async def test_webhook_idempotency(async_client):
    """Test that same event can be processed multiple times safely"""
    payload = {
        "id": "evt_idempotent_123",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_123",
                "customer": "cus_123",
                "subscription": "sub_123"
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    headers = {
        "Stripe-Signature": signature,
        "Content-Type": "application/json"
    }

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        # Premier traitement
        response1 = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers=headers
        )

        # Deuxième traitement (même événement)
        response2 = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers=headers
        )

        # Les deux devraient réussir (idempotence)
        assert response1.status_code in [200, 204]
        assert response2.status_code in [200, 204]


# ============================================
# TESTS - CUSTOMER EVENTS
# ============================================

@pytest.mark.asyncio
async def test_customer_created(async_client):
    """Test handling customer.created event"""
    payload = {
        "id": "evt_customer_created_123",
        "type": "customer.created",
        "data": {
            "object": {
                "id": "cus_new_123",
                "email": "customer@example.com",
                "created": int(time.time())
            }
        }
    }

    secret = "whsec_test_secret"
    payload_str = json.dumps(payload)
    signature = generate_stripe_signature(payload_str, secret)

    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': secret}):
        response = await async_client.post(
            "/api/stripe/webhook",
            content=payload_str,
            headers={
                "Stripe-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code in [200, 204]
