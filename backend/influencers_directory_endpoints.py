"""
============================================
INFLUENCERS DIRECTORY ENDPOINTS
Share Your Sales - Annuaire des Influenceurs
============================================

Annuaire public des influenceurs disponibles:
- Création et gestion de profils avec stats réseaux sociaux
- Recherche par niche, followers, engagement
- Demandes de collaboration
- Système d'évaluation
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
import os
from auth import get_current_user

router = APIRouter(prefix="/api/influencers", tags=["Influencers Directory"])

# ============================================
# ENVIRONMENT VARIABLES VALIDATION
# ============================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing required Supabase environment variables")

# ============================================
# SUPABASE CLIENT
# ============================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# PYDANTIC MODELS
# ============================================

class CreateInfluencerProfileRequest(BaseModel):
    """Création d'un profil influenceur"""
    display_name: str = Field(..., max_length=255)
    headline: str = Field(..., max_length=255)
    bio: str
    niches: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    content_types: List[str] = Field(default_factory=list)
    city: Optional[str] = None
    region: Optional[str] = None

    # Réseaux sociaux
    instagram_handle: Optional[str] = None
    instagram_followers: Optional[int] = Field(None, ge=0)
    instagram_engagement_rate: Optional[float] = Field(None, ge=0, le=100)

    facebook_handle: Optional[str] = None
    facebook_followers: Optional[int] = Field(None, ge=0)
    facebook_engagement_rate: Optional[float] = Field(None, ge=0, le=100)

    tiktok_handle: Optional[str] = None
    tiktok_followers: Optional[int] = Field(None, ge=0)
    tiktok_engagement_rate: Optional[float] = Field(None, ge=0, le=100)

    youtube_handle: Optional[str] = None
    youtube_subscribers: Optional[int] = Field(None, ge=0)
    youtube_avg_views: Optional[int] = Field(None, ge=0)

    # Tarification
    rate_per_post: Optional[float] = Field(None, ge=0)
    rate_per_story: Optional[float] = Field(None, ge=0)
    rate_per_video: Optional[float] = Field(None, ge=0)
    preferred_commission_rate: Optional[float] = Field(None, ge=0, le=100)

    # Disponibilité
    accepts_affiliate: bool = True
    accepts_sponsored: bool = True
    minimum_campaign_budget: Optional[float] = Field(None, ge=0)

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_public: bool = True

class UpdateInfluencerProfileRequest(BaseModel):
    """Mise à jour du profil influenceur"""
    display_name: Optional[str] = Field(None, max_length=255)
    headline: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    niches: Optional[List[str]] = None
    target_audience: Optional[str] = None
    content_types: Optional[List[str]] = None
    city: Optional[str] = None
    region: Optional[str] = None

    instagram_handle: Optional[str] = None
    instagram_followers: Optional[int] = Field(None, ge=0)
    instagram_engagement_rate: Optional[float] = Field(None, ge=0, le=100)

    facebook_handle: Optional[str] = None
    facebook_followers: Optional[int] = Field(None, ge=0)
    facebook_engagement_rate: Optional[float] = Field(None, ge=0, le=100)

    tiktok_handle: Optional[str] = None
    tiktok_followers: Optional[int] = Field(None, ge=0)
    tiktok_engagement_rate: Optional[float] = Field(None, ge=0, le=100)

    youtube_handle: Optional[str] = None
    youtube_subscribers: Optional[int] = Field(None, ge=0)
    youtube_avg_views: Optional[int] = Field(None, ge=0)

    rate_per_post: Optional[float] = Field(None, ge=0)
    rate_per_story: Optional[float] = Field(None, ge=0)
    rate_per_video: Optional[float] = Field(None, ge=0)
    preferred_commission_rate: Optional[float] = Field(None, ge=0, le=100)

    accepts_affiliate: Optional[bool] = None
    accepts_sponsored: Optional[bool] = None
    minimum_campaign_budget: Optional[float] = Field(None, ge=0)

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_public: Optional[bool] = None
    is_available: Optional[bool] = None

