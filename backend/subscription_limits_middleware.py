"""
============================================
SUBSCRIPTION LIMITS MIDDLEWARE - VERSION CORRIGÉE
Vérifie les limites d'abonnement avant les actions
BUG 7 CORRIGÉ: Utilise factory functions au lieu de Depends dans méthodes statiques
============================================
"""

from fastapi import HTTPException, Depends
from typing import Optional, Callable
from auth import get_current_user
from subscription_helpers_simple import get_user_subscription_data

class SubscriptionLimits:
    """Middleware pour vérifier les limites d'abonnement"""
    
    @staticmethod
    def check_product_limit() -> Callable:
        """Factory qui retourne une dépendance pour vérifier les produits (BUG 7 CORRIGÉ)"""
        async def checker(current_user: dict = Depends(get_current_user)):
            if current_user.get("role") != "merchant":
                raise HTTPException(status_code=403, detail="Only merchants can create products")
            
            subscription_data = await get_user_subscription_data(
                current_user.get("id"),
                current_user.get("role")
            )
            
            if not subscription_data:
                raise HTTPException(status_code=400, detail="No active subscription")
            
            limits = subscription_data.get("limits", {})
            usage = subscription_data.get("usage", {})
            
            max_products = limits.get("products")
            current_products = usage.get("products", 0)
            
            if max_products is not None and current_products >= max_products:
                raise HTTPException(
                    status_code=403,
                    detail=f"Product limit reached ({current_products}/{max_products}). Please upgrade your plan."
                )
            
            return True
        
        return checker
    
    @staticmethod
    def check_campaign_limit() -> Callable:
        """Factory qui retourne une dépendance pour vérifier les campagnes (BUG 7 CORRIGÉ)"""
        async def checker(current_user: dict = Depends(get_current_user)):
            subscription_data = await get_user_subscription_data(
                current_user.get("id"),
                current_user.get("role")
            )
            
            if not subscription_data:
                raise HTTPException(status_code=400, detail="No active subscription")
            
            limits = subscription_data.get("limits", {})
            usage = subscription_data.get("usage", {})
            
            max_campaigns = limits.get("campaigns")
            current_campaigns = usage.get("campaigns", 0)
            
            if max_campaigns is not None and current_campaigns >= max_campaigns:
                raise HTTPException(
                    status_code=403,
                    detail=f"Campaign limit reached ({current_campaigns}/{max_campaigns}). Please upgrade your plan."
                )
            
            return True
        
        return checker
    
    @staticmethod
    def check_affiliate_limit() -> Callable:
        """Factory qui retourne une dépendance pour vérifier les affiliés (BUG 7 CORRIGÉ)"""
        async def checker(current_user: dict = Depends(get_current_user)):
            if current_user.get("role") != "merchant":
                raise HTTPException(status_code=403, detail="Only merchants can manage affiliates")
            
            subscription_data = await get_user_subscription_data(
                current_user.get("id"),
                current_user.get("role")
            )
            
            if not subscription_data:
                raise HTTPException(status_code=400, detail="No active subscription")
            
            limits = subscription_data.get("limits", {})
            usage = subscription_data.get("usage", {})
            
            max_affiliates = limits.get("affiliates")
            current_affiliates = usage.get("affiliates", 0)
            
            if max_affiliates is not None and current_affiliates >= max_affiliates:
                raise HTTPException(
                    status_code=403,
                    detail=f"Affiliate limit reached ({current_affiliates}/{max_affiliates}). Please upgrade your plan."
                )
            
            return True
        
        return checker
    
    @staticmethod
    def check_link_limit() -> Callable:
        """Factory qui retourne une dépendance pour vérifier les liens (BUG 7 CORRIGÉ)"""
        async def checker(current_user: dict = Depends(get_current_user)):
            if current_user.get("role") != "influencer":
                raise HTTPException(status_code=403, detail="Only influencers can create tracking links")
            
            subscription_data = await get_user_subscription_data(
                current_user.get("id"),
                current_user.get("role")
            )
            
            if not subscription_data:
                raise HTTPException(status_code=400, detail="No active subscription")
            
            limits = subscription_data.get("limits", {})
            usage = subscription_data.get("usage", {})
            
            max_links = limits.get("links")
            current_links = usage.get("links", 0)
            
            if max_links is not None and current_links >= max_links:
                raise HTTPException(
                    status_code=403,
                    detail=f"Tracking link limit reached ({current_links}/{max_links}). Please upgrade your plan."
                )
            
            return True
        
        return checker
    
    @staticmethod
    async def get_plan_features(current_user: dict = Depends(get_current_user)) -> list:
        """Retourne les features disponibles pour le plan actuel"""
        subscription_data = await get_user_subscription_data(
            current_user.get("id"),
            current_user.get("role")
        )
        
        if not subscription_data:
            return []
        
        return subscription_data.get("features", [])
    
    @staticmethod
    async def has_feature(feature_name: str, current_user: dict = Depends(get_current_user)) -> bool:
        """Vérifie si l'utilisateur a accès à une fonctionnalité spécifique"""
        features = await SubscriptionLimits.get_plan_features(current_user)
        
        # Mapping des features
        feature_keywords = {
            "api_access": ["API", "api"],
            "white_label": ["White label", "white label"],
            "analytics_advanced": ["Analytics avancées", "Analytics premium"],
            "priority_support": ["Support prioritaire", "Support 24/7", "Support dédié"],
            "instant_payout": ["Paiement instantané"],
            "custom_links": ["Liens personnalisés", "Liens ultra-personnalisés"],
            "account_manager": ["Account manager"],
            "unlimited": ["illimité", "Illimité", "illimitées"]
        }
        
        keywords = feature_keywords.get(feature_name, [feature_name])
        
        for feature in features:
            for keyword in keywords:
                if keyword.lower() in feature.lower():
                    return True
        
        return False
    
    @staticmethod
    async def require_feature(feature_name: str, current_user: dict = Depends(get_current_user)):
        """Middleware qui requiert une fonctionnalité spécifique"""
        has_access = await SubscriptionLimits.has_feature(feature_name, current_user)
        
        if not has_access:
            subscription_data = await get_user_subscription_data(
                current_user.get("id"),
                current_user.get("role")
            )
            
            plan_name = subscription_data.get("plan_name", "current") if subscription_data else "current"
            
            raise HTTPException(
                status_code=403,
                detail=f"This feature requires a higher plan. Your {plan_name} plan does not include '{feature_name}'."
            )
        
        return True


