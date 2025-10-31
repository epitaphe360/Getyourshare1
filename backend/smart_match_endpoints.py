"""
Smart Match Endpoints
Endpoints pour le matching intelligent influenceurs-marques
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from smart_match_service import (
    SmartMatchService,
    BatchMatchingService,
    InfluencerProfile,
    BrandProfile,
    MatchResult,
    Niche,
    AudienceAge,
    AudienceGender
)
from auth import get_current_user
from db_helpers import log_user_activity

router = APIRouter(prefix="/api/smart-match", tags=["Smart Match"])

# Initialiser les services
matcher = SmartMatchService()
batch_matcher = BatchMatchingService()

# ============================================
# ENDPOINTS
# ============================================

@router.post("/find-influencers", response_model=List[MatchResult])
async def find_matching_influencers(
    brand_profile: BrandProfile,
    top_n: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Trouve les meilleurs influenceurs pour une marque

    Retourne une liste de matches triée par score de compatibilité
    avec prédictions de ROI, reach, et conversions.
    """

    try:
        # TODO: Récupérer les vrais influenceurs de la DB
        # Pour l'instant, utiliser des données mock
        mock_influencers = await get_mock_influencers()

        matches = await matcher.find_matches_for_brand(
            brand=brand_profile,
            influencers=mock_influencers,
            top_n=top_n
        )

        # Logger l'activité
        await log_user_activity(
            user_id=current_user["id"],
            action="smart_match_search",
            details={
                "product_category": brand_profile.product_category,
                "matches_found": len(matches)
            }
        )

        return matches

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du matching: {str(e)}"
        )


@router.post("/find-brands", response_model=List[MatchResult])
async def find_matching_brands(
    influencer_profile: InfluencerProfile,
    top_n: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Trouve les meilleures marques pour un influenceur

    Retourne les opportunités les plus compatibles avec l'influenceur.
    """

    try:
        # TODO: Récupérer les vraies marques de la DB
        mock_brands = await get_mock_brands()

        matches = await matcher.find_matches_for_influencer(
            influencer=influencer_profile,
            brands=mock_brands,
            top_n=top_n
        )

        await log_user_activity(
            user_id=current_user["id"],
            action="smart_match_opportunities",
            details={
                "niches": influencer_profile.niches,
                "matches_found": len(matches)
            }
        )

        return matches

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du matching: {str(e)}"
        )


@router.post("/batch-match-campaign")
async def batch_match_campaign(
    campaign_id: str,
    brand_profile: BrandProfile,
    target_influencer_count: int = 10,
    min_score: float = 65.0,
    current_user: dict = Depends(get_current_user)
):
    """
    Matche une campagne complète avec les meilleurs influenceurs

    Retourne un rapport détaillé avec:
    - Influenceurs recommandés
    - Prédictions globales (reach, conversions, ROI)
    - Budget total estimé
    """

    try:
        # TODO: Récupérer les vrais influenceurs
        all_influencers = await get_mock_influencers()

        campaign_report = await batch_matcher.match_campaign_to_influencers(
            campaign_id=campaign_id,
            brand=brand_profile,
            all_influencers=all_influencers,
            target_influencer_count=target_influencer_count,
            min_score=min_score
        )

        await log_user_activity(
            user_id=current_user["id"],
            action="batch_campaign_match",
            details={
                "campaign_id": campaign_id,
                "influencers_matched": campaign_report["selected_influencers_count"]
            }
        )

        return campaign_report

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du batch matching: {str(e)}"
        )


@router.get("/my-compatibility/{brand_id}")
async def check_my_compatibility(
    brand_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifie la compatibilité de l'influenceur connecté avec une marque spécifique

    Retourne un score détaillé et des recommandations
    """

    try:
        # TODO: Récupérer le profil de l'influenceur depuis la DB
        # TODO: Récupérer le profil de la marque depuis la DB

        # Mock pour l'instant
        influencer_profile = await get_mock_influencer_profile(current_user["id"])
        brand_profile = await get_mock_brand_profile(brand_id)

        match_result = await matcher._calculate_match_score(
            influencer=influencer_profile,
            brand=brand_profile
        )

        return match_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


# ============================================
# MOCK DATA HELPERS (À remplacer par vraies requêtes DB)
# ============================================

async def get_mock_influencers() -> List[InfluencerProfile]:
    """Mock influencers data"""
    return [
        InfluencerProfile(
            user_id="inf_1",
            name="Sarah Fashion",
            niches=[Niche.FASHION, Niche.BEAUTY],
            followers_count=50000,
            engagement_rate=4.5,
            audience_age=[AudienceAge.YOUNG_ADULT, AudienceAge.ADULT],
            audience_gender=AudienceGender.FEMALE,
            audience_location=["MA", "FR"],
            platforms=["instagram", "tiktok"],
            average_views=15000,
            content_quality_score=85.0,
            reliability_score=92.0,
            preferred_commission=10.0,
            language=["fr", "ar"]
        ),
        InfluencerProfile(
            user_id="inf_2",
            name="Tech Morocco",
            niches=[Niche.TECH, Niche.BUSINESS],
            followers_count=120000,
            engagement_rate=3.2,
            audience_age=[AudienceAge.ADULT],
            audience_gender=AudienceGender.MIXED,
            audience_location=["MA"],
            platforms=["youtube", "instagram"],
            average_views=45000,
            content_quality_score=90.0,
            reliability_score=95.0,
            preferred_commission=15.0,
            language=["fr", "ar", "en"]
        )
    ]


async def get_mock_brands() -> List[BrandProfile]:
    """Mock brands data"""
    return [
        BrandProfile(
            company_id="brand_1",
            company_name="Moroccan Beauty Co",
            product_category=Niche.BEAUTY,
            target_audience_age=[AudienceAge.YOUNG_ADULT, AudienceAge.ADULT],
            target_audience_gender=AudienceGender.FEMALE,
            target_locations=["MA"],
            budget_per_influencer=3000.0,
            commission_percentage=12.0,
            campaign_description="Produits de beauté naturels marocains",
            required_followers_min=10000,
            required_engagement_min=3.0,
            preferred_platforms=["instagram", "tiktok"],
            language=["fr", "ar"]
        )
    ]


async def get_mock_influencer_profile(user_id: str) -> InfluencerProfile:
    """Get mock influencer profile"""
    influencers = await get_mock_influencers()
    return influencers[0] if influencers else None


async def get_mock_brand_profile(brand_id: str) -> BrandProfile:
    """Get mock brand profile"""
    brands = await get_mock_brands()
    return brands[0] if brands else None
