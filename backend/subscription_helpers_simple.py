"""
============================================
SUBSCRIPTION HELPERS - SIMPLE VERSION
Fonctions partagées pour éviter imports circulaires
Version simplifiée qui utilise merchants/influencers tables
============================================
"""

from typing import Optional, Dict, Any
from supabase import create_client, Client
import os

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("⚠️ Warning: Supabase credentials not configured for subscription helpers")
    supabase = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# USAGE COUNTING FUNCTIONS
# ============================================

async def get_real_usage_counts(user_id: str, user_role: str) -> Dict[str, int]:
    """Compte l'utilisation réelle depuis la base de données"""
    if not supabase:
        print("⚠️ Supabase not configured, returning mock data")
        return {"products": 0, "campaigns": 0, "affiliates": 0}
    
    try:
        if user_role == "merchant":
            # Trouver le merchant_id
            merchant_response = supabase.from_("merchants")\
                .select("id")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not merchant_response.data:
                return {"products": 0, "campaigns": 0, "affiliates": 0}
            
            merchant_id = merchant_response.data["id"]
            
            # Compter les produits
            products_response = supabase.from_("products")\
                .select("id", count="exact")\
                .eq("merchant_id", merchant_id)\
                .execute()
            
            # Compter les campagnes
            campaigns_response = supabase.from_("campaigns")\
                .select("id", count="exact")\
                .eq("merchant_id", merchant_id)\
                .execute()
            
            # Compter les affiliations (affiliés)
            affiliates_response = supabase.from_("affiliations")\
                .select("id", count="exact")\
                .eq("merchant_id", merchant_id)\
                .execute()
            
            return {
                "products": products_response.count or 0,
                "campaigns": campaigns_response.count or 0,
                "affiliates": affiliates_response.count or 0
            }
        
        elif user_role == "influencer":
            # Trouver l'influencer_id
            influencer_response = supabase.from_("influencers")\
                .select("id")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not influencer_response.data:
                return {"campaigns": 0, "links": 0}
            
            influencer_id = influencer_response.data["id"]
            
            # Compter les campagnes (affiliations)
            campaigns_response = supabase.from_("affiliations")\
                .select("id", count="exact")\
                .eq("influencer_id", influencer_id)\
                .execute()
            
            # Compter les liens de tracking
            links_response = supabase.from_("trackable_links")\
                .select("id", count="exact")\
                .eq("influencer_id", influencer_id)\
                .execute()
            
            return {
                "campaigns": campaigns_response.count or 0,
                "links": links_response.count or 0
            }
    
    except Exception as e:
        print(f"❌ Error counting usage: {e}")
        # Retourner des valeurs par défaut en cas d'erreur
        if user_role == "merchant":
            return {"products": 0, "campaigns": 0, "affiliates": 0}
        else:
            return {"campaigns": 0, "links": 0}
    
    return {}

# ============================================
# SUBSCRIPTION DATA FUNCTIONS
# ============================================

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
                
                # Obtenir l'utilisation réelle
                usage = await get_real_usage_counts(user_id, user_role)
                
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
                    
                    # Utilisation actuelle (réelle)
                    "usage": usage
                }
        
        elif user_role == "influencer":
            response = supabase.from_("influencers") \
                .select("*") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
                
            if response.data:
                data = response.data
                
                # Obtenir l'utilisation réelle
                usage = await get_real_usage_counts(user_id, user_role)
                
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
                    
                    # Utilisation actuelle (réelle)
                    "usage": usage
                }
                
    except Exception as e:
        print(f"❌ Error fetching subscription data: {e}")
        return None
    
    return None