class CollaborationRequestCreate(BaseModel):
    """Demande de collaboration"""
    message: str = Field(..., min_length=20)
    proposed_commission_rate: Optional[float] = Field(None, ge=0, le=100)
    proposed_budget: Optional[float] = Field(None, ge=0)
    proposed_duration_days: Optional[int] = Field(None, ge=1)
    campaign_details: Optional[Dict[str, Any]] = None

class CollaborationRequestResponse(BaseModel):
    """Réponse à une demande de collaboration"""
    status: str
    response_message: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        allowed = ['accepted', 'declined', 'negotiating']
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v

class ReviewCreate(BaseModel):
    """Création d'un avis"""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    professionalism_rating: Optional[int] = Field(None, ge=1, le=5)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    results_rating: Optional[int] = Field(None, ge=1, le=5)
    would_work_again: Optional[bool] = None

# ============================================
# HELPER FUNCTIONS
# ============================================

async def increment_view_count(profile_id: str):
    """Incrémenter le compteur de vues"""
    try:
        supabase.from_("influencer_profiles") \
            .update({"view_count": supabase.sql("view_count + 1")}) \
            .eq("id", profile_id) \
            .execute()
    except Exception as e:
        print(f"Error incrementing view count: {e}")

async def increment_contact_count(profile_id: str):
    """Incrémenter le compteur de contacts"""
    try:
        supabase.from_("influencer_profiles") \
            .update({"contact_count": supabase.sql("contact_count + 1")}) \
            .eq("id", profile_id) \
            .execute()
    except Exception as e:
        print(f"Error incrementing contact count: {e}")

# ============================================
# ENDPOINTS - PROFILE MANAGEMENT
# ============================================

