"""
============================================
COMMERCIALS DIRECTORY ENDPOINTS
Share Your Sales - Annuaire des Commerciaux
============================================

Annuaire public des commerciaux disponibles:
- Création et gestion de profils professionnels
- Recherche et filtrage
- Demandes de collaboration
- Système d'évaluation
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
import os
from auth import get_current_user

router = APIRouter(prefix="/api/commercials", tags=["Commercials Directory"])

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

class CreateCommercialProfileRequest(BaseModel):
    """Création d'un profil commercial"""
    headline: str = Field(..., max_length=255)
    bio: str
    specialties: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    city: Optional[str] = None
    region: Optional[str] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    industries: List[str] = Field(default_factory=list)
    availability_type: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    commission_expectation: Optional[float] = Field(None, ge=0, le=100)
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    is_public: bool = True

    @validator('availability_type')
    def validate_availability_type(cls, v):
        if v is not None:
            allowed = ['full_time', 'part_time', 'freelance', 'contract']
            if v not in allowed:
                raise ValueError(f"Availability type must be one of: {', '.join(allowed)}")
        return v

class UpdateCommercialProfileRequest(BaseModel):
    """Mise à jour du profil commercial"""
    headline: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    specialties: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    city: Optional[str] = None
    region: Optional[str] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    industries: Optional[List[str]] = None
    availability_type: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    commission_expectation: Optional[float] = Field(None, ge=0, le=100)
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
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
        supabase.rpc("increment", {
            "table_name": "commercial_profiles",
            "id_value": profile_id,
            "column_name": "view_count"
        }).execute()
    except Exception as e:
        print(f"Error incrementing view count: {e}")

async def increment_contact_count(profile_id: str):
    """Incrémenter le compteur de contacts"""
    try:
        supabase.rpc("increment", {
            "table_name": "commercial_profiles",
            "id_value": profile_id,
            "column_name": "contact_count"
        }).execute()
    except Exception as e:
        print(f"Error incrementing contact count: {e}")

# ============================================
# ENDPOINTS - PROFILE MANAGEMENT
# ============================================

