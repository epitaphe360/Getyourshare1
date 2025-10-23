"""
Endpoints API pour le système d'abonnement SaaS
Tous les endpoints liés aux plans, abonnements, paiements et factures
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

from subscription_helpers import *
from payment_service import PaymentService
from invoice_service import InvoiceService
import jwt
import os

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

# Configuration JWT
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-please-set-env-variable")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


# ============================================
# MODELS
# ============================================

class SubscriptionCreate(BaseModel):
    plan_id: str
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    payment_method_id: Optional[str] = None
    coupon_code: Optional[str] = None
    start_trial: bool = False


class SubscriptionUpdate(BaseModel):
    auto_renew: Optional[bool] = None
    payment_method_id: Optional[str] = None


class SubscriptionCancel(BaseModel):
    reason: Optional[str] = None
    immediate: bool = False


class PlanUpgrade(BaseModel):
    new_plan_id: str


class PaymentMethodCreate(BaseModel):
    payment_type: str = Field(..., pattern="^(card|bank_transfer|wallet)$")
    provider: str
    stripe_payment_method_id: Optional[str] = None
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    set_default: bool = False


class CouponValidate(BaseModel):
    coupon_code: str
    plan_id: str


class StripeWebhook(BaseModel):
    pass  # Le corps sera traité directement


# ============================================
# HELPER - Extraction User ID du JWT
# ============================================

def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extrait l'ID utilisateur du token JWT"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================
# ENDPOINTS - SUBSCRIPTION PLANS
# ============================================

@router.get("/plans")
async def get_subscription_plans(user_type: Optional[str] = None):
    """Récupère tous les plans d'abonnement disponibles"""
    try:
        plans = get_all_plans(user_type=user_type, active_only=True)
        return {"success": True, "plans": plans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}")
async def get_plan_detail(plan_id: str):
    """Récupère les détails d'un plan spécifique"""
    try:
        plan = get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return {"success": True, "plan": plan}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - USER SUBSCRIPTION
# ============================================

@router.get("/my-subscription")
async def get_my_subscription(user_id: str = Depends(get_current_user_id)):
    """Récupère l'abonnement actuel de l'utilisateur"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            return {
                "success": True,
                "has_subscription": False,
                "message": "No active subscription"
            }

        # Récupérer l'usage actuel
        usage = get_current_usage(subscription["id"])

        return {
            "success": True,
            "has_subscription": True,
            "subscription": subscription,
            "usage": usage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscribe")
async def subscribe_to_plan(
    data: SubscriptionCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Crée un nouvel abonnement pour l'utilisateur"""
    try:
        # Vérifier si l'utilisateur a déjà un abonnement
        existing = get_user_subscription(user_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already has an active subscription. Please cancel or upgrade instead."
            )

        # Créer l'abonnement
        subscription = create_subscription(
            user_id=user_id,
            plan_id=data.plan_id,
            billing_cycle=data.billing_cycle,
            payment_method_id=data.payment_method_id,
            coupon_code=data.coupon_code,
            trial=data.start_trial
        )

        if not subscription:
            raise HTTPException(status_code=400, detail="Failed to create subscription")

        # Si pas en période d'essai et méthode de paiement fournie, créer le premier paiement
        if not data.start_trial and data.payment_method_id:
            plan = get_plan_by_id(data.plan_id)
            amount = float(plan["price_monthly"] if data.billing_cycle == "monthly" else plan["price_yearly"])

            # Appliquer les réductions si coupon
            if data.coupon_code:
                coupon = get_coupon_by_code(data.coupon_code)
                if coupon and is_coupon_valid(coupon, data.plan_id, user_id):
                    if coupon["discount_type"] == "percentage":
                        amount = amount * (1 - coupon["discount_value"] / 100)
                    else:
                        amount = max(0, amount - float(coupon["discount_value"]))

            # Créer le paiement
            payment_result = PaymentService.create_subscription_payment(
                user_id=user_id,
                subscription_id=subscription["id"],
                amount=amount,
                payment_method_id=data.payment_method_id,
                description=f"Subscription - {plan['name']}"
            )

            if not payment_result["success"]:
                # Annuler l'abonnement si le paiement échoue
                cancel_subscription(subscription["id"], reason="Initial payment failed", immediate=True)
                raise HTTPException(status_code=402, detail="Payment failed")

        return {
            "success": True,
            "subscription": subscription,
            "message": "Subscription created successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/my-subscription")
