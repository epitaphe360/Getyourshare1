"""
Endpoints pour la recherche avancée d'influenceurs
"""

from fastapi import HTTPException, Depends, Query
from typing import Optional, List
from db_helpers import get_supabase_client, get_user_by_id

def add_influencer_search_endpoints(app, verify_token):
    """Ajoute les endpoints de recherche avancée d'influenceurs"""
    
    @app.get("/api/influencers/search")
    async def search_influencers(
        category: Optional[str] = None,
        min_followers: Optional[int] = None,
        max_followers: Optional[int] = None,
        min_engagement: Optional[float] = None,
        platform: Optional[str] = None,
        location: Optional[str] = None,
        verified_only: bool = False,
        sort_by: str = "followers",
        order: str = "desc",
        limit: int = Query(default=20, le=100),
        offset: int = 0,
        payload: dict = Depends(verify_token)
    ):
        """
        Recherche avancée d'influenceurs avec filtres multiples
        
        Paramètres:
        - category: Catégorie/niche (Mode, Beauté, etc.)
        - min_followers: Nombre minimum de followers
        - max_followers: Nombre maximum de followers
        - min_engagement: Taux d'engagement minimum (%)
        - platform: Plateforme principale (Instagram, TikTok, YouTube)
        - location: Localisation géographique
        - verified_only: Seulement les comptes vérifiés
        - sort_by: Tri par (followers, engagement_rate, total_sales)
        - order: Ordre (asc, desc)
        - limit: Nombre de résultats max
        - offset: Pagination offset
        """
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant" and user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        supabase = get_supabase_client()
        
        # Construire la requête
        query = supabase.table("users").select("""
            id,
            email,
            full_name,
            bio,
            profile_image,
            is_verified,
            location,
            influencers!inner(
                id,
                category,
                followers_count,
                engagement_rate,
                platform,
                instagram_handle,
                tiktok_handle,
                youtube_handle,
                total_sales,
                total_commissions
            )
        """).eq("role", "influencer").eq("status", "active")
        
        # Appliquer les filtres
        if category:
            query = query.eq("influencers.category", category)
        
        if min_followers is not None:
            query = query.gte("influencers.followers_count", min_followers)
        
        if max_followers is not None:
            query = query.lte("influencers.followers_count", max_followers)
        
        if min_engagement is not None:
            query = query.gte("influencers.engagement_rate", min_engagement)
        
        if platform:
            query = query.eq("influencers.platform", platform)
        
        if location:
            query = query.ilike("location", f"%{location}%")
        
        if verified_only:
            query = query.eq("is_verified", True)
        
        # Tri
        order_direction = {"asc": False, "desc": True}.get(order.lower(), True)
        
        if sort_by == "followers":
            query = query.order("influencers.followers_count", desc=order_direction)
        elif sort_by == "engagement_rate":
            query = query.order("influencers.engagement_rate", desc=order_direction)
        elif sort_by == "total_sales":
            query = query.order("influencers.total_sales", desc=order_direction)
        else:
            query = query.order("created_at", desc=order_direction)
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        # Exécuter
        result = query.execute()
        
        # Formater les résultats
        influencers = []
        for user_data in result.data:
            if user_data.get("influencers") and len(user_data["influencers"]) > 0:
                influencer_data = user_data["influencers"][0]
                
                influencers.append({
                    "user_id": user_data["id"],
                    "email": user_data["email"],
                    "full_name": user_data["full_name"],
                    "bio": user_data["bio"],
                    "profile_image": user_data["profile_image"],
                    "is_verified": user_data["is_verified"],
                    "location": user_data["location"],
                    "influencer_id": influencer_data["id"],
                    "category": influencer_data["category"],
                    "followers_count": influencer_data["followers_count"],
                    "engagement_rate": influencer_data["engagement_rate"],
                    "platform": influencer_data["platform"],
                    "instagram_handle": influencer_data.get("instagram_handle"),
                    "tiktok_handle": influencer_data.get("tiktok_handle"),
                    "youtube_handle": influencer_data.get("youtube_handle"),
                    "total_sales": influencer_data.get("total_sales", 0),
                    "total_commissions": influencer_data.get("total_commissions", 0)
                })
        
        return {
            "influencers": influencers,
            "total": len(influencers),
            "offset": offset,
            "limit": limit,
            "filters_applied": {
                "category": category,
                "min_followers": min_followers,
                "max_followers": max_followers,
                "min_engagement": min_engagement,
                "platform": platform,
                "location": location,
                "verified_only": verified_only
            }
        }
    
    @app.get("/api/influencers/stats")
    async def get_influencer_statistics(payload: dict = Depends(verify_token)):
        """Récupère les statistiques globales des influenceurs (pour afficher dans les filtres)"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant" and user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        supabase = get_supabase_client()
        
        # Récupérer toutes les données des influenceurs
        result = supabase.table("influencers").select("*").execute()
        
        if not result.data:
            return {
                "total_influencers": 0,
                "categories": [],
                "platforms": [],
                "followers_range": {"min": 0, "max": 0},
                "engagement_range": {"min": 0, "max": 0}
            }
        
        influencers = result.data
        
        # Calculer les statistiques
        categories = list(set(inf["category"] for inf in influencers if inf.get("category")))
        platforms = list(set(inf["platform"] for inf in influencers if inf.get("platform")))
        
        followers_counts = [inf["followers_count"] for inf in influencers if inf.get("followers_count")]
        engagement_rates = [inf["engagement_rate"] for inf in influencers if inf.get("engagement_rate")]
        
        return {
            "total_influencers": len(influencers),
            "categories": sorted(categories),
            "platforms": sorted(platforms),
            "followers_range": {
                "min": min(followers_counts) if followers_counts else 0,
                "max": max(followers_counts) if followers_counts else 0,
                "avg": sum(followers_counts) / len(followers_counts) if followers_counts else 0
            },
            "engagement_range": {
                "min": min(engagement_rates) if engagement_rates else 0,
                "max": max(engagement_rates) if engagement_rates else 0,
                "avg": sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
            }
        }
