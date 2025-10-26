"""
Predictive Dashboard Endpoints
Endpoints pour le dashboard prédictif Netflix-Style
"""

from fastapi import APIRouter, Depends, HTTPException, status

from predictive_dashboard_service import (
    PredictiveDashboardService,
    DashboardData,
    PredictionTimeframe
)
from auth import get_current_user
from db_helpers import log_user_activity
from supabase_client import supabase

router = APIRouter(prefix="/api/dashboard", tags=["Predictive Dashboard"])

# Initialiser le service
dashboard_service = PredictiveDashboardService()

# ============================================
# ENDPOINTS
# ============================================

@router.get("/predictive", response_model=DashboardData)
async def get_predictive_dashboard(
    timeframe: PredictionTimeframe = PredictionTimeframe.MONTH,
    current_user: dict = Depends(get_current_user)
):
    """
    Dashboard Netflix-Style avec prédictions ML et gamification

    Retourne:
    - Stats actuelles
    - Prédictions futures (revenus, conversions, etc.)
    - Comparaisons avec autres utilisateurs
    - Achievements et niveau
    - Leaderboards
    - Insights intelligents
    - Wrapped stats (style Spotify)
    """

    try:
        # Récupérer l'historique de campagnes
        campaign_history = await get_user_campaigns(current_user["id"])

        # Générer le dashboard complet
        dashboard_data = await dashboard_service.generate_dashboard(
            user_id=current_user["id"],
            user_data=current_user,
            campaign_history=campaign_history,
            timeframe=timeframe
        )

        await log_user_activity(
            user_id=current_user["id"],
            action="viewed_predictive_dashboard",
            details={"timeframe": timeframe}
        )

        return dashboard_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du dashboard: {str(e)}"
        )


@router.get("/predictions")
async def get_predictions_only(
    timeframe: PredictionTimeframe = PredictionTimeframe.MONTH,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère uniquement les prédictions sans le dashboard complet

    Plus léger pour des requêtes rapides
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])

        predictions = await dashboard_service._generate_predictions(
            campaign_history=campaign_history,
            timeframe=timeframe
        )

        return {
            "timeframe": timeframe,
            "predictions": predictions,
            "generated_at": "2025-10-26T00:00:00Z"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/wrapped")
async def get_wrapped_stats(
    year: int = 2025,
    current_user: dict = Depends(get_current_user)
):
    """
    Stats Wrapped style Spotify / Netflix Year in Review

    Résumé annuel avec stats impressionnantes et partageables
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])

        # Filtrer par année si nécessaire
        # TODO: Implémenter le filtrage par année

        wrapped_stats = dashboard_service._generate_wrapped_stats(
            campaign_history=campaign_history,
            user_data=current_user
        )

        return {
            "year": year,
            "wrapped": wrapped_stats,
            "shareable_image_url": None  # TODO: Générer une image partageable
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/achievements")
async def get_my_achievements(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère tous les achievements de l'utilisateur

    Affiche la progression pour chaque achievement
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])

        achievements = await dashboard_service._calculate_achievements(
            user_data=current_user,
            campaign_history=campaign_history
        )

        level_data = dashboard_service._calculate_level(campaign_history)

        return {
            "achievements": achievements,
            "level": level_data["level"],
            "xp": level_data["xp"],
            "xp_for_next_level": level_data["xp_for_next_level"],
            "progress_to_next_level": level_data["progress"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/leaderboards")
async def get_all_leaderboards(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère tous les leaderboards

    Catégories:
    - Top Earners
    - Best Conversion Rates
    - Most Campaigns
    - Highest Trust Score
    """

    try:
        # TODO: Implémenter avec vraies données
        leaderboards = [
            {
                "category": "Top Earners (Ce mois)",
                "user_rank": 45,
                "total_users": 500,
                "top_users": [
                    {"rank": 1, "username": "TopInfluencer1", "value": 25000, "avatar": None},
                    {"rank": 2, "username": "ProMarketer", "value": 22000, "avatar": None},
                    {"rank": 3, "username": "EliteAffiliate", "value": 20000, "avatar": None}
                ]
            },
            {
                "category": "Meilleurs Taux de Conversion",
                "user_rank": 23,
                "total_users": 500,
                "top_users": [
                    {"rank": 1, "username": "ConversionKing", "value": 8.5, "avatar": None},
                    {"rank": 2, "username": "SalesPro", "value": 7.2, "avatar": None},
                    {"rank": 3, "username": "MarketingGuru", "value": 6.8, "avatar": None}
                ]
            }
        ]

        return {"leaderboards": leaderboards}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/insights")
async def get_smart_insights(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les insights intelligents personnalisés

    Suggestions basées sur l'IA pour améliorer les performances
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])
        current_stats = dashboard_service._calculate_current_stats(campaign_history)
        predictions = await dashboard_service._generate_predictions(
            campaign_history,
            PredictionTimeframe.MONTH
        )

        insights = await dashboard_service._generate_insights(
            user_data=current_user,
            campaign_history=campaign_history,
            current_stats=current_stats,
            predictions=predictions
        )

        return {"insights": insights, "count": len(insights)}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/comparisons")
async def get_my_comparisons(
    current_user: dict = Depends(get_current_user)
):
    """
    Compare les stats de l'utilisateur avec la moyenne de la plateforme

    "Tu es dans le top 15% des influenceurs !"
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])
        current_stats = dashboard_service._calculate_current_stats(campaign_history)

        comparisons = await dashboard_service._generate_comparisons(
            user_id=current_user["id"],
            current_stats=current_stats
        )

        return comparisons

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_user_campaigns(user_id: str):
    """Récupère l'historique de campagnes d'un utilisateur"""
    try:
        result = supabase.table("campaigns").select("*").eq(
            "user_id", user_id
        ).execute()

        return result.data if result.data else []
    except:
        return []
