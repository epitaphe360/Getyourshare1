"""
============================================
STRIPE WEBHOOK HANDLER
Share Your Sales - Événements Stripe
============================================

Gestion des webhooks Stripe pour:
- Paiements réussis
- Échecs de paiement
- Renouvellement d'abonnement
- Annulation d'abonnement
- Mise à jour d'abonnement
"""

from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
from datetime import datetime
from supabase import create_client, Client
import os
import stripe

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

# ============================================
# ENVIRONMENT VARIABLES VALIDATION
# ============================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing required Supabase environment variables")

# ============================================
# SUPABASE CLIENT
# ============================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# STRIPE CONFIGURATION
# ============================================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY or not STRIPE_SECRET_KEY.startswith("sk_"):
    raise ValueError("Missing or invalid STRIPE_SECRET_KEY")

if not STRIPE_WEBHOOK_SECRET or not STRIPE_WEBHOOK_SECRET.startswith("whsec_"):
    raise ValueError("Missing or invalid STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET_KEY
stripe.max_network_retries = 2

# ============================================
# WEBHOOK EVENT HANDLERS
# ============================================

async def handle_subscription_created(subscription: dict):
    """Nouvel abonnement créé"""
    try:
        customer_id = subscription["customer"]
        subscription_id = subscription["id"]

        print(f"[Webhook] New subscription created: {subscription_id}")

        # Récupérer l'abonnement en base
        response = supabase.from_("subscriptions") \
            .select("*") \
            .eq("stripe_subscription_id", subscription_id) \
            .single() \
            .execute()

        if response.data:
            # Mettre à jour le statut si nécessaire
            supabase.from_("subscriptions") \
                .update({
                    "status": subscription["status"],
                    "current_period_start": datetime.fromtimestamp(subscription["current_period_start"]).isoformat(),
                    "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]).isoformat()
                }) \
                .eq("stripe_subscription_id", subscription_id) \
                .execute()

            print(f"[Webhook] Subscription updated: {subscription_id}")

    except Exception as e:
        print(f"[Webhook Error] handle_subscription_created: {e}")

async def handle_subscription_updated(subscription: dict):
    """Abonnement mis à jour (changement de plan, renouvellement, etc.)"""
    try:
        subscription_id = subscription["id"]
        status = subscription["status"]

        print(f"[Webhook] Subscription updated: {subscription_id}, status: {status}")

        # Mettre à jour en base de données
        update_data = {
            "status": status,
            "current_period_start": datetime.fromtimestamp(subscription["current_period_start"]).isoformat(),
            "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]).isoformat()
        }

        # Si annulation programmée
        if subscription.get("cancel_at"):
            update_data["cancel_at"] = datetime.fromtimestamp(subscription["cancel_at"]).isoformat()

        supabase.from_("subscriptions") \
            .update(update_data) \
            .eq("stripe_subscription_id", subscription_id) \
            .execute()

        print(f"[Webhook] Subscription data updated: {subscription_id}")

    except Exception as e:
        print(f"[Webhook Error] handle_subscription_updated: {e}")

async def handle_subscription_deleted(subscription: dict):
    """Abonnement annulé/supprimé"""
    try:
        subscription_id = subscription["id"]

        print(f"[Webhook] Subscription deleted: {subscription_id}")

        # Marquer l'abonnement comme annulé
        supabase.from_("subscriptions") \
            .update({
                "status": "canceled",
                "canceled_at": datetime.now().isoformat(),
                "ended_at": datetime.now().isoformat()
            }) \
            .eq("stripe_subscription_id", subscription_id) \
            .execute()

        print(f"[Webhook] Subscription marked as canceled: {subscription_id}")

    except Exception as e:
        print(f"[Webhook Error] handle_subscription_deleted: {e}")

async def handle_invoice_paid(invoice: dict):
    """Facture payée avec succès"""
    try:
        subscription_id = invoice.get("subscription")

        if not subscription_id:
            return

        print(f"[Webhook] Invoice paid for subscription: {subscription_id}")

        # Mettre à jour le statut de l'abonnement à 'active'
        supabase.from_("subscriptions") \
            .update({"status": "active"}) \
            .eq("stripe_subscription_id", subscription_id) \
            .execute()

        # TODO: Envoyer email de confirmation de paiement

        print(f"[Webhook] Subscription activated: {subscription_id}")

    except Exception as e:
        print(f"[Webhook Error] handle_invoice_paid: {e}")

async def handle_invoice_payment_failed(invoice: dict):
    """Échec de paiement de facture"""
    try:
        subscription_id = invoice.get("subscription")
        customer_id = invoice.get("customer")

        if not subscription_id:
            return

        print(f"[Webhook] Payment failed for subscription: {subscription_id}")

        # Mettre à jour le statut de l'abonnement
        supabase.from_("subscriptions") \
            .update({"status": "past_due"}) \
            .eq("stripe_subscription_id", subscription_id) \
            .execute()

        # Récupérer l'utilisateur
        subscription_response = supabase.from_("subscriptions") \
            .select("user_id") \
            .eq("stripe_subscription_id", subscription_id) \
            .single() \
            .execute()

        if subscription_response.data:
            user_id = subscription_response.data["user_id"]

            # TODO: Envoyer email d'alerte de paiement échoué
            # TODO: Créer une notification in-app

            print(f"[Webhook] User notified about payment failure: {user_id}")

    except Exception as e:
        print(f"[Webhook Error] handle_invoice_payment_failed: {e}")

async def handle_customer_subscription_trial_will_end(subscription: dict):
    """Période d'essai sur le point de se terminer (3 jours avant)"""
    try:
        subscription_id = subscription["id"]
        trial_end = subscription.get("trial_end")

        if not trial_end:
            return

        print(f"[Webhook] Trial ending soon for subscription: {subscription_id}")

        # Récupérer l'utilisateur
        subscription_response = supabase.from_("subscriptions") \
            .select("user_id") \
            .eq("stripe_subscription_id", subscription_id) \
            .single() \
            .execute()

        if subscription_response.data:
            user_id = subscription_response.data["user_id"]

            # TODO: Envoyer email de rappel de fin de période d'essai
            # TODO: Créer une notification in-app

            print(f"[Webhook] User notified about trial ending: {user_id}")

    except Exception as e:
        print(f"[Webhook Error] handle_customer_subscription_trial_will_end: {e}")

async def handle_payment_method_attached(payment_method: dict):
    """Méthode de paiement attachée à un client"""
    try:
        customer_id = payment_method.get("customer")

        if not customer_id:
            return

        print(f"[Webhook] Payment method attached to customer: {customer_id}")

        # Mettre à jour les informations du client si nécessaire
        # TODO: Enregistrer les détails de la méthode de paiement

    except Exception as e:
        print(f"[Webhook Error] handle_payment_method_attached: {e}")

async def handle_payment_method_detached(payment_method: dict):
    """Méthode de paiement retirée d'un client"""
    try:
        customer_id = payment_method.get("customer")

        if not customer_id:
            return

        print(f"[Webhook] Payment method detached from customer: {customer_id}")

        # TODO: Notifier l'utilisateur de retirer une méthode de paiement

    except Exception as e:
        print(f"[Webhook Error] handle_payment_method_detached: {e}")

# ============================================
# WEBHOOK ENDPOINT
# ============================================

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None)
):
    """
    Endpoint pour recevoir les webhooks Stripe

    Configuration dans Stripe Dashboard:
    - URL: https://yourdomain.com/api/webhooks/stripe
    - Événements à écouter:
      - customer.subscription.created
      - customer.subscription.updated
      - customer.subscription.deleted
      - customer.subscription.trial_will_end
      - invoice.paid
      - invoice.payment_failed
      - payment_method.attached
      - payment_method.detached

    Sécurité:
    - Vérifie la signature Stripe pour authentifier les requêtes
    """
    try:
        # Récupérer le body brut
        payload = await request.body()

        # Vérifier la signature Stripe
        if not STRIPE_WEBHOOK_SECRET:
            print("[Webhook Warning] STRIPE_WEBHOOK_SECRET not configured")
            # En développement, on peut ignorer la vérification
            event = stripe.Event.construct_from(
                await request.json(), stripe.api_key
            )
        else:
            if not stripe_signature:
                raise HTTPException(status_code=400, detail="Missing stripe-signature header")

            try:
                event = stripe.Webhook.construct_event(
                    payload, stripe_signature, STRIPE_WEBHOOK_SECRET
                )
            except stripe.error.SignatureVerificationError:
                raise HTTPException(status_code=400, detail="Invalid signature")

        # Traiter l'événement
        event_type = event["type"]
        event_data = event["data"]["object"]

        print(f"[Webhook] Received event: {event_type}")

        # Router vers le bon handler
        if event_type == "customer.subscription.created":
            await handle_subscription_created(event_data)

        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event_data)

        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(event_data)

        elif event_type == "invoice.paid":
            await handle_invoice_paid(event_data)

        elif event_type == "invoice.payment_failed":
            await handle_invoice_payment_failed(event_data)

        elif event_type == "customer.subscription.trial_will_end":
            await handle_customer_subscription_trial_will_end(event_data)

        elif event_type == "payment_method.attached":
            await handle_payment_method_attached(event_data)

        elif event_type == "payment_method.detached":
            await handle_payment_method_detached(event_data)

        else:
            print(f"[Webhook] Unhandled event type: {event_type}")

        return {"success": True, "event_type": event_type}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Webhook Error] Error processing webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing webhook: {str(e)}"
        )

