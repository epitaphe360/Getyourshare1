"""
============================================
SUBSCRIPTION ENDPOINTS - VERSION SIMPLIFIÉE
Utilise les données existantes dans merchants/influencers
============================================
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from supabase import create_client, Client
import os
from auth import get_current_user

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("⚠️ Warning: Supabase credentials not configured")
    supabase = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_user_subscription_data(user_id: str, user_role: str) -> Optional[Dict[str, Any]]:
    """Récupère les données d'abonnement depuis merchants ou influencers"""
    if not supabase:
        return None
    
    try:
        if user_role == "merchant":
            response = supabase.from_("merchants") \
                .select("*") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
                
            if response.data:
                data = response.data
                return {
                    "plan_name": data.get("subscription_plan", "free").capitalize(),
                    "plan_code": data.get("subscription_plan", "free"),
                    "type": "merchant",
                    "status": data.get("subscription_status", "active"),
                    "monthly_fee": float(data.get("monthly_fee", 0)),
                    "commission_rate": float(data.get("commission_rate", 5)),
                    "total_sales": float(data.get("total_sales", 0)),
                    "total_commission_paid": float(data.get("total_commission_paid", 0)),
                    
                    # Limites selon le plan
                    "limits": get_merchant_limits(data.get("subscription_plan", "free")),
                    
                    # Utilisation actuelle (simulée pour l'instant)
                    "usage": {
                        "products": 3,
                        "campaigns": 1,
                        "affiliates": 8
                    }
                }
        
        elif user_role == "influencer":
            response = supabase.from_("influencers") \
                .select("*") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
                
            if response.data:
                data = response.data
                return {
                    "plan_name": data.get("subscription_plan", "starter").capitalize(),
                    "plan_code": data.get("subscription_plan", "starter"),
                    "type": "influencer",
                    "status": data.get("subscription_status", "active"),
                    "monthly_fee": float(data.get("monthly_fee", 0)),
                    "platform_fee_rate": float(data.get("platform_fee_rate", 5)),
                    "total_earnings": float(data.get("total_earnings", 0)),
                    "balance": float(data.get("balance", 0)),
                    "audience_size": data.get("audience_size", 0),
                    "engagement_rate": float(data.get("engagement_rate", 0)),
                    
                    # Limites selon le plan
                    "limits": get_influencer_limits(data.get("subscription_plan", "starter")),
                    
                    # Utilisation actuelle
                    "usage": {
                        "campaigns": data.get("total_sales", 5),
                        "links": 15
                    }
                }
                
    except Exception as e:
        print(f"Error fetching subscription data: {e}")
        return None
    
    return None

def get_merchant_limits(plan: str) -> Dict[str, Any]:
    """Retourne les limites du plan merchant"""
    limits_map = {
        "free": {
            "products": 10,
            "campaigns": 5,
            "affiliates": 50,
            "commission_rate": 5.0
        },
        "starter": {
            "products": 50,
            "campaigns": 20,
            "affiliates": 200,
            "commission_rate": 4.0
        },
        "pro": {
            "products": 200,
            "campaigns": 100,
            "affiliates": 1000,
            "commission_rate": 3.0
        },
        "enterprise": {
            "products": None,  # Illimité
            "campaigns": None,
            "affiliates": None,
            "commission_rate": 2.0
        }
    }
    return limits_map.get(plan, limits_map["free"])

def get_influencer_limits(plan: str) -> Dict[str, Any]:
    """Retourne les limites du plan influencer"""
    limits_map = {
        "starter": {
            "campaigns": 5,
            "links": 10,
            "platform_fee_rate": 5.0
        },
        "pro": {
            "campaigns": 50,
            "links": 100,
            "platform_fee_rate": 3.0
        },
        "elite": {
            "campaigns": None,  # Illimité
            "links": None,
            "platform_fee_rate": 2.0
        }
    }
    return limits_map.get(plan, limits_map["starter"])

def get_plan_features(plan_code: str, plan_type: str) -> list:
    """Retourne les features du plan"""
    if plan_type == "merchant":
        features_map = {
            "free": [
                "Dashboard basique",
                "Support email",
                "Rapports mensuels",
                "10 produits max",
                "5 campagnes max",
                "50 affiliés max"
            ],
            "starter": [
                "Dashboard avancé",
                "Support prioritaire",
                "Rapports hebdomadaires",
                "50 produits",
                "20 campagnes",
                "200 affiliés",
                "Analytics avancées"
            ],
            "pro": [
                "Dashboard premium",
                "Support 24/7",
                "Rapports en temps réel",
                "200 produits",
                "100 campagnes",
                "1000 affiliés",
                "API access",
                "White label"
            ],
            "enterprise": [
                "Dashboard enterprise",
                "Support dédié",
                "Illimité",
                "API complète",
                "Account manager",
                "Formation sur mesure"
            ]
        }
    else:  # influencer
        features_map = {
            "starter": [
                "Dashboard basique",
                "5 campagnes actives",
                "10 liens d'affiliation",
                "Statistiques de base",
                "Paiement mensuel"
            ],
            "pro": [
                "Dashboard avancé",
                "50 campagnes actives",
                "100 liens d'affiliation",
                "Analytics avancées",
                "Paiement hebdomadaire",
                "Support prioritaire"
            ],
            "elite": [
                "Dashboard premium",
                "Campagnes illimitées",
                "Liens illimités",
                "Paiement instantané",
                "Support 24/7",
                "Account manager dédié"
            ]
        }
    
    return features_map.get(plan_code, [])

