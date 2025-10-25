"""
API Endpoints Stripe - Gestion Abonnements SaaS

Endpoints:
- POST /api/stripe/create-subscription - Créer abonnement
- POST /api/stripe/cancel-subscription - Annuler abonnement
- POST /api/stripe/reactivate-subscription - Réactiver
- PUT /api/stripe/update-subscription - Changer de plan
- GET /api/stripe/portal - Customer Portal Stripe
- POST /api/stripe/webhook - Webhook Stripe
- GET /api/stripe/plans - Liste des plans disponibles
- GET /api/stripe/subscription - Info abonnement actuel
- GET /api/stripe/invoices - Historique factures
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import structlog

from services.stripe_service import (
    StripeService,
    SubscriptionPlan,
    SUBSCRIPTION_PLANS
)
from auth import get_current_user

router = APIRouter(prefix="/api/stripe", tags=["Stripe"])
logger = structlog.get_logger()

# ============================================
# MODÈLES PYDANTIC
# ============================================

class CreateSubscriptionRequest(BaseModel):
    """Requête création abonnement"""
    plan: str = Field(..., description="Plan: starter, pro, enterprise")
    billing_cycle: str = Field("monthly", description="monthly ou yearly")
    payment_method_id: Optional[str] = Field(None, description="Stripe Payment Method ID")

    @validator('plan')
    def validate_plan(cls, v):
        if v not in ['starter', 'pro', 'enterprise']:
            raise ValueError('Plan must be starter, pro, or enterprise')
        return v

    @validator('billing_cycle')
    def validate_cycle(cls, v):
        if v not in ['monthly', 'yearly']:
            raise ValueError('Billing cycle must be monthly or yearly')
        return v


class UpdateSubscriptionRequest(BaseModel):
    """Requête modification abonnement"""
    new_plan: str = Field(..., description="Nouveau plan")
    billing_cycle: str = Field("monthly", description="monthly ou yearly")

    @validator('new_plan')
    def validate_plan(cls, v):
        if v not in ['starter', 'pro', 'enterprise']:
            raise ValueError('Plan must be starter, pro, or enterprise')
        return v


class CancelSubscriptionRequest(BaseModel):
    """Requête annulation abonnement"""
    cancel_immediately: bool = Field(False, description="Annuler immédiatement ou à la fin de la période")
    cancellation_reason: Optional[str] = Field(None, max_length=500)


class SubscriptionResponse(BaseModel):
    """Réponse info abonnement"""
    plan: str
    status: str
    billing_cycle: Optional[str]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    trial_end: Optional[datetime]
    features: dict


class InvoiceResponse(BaseModel):
    """Réponse facture"""
    id: str
    amount_paid: float
    currency: str
    status: str
    invoice_date: datetime
    invoice_pdf_url: Optional[str]
    hosted_invoice_url: Optional[str]


# ============================================
# ENDPOINTS - ABONNEMENTS
# ============================================

@router.post("/create-subscription", status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request_data: CreateSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Créer un nouvel abonnement

    Workflow:
    1. Frontend collecte payment method via Stripe Elements
    2. Frontend envoie payment_method_id à cet endpoint
    3. Backend crée l'abonnement
    4. Retourne client_secret pour confirmer le paiement
    """
    try:
        service = StripeService()

        result = await service.create_subscription(
            user_id=current_user["id"],
            email=current_user["email"],
            plan=SubscriptionPlan(request_data.plan),
            billing_cycle=request_data.billing_cycle,
            payment_method_id=request_data.payment_method_id
        )

        logger.info(
            "subscription_created",
            user_id=current_user["id"],
            plan=request_data.plan,
            subscription_id=result["subscription_id"]
        )

        return {
            "status": "success",
            "subscription_id": result["subscription_id"],
            "client_secret": result["client_secret"],
            "subscription_status": result["status"],
            "trial_end": result.get("trial_end"),
            "message": "Abonnement créé avec succès! Vous bénéficiez de 14 jours d'essai gratuit."
        }

    except ValueError as e:
        logger.warning("subscription_creation_failed", error=str(e), user_id=current_user["id"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("subscription_creation_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'abonnement"
        )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(current_user: dict = Depends(get_current_user)):
    """
    Récupérer l'abonnement actuel de l'utilisateur
    """
    try:
        # TODO: Récupérer depuis DB
        # Pour l'instant, retourner plan gratuit par défaut
        return {
            "plan": "free",
            "status": "active",
            "billing_cycle": None,
            "current_period_end": None,
            "cancel_at_period_end": False,
            "trial_end": None,
            "features": SUBSCRIPTION_PLANS[SubscriptionPlan.FREE]["features"]
        }

    except Exception as e:
        logger.error("get_subscription_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'abonnement"
        )


@router.put("/update-subscription")
async def update_subscription(
    request_data: UpdateSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Modifier le plan d'abonnement (upgrade/downgrade)

    Proration automatique gérée par Stripe
    """
    try:
        service = StripeService()

        result = await service.update_subscription_plan(
            user_id=current_user["id"],
            new_plan=SubscriptionPlan(request_data.new_plan),
            billing_cycle=request_data.billing_cycle
        )

        logger.info(
            "subscription_updated",
            user_id=current_user["id"],
            new_plan=request_data.new_plan
        )

        return {
            "status": "success",
            "new_plan": request_data.new_plan,
            "message": "Votre abonnement a été modifié avec succès!",
            "next_billing_date": result["next_billing_date"]
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("update_subscription_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la modification de l'abonnement"
        )


@router.post("/cancel-subscription")
async def cancel_subscription(
    request_data: CancelSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Annuler un abonnement

    Options:
    - Annulation immédiate: accès coupé tout de suite
    - Annulation en fin de période: accès jusqu'à la fin de la période payée
    """
    try:
        service = StripeService()

        result = await service.cancel_subscription(
            user_id=current_user["id"],
            cancel_immediately=request_data.cancel_immediately
        )

        # TODO: Sauvegarder raison annulation pour analytics
        if request_data.cancellation_reason:
            logger.info(
                "cancellation_reason",
                user_id=current_user["id"],
                reason=request_data.cancellation_reason
            )

        logger.info(
            "subscription_canceled",
            user_id=current_user["id"],
            immediate=request_data.cancel_immediately
        )

        message = (
            "Votre abonnement a été annulé. Vous gardez accès jusqu'au " +
            result["cancel_at"].strftime("%d/%m/%Y")
            if not request_data.cancel_immediately
            else "Votre abonnement a été annulé immédiatement."
        )

        return {
            "status": "success",
            "message": message,
            "access_until": result["cancel_at"]
        }

    except Exception as e:
        logger.error("cancel_subscription_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'annulation"
        )


@router.post("/reactivate-subscription")
async def reactivate_subscription(current_user: dict = Depends(get_current_user)):
    """
    Réactiver un abonnement annulé (si pas encore expiré)
    """
    try:
        service = StripeService()

        result = await service.reactivate_subscription(user_id=current_user["id"])

        logger.info("subscription_reactivated", user_id=current_user["id"])

        return {
            "status": "success",
            "message": "Votre abonnement a été réactivé avec succès!",
            "subscription_status": result["status"]
        }

    except Exception as e:
        logger.error("reactivate_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la réactivation"
        )


# ============================================
# CUSTOMER PORTAL
# ============================================

@router.get("/portal")
async def get_customer_portal(
    return_url: str = "https://shareyoursales.ma/dashboard",
    current_user: dict = Depends(get_current_user)
):
    """
    Créer une session Customer Portal Stripe

    Le portal permet de:
    - Mettre à jour le moyen de paiement
    - Voir l'historique des factures
    - Télécharger les invoices
    - Annuler l'abonnement
    """
    try:
        service = StripeService()

        portal_url = await service.create_customer_portal_session(
            user_id=current_user["id"],
            return_url=return_url
        )

        return {
            "url": portal_url
        }

    except Exception as e:
        logger.error("portal_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de la session"
        )


# ============================================
# FACTURES
# ============================================

@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer l'historique des factures
    """
    try:
        # TODO: Récupérer depuis DB
        return []

    except Exception as e:
        logger.error("get_invoices_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des factures"
        )


# ============================================
# PLANS
# ============================================

@router.get("/plans")
async def get_plans():
    """
    Récupérer la liste des plans disponibles

    Retourne les features et prix de chaque plan
    """
    plans = []

    for plan_key, plan_config in SUBSCRIPTION_PLANS.items():
        plans.append({
            "id": plan_key.value,
            "name": plan_config["name"],
            "price_monthly": plan_config["price_monthly"],
            "price_yearly": plan_config["price_yearly"],
            "features": plan_config["features"],
            "popular": plan_key == SubscriptionPlan.PRO  # Marquer Pro comme populaire
        })

    return {"plans": plans}


# ============================================
# WEBHOOKS
# ============================================

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Endpoint webhook Stripe

    Reçoit les événements Stripe en temps réel:
    - Paiement réussi/échoué
    - Abonnement créé/modifié/supprimé
    - etc.

    IMPORTANT: Cet endpoint doit être PUBLIC (pas d'auth)
    """
    try:
        payload = await request.body()

        service = StripeService()
        result = await service.handle_webhook(payload, stripe_signature)

        return {"status": "success"}

    except ValueError as e:
        logger.error("webhook_signature_error", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("webhook_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing error"
        )


# ============================================
# QUOTAS & FEATURES
# ============================================

@router.get("/quotas")
async def get_quotas(current_user: dict = Depends(get_current_user)):
    """
    Récupérer les quotas actuels de l'utilisateur

    Utile pour afficher dans le dashboard:
    - Nombre de produits utilisés / max
    - Nombre d'influenceurs / max
    - Features activées
    """
    try:
        # TODO: Récupérer depuis DB (table user_quotas)
        return {
            "products": {"current": 0, "max": 5},
            "influencers": {"current": 0, "max": 3},
            "links": {"current": 0, "max": 10},
            "features": {
                "social_media_sync": False,
                "ai_bot": False,
                "custom_domain": False,
                "api_access": False
            },
            "platform_commission_rate": 10.0
        }

    except Exception as e:
        logger.error("get_quotas_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des quotas"
        )


@router.get("/check-feature/{feature}")
async def check_feature_access(
    feature: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifier si l'utilisateur a accès à une feature

    Usage:
    - Avant d'afficher bouton "Connecter Instagram" → check social_media_sync
    - Avant d'afficher chatbot → check ai_bot
    """
    try:
        service = StripeService()

        has_access = await service.check_feature_access(
            user_id=current_user["id"],
            feature=feature
        )

        return {
            "feature": feature,
            "has_access": has_access
        }

    except Exception as e:
        logger.error("check_feature_error", error=str(e), user_id=current_user["id"])
        return {"feature": feature, "has_access": False}
