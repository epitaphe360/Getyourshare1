"""
============================================
SUBSCRIPTION MANAGEMENT ENDPOINTS
Share Your Sales - Plans d'Abonnement
============================================

Gestion des abonnements entreprise et marketplace:
- Small: 199 MAD/mois (2 membres, 1 domaine)
- Medium: 499 MAD/mois (10 membres, 2 domaines)
- Large: 799 MAD/mois (30 membres, domaines illimités)
- Marketplace: 99 MAD/mois (indépendant)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
import stripe
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

# ============================================
# ENVIRONMENT VARIABLES VALIDATION
# ============================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing required Supabase environment variables")

if not STRIPE_SECRET_KEY or not STRIPE_SECRET_KEY.startswith("sk_"):
    raise ValueError("Missing or invalid STRIPE_SECRET_KEY")

# ============================================
# SUPABASE CLIENT
# ============================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# STRIPE CONFIGURATION
# ============================================

stripe.api_key = STRIPE_SECRET_KEY
stripe.max_network_retries = 2

# ============================================
# PYDANTIC MODELS
# ============================================

class SubscriptionPlanResponse(BaseModel):
    """Plan d'abonnement disponible"""
    id: str
    name: str
    code: str
    type: str  # 'enterprise' ou 'marketplace'
    price_mad: float
    currency: str = "MAD"
    max_team_members: Optional[int]
    max_domains: Optional[int]
    features: List[str]
    description: Optional[str]
    is_active: bool
    display_order: int
    stripe_price_id: Optional[str]

class SubscribeRequest(BaseModel):
    """Demande de souscription à un plan"""
    plan_id: str
    payment_method_id: Optional[str] = None  # Stripe payment method
    trial: bool = False

class SubscriptionResponse(BaseModel):
    """Abonnement actif de l'utilisateur"""
    id: str
    user_id: str
    plan_id: str
    plan_name: str
    plan_code: str
    plan_type: str
    status: str
    trial_end: Optional[datetime]
    current_period_start: datetime
    current_period_end: datetime
    current_team_members: int
    current_domains: int
    plan_max_team_members: Optional[int]
    plan_max_domains: Optional[int]
    can_add_team_member: bool
    can_add_domain: bool

class UpgradeRequest(BaseModel):
    """Demande de changement de plan"""
    new_plan_id: str
    immediate: bool = False  # True = immédiat, False = fin de période

class CancelRequest(BaseModel):
    """Demande d'annulation d'abonnement"""
    reason: Optional[str] = None
    immediate: bool = False  # True = immédiat, False = fin de période

class UsageResponse(BaseModel):
    """Utilisation actuelle vs limites du plan"""
    plan_name: str
    team_members_used: int
    team_members_limit: Optional[int]
    team_members_available: Optional[int]
    domains_used: int
    domains_limit: Optional[int]
    domains_available: Optional[int]
    can_add_team_member: bool
    can_add_domain: bool

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_user_subscription(user_id: str) -> Optional[Dict[str, Any]]:
    """Récupère l'abonnement actif d'un utilisateur"""
    try:
        response = supabase.from_("v_active_subscriptions") \
            .select("*") \
            .eq("user_id", user_id) \
            .limit(1) \
            .execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting subscription: {e}")
        return None

async def check_limit(user_id: str, limit_type: str) -> bool:
    """Vérifie si l'utilisateur peut ajouter un membre/domaine"""
    try:
        response = supabase.rpc("check_subscription_limit", {
            "p_user_id": user_id,
            "p_limit_type": limit_type
        }).execute()

        return response.data if response.data is not None else False
    except Exception as e:
        print(f"Error checking limit: {e}")
        return False

