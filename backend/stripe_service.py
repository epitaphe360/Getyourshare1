"""
Service Stripe pour gérer les paiements et abonnements
"""

import stripe
import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000/subscription/success")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "http://localhost:3000/subscription/cancel")

STRIPE_ENABLED = bool(stripe.api_key and stripe.api_key.startswith("sk_"))


async def get_customer_invoices(customer_id: str, limit: int = 100) -> list:
    """
    Récupérer l'historique des factures d'un client depuis Stripe
    
    Args:
        customer_id: ID du client Stripe
        limit: Nombre maximum de factures à retourner
        
    Returns:
        Liste des factures avec métadonnées
    """
    if not STRIPE_ENABLED:
        return []
    
    try:
        # Récupérer les factures du client
        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=limit
        )
        
        # Formater les données
        formatted_invoices = []
        for invoice in invoices.data:
            formatted_invoices.append({
                "id": invoice.id,
                "invoice_number": invoice.number,
                "amount_paid": invoice.amount_paid / 100,  # Convertir centimes en euros
                "amount_due": invoice.amount_due / 100,
                "currency": invoice.currency.upper(),
                "status": invoice.status,
                "created": datetime.fromtimestamp(invoice.created).isoformat(),
                "due_date": datetime.fromtimestamp(invoice.due_date).isoformat() if invoice.due_date else None,
                "paid_at": datetime.fromtimestamp(invoice.status_transitions.paid_at).isoformat() if invoice.status_transitions.paid_at else None,
                "invoice_pdf": invoice.invoice_pdf,
                "hosted_invoice_url": invoice.hosted_invoice_url,
                "description": invoice.description or "",
                "period_start": datetime.fromtimestamp(invoice.period_start).isoformat() if invoice.period_start else None,
                "period_end": datetime.fromtimestamp(invoice.period_end).isoformat() if invoice.period_end else None,
                "subscription_id": invoice.subscription
            })
        
        return formatted_invoices
        
    except stripe.error.StripeError as e:
        print(f"Erreur Stripe lors de la récupération des factures: {str(e)}")
        return []
    except Exception as e:
        print(f"Erreur lors de la récupération des factures: {str(e)}")
        return []


async def create_checkout_session(
    user_id: str,
    user_email: str,
    plan_id: str,
    plan_name: str,
    price_amount: float,
    billing_cycle: str = "monthly",
    currency: str = "eur"
) -> dict:
    """
    Créer une session Stripe Checkout pour un abonnement
    
    Args:
        user_id: ID de l'utilisateur
        user_email: Email de l'utilisateur
        plan_id: ID du plan d'abonnement
        plan_name: Nom du plan
        price_amount: Montant en euros
        billing_cycle: monthly ou yearly
        currency: Devise (eur, mad, usd)
    
    Returns:
        dict avec session_id et checkout_url
    """
    if not STRIPE_ENABLED:
        return {
            "error": "stripe_not_configured",
            "message": "Stripe n'est pas configuré. Ajoutez STRIPE_SECRET_KEY au fichier .env"
        }
    
    try:
        # Convertir le montant en centimes
        amount_cents = int(price_amount * 100)
        
        # Créer ou récupérer le client Stripe
        customers = stripe.Customer.list(email=user_email, limit=1)
        
        if customers.data:
            customer = customers.data[0]
        else:
            customer = stripe.Customer.create(
                email=user_email,
                metadata={"user_id": user_id}
            )
        
        # Créer la session de paiement
        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": f"Abonnement {plan_name}",
                        "description": f"Plan {plan_name} - Facturation {billing_cycle}"
                    },
                    "unit_amount": amount_cents,
                    "recurring": {
                        "interval": "month" if billing_cycle == "monthly" else "year"
                    }
                },
                "quantity": 1
            }],
            mode="subscription",
            success_url=f"{STRIPE_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=STRIPE_CANCEL_URL,
            metadata={
                "user_id": user_id,
                "plan_id": plan_id,
                "billing_cycle": billing_cycle
            }
        )
        
        return {
            "success": True,
            "session_id": session.id,
            "checkout_url": session.url,
            "customer_id": customer.id
        }
        
    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": "stripe_error",
            "message": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "internal_error",
            "message": str(e)
        }


async def create_customer_portal_session(customer_id: str, return_url: str) -> dict:
    """
    Créer une session du portail client Stripe pour gérer l'abonnement
    
    Args:
        customer_id: ID du client Stripe
        return_url: URL de retour après gestion
    
    Returns:
        dict avec portal_url
    """
    if not STRIPE_ENABLED:
        return {
            "error": "stripe_not_configured",
            "message": "Stripe n'est pas configuré"
        }
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
        
        return {
            "success": True,
            "portal_url": session.url
        }
        
    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": "stripe_error",
            "message": str(e)
        }


async def cancel_stripe_subscription(subscription_id: str, immediate: bool = False) -> dict:
    """
    Annuler un abonnement Stripe
    
    Args:
        subscription_id: ID de l'abonnement Stripe
        immediate: Si True, annulation immédiate, sinon à la fin de la période
    
    Returns:
        dict avec success et informations
    """
    if not STRIPE_ENABLED:
        return {"success": False, "error": "stripe_not_configured"}
    
    try:
        if immediate:
            # Annulation immédiate
            subscription = stripe.Subscription.delete(subscription_id)
        else:
            # Annulation à la fin de la période
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        
        return {
            "success": True,
            "status": subscription.status,
            "canceled_at": subscription.canceled_at,
            "current_period_end": subscription.current_period_end
        }
        
    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": "stripe_error",
            "message": str(e)
        }