# ============================================
# TEST ENDPOINT (Development only)
# ============================================

@router.post("/stripe/test")
async def test_webhook(event_type: str, subscription_id: str):
    """
    [DEV ONLY] Simuler un événement webhook Stripe

    Usage:
    POST /api/webhooks/stripe/test?event_type=invoice.paid&subscription_id=sub_xxx
    """
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(status_code=403, detail="Test endpoint not available in production")

    print(f"[Test Webhook] Simulating event: {event_type}")

    # Simuler l'événement
    if event_type == "invoice.paid":
        await handle_invoice_paid({"subscription": subscription_id})
    elif event_type == "invoice.payment_failed":
        await handle_invoice_payment_failed({"subscription": subscription_id})
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated({
            "id": subscription_id,
            "status": "active",
            "current_period_start": 1234567890,
            "current_period_end": 1234567890 + (30 * 24 * 60 * 60)
        })

    return {"success": True, "message": f"Simulated {event_type} for {subscription_id}"}

# ============================================
# HELPER ENDPOINTS
# ============================================

@router.get("/stripe/events")
async def list_recent_events(limit: int = 10):
    """
    [ADMIN] Liste les événements Stripe récents

    Utile pour le debugging
    """
    try:
        events = stripe.Event.list(limit=limit)

        return {
            "events": [
                {
                    "id": event.id,
                    "type": event.type,
                    "created": datetime.fromtimestamp(event.created).isoformat(),
                    "livemode": event.livemode
                }
                for event in events.data
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching events: {str(e)}"
        )

@router.post("/stripe/retry-event/{event_id}")
async def retry_event(event_id: str):
    """
    [ADMIN] Rejouer un événement Stripe

    Utile si un webhook a échoué
    """
    try:
        # Récupérer l'événement
        event = stripe.Event.retrieve(event_id)

        event_type = event.type
        event_data = event.data.object

        print(f"[Webhook Retry] Retrying event: {event_type}")

        # Router vers le bon handler
        if event_type == "customer.subscription.created":
            await handle_subscription_created(event_data)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event_data)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(event_data)
        elif event_type == "invoice.paid":
            await handle_invoice_paid(event_data)
        elif event_type == "invoice.payment_failed":
            await handle_invoice_payment_failed(event_data)

        return {
            "success": True,
            "message": f"Event {event_id} reprocessed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrying event: {str(e)}"
        )