async def create_stripe_subscription(
    user_id: str,
    email: str,
    plan_id: str,
    payment_method_id: Optional[str],
    trial: bool
) -> Dict[str, Any]:
    """Crée un abonnement Stripe"""

    # Récupérer le plan
    plan_response = supabase.from_("subscription_plans") \
        .select("*") \
        .eq("id", plan_id) \
        .single() \
        .execute()

    if not plan_response.data:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan = plan_response.data

    if not plan.get("stripe_price_id"):
        raise HTTPException(
            status_code=400,
            detail="Plan does not have Stripe integration configured"
        )

    # Créer ou récupérer le client Stripe
    customers = stripe.Customer.list(email=email, limit=1)

    if customers.data:
        customer = customers.data[0]
    else:
        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": user_id}
        )

    # Attacher le mode de paiement si fourni
    if payment_method_id:
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer.id
        )
        stripe.Customer.modify(
            customer.id,
            invoice_settings={"default_payment_method": payment_method_id}
        )

    # Créer l'abonnement Stripe
    subscription_params = {
        "customer": customer.id,
        "items": [{"price": plan["stripe_price_id"]}],
        "expand": ["latest_invoice.payment_intent"]
    }

    if trial:
        subscription_params["trial_period_days"] = 14

    stripe_subscription = stripe.Subscription.create(**subscription_params)

    return {
        "stripe_subscription_id": stripe_subscription.id,
        "stripe_customer_id": customer.id,
        "status": stripe_subscription.status,
        "current_period_start": datetime.fromtimestamp(stripe_subscription.current_period_start),
        "current_period_end": datetime.fromtimestamp(stripe_subscription.current_period_end),
        "trial_end": datetime.fromtimestamp(stripe_subscription.trial_end) if stripe_subscription.trial_end else None
    }

# ============================================
# ENDPOINTS - PLANS
# ============================================

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_available_plans():
    """
    Liste tous les plans d'abonnement disponibles

    Retourne les 4 plans:
    - Small (199 MAD): 2 membres, 1 domaine
    - Medium (499 MAD): 10 membres, 2 domaines
    - Large (799 MAD): 30 membres, domaines illimités
    - Marketplace (99 MAD): Accès marketplace pour indépendants
    """
    try:
        response = supabase.from_("subscription_plans") \
            .select("*") \
            .eq("is_active", True) \
            .order("display_order") \
            .execute()

        return response.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching plans: {str(e)}"
        )

@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_plan_details(plan_id: str):
    """Détails d'un plan spécifique"""
    try:
        response = supabase.from_("subscription_plans") \
            .select("*") \
            .eq("id", plan_id) \
            .eq("is_active", True) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        return response.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching plan: {str(e)}"
        )

# ============================================
# ENDPOINTS - SUBSCRIPTION MANAGEMENT
# ============================================

