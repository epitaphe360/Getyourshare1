"""
Middleware de vérification d'abonnement
Vérifie si l'utilisateur a un abonnement actif et les accès aux fonctionnalités
"""

from fastapi import HTTPException, Header, Depends
from typing import Optional
import jwt
import os

from subscription_helpers import (
    get_user_subscription,
    has_feature_access,
    check_usage_limit,
    is_subscription_active
)

# Configuration JWT
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-please-set-env-variable")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class SubscriptionMiddleware:
    """Middleware pour vérifier l'abonnement et les accès"""

    @staticmethod
    def get_user_id_from_token(authorization: Optional[str] = Header(None)) -> str:
        """Extrait l'ID utilisateur du token JWT"""
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authorization header"
            )

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

    @staticmethod
    def require_active_subscription(user_id: str = Depends(get_user_id_from_token)) -> str:
        """
        Vérifie que l'utilisateur a un abonnement actif
        Usage: Depends(SubscriptionMiddleware.require_active_subscription)
        """
        if not is_subscription_active(user_id):
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "SUBSCRIPTION_REQUIRED",
                    "message": "An active subscription is required to access this feature",
                    "upgrade_url": "/subscription/plans"
                }
            )
        return user_id

    @staticmethod
    def require_feature(feature: str):
        """
        Crée un middleware qui vérifie l'accès à une fonctionnalité spécifique

        Usage:
        @router.get("/ai-content")
        async def generate_ai_content(
            user_id: str = Depends(SubscriptionMiddleware.require_feature("ai_content_generation"))
        ):
            ...
        """
        def check_feature_access(user_id: str = Depends(SubscriptionMiddleware.get_user_id_from_token)) -> str:
            if not has_feature_access(user_id, feature):
                subscription = get_user_subscription(user_id)
                current_plan = subscription["subscription_plans"]["name"] if subscription else "Free"

                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FEATURE_NOT_AVAILABLE",
                        "message": f"This feature is not available in your current plan: {current_plan}",
                        "feature": feature,
                        "upgrade_url": "/subscription/plans"
                    }
                )
            return user_id

        return check_feature_access

    @staticmethod
    def check_limit(limit_type: str):
        """
        Crée un middleware qui vérifie les limites d'usage

        Usage:
        @router.post("/products")
        async def create_product(
            user_id: str = Depends(SubscriptionMiddleware.check_limit("products"))
        ):
            ...
        """
        def verify_limit(user_id: str = Depends(SubscriptionMiddleware.get_user_id_from_token)) -> str:
            result = check_usage_limit(user_id, limit_type)

            if not result.get("allowed", False):
                subscription = get_user_subscription(user_id)
                current_plan = subscription["subscription_plans"]["name"] if subscription else "Free"

                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "LIMIT_REACHED",
                        "message": f"You have reached your {limit_type} limit for your current plan: {current_plan}",
                        "current": result.get("current", 0),
                        "limit": result.get("limit", 0),
                        "upgrade_url": "/subscription/plans"
                    }
                )

            return user_id

        return verify_limit

    @staticmethod
    def get_subscription_info(user_id: str = Depends(get_user_id_from_token)) -> dict:
        """
        Récupère les informations d'abonnement pour l'utilisateur

        Usage:
        @router.get("/dashboard")
        async def dashboard(subscription_info: dict = Depends(SubscriptionMiddleware.get_subscription_info)):
            plan_name = subscription_info.get("plan", {}).get("name", "Free")
            ...
        """
        subscription = get_user_subscription(user_id)
        if not subscription:
            return {
                "has_subscription": False,
                "status": "none",
                "plan": None,
                "features": {}
            }

        plan = subscription["subscription_plans"]

        return {
            "has_subscription": True,
            "status": subscription["status"],
            "plan": {
                "id": plan["id"],
                "name": plan["name"],
                "slug": plan["slug"]
            },
            "features": {
                "ai_content_generation": plan.get("ai_content_generation", False),
                "advanced_analytics": plan.get("advanced_analytics", False),
                "priority_support": plan.get("priority_support", False),
                "custom_branding": plan.get("custom_branding", False),
                "api_access": plan.get("api_access", False),
                "export_data": plan.get("export_data", False)
            },
            "limits": {
                "max_products": plan.get("max_products"),
                "max_campaigns": plan.get("max_campaigns"),
                "max_affiliates": plan.get("max_affiliates")
            },
            "billing": {
                "cycle": subscription.get("billing_cycle"),
                "next_billing_date": subscription.get("next_billing_date"),
                "auto_renew": subscription.get("auto_renew", False)
            }
        }


