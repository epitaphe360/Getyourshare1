"""
Service Stripe pour la gestion des abonnements SaaS

Fonctionnalités:
- Création d'abonnements (Starter, Pro, Enterprise)
- Gestion des webhooks Stripe
- Annulation/modification d'abonnements
- Facturation automatique
- Gestion des échecs de paiement
- Génération d'invoices
- Customer portal
"""

import stripe
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import structlog

logger = structlog.get_logger()

# Configuration Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")


class SubscriptionPlan(str, Enum):
    """Plans d'abonnement disponibles"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Statuts d'abonnement"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


# Configuration des plans
SUBSCRIPTION_PLANS = {
    SubscriptionPlan.FREE: {
        "name": "Gratuit",
        "price_monthly": 0,
        "price_yearly": 0,
        "stripe_price_id_monthly": None,
        "stripe_price_id_yearly": None,
        "features": {
            "max_products": 5,
            "max_influencers": 3,
            "max_links": 10,
            "commission_fee": 10.0,  # 10% de frais plateforme
            "analytics": "basic",
            "support": "email",
            "social_media_sync": False,
            "ai_bot": False,
            "custom_domain": False,
            "priority_support": False
        }
    },
    SubscriptionPlan.STARTER: {
        "name": "Starter",
        "price_monthly": 299,  # 299 MAD/mois
        "price_yearly": 2990,  # 2990 MAD/an (économie 1 mois)
        "stripe_price_id_monthly": "price_starter_monthly",
        "stripe_price_id_yearly": "price_starter_yearly",
        "features": {
            "max_products": 50,
            "max_influencers": 20,
            "max_links": 100,
            "commission_fee": 5.0,  # 5% de frais plateforme
            "analytics": "advanced",
            "support": "email",
            "social_media_sync": True,
            "ai_bot": True,
            "custom_domain": False,
            "priority_support": False
        }
    },
    SubscriptionPlan.PRO: {
        "name": "Pro",
        "price_monthly": 799,  # 799 MAD/mois
        "price_yearly": 7990,  # 7990 MAD/an
        "stripe_price_id_monthly": "price_pro_monthly",
        "stripe_price_id_yearly": "price_pro_yearly",
        "features": {
            "max_products": 200,
            "max_influencers": 100,
            "max_links": 500,
            "commission_fee": 3.0,  # 3% de frais plateforme
            "analytics": "professional",
            "support": "priority",
            "social_media_sync": True,
            "ai_bot": True,
            "custom_domain": True,
            "priority_support": True,
            "api_access": True,
            "white_label": False
        }
    },
    SubscriptionPlan.ENTERPRISE: {
        "name": "Enterprise",
        "price_monthly": 1999,  # 1999 MAD/mois
        "price_yearly": 19990,  # 19990 MAD/an
        "stripe_price_id_monthly": "price_enterprise_monthly",
        "stripe_price_id_yearly": "price_enterprise_yearly",
        "features": {
            "max_products": -1,  # Illimité
            "max_influencers": -1,  # Illimité
            "max_links": -1,  # Illimité
            "commission_fee": 2.0,  # 2% de frais plateforme
            "analytics": "enterprise",
            "support": "dedicated",
            "social_media_sync": True,
            "ai_bot": True,
            "custom_domain": True,
            "priority_support": True,
            "api_access": True,
            "white_label": True,
            "dedicated_account_manager": True,
            "sla": "99.9%"
        }
    }
}


class StripeService:
    """Service principal pour Stripe"""

    def __init__(self):
        self.stripe = stripe

    # ============================================
    # CRÉATION ABONNEMENT
    # ============================================

    async def create_subscription(
        self,
        user_id: str,
        email: str,
        plan: SubscriptionPlan,
        billing_cycle: str = "monthly",  # monthly ou yearly
        payment_method_id: Optional[str] = None
    ) -> Dict:
        """
        Créer un nouvel abonnement pour un utilisateur

        Args:
            user_id: ID de l'utilisateur
            email: Email de l'utilisateur
            plan: Plan d'abonnement (starter, pro, enterprise)
            billing_cycle: Cycle de facturation (monthly/yearly)
            payment_method_id: ID du moyen de paiement Stripe

        Returns:
            Dict avec subscription_id, client_secret, status
        """
        try:
            logger.info("creating_subscription", user_id=user_id, plan=plan, cycle=billing_cycle)

            # 1. Créer ou récupérer le customer Stripe
            customer = await self._get_or_create_customer(user_id, email)

            # 2. Attacher le moyen de paiement au customer
            if payment_method_id:
                await self._attach_payment_method(customer.id, payment_method_id)

            # 3. Récupérer le price_id selon le plan et le cycle
            plan_config = SUBSCRIPTION_PLANS[plan]
            price_id = (
                plan_config[f"stripe_price_id_{billing_cycle}"]
                if billing_cycle == "yearly"
                else plan_config["stripe_price_id_monthly"]
            )

            if not price_id:
                raise ValueError(f"No Stripe price ID for plan {plan} and cycle {billing_cycle}")

            # 4. Créer l'abonnement
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "user_id": user_id,
                    "plan": plan.value,
                    "billing_cycle": billing_cycle
                },
                # Trial de 14 jours pour nouveaux clients
                trial_period_days=14 if not await self._has_had_trial(user_id) else 0
            )

            # 5. Sauvegarder en base de données
            await self._save_subscription_to_db(user_id, subscription, plan, billing_cycle)

            # 6. Retourner les informations
            client_secret = subscription.latest_invoice.payment_intent.client_secret

            logger.info("subscription_created", subscription_id=subscription.id, user_id=user_id)

            return {
                "subscription_id": subscription.id,
                "client_secret": client_secret,
                "status": subscription.status,
                "trial_end": subscription.trial_end,
                "current_period_end": subscription.current_period_end
            }

        except stripe.error.StripeError as e:
            logger.error("stripe_error", error=str(e), user_id=user_id)
            raise ValueError(f"Stripe error: {e.user_message}")
        except Exception as e:
            logger.error("subscription_creation_error", error=str(e), user_id=user_id)
            raise

    async def _get_or_create_customer(self, user_id: str, email: str) -> stripe.Customer:
        """Récupérer ou créer un customer Stripe"""
        # TODO: Vérifier en DB si customer existe
        # Pour l'instant, chercher par email
        customers = stripe.Customer.list(email=email, limit=1)

        if customers.data:
            return customers.data[0]

        # Créer nouveau customer
        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": user_id}
        )

        # TODO: Sauvegarder customer_id en DB
        return customer

    async def _attach_payment_method(self, customer_id: str, payment_method_id: str):
        """Attacher un moyen de paiement à un customer"""
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )

        # Définir comme moyen de paiement par défaut
        stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": payment_method_id}
        )

    async def _has_had_trial(self, user_id: str) -> bool:
        """Vérifier si l'utilisateur a déjà bénéficié d'un trial"""
        # TODO: Vérifier en DB
        return False

    async def _save_subscription_to_db(
        self,
        user_id: str,
        subscription: stripe.Subscription,
        plan: SubscriptionPlan,
        billing_cycle: str
    ):
        """Sauvegarder l'abonnement en base de données"""
        # TODO: Implémenter sauvegarde DB
        # Table: user_subscriptions
        # Colonnes: user_id, stripe_subscription_id, stripe_customer_id,
        #           plan, status, current_period_start, current_period_end,
        #           cancel_at_period_end, trial_end, created_at, updated_at
        pass

    # ============================================
    # GESTION ABONNEMENT
    # ============================================

    async def cancel_subscription(
        self,
        user_id: str,
        cancel_immediately: bool = False
    ) -> Dict:
        """
        Annuler un abonnement

        Args:
            user_id: ID de l'utilisateur
            cancel_immediately: Si True, annule immédiatement. Sinon, à la fin de la période

        Returns:
            Dict avec status
        """
        try:
            # Récupérer subscription_id depuis DB
            subscription_id = await self._get_user_subscription_id(user_id)

            if cancel_immediately:
                # Annulation immédiate
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                # Annulation à la fin de la période
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )

            # Mettre à jour en DB
            await self._update_subscription_status(user_id, subscription.status)

            logger.info("subscription_canceled", user_id=user_id, immediate=cancel_immediately)

            return {
                "status": subscription.status,
                "cancel_at": subscription.cancel_at if cancel_immediately else subscription.current_period_end
            }

        except Exception as e:
            logger.error("cancel_subscription_error", error=str(e), user_id=user_id)
            raise

    async def reactivate_subscription(self, user_id: str) -> Dict:
        """Réactiver un abonnement annulé (mais pas encore terminé)"""
        try:
            subscription_id = await self._get_user_subscription_id(user_id)

            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )

            await self._update_subscription_status(user_id, subscription.status)

            logger.info("subscription_reactivated", user_id=user_id)

            return {"status": subscription.status}

        except Exception as e:
            logger.error("reactivate_error", error=str(e), user_id=user_id)
            raise

    async def update_subscription_plan(
        self,
        user_id: str,
        new_plan: SubscriptionPlan,
        billing_cycle: str = "monthly"
    ) -> Dict:
        """
        Changer de plan d'abonnement (upgrade/downgrade)

        Proration automatique par Stripe
        """
        try:
            subscription_id = await self._get_user_subscription_id(user_id)
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Nouveau price_id
            plan_config = SUBSCRIPTION_PLANS[new_plan]
            new_price_id = plan_config[f"stripe_price_id_{billing_cycle}"]

            # Modifier l'abonnement
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id
                }],
                proration_behavior="always_invoice",  # Facturer immédiatement la prorata
                metadata={
                    **subscription.metadata,
                    "plan": new_plan.value,
                    "billing_cycle": billing_cycle
                }
            )

            # Mettre à jour en DB
            await self._update_subscription_plan(user_id, new_plan, billing_cycle)

            logger.info("subscription_updated", user_id=user_id, new_plan=new_plan)

            return {
                "status": "success",
                "new_plan": new_plan.value,
                "next_billing_date": updated_subscription.current_period_end
            }

        except Exception as e:
            logger.error("update_plan_error", error=str(e), user_id=user_id)
            raise

    # ============================================
    # CUSTOMER PORTAL
    # ============================================

    async def create_customer_portal_session(
        self,
        user_id: str,
        return_url: str
    ) -> str:
        """
        Créer une session Customer Portal Stripe

        Permet à l'utilisateur de gérer son abonnement (paiement, invoices, etc.)
        """
        try:
            customer_id = await self._get_user_customer_id(user_id)

            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )

            return session.url

        except Exception as e:
            logger.error("portal_session_error", error=str(e), user_id=user_id)
            raise

    # ============================================
    # WEBHOOKS
    # ============================================

    async def handle_webhook(self, payload: bytes, sig_header: str) -> Dict:
        """
        Gérer les webhooks Stripe

        Events importants:
        - customer.subscription.created
        - customer.subscription.updated
        - customer.subscription.deleted
        - invoice.payment_succeeded
        - invoice.payment_failed
        """
        try:
            # Vérifier la signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )

            logger.info("webhook_received", event_type=event["type"])

            # Router selon le type d'event
            if event["type"] == "customer.subscription.created":
                await self._handle_subscription_created(event["data"]["object"])
            elif event["type"] == "customer.subscription.updated":
                await self._handle_subscription_updated(event["data"]["object"])
            elif event["type"] == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event["data"]["object"])
            elif event["type"] == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(event["data"]["object"])
            elif event["type"] == "invoice.payment_failed":
                await self._handle_payment_failed(event["data"]["object"])
            else:
                logger.info("unhandled_webhook", event_type=event["type"])

            return {"status": "success"}

        except stripe.error.SignatureVerificationError as e:
            logger.error("invalid_webhook_signature", error=str(e))
            raise ValueError("Invalid signature")
        except Exception as e:
            logger.error("webhook_error", error=str(e))
            raise

    async def _handle_subscription_created(self, subscription: Dict):
        """Abonnement créé"""
        user_id = subscription["metadata"].get("user_id")
        # Déjà géré dans create_subscription
        pass

    async def _handle_subscription_updated(self, subscription: Dict):
        """Abonnement mis à jour"""
        user_id = subscription["metadata"].get("user_id")
        await self._update_subscription_status(user_id, subscription["status"])

    async def _handle_subscription_deleted(self, subscription: Dict):
        """Abonnement supprimé/expiré"""
        user_id = subscription["metadata"].get("user_id")
        await self._update_subscription_status(user_id, "canceled")
        # TODO: Révoquer accès features premium

    async def _handle_payment_succeeded(self, invoice: Dict):
        """Paiement réussi"""
        customer_id = invoice["customer"]
        user_id = await self._get_user_id_from_customer(customer_id)

        # TODO: Envoyer email de confirmation
        # TODO: Créer invoice en DB
        logger.info("payment_succeeded", user_id=user_id, amount=invoice["amount_paid"])

    async def _handle_payment_failed(self, invoice: Dict):
        """Paiement échoué"""
        customer_id = invoice["customer"]
        user_id = await self._get_user_id_from_customer(customer_id)

        # TODO: Envoyer email d'alerte
        # TODO: Suspendre compte si multiple échecs
        logger.warning("payment_failed", user_id=user_id, attempt=invoice["attempt_count"])

    # ============================================
    # HELPERS DB (À IMPLÉMENTER)
    # ============================================

    async def _get_user_subscription_id(self, user_id: str) -> str:
        """Récupérer subscription_id depuis la DB"""
        # TODO: Implémenter
        return "sub_xxxxx"

    async def _get_user_customer_id(self, user_id: str) -> str:
        """Récupérer customer_id depuis la DB"""
        # TODO: Implémenter
        return "cus_xxxxx"

    async def _get_user_id_from_customer(self, customer_id: str) -> str:
        """Récupérer user_id depuis customer_id"""
        # TODO: Implémenter
        return "user_xxxxx"

    async def _update_subscription_status(self, user_id: str, status: str):
        """Mettre à jour le statut de l'abonnement"""
        # TODO: Implémenter UPDATE en DB
        pass

    async def _update_subscription_plan(self, user_id: str, plan: SubscriptionPlan, billing_cycle: str):
        """Mettre à jour le plan de l'abonnement"""
        # TODO: Implémenter UPDATE en DB
        pass

    # ============================================
    # VÉRIFICATIONS
    # ============================================

    async def check_feature_access(self, user_id: str, feature: str) -> bool:
        """
        Vérifier si l'utilisateur a accès à une feature

        Args:
            user_id: ID de l'utilisateur
            feature: Feature à vérifier (ex: "social_media_sync", "ai_bot")

        Returns:
            True si accès autorisé
        """
        # Récupérer le plan de l'utilisateur
        user_plan = await self._get_user_plan(user_id)

        if user_plan == SubscriptionPlan.FREE:
            return SUBSCRIPTION_PLANS[SubscriptionPlan.FREE]["features"].get(feature, False)

        plan_features = SUBSCRIPTION_PLANS.get(user_plan, {}).get("features", {})
        return plan_features.get(feature, False)

    async def check_quota(self, user_id: str, resource: str, current_count: int) -> bool:
        """
        Vérifier si l'utilisateur n'a pas dépassé son quota

        Args:
            user_id: ID de l'utilisateur
            resource: Ressource (max_products, max_influencers, max_links)
            current_count: Nombre actuel de ressources

        Returns:
            True si quota OK
        """
        user_plan = await self._get_user_plan(user_id)
        plan_features = SUBSCRIPTION_PLANS[user_plan]["features"]

        max_allowed = plan_features.get(resource, 0)

        # -1 = illimité
        if max_allowed == -1:
            return True

        return current_count < max_allowed

    async def _get_user_plan(self, user_id: str) -> SubscriptionPlan:
        """Récupérer le plan actuel de l'utilisateur"""
        # TODO: Implémenter récupération depuis DB
        return SubscriptionPlan.FREE