async def update_my_subscription(
    data: SubscriptionUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Met à jour l'abonnement de l'utilisateur"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        from supabase_client import supabase
        update_data = {}

        if data.auto_renew is not None:
            update_data["auto_renew"] = data.auto_renew

        if data.payment_method_id:
            update_data["payment_method_id"] = data.payment_method_id

        if update_data:
            supabase.table("subscriptions").update(update_data).eq("id", subscription["id"]).execute()

        return {"success": True, "message": "Subscription updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/my-subscription/cancel")
async def cancel_my_subscription(
    data: SubscriptionCancel,
    user_id: str = Depends(get_current_user_id)
):
    """Annule l'abonnement de l'utilisateur"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        success = cancel_subscription(
            subscription_id=subscription["id"],
            reason=data.reason,
            immediate=data.immediate
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel subscription")

        return {
            "success": True,
            "message": "Subscription canceled successfully" if data.immediate else "Subscription will be canceled at the end of the billing period"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/my-subscription/upgrade")
async def upgrade_my_subscription(
    data: PlanUpgrade,
    user_id: str = Depends(get_current_user_id)
):
    """Upgrade l'abonnement vers un plan supérieur"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        updated_subscription = upgrade_subscription(subscription["id"], data.new_plan_id)

        if not updated_subscription:
            raise HTTPException(status_code=400, detail="Failed to upgrade subscription")

        return {
            "success": True,
            "subscription": updated_subscription,
            "message": "Subscription upgraded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/my-subscription/downgrade")
async def downgrade_my_subscription(
    data: PlanUpgrade,
    user_id: str = Depends(get_current_user_id)
):
    """Downgrade l'abonnement vers un plan inférieur"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        updated_subscription = downgrade_subscription(subscription["id"], data.new_plan_id)

        if not updated_subscription:
            raise HTTPException(status_code=400, detail="Failed to downgrade subscription")

        return {
            "success": True,
            "subscription": updated_subscription,
            "message": "Downgrade scheduled for next billing period"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - PAYMENT METHODS
# ============================================

@router.get("/payment-methods")
async def get_my_payment_methods(user_id: str = Depends(get_current_user_id)):
    """Récupère les méthodes de paiement de l'utilisateur"""
    try:
        payment_methods = get_user_payment_methods(user_id)
        return {"success": True, "payment_methods": payment_methods}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment-methods")
async def add_my_payment_method(
    data: PaymentMethodCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Ajoute une nouvelle méthode de paiement"""
    try:
        payment_method = add_payment_method(
            user_id=user_id,
            payment_type=data.payment_type,
            provider=data.provider,
            stripe_payment_method_id=data.stripe_payment_method_id,
            card_brand=data.card_brand,
            card_last4=data.card_last4,
            card_exp_month=data.card_exp_month,
            card_exp_year=data.card_exp_year,
            set_default=data.set_default
        )

        if not payment_method:
            raise HTTPException(status_code=400, detail="Failed to add payment method")

        return {
            "success": True,
            "payment_method": payment_method,
            "message": "Payment method added successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/payment-methods/{payment_method_id}/set-default")
async def set_payment_method_as_default(
    payment_method_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Définit une méthode de paiement comme défaut"""
    try:
        success = set_default_payment_method(payment_method_id, user_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to set default payment method")

        return {"success": True, "message": "Default payment method updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/payment-methods/{payment_method_id}")
async def delete_my_payment_method(
    payment_method_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Supprime une méthode de paiement"""
    try:
        success = delete_payment_method(payment_method_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete payment method")

        return {"success": True, "message": "Payment method deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - INVOICES
# ============================================

@router.get("/invoices")
async def get_my_invoices(
    limit: int = 20,
    user_id: str = Depends(get_current_user_id)
):
    """Récupère les factures de l'utilisateur"""
    try:
        invoices = get_user_invoices(user_id, limit)
        return {"success": True, "invoices": invoices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}")
async def get_invoice_detail(
    invoice_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Récupère les détails d'une facture"""
    try:
        invoice = get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Vérifier que la facture appartient à l'utilisateur
        if invoice["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return {"success": True, "invoice": invoice}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Télécharge le PDF d'une facture"""
    try:
        # Vérifier que la facture appartient à l'utilisateur
        invoice = get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        if invoice["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Générer le PDF
        pdf_bytes = InvoiceService.generate_invoice_pdf(invoice_id)
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")

        # Retourner le PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=invoice-{invoice['invoice_number']}.pdf"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - COUPONS
# ============================================

@router.post("/coupons/validate")
async def validate_coupon(
    data: CouponValidate,
    user_id: str = Depends(get_current_user_id)
):
    """Valide un code coupon"""
    try:
        coupon = get_coupon_by_code(data.coupon_code)
        if not coupon:
            raise HTTPException(status_code=404, detail="Coupon not found")

        is_valid = is_coupon_valid(coupon, data.plan_id, user_id)

        if not is_valid:
            return {
                "success": False,
                "valid": False,
                "message": "Coupon is not valid for this plan or user"
            }

        # Calculer le montant de la réduction
        plan = get_plan_by_id(data.plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        discount_amount = 0
        if coupon["discount_type"] == "percentage":
            discount_amount = float(plan["price_monthly"]) * (coupon["discount_value"] / 100)
        else:
            discount_amount = float(coupon["discount_value"])

        return {
            "success": True,
            "valid": True,
            "coupon": coupon,
            "discount_amount": discount_amount,
            "message": "Coupon is valid"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - USAGE
# ============================================

@router.get("/usage")
async def get_my_usage(user_id: str = Depends(get_current_user_id)):
    """Récupère l'usage actuel de l'utilisateur"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            return {
                "success": True,
                "has_subscription": False,
                "message": "No active subscription"
            }

        usage = get_current_usage(subscription["id"])
        plan = subscription["subscription_plans"]

        return {
            "success": True,
            "usage": usage,
            "limits": {
                "max_products": plan.get("max_products"),
                "max_campaigns": plan.get("max_campaigns"),
                "max_affiliates": plan.get("max_affiliates")
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/check/{limit_type}")
async def check_usage_limit_endpoint(
    limit_type: str,
    user_id: str = Depends(get_current_user_id)
):
    """Vérifie si l'utilisateur a atteint une limite"""
    try:
        result = check_usage_limit(user_id, limit_type)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - WEBHOOKS
# ============================================

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Webhook Stripe pour les événements de paiement"""
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")

        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")

        result = PaymentService.handle_webhook(payload, signature)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Webhook processing failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - SUBSCRIPTION EVENTS
# ============================================

@router.get("/events")
async def get_subscription_events(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id)
):
    """Récupère l'historique des événements d'abonnement"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            return {
                "success": True,
                "has_subscription": False,
                "events": []
            }

        events = get_subscription_events(subscription["id"], limit)
        return {"success": True, "events": events}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - ADMIN (à protéger avec un middleware admin)
# ============================================

@router.get("/admin/all")
async def get_all_subscriptions():
    """Récupère tous les abonnements (admin uniquement)"""
    # TODO: Ajouter vérification admin
    try:
        from supabase_client import supabase
        result = supabase.table("subscriptions").select("""
            *,
            users:user_id (email),
            subscription_plans:plan_id (name, slug)
        """).execute()

        return {"success": True, "subscriptions": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/stats")
async def get_subscription_stats():
    """Récupère les statistiques d'abonnement (admin uniquement)"""
    # TODO: Ajouter vérification admin
    try:
        from supabase_client import supabase

        # Compter les abonnements par statut
        subscriptions = supabase.table("subscriptions").select("status").execute()
        status_counts = {}
        for sub in subscriptions.data:
            status = sub["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        # Revenue total
        invoices = supabase.table("invoices").select("total").eq("status", "paid").execute()
        total_revenue = sum([float(inv["total"]) for inv in invoices.data])

        # MRR (Monthly Recurring Revenue)
        active_subscriptions = supabase.table("subscriptions").select("""
            *,
            subscription_plans:plan_id (price_monthly)
        """).eq("status", "active").eq("billing_cycle", "monthly").execute()

        mrr = sum([float(sub["subscription_plans"]["price_monthly"]) for sub in active_subscriptions.data])

        return {
            "success": True,
            "stats": {
                "total_subscriptions": len(subscriptions.data),
                "by_status": status_counts,
                "total_revenue": total_revenue,
                "mrr": mrr
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