@router.post("/profile", status_code=status.HTTP_201_CREATED)
async def create_commercial_profile(
    request: CreateCommercialProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Créer un profil commercial dans l'annuaire

    Accessible à:
    - Commerciaux indépendants (abonnement Marketplace 99 MAD)
    - Membres d'équipe (invités par entreprises)
    """
    try:
        user_id = current_user["id"]

        # Vérifier qu'il n'existe pas déjà un profil
        existing = supabase.from_("commercial_profiles") \
            .select("id") \
            .eq("user_id", user_id) \
            .execute()

        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=400,
                detail="Commercial profile already exists"
            )

        # Créer le profil
        profile_data = {
            "user_id": user_id,
            "headline": request.headline,
            "bio": request.bio,
            "specialties": request.specialties,
            "languages": request.languages,
            "city": request.city,
            "region": request.region,
            "years_of_experience": request.years_of_experience,
            "industries": request.industries,
            "availability_type": request.availability_type,
            "hourly_rate": request.hourly_rate,
            "commission_expectation": request.commission_expectation,
            "phone": request.phone,
            "linkedin_url": request.linkedin_url,
            "website_url": request.website_url,
            "is_public": request.is_public,
            "is_available": True
        }

        response = supabase.from_("commercial_profiles") \
            .insert(profile_data) \
            .execute()

        return {
            "success": True,
            "message": "Commercial profile created successfully",
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
async def get_my_commercial_profile(current_user: dict = Depends(get_current_user)):
    """Récupérer son propre profil commercial"""
    try:
        user_id = current_user["id"]

        response = supabase.from_("commercial_profiles") \
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
async def update_commercial_profile(
    request: UpdateCommercialProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour son profil commercial"""
    try:
        user_id = current_user["id"]

        # Préparer les données de mise à jour
        update_data = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        response = supabase.from_("commercial_profiles") \
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
async def delete_commercial_profile(current_user: dict = Depends(get_current_user)):
    """Supprimer son profil commercial de l'annuaire"""
    try:
        user_id = current_user["id"]

        supabase.from_("commercial_profiles") \
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
async def search_commercials(
    search: Optional[str] = Query(None, description="Search query"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    city: Optional[str] = Query(None, description="Filter by city"),
    availability_type: Optional[str] = Query(None, description="Filter by availability type"),
    min_experience: Optional[int] = Query(None, description="Minimum years of experience"),
    featured_only: bool = Query(False, description="Featured commercials only"),
    verified_only: bool = Query(False, description="Verified commercials only"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Rechercher dans l'annuaire des commerciaux

    Filtres disponibles:
    - search: Recherche full-text (nom, titre, bio)
    - specialty: Spécialité (Tech, Finance, etc.)
    - industry: Industrie (E-commerce, SaaS, etc.)
    - city: Ville
    - availability_type: Type de disponibilité
    - min_experience: Années d'expérience minimum
    - featured_only: Commerciaux mis en avant
    - verified_only: Profils vérifiés uniquement

    Tri:
    - sort_by: created_at, total_sales, average_rating, view_count
    - sort_order: asc, desc
    """
    try:
        query = supabase.from_("v_commercial_profiles_public").select("*")

        # Recherche full-text
        if search:
            query = query.text_search("search_vector", search, config="french")

        # Filtres
        if specialty:
            query = query.contains("specialties", [specialty])

        if industry:
            query = query.contains("industries", [industry])

        if city:
            query = query.ilike("city", f"%{city}%")

        if availability_type:
            query = query.eq("availability_type", availability_type)

        if min_experience is not None:
            query = query.gte("years_of_experience", min_experience)

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
            "commercials": response.data,
            "count": len(response.data),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching commercials: {str(e)}"
        )

@router.get("/{user_id}")
async def get_commercial_profile(user_id: str):
    """
    Détails d'un profil commercial public

    Incrémente le compteur de vues
    """
    try:
        response = supabase.from_("v_commercial_profiles_public") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Commercial not found")

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
            detail=f"Error fetching commercial: {str(e)}"
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
    Demander une collaboration avec un commercial

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

        # Vérifier que le commercial existe
        commercial = supabase.from_("commercial_profiles") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_public", True) \
            .eq("is_available", True) \
            .single() \
            .execute()

        if not commercial.data:
            raise HTTPException(
                status_code=404,
                detail="Commercial not found or not available"
            )

        # Créer la demande
        collaboration_data = {
            "company_id": company_id,
            "target_user_id": user_id,
            "target_type": "commercial",
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
        await increment_contact_count(commercial.data["id"])

        # TODO: Envoyer notification au commercial

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
    """Demandes de collaboration reçues (pour commerciaux)"""
    try:
        user_id = current_user["id"]

        query = supabase.from_("collaboration_requests") \
            .select("*, company:company_id(*)") \
            .eq("target_user_id", user_id) \
            .eq("target_type", "commercial")

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

@router.get("/collaborations/sent")
async def get_sent_collaboration_requests(
    status_filter: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Demandes de collaboration envoyées (pour entreprises)"""
    try:
        company_id = current_user["id"]

        query = supabase.from_("collaboration_requests") \
            .select("*, target:target_user_id(*)") \
            .eq("company_id", company_id)

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
    """Répondre à une demande de collaboration (pour commerciaux)"""
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
    Créer un avis pour un commercial

    Réservé aux entreprises ayant travaillé avec le commercial
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
                detail="You have already reviewed this commercial"
            )

        # Créer l'avis
        review_data = {
            "profile_user_id": user_id,
            "profile_type": "commercial",
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
async def get_commercial_reviews(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Récupérer les avis d'un commercial"""
    try:
        response = supabase.from_("profile_reviews") \
            .select("*, reviewer:reviewer_id(first_name, last_name, profile_picture)") \
            .eq("profile_user_id", user_id) \
            .eq("profile_type", "commercial") \
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
