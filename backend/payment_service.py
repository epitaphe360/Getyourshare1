"""
Service de paiement avec intégration Stripe et autres passerelles
Gestion des paiements récurrents, webhooks et transactions
"""

import os
import stripe
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from subscription_helpers import (
    create_transaction, update_transaction_status,
    mark_invoice_paid, update_subscription_status,
    get_subscription_by_id, create_invoice
)

load_dotenv()

# Configuration Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

class PaymentService:
    """Service de gestion des paiements"""

    @staticmethod
    def create_stripe_customer(email: str, name: Optional[str] = None, metadata: Optional[Dict] = None) -> Optional[str]:
        """Crée un client Stripe"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer.id
        except stripe.error.StripeError as e:
            print(f"Error creating Stripe customer: {e}")
            return None

    @staticmethod
    def attach_payment_method(customer_id: str, payment_method_id: str) -> bool:
        """Attache une méthode de paiement à un client"""
        try:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )

            # Définir comme méthode par défaut
            stripe.Customer.modify(
                customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
            return True
        except stripe.error.StripeError as e:
            print(f"Error attaching payment method: {e}")
            return False

    @staticmethod
    def create_payment_intent(
        amount: float,
        currency: str = "mad",
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Crée un Payment Intent Stripe"""
        try:
            # Convertir en centimes
            amount_cents = int(amount * 100)

            intent_data = {
                "amount": amount_cents,
                "currency": currency.lower(),
                "metadata": metadata or {}
            }

            if customer_id:
                intent_data["customer"] = customer_id
            if payment_method_id:
                intent_data["payment_method"] = payment_method_id
                intent_data["confirm"] = True
                intent_data["automatic_payment_methods"] = {"enabled": True, "allow_redirects": "never"}

            intent = stripe.PaymentIntent.create(**intent_data)

            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": amount
            }
        except stripe.error.StripeError as e:
            print(f"Error creating payment intent: {e}")
            return None

    @staticmethod
    def confirm_payment_intent(payment_intent_id: str) -> Optional[Dict]:
        """Confirme un Payment Intent"""
        try:
            intent = stripe.PaymentIntent.confirm(payment_intent_id)
            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100
            }
        except stripe.error.StripeError as e:
            print(f"Error confirming payment intent: {e}")
            return None

    @staticmethod
    def create_subscription_payment(
        user_id: str,
        subscription_id: str,
        amount: float,
        payment_method_id: str,
        description: str = "Subscription payment"
    ) -> Dict[str, Any]:
        """Crée un paiement pour un abonnement"""
        try:
            # Créer une facture
            invoice = create_invoice(
                user_id=user_id,
                subscription_id=subscription_id,
                subtotal=amount,
                items=[{
                    "description": description,
                    "amount": amount,
                    "quantity": 1
                }],
                payment_method="stripe"
            )

            if not invoice:
                return {"success": False, "error": "Failed to create invoice"}

            # Créer une transaction
            transaction = create_transaction(
                user_id=user_id,
                subscription_id=subscription_id,
                invoice_id=invoice["id"],
                transaction_type="charge",
                amount=amount,
                payment_provider="stripe",
                status="pending"
            )

            if not transaction:
                return {"success": False, "error": "Failed to create transaction"}

            # Créer le Payment Intent
            payment_intent = PaymentService.create_payment_intent(
                amount=amount,
                payment_method_id=payment_method_id,
                metadata={
                    "user_id": user_id,
                    "subscription_id": subscription_id,
                    "invoice_id": invoice["id"],
                    "transaction_id": transaction["id"]
                }
            )

            if not payment_intent:
                update_transaction_status(transaction["id"], "failed", failure_message="Failed to create payment intent")
                return {"success": False, "error": "Payment failed"}

            # Mettre à jour la transaction
            update_transaction_status(
                transaction["id"],
                "succeeded" if payment_intent["status"] == "succeeded" else "pending",
                provider_response=payment_intent,
                provider_transaction_id=payment_intent["id"]
            )

            # Si paiement réussi, marquer la facture comme payée
            if payment_intent["status"] == "succeeded":
                mark_invoice_paid(invoice["id"], payment_intent["id"])

            return {
                "success": True,
                "payment_intent": payment_intent,
                "invoice": invoice,
                "transaction": transaction
            }

        except Exception as e:
            print(f"Error creating subscription payment: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def process_recurring_payment(subscription_id: str) -> Dict[str, Any]:
        """Traite un paiement récurrent pour un abonnement"""
        try:
            subscription = get_subscription_by_id(subscription_id)
            if not subscription:
                return {"success": False, "error": "Subscription not found"}

            # Vérifier si l'abonnement a auto_renew activé
            if not subscription.get("auto_renew"):
                return {"success": False, "error": "Auto-renew is disabled"}

            # Calculer le montant
            plan = subscription["subscription_plans"]
            if subscription["billing_cycle"] == "monthly":
                amount = float(plan["price_monthly"])
            else:
                amount = float(plan["price_yearly"])

            # Appliquer les réductions
            if subscription.get("discount_percentage"):
                amount = amount * (1 - subscription["discount_percentage"] / 100)
            if subscription.get("discount_amount"):
                amount = max(0, amount - float(subscription["discount_amount"]))

            # Récupérer la méthode de paiement
            payment_method_id = subscription.get("payment_method_id")
            if not payment_method_id:
                update_subscription_status(subscription_id, "past_due", "No payment method")
                return {"success": False, "error": "No payment method"}

            # Effectuer le paiement
            result = PaymentService.create_subscription_payment(
                user_id=subscription["user_id"],
                subscription_id=subscription_id,
                amount=amount,
                payment_method_id=payment_method_id,
                description=f"Subscription renewal - {plan['name']}"
            )

            if result["success"]:
                # Mettre à jour les dates de l'abonnement
                from datetime import timedelta
                current_end = datetime.fromisoformat(subscription["current_period_end"].replace('Z', '+00:00'))

                if subscription["billing_cycle"] == "monthly":
                    new_end = current_end + timedelta(days=30)
                else:
                    new_end = current_end + timedelta(days=365)

                from supabase_client import supabase
                supabase.table("subscriptions").update({
                    "current_period_start": current_end.isoformat(),
                    "current_period_end": new_end.isoformat(),
                    "next_billing_date": new_end.isoformat(),
                    "status": "active"
                }).eq("id", subscription_id).execute()

            else:
                # Paiement échoué
                update_subscription_status(subscription_id, "past_due", "Payment failed")

            return result

        except Exception as e:
            print(f"Error processing recurring payment: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def create_refund(payment_intent_id: str, amount: Optional[float] = None, reason: Optional[str] = None) -> Optional[Dict]:
        """Crée un remboursement"""
        try:
            refund_data = {
                "payment_intent": payment_intent_id
            }

            if amount:
                refund_data["amount"] = int(amount * 100)
            if reason:
                refund_data["reason"] = reason

            refund = stripe.Refund.create(**refund_data)

            return {
                "id": refund.id,
                "status": refund.status,
                "amount": refund.amount / 100
            }
        except stripe.error.StripeError as e:
            print(f"Error creating refund: {e}")
            return None

    @staticmethod
    def handle_webhook(payload: bytes, signature: str) -> Dict[str, Any]:
        """Traite un webhook Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )

            event_type = event["type"]
            data = event["data"]["object"]

            print(f"Received webhook: {event_type}")

            # Payment Intent réussi
            if event_type == "payment_intent.succeeded":
                payment_intent_id = data["id"]
                metadata = data.get("metadata", {})

                transaction_id = metadata.get("transaction_id")
                invoice_id = metadata.get("invoice_id")

                if transaction_id:
                    update_transaction_status(transaction_id, "succeeded", provider_response=data)

                if invoice_id:
                    mark_invoice_paid(invoice_id, payment_intent_id)

                return {"success": True, "message": "Payment succeeded"}

            # Payment Intent échoué
            elif event_type == "payment_intent.payment_failed":
                metadata = data.get("metadata", {})
                transaction_id = metadata.get("transaction_id")
                subscription_id = metadata.get("subscription_id")

                if transaction_id:
                    update_transaction_status(
                        transaction_id,
                        "failed",
                        provider_response=data,
                        failure_code=data.get("last_payment_error", {}).get("code"),
                        failure_message=data.get("last_payment_error", {}).get("message")
                    )

                if subscription_id:
                    update_subscription_status(subscription_id, "past_due", "Payment failed")

                return {"success": True, "message": "Payment failed handled"}

            # Customer.subscription.deleted (annulation)
            elif event_type == "customer.subscription.deleted":
                # Gérer l'annulation si nécessaire
                return {"success": True, "message": "Subscription deleted"}

            return {"success": True, "message": f"Unhandled event: {event_type}"}

        except stripe.error.SignatureVerificationError as e:
            print(f"Webhook signature verification failed: {e}")
            return {"success": False, "error": "Invalid signature"}
        except Exception as e:
            print(f"Error handling webhook: {e}")
            return {"success": False, "error": str(e)}


# ============================================
# AUTRES PASSERELLES (CMI, PayZen, SG Maroc)
# ============================================

class CMIPaymentService:
    """Service de paiement CMI (Center Monétique Interbancaire)"""

    @staticmethod
    def create_payment(amount: float, order_id: str, customer_email: str) -> Dict[str, Any]:
        """Crée un paiement CMI"""
        # TODO: Implémenter l'intégration CMI
        # Documentation: https://www.cmi.co.ma
        return {
            "success": False,
            "error": "CMI integration not implemented yet"
        }


class PayZenService:
    """Service de paiement PayZen"""

    @staticmethod
    def create_payment(amount: float, order_id: str, customer_email: str) -> Dict[str, Any]:
        """Crée un paiement PayZen"""
        # TODO: Implémenter l'intégration PayZen
        # Documentation: https://payzen.eu
        return {
            "success": False,
            "error": "PayZen integration not implemented yet"
        }


class SGMarocService:
    """Service de paiement Société Générale Maroc"""

    @staticmethod
    def create_payment(amount: float, order_id: str, customer_email: str) -> Dict[str, Any]:
        """Crée un paiement SG Maroc"""
        # TODO: Implémenter l'intégration SG Maroc
        return {
            "success": False,
            "error": "SG Maroc integration not implemented yet"
        }