@router.get("/my-subscription", response_model=Optional[SubscriptionResponse])
async def get_my_subscription(current_user: dict = Depends(get_current_user)):
    """
    Récupère l'abonnement actif de l'utilisateur connecté

    Inclut:
    - Détails du plan
    - Utilisation actuelle (membres, domaines)
    - Limites du plan
    - Capacité à ajouter membres/domaines
    """
    try:
        subscription = await get_user_subscription(current_user["id"])

        if not subscription:
            return None

        # Vérifier les limites
        can_add_team_member = await check_limit(current_user["id"], "team_members")
        can_add_domain = await check_limit(current_user["id"], "domains")

        return {
            **subscription,
            "can_add_team_member": can_add_team_member,
            "can_add_domain": can_add_domain
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching subscription: {str(e)}"
        )

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_to_plan(
    request: SubscribeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Souscrire à un plan d'abonnement

    Process:
    1. Vérifie qu'il n'y a pas d'abonnement actif
    2. Crée l'abonnement Stripe
    3. Enregistre l'abonnement en base de données
    4. Active l'abonnement

    Paramètres:
    - plan_id: ID du plan choisi
    - payment_method_id: ID du mode de paiement Stripe (optionnel si trial)
    - trial: True pour période d'essai de 14 jours
    """
    try:
        user_id = current_user["id"]

        # Vérifier qu'il n'y a pas déjà un abonnement actif
        existing_subscription = await get_user_subscription(user_id)
        if existing_subscription:
            raise HTTPException(
                status_code=400,
                detail="You already have an active subscription"
            )

        # Créer l'abonnement Stripe
        stripe_data = await create_stripe_subscription(
            user_id=user_id,
            email=current_user["email"],
            plan_id=request.plan_id,
            payment_method_id=request.payment_method_id,
            trial=request.trial
        )

        # Créer l'abonnement en base de données
        subscription_data = {
            "user_id": user_id,
            "plan_id": request.plan_id,
            "status": "trialing" if request.trial else "active",
            "stripe_subscription_id": stripe_data["stripe_subscription_id"],
            "stripe_customer_id": stripe_data["stripe_customer_id"],
            "current_period_start": stripe_data["current_period_start"].isoformat(),
            "current_period_end": stripe_data["current_period_end"].isoformat(),
            "trial_end": stripe_data["trial_end"].isoformat() if stripe_data["trial_end"] else None,
            "current_team_members": 0,
            "current_domains": 0
        }

        response = supabase.from_("subscriptions") \
            .insert(subscription_data) \
            .execute()

        return {
            "success": True,
            "message": "Subscription created successfully",
            "subscription": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating subscription: {str(e)}"
        )

@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Changer de plan (upgrade ou downgrade)

    Options:
    - immediate=True: Changement immédiat avec prorata
    - immediate=False: Changement à la fin de la période en cours
    """
    try:
        user_id = current_user["id"]

        # Récupérer l'abonnement actuel
        subscription = await get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        # Vérifier que le nouveau plan existe
        new_plan_response = supabase.from_("subscription_plans") \
            .select("*") \
            .eq("id", request.new_plan_id) \
            .single() \
            .execute()

        if not new_plan_response.data:
            raise HTTPException(status_code=404, detail="New plan not found")

        new_plan = new_plan_response.data

        # Modifier l'abonnement Stripe
        stripe_subscription = stripe.Subscription.modify(
            subscription["stripe_subscription_id"],
            items=[{
                "id": stripe.Subscription.retrieve(subscription["stripe_subscription_id"]).items.data[0].id,
                "price": new_plan["stripe_price_id"]
            }],
            proration_behavior="always_invoice" if request.immediate else "create_prorations"
        )

        # Mettre à jour en base de données
        update_data = {"plan_id": request.new_plan_id}

        if request.immediate:
            update_data["current_period_end"] = datetime.fromtimestamp(
                stripe_subscription.current_period_end
            ).isoformat()

        supabase.from_("subscriptions") \
            .update(update_data) \
            .eq("id", subscription["id"]) \
            .execute()

        return {
            "success": True,
            "message": f"Subscription will be {'immediately' if request.immediate else 'scheduled to be'} upgraded to {new_plan['name']}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error upgrading subscription: {str(e)}"
        )

@router.post("/cancel")
async def cancel_subscription(
    request: CancelRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Annuler l'abonnement

    Options:
    - immediate=True: Annulation immédiate (remboursement prorata)
    - immediate=False: Annulation à la fin de la période en cours
    """
    try:
        user_id = current_user["id"]

        # Récupérer l'abonnement actuel
        subscription = await get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        # Annuler l'abonnement Stripe
        if request.immediate:
            stripe.Subscription.delete(subscription["stripe_subscription_id"])

            # Mettre à jour en base de données
            supabase.from_("subscriptions") \
                .update({
                    "status": "canceled",
                    "canceled_at": datetime.now().isoformat(),
                    "ended_at": datetime.now().isoformat()
                }) \
                .eq("id", subscription["id"]) \
                .execute()

            message = "Subscription canceled immediately"
        else:
            stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                cancel_at_period_end=True
            )

            # Mettre à jour en base de données
            supabase.from_("subscriptions") \
                .update({
                    "cancel_at": subscription["current_period_end"]
                }) \
                .eq("id", subscription["id"]) \
                .execute()

            message = f"Subscription will be canceled at the end of the current period ({subscription['current_period_end']})"

        # Enregistrer la raison
        if request.reason:
            supabase.from_("subscriptions") \
                .update({
                    "metadata": {"cancellation_reason": request.reason}
                }) \
                .eq("id", subscription["id"]) \
                .execute()

        return {
            "success": True,
            "message": message
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error canceling subscription: {str(e)}"
        )

@router.post("/reactivate")
async def reactivate_subscription(current_user: dict = Depends(get_current_user)):
    """Réactiver un abonnement annulé (avant la fin de période)"""
    try:
        user_id = current_user["id"]

        # Récupérer l'abonnement
        subscription = await get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No subscription found")

        if not subscription.get("cancel_at"):
            raise HTTPException(status_code=400, detail="Subscription is not scheduled for cancellation")

        # Réactiver dans Stripe
        stripe.Subscription.modify(
            subscription["stripe_subscription_id"],
            cancel_at_period_end=False
        )

        # Mettre à jour en base de données
        supabase.from_("subscriptions") \
            .update({"cancel_at": None}) \
            .eq("id", subscription["id"]) \
            .execute()

        return {
            "success": True,
            "message": "Subscription reactivated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reactivating subscription: {str(e)}"
        )

# ============================================
# ENDPOINTS - USAGE & LIMITS
# ============================================

@router.get("/usage", response_model=UsageResponse)
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    """
    Statistiques d'utilisation vs limites du plan

    Retourne:
    - Nombre de membres d'équipe utilisés vs limite
    - Nombre de domaines utilisés vs limite
    - Capacité à ajouter membres/domaines
    """
    try:
        user_id = current_user["id"]

        subscription = await get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        # Calculer les disponibilités
        team_members_available = None
        if subscription["plan_max_team_members"] is not None:
            team_members_available = subscription["plan_max_team_members"] - subscription["current_team_members"]

        domains_available = None
        if subscription["plan_max_domains"] is not None:
            domains_available = subscription["plan_max_domains"] - subscription["current_domains"]

        # Vérifier les limites
        can_add_team_member = await check_limit(user_id, "team_members")
        can_add_domain = await check_limit(user_id, "domains")

        return {
            "plan_name": subscription["plan_name"],
            "team_members_used": subscription["current_team_members"],
            "team_members_limit": subscription["plan_max_team_members"],
            "team_members_available": team_members_available,
            "domains_used": subscription["current_domains"],
            "domains_limit": subscription["plan_max_domains"],
            "domains_available": domains_available,
            "can_add_team_member": can_add_team_member,
            "can_add_domain": can_add_domain
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching usage stats: {str(e)}"
        )

# ============================================
# ENDPOINTS - ADMIN
# ============================================

@router.get("/admin/all", dependencies=[Depends(get_current_admin)])
async def get_all_subscriptions(
    status_filter: Optional[str] = None,
    plan_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    [ADMIN] Liste tous les abonnements

    Filtres:
    - status: active, trialing, canceled, etc.
    - plan_type: enterprise, marketplace
    """
    try:
        query = supabase.from_("v_active_subscriptions").select("*")

        if status_filter:
            query = query.eq("status", status_filter)

        if plan_type:
            query = query.eq("plan_type", plan_type)

        response = query.range(offset, offset + limit - 1).execute()

        return {
            "subscriptions": response.data,
            "count": len(response.data)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching subscriptions: {str(e)}"
        )

@router.get("/admin/stats", dependencies=[Depends(get_current_admin)])
async def get_subscription_stats():
    """[ADMIN] Statistiques globales des abonnements"""
    try:
        # Abonnements actifs par plan
        response = supabase.from_("v_active_subscriptions") \
            .select("plan_name, plan_code, plan_type") \
            .execute()

        subscriptions = response.data

        # Compter par plan
        plan_counts = {}
        total_mrr = 0

        for sub in subscriptions:
            plan_name = sub["plan_name"]
            if plan_name not in plan_counts:
                plan_counts[plan_name] = 0
            plan_counts[plan_name] += 1

        # Calculer MRR (Monthly Recurring Revenue)
        plans_response = supabase.from_("subscription_plans").select("*").execute()
        plans_by_code = {p["code"]: p for p in plans_response.data}

        for sub in subscriptions:
            plan = plans_by_code.get(sub["plan_code"])
            if plan:
                total_mrr += float(plan["price_mad"])

        return {
            "total_active_subscriptions": len(subscriptions),
            "subscriptions_by_plan": plan_counts,
            "monthly_recurring_revenue": total_mrr,
            "currency": "MAD"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stats: {str(e)}"
        )