@router.post("/profile", status_code=status.HTTP_201_CREATED)
async def create_influencer_profile(
    request: CreateInfluencerProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Créer un profil influenceur dans l'annuaire

    Accessible à:
    - Influenceurs indépendants (abonnement Marketplace 99 MAD)
    - Membres d'équipe (invités par entreprises)
    """
    try:
        user_id = current_user["id"]

        # Vérifier qu'il n'existe pas déjà un profil
        existing = supabase.from_("influencer_profiles") \
            .select("id") \
            .eq("user_id", user_id) \
            .execute()

        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=400,
                detail="Influencer profile already exists"
            )

        # Calculer le taux d'engagement moyen
        engagement_rates = []
        total_followers = 0

        if request.instagram_followers and request.instagram_engagement_rate:
            engagement_rates.append(request.instagram_engagement_rate)
            total_followers += request.instagram_followers
        if request.facebook_followers and request.facebook_engagement_rate:
            engagement_rates.append(request.facebook_engagement_rate)
            total_followers += request.facebook_followers
        if request.tiktok_followers and request.tiktok_engagement_rate:
            engagement_rates.append(request.tiktok_engagement_rate)
            total_followers += request.tiktok_followers

        average_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else None

        # Créer le profil
        profile_data = {
            "user_id": user_id,
            "display_name": request.display_name,
            "headline": request.headline,
            "bio": request.bio,
            "niches": request.niches,
            "target_audience": request.target_audience,
            "content_types": request.content_types,
            "city": request.city,
            "region": request.region,
            "instagram_handle": request.instagram_handle,
            "instagram_followers": request.instagram_followers,
            "instagram_engagement_rate": request.instagram_engagement_rate,
            "facebook_handle": request.facebook_handle,
            "facebook_followers": request.facebook_followers,
            "facebook_engagement_rate": request.facebook_engagement_rate,
            "tiktok_handle": request.tiktok_handle,
            "tiktok_followers": request.tiktok_followers,
            "tiktok_engagement_rate": request.tiktok_engagement_rate,
            "youtube_handle": request.youtube_handle,
            "youtube_subscribers": request.youtube_subscribers,
            "youtube_avg_views": request.youtube_avg_views,
            "average_engagement_rate": average_engagement,
            "rate_per_post": request.rate_per_post,
            "rate_per_story": request.rate_per_story,
            "rate_per_video": request.rate_per_video,
            "preferred_commission_rate": request.preferred_commission_rate,
            "accepts_affiliate": request.accepts_affiliate,
            "accepts_sponsored": request.accepts_sponsored,
            "minimum_campaign_budget": request.minimum_campaign_budget,
            "email": request.email,
            "phone": request.phone,
            "is_public": request.is_public,
            "is_available": True
        }

        response = supabase.from_("influencer_profiles") \
            .insert(profile_data) \
            .execute()

        return {
            "success": True,
            "message": "Influencer profile created successfully",
            "profile": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating profile: {str(e)}"
        )

@router.get("/profile/my-profile")
async def get_my_influencer_profile(current_user: dict = Depends(get_current_user)):
    """Récupérer son propre profil influenceur"""
    try:
        user_id = current_user["id"]

        response = supabase.from_("influencer_profiles") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()

        if not response.data:
            return None

        return response.data

    except Exception as e:
        if "JSON object requested, multiple" in str(e) or "PGRST116" in str(e):
            return None
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching profile: {str(e)}"
        )

@router.patch("/profile")
async def update_influencer_profile(
    request: UpdateInfluencerProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour son profil influenceur"""
    try:
        user_id = current_user["id"]

        # Préparer les données de mise à jour
        update_data = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Recalculer l'engagement moyen si nécessaire
        if any(k.endswith('_followers') or k.endswith('_engagement_rate') for k in update_data.keys()):
            # Récupérer le profil actuel
            current = supabase.from_("influencer_profiles") \
                .select("*") \
                .eq("user_id", user_id) \
                .single() \
                .execute()

            if current.data:
                # Fusionner avec les nouvelles données
                merged = {**current.data, **update_data}

                engagement_rates = []
                for platform in ['instagram', 'facebook', 'tiktok']:
                    followers_key = f'{platform}_followers'
                    engagement_key = f'{platform}_engagement_rate'
                    if merged.get(followers_key) and merged.get(engagement_key):
                        engagement_rates.append(merged[engagement_key])

                update_data['average_engagement_rate'] = sum(engagement_rates) / len(engagement_rates) if engagement_rates else None

        response = supabase.from_("influencer_profiles") \
            .update(update_data) \
            .eq("user_id", user_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating profile: {str(e)}"
        )

@router.delete("/profile")
async def delete_influencer_profile(current_user: dict = Depends(get_current_user)):
    """Supprimer son profil influenceur de l'annuaire"""
    try:
        user_id = current_user["id"]

        supabase.from_("influencer_profiles") \
            .delete() \
            .eq("user_id", user_id) \
            .execute()

        return {
            "success": True,
            "message": "Profile deleted successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting profile: {str(e)}"
        )

# ============================================
# ENDPOINTS - PUBLIC DIRECTORY
# ============================================

@router.get("/directory")
async def search_influencers(
    search: Optional[str] = Query(None, description="Search query"),
    niche: Optional[str] = Query(None, description="Filter by niche"),
    platform: Optional[str] = Query(None, description="Filter by platform (instagram, tiktok, youtube, facebook)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    min_followers: Optional[int] = Query(None, description="Minimum followers"),
    max_followers: Optional[int] = Query(None, description="Maximum followers"),
    min_engagement: Optional[float] = Query(None, description="Minimum engagement rate"),
    accepts_affiliate: Optional[bool] = Query(None, description="Accepts affiliate programs"),
    accepts_sponsored: Optional[bool] = Query(None, description="Accepts sponsored posts"),
    featured_only: bool = Query(False, description="Featured influencers only"),
    verified_only: bool = Query(False, description="Verified influencers only"),
    sort_by: str = Query("total_followers", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Rechercher dans l'annuaire des influenceurs

    Filtres disponibles:
    - search: Recherche full-text (nom, titre, bio)
    - niche: Niche (Fashion, Beauty, Tech, etc.)
    - platform: Plateforme principale
    - city: Ville
    - min_followers: Nombre de followers minimum
    - max_followers: Nombre de followers maximum
    - min_engagement: Taux d'engagement minimum
    - accepts_affiliate: Accepte les programmes d'affiliation
    - accepts_sponsored: Accepte les posts sponsorisés
    - featured_only: Influenceurs mis en avant
    - verified_only: Profils vérifiés uniquement

    Tri:
    - sort_by: total_followers, average_engagement_rate, created_at, view_count
    - sort_order: asc, desc
    """
    try:
        query = supabase.from_("v_influencer_profiles_public").select("*")

        # Recherche full-text
        if search:
            query = query.text_search("search_vector", search, config="french")

        # Filtres
        if niche:
            query = query.contains("niches", [niche])

        # Filtre par plateforme
        if platform:
            platform_lower = platform.lower()
            if platform_lower == "instagram":
                query = query.gt("instagram_followers", 0)
            elif platform_lower == "facebook":
                query = query.gt("facebook_followers", 0)
            elif platform_lower == "tiktok":
                query = query.gt("tiktok_followers", 0)
            elif platform_lower == "youtube":
                query = query.gt("youtube_subscribers", 0)

        if city:
            query = query.ilike("city", f"%{city}%")

        if min_followers is not None:
            query = query.gte("total_followers", min_followers)

        if max_followers is not None:
            query = query.lte("total_followers", max_followers)

        if min_engagement is not None:
            query = query.gte("average_engagement_rate", min_engagement)

        if accepts_affiliate is not None:
            query = query.eq("accepts_affiliate", accepts_affiliate)

        if accepts_sponsored is not None:
            query = query.eq("accepts_sponsored", accepts_sponsored)

        if featured_only:
            query = query.eq("featured", True)

        if verified_only:
            query = query.eq("verified", True)

        # Toujours filtrer par disponibilité et visibilité
        query = query.eq("is_available", True)

        # Tri
        desc = (sort_order.lower() == "desc")
        query = query.order(sort_by, desc=desc)

        # Pagination
        query = query.range(offset, offset + limit - 1)

        response = query.execute()

        return {
            "influencers": response.data,
            "count": len(response.data),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching influencers: {str(e)}"
        )

@router.get("/{user_id}")
async def get_influencer_profile(user_id: str):
    """
    Détails d'un profil influenceur public

    Incrémente le compteur de vues
    """
    try:
        response = supabase.from_("v_influencer_profiles_public") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Influencer not found")

        # Incrémenter le compteur de vues
        profile_id = response.data.get("id")
        if profile_id:
            await increment_view_count(profile_id)

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching influencer: {str(e)}"
        )

# ============================================
# ENDPOINTS - COLLABORATION REQUESTS
# ============================================

@router.post("/{user_id}/collaborate", status_code=status.HTTP_201_CREATED)
async def request_collaboration(
    user_id: str,
    request: CollaborationRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Demander une collaboration avec un influenceur

    Réservé aux entreprises (merchants)
    """
    try:
        # Vérifier que c'est une entreprise
        if current_user.get("role") != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only companies can request collaborations"
            )

        company_id = current_user["id"]

        # Vérifier que l'influenceur existe
        influencer = supabase.from_("influencer_profiles") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_public", True) \
            .eq("is_available", True) \
            .single() \
            .execute()

        if not influencer.data:
            raise HTTPException(
                status_code=404,
                detail="Influencer not found or not available"
            )

        # Créer la demande
        collaboration_data = {
            "company_id": company_id,
            "target_user_id": user_id,
            "target_type": "influencer",
            "message": request.message,
            "proposed_commission_rate": request.proposed_commission_rate,
            "proposed_budget": request.proposed_budget,
            "proposed_duration_days": request.proposed_duration_days,
            "campaign_details": request.campaign_details,
            "status": "pending"
        }

        response = supabase.from_("collaboration_requests") \
            .insert(collaboration_data) \
            .execute()

        # Incrémenter le compteur de contacts
        await increment_contact_count(influencer.data["id"])

        # TODO: Envoyer notification à l'influenceur

        return {
            "success": True,
            "message": "Collaboration request sent successfully",
            "request": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating collaboration request: {str(e)}"
        )

@router.get("/collaborations/received")
async def get_received_collaboration_requests(
    status_filter: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Demandes de collaboration reçues (pour influenceurs)"""
    try:
        user_id = current_user["id"]

        query = supabase.from_("collaboration_requests") \
            .select("*, company:company_id(*)") \
            .eq("target_user_id", user_id) \
            .eq("target_type", "influencer")

        if status_filter:
            query = query.eq("status", status_filter)

        response = query.order("created_at", desc=True).execute()

        return {
            "requests": response.data,
            "count": len(response.data)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching requests: {str(e)}"
        )

@router.patch("/collaborations/{request_id}/respond")
async def respond_to_collaboration_request(
    request_id: str,
    response_data: CollaborationRequestResponse,
    current_user: dict = Depends(get_current_user)
):
    """Répondre à une demande de collaboration (pour influenceurs)"""
    try:
        user_id = current_user["id"]

        # Vérifier que la demande existe et concerne cet utilisateur
        existing = supabase.from_("collaboration_requests") \
            .select("*") \
            .eq("id", request_id) \
            .eq("target_user_id", user_id) \
            .single() \
            .execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Request not found")

        # Mettre à jour la demande
        update_data = {
            "status": response_data.status,
            "response_message": response_data.response_message,
            "responded_at": datetime.now().isoformat()
        }

        supabase.from_("collaboration_requests") \
            .update(update_data) \
            .eq("id", request_id) \
            .execute()

        # TODO: Envoyer notification à l'entreprise

        return {
            "success": True,
            "message": f"Collaboration request {response_data.status}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error responding to request: {str(e)}"
        )

# ============================================
# ENDPOINTS - REVIEWS
# ============================================

@router.post("/{user_id}/review", status_code=status.HTTP_201_CREATED)
async def create_review(
    user_id: str,
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Créer un avis pour un influenceur

    Réservé aux entreprises ayant travaillé avec l'influenceur
    """
    try:
        # Vérifier que c'est une entreprise
        if current_user.get("role") != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only companies can write reviews"
            )

        reviewer_id = current_user["id"]

        # Vérifier qu'il n'existe pas déjà un avis
        existing = supabase.from_("profile_reviews") \
            .select("id") \
            .eq("profile_user_id", user_id) \
            .eq("reviewer_id", reviewer_id) \
            .execute()

        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=400,
                detail="You have already reviewed this influencer"
            )

        # Créer l'avis
        review_data = {
            "profile_user_id": user_id,
            "profile_type": "influencer",
            "reviewer_id": reviewer_id,
            "rating": review.rating,
            "title": review.title,
            "comment": review.comment,
            "professionalism_rating": review.professionalism_rating,
            "communication_rating": review.communication_rating,
            "results_rating": review.results_rating,
            "would_work_again": review.would_work_again,
            "is_public": True
        }

        response = supabase.from_("profile_reviews") \
            .insert(review_data) \
            .execute()

        return {
            "success": True,
            "message": "Review created successfully",
            "review": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating review: {str(e)}"
        )

@router.get("/{user_id}/reviews")
async def get_influencer_reviews(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Récupérer les avis d'un influenceur"""
    try:
        response = supabase.from_("profile_reviews") \
            .select("*, reviewer:reviewer_id(first_name, last_name, profile_picture)") \
            .eq("profile_user_id", user_id) \
            .eq("profile_type", "influencer") \
            .eq("is_public", True) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()

        return {
            "reviews": response.data,
            "count": len(response.data)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching reviews: {str(e)}"
        )