async def update_stripe_subscription(subscription_id: str, new_price_id: str) -> dict:
    """
    Mettre à jour un abonnement Stripe (upgrade/downgrade)
    
    Args:
        subscription_id: ID de l'abonnement Stripe
        new_price_id: ID du nouveau prix Stripe
    
    Returns:
        dict avec success et informations
    """
    if not STRIPE_ENABLED:
        return {"success": False, "error": "stripe_not_configured"}
    
    try:
        # Récupérer l'abonnement actuel
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Mettre à jour avec le nouveau prix
        updated_subscription = stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": subscription["items"].data[0].id,
                "price": new_price_id
            }],
            proration_behavior="create_prorations"  # Prorata automatique
        )
        
        return {
            "success": True,
            "status": updated_subscription.status,
            "current_period_end": updated_subscription.current_period_end
        }
        
    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": "stripe_error",
            "message": str(e)
        }


def verify_webhook_signature(payload: bytes, sig_header: str) -> dict:
    """
    Vérifier la signature d'un webhook Stripe
    
    Args:
        payload: Corps de la requête (bytes)
        sig_header: Header Stripe-Signature
    
    Returns:
        dict de l'événement si valide, sinon None
    """
    if not STRIPE_WEBHOOK_SECRET:
        return None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        # Payload invalide
        return None
    except stripe.error.SignatureVerificationError:
        # Signature invalide
        return None


async def handle_webhook_event(event: dict, supabase) -> dict:
    """
    Traiter un événement webhook Stripe
    
    Args:
        event: Événement Stripe
        supabase: Client Supabase
    
    Returns:
        dict avec success et message
    """
    event_type = event["type"]
    event_data = event["data"]["object"]
    
    try:
        # Invoice paid - Activer/renouveler l'abonnement
        if event_type == "invoice.paid":
            subscription_id = event_data.get("subscription")
            customer_id = event_data.get("customer")
            
            # Mettre à jour le statut dans la DB
            supabase.table("subscriptions") \
                .update({"status": "active"}) \
                .eq("stripe_subscription_id", subscription_id) \
                .execute()
            
            return {"success": True, "message": "Invoice paid processed"}
        
        # Invoice payment failed - Marquer l'abonnement en past_due
        elif event_type == "invoice.payment_failed":
            subscription_id = event_data.get("subscription")
            
            supabase.table("subscriptions") \
                .update({"status": "past_due"}) \
                .eq("stripe_subscription_id", subscription_id) \
                .execute()
            
            return {"success": True, "message": "Payment failed processed"}
        
        # Subscription deleted - Annuler l'abonnement
        elif event_type == "customer.subscription.deleted":
            subscription_id = event_data.get("id")
            
            supabase.table("subscriptions") \
                .update({
                    "status": "canceled",
                    "canceled_at": datetime.now().isoformat()
                }) \
                .eq("stripe_subscription_id", subscription_id) \
                .execute()
            
            return {"success": True, "message": "Subscription canceled processed"}
        
        # Subscription updated - Mettre à jour les infos
        elif event_type == "customer.subscription.updated":
            subscription_id = event_data.get("id")
            status = event_data.get("status")
            current_period_end = datetime.fromtimestamp(event_data.get("current_period_end"))
            
            supabase.table("subscriptions") \
                .update({
                    "status": status,
                    "current_period_end": current_period_end.isoformat()
                }) \
                .eq("stripe_subscription_id", subscription_id) \
                .execute()
            
            return {"success": True, "message": "Subscription updated processed"}
        
        # Checkout session completed - Créer l'abonnement initial
        elif event_type == "checkout.session.completed":
            session = event_data
            customer_id = session.get("customer")
            subscription_id = session.get("subscription")
            
            metadata = session.get("metadata", {})
            user_id = metadata.get("user_id")
            plan_id = metadata.get("plan_id")
            
            if user_id and plan_id:
                # L'abonnement sera créé par l'endpoint /api/subscriptions/current
                # On stocke juste les IDs Stripe
                supabase.table("subscriptions") \
                    .update({
                        "stripe_customer_id": customer_id,
                        "stripe_subscription_id": subscription_id,
                        "status": "active"
                    }) \
                    .eq("user_id", user_id) \
                    .execute()
            
            return {"success": True, "message": "Checkout completed processed"}
        
        else:
            return {"success": True, "message": f"Event {event_type} ignored"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_invoice_pdf_url(invoice_id: str) -> Optional[str]:
    """
    Récupérer l'URL du PDF d'une facture Stripe
    
    Args:
        invoice_id: ID de la facture Stripe
    
    Returns:
        URL du PDF ou None
    """
    if not STRIPE_ENABLED:
        return None
    
    try:
        invoice = stripe.Invoice.retrieve(invoice_id)
        return invoice.invoice_pdf
    except:
        return None