# ============================================
# DECORATEURS HELPER
# ============================================

def require_plan(min_plan_level: int):
    """
    Décorateu

r qui vérifie si l'utilisateur a un plan d'un niveau minimum

    Niveaux:
    0 = Free
    1 = Standard
    2 = Premium
    3 = Enterprise

    Usage:
    @router.get("/advanced-analytics")
    @require_plan(min_plan_level=2)
    async def advanced_analytics(user_id: str = Depends(get_user_id_from_token)):
        ...
    """
    def decorator(func):
        async def wrapper(*args, user_id: str = Depends(SubscriptionMiddleware.get_user_id_from_token), **kwargs):
            subscription = get_user_subscription(user_id)
            if not subscription:
                current_level = 0
            else:
                plan_slug = subscription["subscription_plans"]["slug"]
                # Extraire le niveau du slug (ex: "merchant-premium" -> 2)
                level_map = {
                    "freemium": 0,
                    "free": 0,
                    "standard": 1,
                    "pro": 1,
                    "premium": 2,
                    "elite": 2,
                    "enterprise": 3
                }

                current_level = 0
                for key, level in level_map.items():
                    if key in plan_slug.lower():
                        current_level = level
                        break

            if current_level < min_plan_level:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "PLAN_UPGRADE_REQUIRED",
                        "message": "This feature requires a higher plan",
                        "current_level": current_level,
                        "required_level": min_plan_level,
                        "upgrade_url": "/subscription/plans"
                    }
                )

            return await func(*args, user_id=user_id, **kwargs)

        return wrapper

    return decorator


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def get_restricted_mode_response():
    """Retourne une réponse standard pour le mode restreint"""
    return {
        "success": False,
        "error": "RESTRICTED_MODE",
        "message": "Your account is in restricted mode. Please update your payment method or renew your subscription.",
        "actions": {
            "update_payment_method": "/subscription/payment-methods",
            "view_subscription": "/subscription/my-subscription",
            "upgrade_plan": "/subscription/plans"
        }
    }


def check_subscription_status(user_id: str) -> dict:
    """
    Vérifie le statut de l'abonnement et retourne les informations

    Returns:
        dict avec:
            - is_active: bool
            - status: str (active, trialing, past_due, canceled, expired, none)
            - is_restricted: bool (si l'utilisateur est en mode restreint)
            - can_access_features: bool
    """
    subscription = get_user_subscription(user_id)

    if not subscription:
        return {
            "is_active": False,
            "status": "none",
            "is_restricted": True,
            "can_access_features": False,
            "message": "No active subscription"
        }

    status = subscription["status"]
    is_active = status in ["active", "trialing"]
    is_restricted = status in ["past_due", "canceled", "expired"]

    return {
        "is_active": is_active,
        "status": status,
        "is_restricted": is_restricted,
        "can_access_features": is_active,
        "message": f"Subscription status: {status}",
        "subscription_id": subscription["id"],
        "plan_name": subscription["subscription_plans"]["name"]
    }


def increment_feature_usage(user_id: str, feature: str) -> bool:
    """
    Incrémente le compteur d'usage pour une fonctionnalité

    Args:
        user_id: ID de l'utilisateur
        feature: Type de fonctionnalité (products, campaigns, affiliates, ai_requests, api_calls)

    Returns:
        bool: True si l'incrémentation a réussi
    """
    try:
        subscription = get_user_subscription(user_id)
        if not subscription:
            return False

        from subscription_helpers import increment_usage
        return increment_usage(subscription["id"], f"{feature}_count")

    except Exception as e:
        print(f"Error incrementing feature usage: {e}")
        return False
