"""
Fonctions helpers pour la gestion des abonnements SaaS
Gestion complète des plans, souscriptions, paiements et facturation
"""

from supabase_client import supabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import random
import string

# ============================================
# SUBSCRIPTION PLANS
# ============================================

def get_all_plans(user_type: Optional[str] = None, active_only: bool = True) -> List[Dict]:
    """Récupère tous les plans d'abonnement"""
    try:
        query = supabase.table("subscription_plans").select("*")

        if user_type:
            query = query.eq("user_type", user_type)
        if active_only:
            query = query.eq("is_active", True)

        result = query.order("display_order").execute()
        return result.data
    except Exception as e:
        print(f"Error getting subscription plans: {e}")
        return []

def get_plan_by_id(plan_id: str) -> Optional[Dict]:
    """Récupère un plan par ID"""
    try:
        result = supabase.table("subscription_plans").select("*").eq("id", plan_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting plan: {e}")
        return None

def get_plan_by_slug(slug: str) -> Optional[Dict]:
    """Récupère un plan par slug"""
    try:
        result = supabase.table("subscription_plans").select("*").eq("slug", slug).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting plan by slug: {e}")
        return None

# ============================================
# SUBSCRIPTIONS
# ============================================

def get_user_subscription(user_id: str) -> Optional[Dict]:
    """Récupère l'abonnement actif d'un utilisateur"""
    try:
        result = supabase.table("subscriptions").select("""
            *,
            subscription_plans:plan_id (
                id,
                name,
                slug,
                price_monthly,
                price_yearly,
                max_products,
                max_campaigns,
                max_affiliates,
                ai_content_generation,
                advanced_analytics,
                priority_support,
                custom_branding,
                api_access,
                export_data,
                commission_rate,
                features
            ),
            payment_methods:payment_method_id (
                id,
                payment_type,
                card_brand,
                card_last4,
                card_exp_month,
                card_exp_year
            )
        """).eq("user_id", user_id).in_("status", ["active", "trialing"]).execute()

        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user subscription: {e}")
        return None

def get_subscription_by_id(subscription_id: str) -> Optional[Dict]:
    """Récupère un abonnement par ID"""
    try:
        result = supabase.table("subscriptions").select("""
            *,
            subscription_plans:plan_id (*)
        """).eq("id", subscription_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting subscription: {e}")
        return None

def create_subscription(
    user_id: str,
    plan_id: str,
    billing_cycle: str = "monthly",
    payment_method_id: Optional[str] = None,
    coupon_code: Optional[str] = None,
    trial: bool = False
) -> Optional[Dict]:
    """Crée un nouvel abonnement"""
    try:
        # Vérifier si l'utilisateur a déjà un abonnement actif
        existing = get_user_subscription(user_id)
        if existing:
            print(f"User {user_id} already has an active subscription")
            return None

        # Récupérer le plan
        plan = get_plan_by_id(plan_id)
        if not plan:
            print(f"Plan {plan_id} not found")
            return None

        # Calculer les dates
        start_date = datetime.now()

        # Période d'essai
        trial_end_date = None
        if trial and plan.get("trial_days", 0) > 0:
            trial_end_date = start_date + timedelta(days=plan["trial_days"])

        # Période de facturation
        if billing_cycle == "monthly":
            period_end = start_date + timedelta(days=30)
        else:  # yearly
            period_end = start_date + timedelta(days=365)

        # Appliquer le coupon si fourni
        discount_amount = 0.00
        discount_percentage = 0.00
        if coupon_code:
            coupon = get_coupon_by_code(coupon_code)
            if coupon and is_coupon_valid(coupon, plan_id, user_id):
                if coupon["discount_type"] == "percentage":
                    discount_percentage = coupon["discount_value"]
                else:
                    discount_amount = coupon["discount_value"]

                # Incrémenter le compteur d'utilisation
                increment_coupon_usage(coupon["id"])

        # Créer l'abonnement
        subscription_data = {
            "user_id": user_id,
            "plan_id": plan_id,
            "status": "trialing" if trial_end_date else "active",
            "start_date": start_date.isoformat(),
            "trial_end_date": trial_end_date.isoformat() if trial_end_date else None,
            "billing_cycle": billing_cycle,
            "current_period_start": start_date.isoformat(),
            "current_period_end": period_end.isoformat(),
            "next_billing_date": trial_end_date.isoformat() if trial_end_date else period_end.isoformat(),
            "payment_method_id": payment_method_id,
            "auto_renew": True,
            "coupon_code": coupon_code,
            "discount_amount": discount_amount,
            "discount_percentage": discount_percentage
        }

        result = supabase.table("subscriptions").insert(subscription_data).execute()

        if result.data:
            subscription = result.data[0]
            # Log l'événement
            log_subscription_event(subscription["id"], user_id, "created", "Subscription created")

            # Créer l'enregistrement d'usage
            create_usage_record(subscription["id"], user_id, start_date, period_end)

            return subscription

        return None
    except Exception as e:
        print(f"Error creating subscription: {e}")
        return None

def update_subscription_status(subscription_id: str, status: str, reason: Optional[str] = None) -> bool:
    """Met à jour le statut d'un abonnement"""
    try:
        update_data = {"status": status}

        if status == "canceled":
            update_data["canceled_at"] = datetime.now().isoformat()
            update_data["cancellation_reason"] = reason
            update_data["auto_renew"] = False

        result = supabase.table("subscriptions").update(update_data).eq("id", subscription_id).execute()

        if result.data:
            subscription = result.data[0]
            log_subscription_event(subscription_id, subscription["user_id"], f"status_changed_to_{status}", reason)
            return True

        return False
    except Exception as e:
        print(f"Error updating subscription status: {e}")
        return False

def cancel_subscription(subscription_id: str, reason: Optional[str] = None, immediate: bool = False) -> bool:
    """Annule un abonnement"""
    try:
        subscription = get_subscription_by_id(subscription_id)
        if not subscription:
            return False

        if immediate:
            # Annulation immédiate
            update_data = {
                "status": "canceled",
                "canceled_at": datetime.now().isoformat(),
                "cancellation_reason": reason,
                "auto_renew": False,
                "end_date": datetime.now().isoformat()
            }
        else:
            # Annulation à la fin de la période
            update_data = {
                "auto_renew": False,
                "cancellation_reason": reason,
                "end_date": subscription["current_period_end"]
            }

        result = supabase.table("subscriptions").update(update_data).eq("id", subscription_id).execute()

        if result.data:
            log_subscription_event(subscription_id, subscription["user_id"], "canceled", reason)
            return True

        return False
    except Exception as e:
        print(f"Error canceling subscription: {e}")
        return False

def upgrade_subscription(subscription_id: str, new_plan_id: str) -> Optional[Dict]:
    """Upgrade un abonnement vers un plan supérieur"""
    try:
        subscription = get_subscription_by_id(subscription_id)
        if not subscription:
            return None

        old_plan = subscription["subscription_plans"]
        new_plan = get_plan_by_id(new_plan_id)

        if not new_plan:
            return None

        # Calculer le prorata
        now = datetime.now()
        period_end = datetime.fromisoformat(subscription["current_period_end"].replace('Z', '+00:00'))
        days_remaining = (period_end - now).days

        if subscription["billing_cycle"] == "monthly":
            old_price = float(old_plan["price_monthly"])
            new_price = float(new_plan["price_monthly"])
            total_days = 30
        else:
            old_price = float(old_plan["price_yearly"])
            new_price = float(new_plan["price_yearly"])
            total_days = 365

        daily_old = old_price / total_days
        daily_new = new_price / total_days

        prorated_amount = (daily_new - daily_old) * days_remaining

        # Mettre à jour l'abonnement
        update_data = {
            "plan_id": new_plan_id,
            "prorated_amount": max(0, prorated_amount)
        }

        result = supabase.table("subscriptions").update(update_data).eq("id", subscription_id).execute()

        if result.data:
            log_subscription_event(
                subscription_id,
                subscription["user_id"],
                "upgraded",
                f"Upgraded from {old_plan['name']} to {new_plan['name']}",
                old_data={"plan_id": old_plan["id"]},
                new_data={"plan_id": new_plan_id}
            )
            return result.data[0]

        return None
    except Exception as e:
        print(f"Error upgrading subscription: {e}")
        return None

def downgrade_subscription(subscription_id: str, new_plan_id: str) -> Optional[Dict]:
    """Downgrade un abonnement vers un plan inférieur (prend effet à la prochaine période)"""
    try:
        subscription = get_subscription_by_id(subscription_id)
        if not subscription:
            return None

        # Pour un downgrade, on stocke le changement dans metadata et il prendra effet à la prochaine période
        metadata = subscription.get("metadata", {}) or {}
        metadata["pending_plan_change"] = new_plan_id

        result = supabase.table("subscriptions").update({"metadata": metadata}).eq("id", subscription_id).execute()

        if result.data:
            log_subscription_event(
                subscription_id,
                subscription["user_id"],
                "downgrade_scheduled",
                f"Downgrade scheduled to plan {new_plan_id} at next billing"
            )
            return result.data[0]

        return None
    except Exception as e:
        print(f"Error downgrading subscription: {e}")
        return None

# ============================================
# PAYMENT METHODS
# ============================================

def get_user_payment_methods(user_id: str) -> List[Dict]:
    """Récupère les méthodes de paiement d'un utilisateur"""
    try:
        result = supabase.table("payment_methods").select("*").eq("user_id", user_id).order("is_default", desc=True).execute()
        return result.data
    except Exception as e:
        print(f"Error getting payment methods: {e}")
        return []

def get_default_payment_method(user_id: str) -> Optional[Dict]:
    """Récupère la méthode de paiement par défaut"""
    try:
        result = supabase.table("payment_methods").select("*").eq("user_id", user_id).eq("is_default", True).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting default payment method: {e}")
        return None

def add_payment_method(
    user_id: str,
    payment_type: str,
    provider: str,
    stripe_payment_method_id: Optional[str] = None,
    card_brand: Optional[str] = None,
    card_last4: Optional[str] = None,
    card_exp_month: Optional[int] = None,
    card_exp_year: Optional[int] = None,
    set_default: bool = False
) -> Optional[Dict]:
    """Ajoute une nouvelle méthode de paiement"""
    try:
        # Si set_default, retirer le default des autres
        if set_default:
            supabase.table("payment_methods").update({"is_default": False}).eq("user_id", user_id).execute()

        payment_data = {
            "user_id": user_id,
            "payment_type": payment_type,
            "provider": provider,
            "stripe_payment_method_id": stripe_payment_method_id,
            "card_brand": card_brand,
            "card_last4": card_last4,
            "card_exp_month": card_exp_month,
            "card_exp_year": card_exp_year,
            "is_default": set_default,
            "is_verified": True  # En production, vérifier via Stripe
        }

        result = supabase.table("payment_methods").insert(payment_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error adding payment method: {e}")
        return None

def set_default_payment_method(payment_method_id: str, user_id: str) -> bool:
    """Définit une méthode de paiement comme défaut"""
    try:
        # Retirer le default des autres
        supabase.table("payment_methods").update({"is_default": False}).eq("user_id", user_id).execute()

        # Définir la nouvelle par défaut
        result = supabase.table("payment_methods").update({"is_default": True}).eq("id", payment_method_id).execute()
        return bool(result.data)
    except Exception as e:
        print(f"Error setting default payment method: {e}")
        return False

def delete_payment_method(payment_method_id: str) -> bool:
    """Supprime une méthode de paiement"""
    try:
        result = supabase.table("payment_methods").delete().eq("id", payment_method_id).execute()
        return bool(result.data)
    except Exception as e:
        print(f"Error deleting payment method: {e}")
        return False

# ============================================
# INVOICES
# ============================================

def generate_invoice_number() -> str:
    """Génère un numéro de facture unique"""
    year = datetime.now().year
    month = datetime.now().month
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"INV-{year}{month:02d}-{random_suffix}"

def create_invoice(
    user_id: str,
    subscription_id: str,
    subtotal: float,
    discount: float = 0.00,
    tax: float = 0.00,
    items: List[Dict] = None,
    payment_method: str = None
) -> Optional[Dict]:
    """Crée une facture"""
    try:
        total = subtotal - discount + tax
        invoice_number = generate_invoice_number()

        invoice_data = {
            "invoice_number": invoice_number,
            "user_id": user_id,
            "subscription_id": subscription_id,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": total,
            "status": "pending",
            "issue_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "payment_method": payment_method,
            "items": items or []
        }

        result = supabase.table("invoices").insert(invoice_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating invoice: {e}")
        return None

def get_user_invoices(user_id: str, limit: int = 20) -> List[Dict]:
    """Récupère les factures d'un utilisateur"""
    try:
        result = supabase.table("invoices").select("""
            *,
            subscriptions:subscription_id (
                subscription_plans:plan_id (
                    name
                )
            )
        """).eq("user_id", user_id).order("issue_date", desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"Error getting invoices: {e}")
        return []

def get_invoice_by_id(invoice_id: str) -> Optional[Dict]:
    """Récupère une facture par ID"""
    try:
        result = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting invoice: {e}")
        return None

def mark_invoice_paid(invoice_id: str, payment_intent_id: Optional[str] = None) -> bool:
    """Marque une facture comme payée"""
    try:
        update_data = {
            "status": "paid",
            "paid_at": datetime.now().isoformat(),
            "payment_intent_id": payment_intent_id
        }

        result = supabase.table("invoices").update(update_data).eq("id", invoice_id).execute()
        return bool(result.data)
    except Exception as e:
        print(f"Error marking invoice paid: {e}")
        return False

# ============================================
# PAYMENT TRANSACTIONS
# ============================================

def create_transaction(
    user_id: str,
    subscription_id: str,
    invoice_id: Optional[str],
    transaction_type: str,
    amount: float,
    payment_provider: str,
    provider_transaction_id: Optional[str] = None,
    status: str = "pending"
) -> Optional[Dict]:
    """Crée une transaction de paiement"""
    try:
        transaction_data = {
            "user_id": user_id,
            "subscription_id": subscription_id,
            "invoice_id": invoice_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "payment_provider": payment_provider,
            "provider_transaction_id": provider_transaction_id,
            "status": status
        }

        result = supabase.table("payment_transactions").insert(transaction_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating transaction: {e}")
        return None

def update_transaction_status(
    transaction_id: str,
    status: str,
    provider_response: Optional[Dict] = None,
    failure_code: Optional[str] = None,
    failure_message: Optional[str] = None
) -> bool:
    """Met à jour le statut d'une transaction"""
    try:
        update_data = {"status": status}

        if provider_response:
            update_data["provider_response"] = provider_response
        if failure_code:
            update_data["failure_code"] = failure_code
        if failure_message:
            update_data["failure_message"] = failure_message

        result = supabase.table("payment_transactions").update(update_data).eq("id", transaction_id).execute()
        return bool(result.data)
    except Exception as e:
        print(f"Error updating transaction: {e}")
        return False

def get_user_transactions(user_id: str, limit: int = 50) -> List[Dict]:
    """Récupère les transactions d'un utilisateur"""
    try:
        result = supabase.table("payment_transactions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"Error getting transactions: {e}")
        return []

# ============================================
# COUPONS
# ============================================

def get_coupon_by_code(code: str) -> Optional[Dict]:
    """Récupère un coupon par code"""
    try:
        result = supabase.table("subscription_coupons").select("*").eq("code", code.upper()).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting coupon: {e}")
        return None

def is_coupon_valid(coupon: Dict, plan_id: str, user_id: str) -> bool:
    """Vérifie si un coupon est valide"""
    try:
        # Vérifier si actif
        if not coupon.get("is_active"):
            return False

        # Vérifier dates
        now = datetime.now()
        if coupon.get("valid_from"):
            valid_from = datetime.fromisoformat(coupon["valid_from"].replace('Z', '+00:00'))
            if now < valid_from:
                return False

        if coupon.get("valid_until"):
            valid_until = datetime.fromisoformat(coupon["valid_until"].replace('Z', '+00:00'))
            if now > valid_until:
                return False

        # Vérifier nombre d'utilisations
        if coupon.get("max_redemptions"):
            if coupon.get("redemptions_count", 0) >= coupon["max_redemptions"]:
                return False

        # Vérifier si premier abonnement seulement
        if coupon.get("first_time_only"):
            # Vérifier si l'utilisateur a déjà eu un abonnement
            result = supabase.table("subscriptions").select("id").eq("user_id", user_id).execute()
            if result.data:
                return False

        # Vérifier applicabilité au plan
        if coupon.get("applicable_to") == "specific_plans":
            plan_ids = coupon.get("plan_ids", [])
            if plan_id not in plan_ids:
                return False

        return True
    except Exception as e:
        print(f"Error validating coupon: {e}")
        return False

def increment_coupon_usage(coupon_id: str) -> bool:
    """Incrémente le compteur d'utilisation d'un coupon"""
    try:
        coupon = supabase.table("subscription_coupons").select("redemptions_count").eq("id", coupon_id).execute()
        if coupon.data:
            current_count = coupon.data[0].get("redemptions_count", 0)
            supabase.table("subscription_coupons").update({"redemptions_count": current_count + 1}).eq("id", coupon_id).execute()
            return True
        return False
    except Exception as e:
        print(f"Error incrementing coupon usage: {e}")
        return False

# ============================================
# SUBSCRIPTION USAGE
# ============================================

def create_usage_record(subscription_id: str, user_id: str, period_start: datetime, period_end: datetime) -> Optional[Dict]:
    """Crée un enregistrement d'usage pour une période"""
    try:
        usage_data = {
            "subscription_id": subscription_id,
            "user_id": user_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "products_count": 0,
            "campaigns_count": 0,
            "affiliates_count": 0,
            "ai_requests_count": 0,
            "api_calls_count": 0
        }

        result = supabase.table("subscription_usage").insert(usage_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating usage record: {e}")
        return None

def get_current_usage(subscription_id: str) -> Optional[Dict]:
    """Récupère l'usage actuel d'un abonnement"""
    try:
        result = supabase.table("subscription_usage").select("*").eq("subscription_id", subscription_id).order("period_start", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting current usage: {e}")
        return None

def increment_usage(subscription_id: str, metric: str) -> bool:
    """Incrémente un compteur d'usage"""
    try:
        usage = get_current_usage(subscription_id)
        if not usage:
            return False

        current_value = usage.get(metric, 0)
        supabase.table("subscription_usage").update({metric: current_value + 1}).eq("id", usage["id"]).execute()
        return True
    except Exception as e:
        print(f"Error incrementing usage: {e}")
        return False

def check_usage_limit(user_id: str, limit_type: str) -> Dict[str, Any]:
    """Vérifie si l'utilisateur a atteint une limite d'usage"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            return {"allowed": False, "reason": "No active subscription"}

        plan = subscription["subscription_plans"]
        usage = get_current_usage(subscription["id"])

        if not usage:
            return {"allowed": True, "current": 0, "limit": None}

        limit_map = {
            "products": ("products_count", "max_products"),
            "campaigns": ("campaigns_count", "max_campaigns"),
            "affiliates": ("affiliates_count", "max_affiliates")
        }

        if limit_type not in limit_map:
            return {"allowed": True}

        usage_key, limit_key = limit_map[limit_type]
        current = usage.get(usage_key, 0)
        limit = plan.get(limit_key)

        if limit is None:  # Illimité
            return {"allowed": True, "current": current, "limit": None}

        allowed = current < limit
        return {
            "allowed": allowed,
            "current": current,
            "limit": limit,
            "remaining": max(0, limit - current)
        }
    except Exception as e:
        print(f"Error checking usage limit: {e}")
        return {"allowed": False, "reason": str(e)}

# ============================================
# SUBSCRIPTION EVENTS
# ============================================

def log_subscription_event(
    subscription_id: str,
    user_id: str,
    event_type: str,
    description: str,
    old_data: Optional[Dict] = None,
    new_data: Optional[Dict] = None
) -> Optional[Dict]:
    """Log un événement lié à un abonnement"""
    try:
        event_data = {
            "subscription_id": subscription_id,
            "user_id": user_id,
            "event_type": event_type,
            "description": description,
            "old_data": old_data,
            "new_data": new_data
        }

        result = supabase.table("subscription_events").insert(event_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error logging subscription event: {e}")
        return None

def get_subscription_events(subscription_id: str, limit: int = 50) -> List[Dict]:
    """Récupère l'historique des événements d'un abonnement"""
    try:
        result = supabase.table("subscription_events").select("*").eq("subscription_id", subscription_id).order("created_at", desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"Error getting subscription events: {e}")
        return []

# ============================================
# UTILITY FUNCTIONS
# ============================================

def is_subscription_active(user_id: str) -> bool:
    """Vérifie si un utilisateur a un abonnement actif"""
    subscription = get_user_subscription(user_id)
    return subscription is not None and subscription["status"] in ["active", "trialing"]

def has_feature_access(user_id: str, feature: str) -> bool:
    """Vérifie si un utilisateur a accès à une fonctionnalité"""
    subscription = get_user_subscription(user_id)
    if not subscription:
        return False

    plan = subscription["subscription_plans"]
    return plan.get(feature, False)

def get_subscription_summary(user_id: str) -> Dict[str, Any]:
    """Récupère un résumé complet de l'abonnement d'un utilisateur"""
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            return {"has_subscription": False}

        plan = subscription["subscription_plans"]
        usage = get_current_usage(subscription["id"])

        return {
            "has_subscription": True,
            "subscription": subscription,
            "plan": plan,
            "usage": usage,
            "is_trial": subscription["status"] == "trialing",
            "auto_renew": subscription["auto_renew"],
            "next_billing_date": subscription["next_billing_date"],
            "features": plan["features"]
        }
    except Exception as e:
        print(f"Error getting subscription summary: {e}")
        return {"has_subscription": False, "error": str(e)}