# ============================================
# ENDPOINTS
# ============================================

@router.get("/current")
async def get_current_subscription(current_user: dict = Depends(get_current_user)):
    """
    Récupère l'abonnement actuel de l'utilisateur
    Compatible avec les dashboards existants
    """
    try:
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        if not user_id or not user_role:
            raise HTTPException(status_code=400, detail="Invalid user data")
        
        subscription_data = await get_user_subscription_data(user_id, user_role)
        
        if not subscription_data:
            # Retourner un plan par défaut si pas trouvé
            return {
                "plan_name": "Free" if user_role == "merchant" else "Starter",
                "plan_code": "free" if user_role == "merchant" else "starter",
                "type": user_role,
                "status": "active",
                "monthly_fee": 0,
                "features": [],
                "limits": get_merchant_limits("free") if user_role == "merchant" else get_influencer_limits("starter"),
                "usage": {}
            }
        
        # Ajouter les features
        subscription_data["features"] = get_plan_features(
            subscription_data["plan_code"],
            subscription_data["type"]
        )
        
        return subscription_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_current_subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching subscription: {str(e)}")

@router.get("/plans")
async def get_available_plans():
    """Liste tous les plans disponibles"""
    try:
        if not supabase:
            # Retourner des plans mockés si Supabase n'est pas configuré
            return {
                "merchants": [
                    {"name": "Free", "code": "free", "price": 0, "commission": 5},
                    {"name": "Starter", "code": "starter", "price": 299, "commission": 4},
                    {"name": "Pro", "code": "pro", "price": 799, "commission": 3},
                    {"name": "Enterprise", "code": "enterprise", "price": 1999, "commission": 2}
                ],
                "influencers": [
                    {"name": "Starter", "code": "starter", "price": 0, "fee": 5},
                    {"name": "Pro", "code": "pro", "price": 99, "fee": 3},
                    {"name": "Elite", "code": "elite", "price": 299, "fee": 2}
                ]
            }
        
        response = supabase.from_("subscription_plans") \
            .select("*") \
            .eq("is_active", True) \
            .order("display_order") \
            .execute()
        
        plans = response.data or []
        
        # Grouper par type
        merchants = [p for p in plans if p["type"] == "merchant"]
        influencers = [p for p in plans if p["type"] == "influencer"]
        
        return {
            "merchants": merchants,
            "influencers": influencers
        }
        
    except Exception as e:
        print(f"Error fetching plans: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/usage")
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    """Statistiques d'utilisation vs limites"""
    try:
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        subscription_data = await get_user_subscription_data(user_id, user_role)
        
        if not subscription_data:
            return {
                "error": "No subscription found"
            }
        
        limits = subscription_data.get("limits", {})
        usage = subscription_data.get("usage", {})
        
        result = {
            "plan_name": subscription_data["plan_name"],
            "plan_code": subscription_data["plan_code"]
        }
        
        # Ajouter les stats d'utilisation
        for key, limit in limits.items():
            if key.endswith("_rate"):
                continue  # Skip rate fields
            
            current = usage.get(key, 0)
            result[key] = {
                "current": current,
                "limit": limit,
                "available": None if limit is None else (limit - current),
                "can_add": True if limit is None else (current < limit),
                "percentage": 0 if limit is None or limit == 0 else round((current / limit) * 100, 1)
            }
        
        return result
        
    except Exception as e:
        print(f"Error fetching usage: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/check-limit")
async def check_limit(
    limit_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Vérifie si l'utilisateur peut ajouter un élément"""
    try:
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        subscription_data = await get_user_subscription_data(user_id, user_role)
        
        if not subscription_data:
            return {"allowed": False, "reason": "No active subscription"}
        
        limits = subscription_data.get("limits", {})
        usage = subscription_data.get("usage", {})
        
        limit = limits.get(limit_type)
        current = usage.get(limit_type, 0)
        
        if limit is None:  # Illimité
            return {
                "allowed": True,
                "reason": "Unlimited",
                "current": current,
                "limit": None
            }
        
        allowed = current < limit
        
        return {
            "allowed": allowed,
            "reason": "Limit reached" if not allowed else "OK",
            "current": current,
            "limit": limit,
            "remaining": limit - current
        }
        
    except Exception as e:
        print(f"Error checking limit: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ============================================
# ENDPOINTS MOCK POUR UPGRADE/CANCEL
# ============================================

@router.post("/upgrade")
async def upgrade_plan(
    new_plan: str,
    current_user: dict = Depends(get_current_user)
):
    """Placeholder pour upgrade de plan"""
    return {
        "success": True,
        "message": f"Upgrade vers {new_plan} sera disponible bientôt",
        "redirect_to_payment": True
    }

@router.post("/cancel")
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """Placeholder pour annulation"""
    return {
        "success": True,
        "message": "L'annulation sera effective à la fin de la période en cours"
    }