# ============================================
# DECORATORS PRATIQUES
# ============================================

def require_product_limit(func):
    """Décorateur pour vérifier la limite de produits"""
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if current_user:
            await SubscriptionLimits.check_product_limit(current_user)
        return await func(*args, **kwargs)
    return wrapper

def require_campaign_limit(func):
    """Décorateur pour vérifier la limite de campagnes"""
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if current_user:
            await SubscriptionLimits.check_campaign_limit(current_user)
        return await func(*args, **kwargs)
    return wrapper

def require_api_access(func):
    """Décorateur pour requérir l'accès API"""
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if current_user:
            await SubscriptionLimits.require_feature("api_access", current_user)
        return await func(*args, **kwargs)
    return wrapper


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

"""
# Dans vos endpoints, utilisez les dépendances:

@app.post("/api/products")
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(SubscriptionLimits.check_product_limit)
):
    # Créer le produit
    pass

@app.post("/api/campaigns")
async def create_campaign(
    campaign: CampaignCreate,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(SubscriptionLimits.check_campaign_limit)
):
    # Créer la campagne
    pass

@app.get("/api/analytics/advanced")
async def get_advanced_analytics(
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(lambda user=Depends(get_current_user): 
                      SubscriptionLimits.require_feature("analytics_advanced", user))
):
    # Retourner analytics avancées
    pass
"""
