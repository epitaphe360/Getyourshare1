"""
Marketplace Endpoints - Style Groupon
API pour marketplace avec deals, produits détaillés, reviews

Endpoints:
- GET /api/marketplace/products - Liste produits marketplace
- GET /api/marketplace/products/{id} - Détails produit complet
- GET /api/marketplace/categories - Catégories
- GET /api/marketplace/featured - Produits featured
- GET /api/marketplace/deals-of-day - Deals du jour
- POST /api/marketplace/products/{id}/view - Incrémenter vues
- POST /api/marketplace/products/{id}/request-affiliate - Demander affiliation
- POST /api/marketplace/products/{id}/review - Ajouter avis
- GET /api/marketplace/products/{id}/reviews - Avis produit
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import structlog

from auth import get_current_user, optional_auth
from supabase_client import supabase

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])
logger = structlog.get_logger()


# ============================================
# PYDANTIC MODELS
# ============================================

class ProductHighlight(BaseModel):
    """Point clé produit"""
    icon: str = Field(..., description="Emoji ou icon")
    text: str = Field(..., description="Texte du highlight")


class ProductFAQ(BaseModel):
    """Question fréquente"""
    question: str
    answer: str


class ProductLocation(BaseModel):
    """Localisation service"""
    address: str
    city: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class ProductReviewRequest(BaseModel):
    """Créer un avis"""
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    title: Optional[str] = Field(None, max_length=255)
    comment: str = Field(..., min_length=10, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "title": "Excellent service!",
                "comment": "J'ai adoré ce service. Personnel professionnel, ambiance agréable. Je recommande!"
            }
        }


class AffiliateRequestCreate(BaseModel):
    """Demande d'affiliation"""
    message: Optional[str] = Field(None, max_length=500, description="Message au marchand")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Bonjour, je suis influenceur avec 50K followers sur Instagram. J'aimerais promouvoir vos produits."
            }
        }


# ============================================
# ENDPOINTS - PUBLIC
# ============================================

@router.get("/products", response_model=dict)
async def get_marketplace_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|price|rating|sold_count|discount)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_discount: Optional[int] = None
):
    """
    Liste des produits marketplace

    **Filtres:**
    - category: Slug de catégorie
    - search: Recherche texte (nom, description)
    - min_price, max_price: Fourchette de prix
    - min_discount: Réduction minimum (%)

    **Tri:**
    - created_at: Date de création
    - price: Prix
    - rating: Note moyenne
    - sold_count: Nombre de ventes
    - discount: % de réduction
    """
    try:
        offset = (page - 1) * limit

        # Construire query
        query = supabase.table('v_products_full').select('*', count='exact')

        # Filtre: produits actifs uniquement
        query = query.eq('deal_status', 'active')

        # Filtre: catégorie
        if category:
            # TODO: Filtrer par catégorie (nécessite ajustement query)
            pass

        # Filtre: recherche
        if search:
            query = query.or_(f'name.ilike.%{search}%,description.ilike.%{search}%')

        # Filtre: prix
        if min_price:
            query = query.gte('discounted_price', min_price)
        if max_price:
            query = query.lte('discounted_price', max_price)

        # Filtre: réduction
        if min_discount:
            query = query.gte('discount_percentage', min_discount)

        # Tri
        if sort_by == "price":
            sort_field = "discounted_price"
        elif sort_by == "rating":
            sort_field = "rating_average"
        elif sort_by == "sold_count":
            sort_field = "sold_count"
        elif sort_by == "discount":
            sort_field = "discount_percentage"
        else:
            sort_field = "created_at"

        query = query.order(sort_field, desc=(order == 'desc'))

        # Pagination
        query = query.range(offset, offset + limit - 1)

        # Exécuter
        result = query.execute()

        return {
            "success": True,
            "products": result.data or [],
            "total": result.count,
            "page": page,
            "limit": limit,
            "total_pages": (result.count + limit - 1) // limit if result.count else 0
        }

    except Exception as e:
        logger.error("get_marketplace_products_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des produits"
        )


@router.get("/products/{product_id}", response_model=dict)
async def get_product_detail(product_id: str):
    """
    Détails complets d'un produit (style Groupon)

    **Inclut:**
    - Toutes les infos produit
    - Images
    - Highlights
    - Conditions
    - FAQ
    - Reviews
    - Marchand info
    - Stats (ventes, vues, rating)
    """
    try:
        # Récupérer produit complet
        result = supabase.table('v_products_full').select('*').eq('id', product_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )

        product = result.data[0]

        # Incrémenter vues (async)
        try:
            supabase.rpc('increment_product_views', {'p_product_id': product_id}).execute()
        except:
            pass  # Non-bloquant

        return {
            "success": True,
            "product": product
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_product_detail_failed", product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du produit"
        )


@router.get("/categories", response_model=dict)
async def get_categories():
    """
    Liste des catégories de produits

    Hiérarchie: catégories parents + sous-catégories
    """
    try:
        # Récupérer toutes les catégories actives
        result = supabase.table('product_categories').select('*').eq('is_active', True).order('display_order').execute()

        categories = result.data or []

        # Organiser en hiérarchie
        categories_map = {cat['id']: {**cat, 'children': []} for cat in categories}
        root_categories = []

        for cat in categories:
            if cat.get('parent_id'):
                # Sous-catégorie
                if cat['parent_id'] in categories_map:
                    categories_map[cat['parent_id']]['children'].append(categories_map[cat['id']])
            else:
                # Catégorie racine
                root_categories.append(categories_map[cat['id']])

        return {
            "success": True,
            "categories": root_categories
        }

    except Exception as e:
        logger.error("get_categories_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des catégories"
        )


@router.get("/featured", response_model=dict)
async def get_featured_products(limit: int = Query(10, ge=1, le=50)):
    """
    Produits mis en avant (featured)

    Triés par nombre de ventes et rating
    """
    try:
        result = supabase.table('v_featured_products').select('*').limit(limit).execute()

        return {
            "success": True,
            "products": result.data or []
        }

    except Exception as e:
        logger.error("get_featured_products_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des produits featured"
        )


@router.get("/deals-of-day", response_model=dict)
async def get_deals_of_day(limit: int = Query(10, ge=1, le=50)):
    """
    Deals du jour

    Produits avec les meilleures réductions actives
    """
    try:
        result = supabase.table('v_deals_of_day').select('*').limit(limit).execute()

        return {
            "success": True,
            "deals": result.data or []
        }

    except Exception as e:
        logger.error("get_deals_of_day_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des deals"
        )


@router.get("/products/{product_id}/reviews", response_model=dict)
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    sort_by: str = Query("created_at", regex="^(created_at|rating|helpful)$")
):
    """
    Avis clients d'un produit

    **Tri:**
    - created_at: Plus récents
    - rating: Meilleure note
    - helpful: Plus utiles
    """
    try:
        offset = (page - 1) * limit

        # Récupérer reviews approuvés
        query = supabase.table('product_reviews').select(
            '*',
            'users(first_name, last_name)'
        ).eq('product_id', product_id).eq('is_approved', True)

        # Tri
        if sort_by == "rating":
            query = query.order('rating', desc=True)
        elif sort_by == "helpful":
            query = query.order('helpful_count', desc=True)
        else:
            query = query.order('created_at', desc=True)

        query = query.range(offset, offset + limit - 1)

        result = query.execute()

        return {
            "success": True,
            "reviews": result.data or [],
            "page": page,
            "limit": limit
        }

    except Exception as e:
        logger.error("get_product_reviews_failed", product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des avis"
        )


# ============================================
# ENDPOINTS - AUTHENTICATED
# ============================================

@router.post("/products/{product_id}/request-affiliate", response_model=dict)
async def request_affiliate(
    product_id: str,
    request_data: AffiliateRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Demander affiliation pour un produit

    **Requis:**
    - Être connecté (influenceur)
    - Produit actif

    **Process:**
    1. Vérifier produit existe
    2. Vérifier pas déjà affilié
    3. Créer demande (status: pending)
    4. Notifier marchand par email
    """
    user_id = current_user.get("id")
    user_role = current_user.get("role")

    try:
        # Vérifier rôle
        if user_role != "influencer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les influenceurs peuvent demander une affiliation"
            )

        # Vérifier produit existe
        product_result = supabase.table('products').select('*').eq('id', product_id).eq('is_active', True).execute()

        if not product_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )

        product = product_result.data[0]
        merchant_id = product['merchant_id']

        # Vérifier pas déjà demandé
        existing = supabase.table('affiliate_requests').select('*').eq('influencer_id', user_id).eq('product_id', product_id).execute()

        if existing.data:
            existing_request = existing.data[0]
            if existing_request['status'] == 'pending':
                return {
                    "success": False,
                    "message": "Vous avez déjà une demande en attente pour ce produit",
                    "request_id": existing_request['id']
                }
            elif existing_request['status'] == 'approved':
                return {
                    "success": False,
                    "message": "Vous êtes déjà affilié à ce produit",
                    "request_id": existing_request['id']
                }

        # Créer demande
        affiliate_request = {
            'influencer_id': user_id,
            'merchant_id': merchant_id,
            'product_id': product_id,
            'status': 'pending',
            'message': request_data.message,
            'created_at': datetime.utcnow().isoformat()
        }

        result = supabase.table('affiliate_requests').insert(affiliate_request).execute()

        request_id = result.data[0]['id'] if result.data else None

        # Envoyer email au marchand (async)
        # TODO: Implémenter notification email
        from celery_tasks import send_new_affiliate_request_email
        # send_new_affiliate_request_email.delay(merchant_email, product_name, influencer_name)

        logger.info("affiliate_request_created", user_id=user_id, product_id=product_id, request_id=request_id)

        return {
            "success": True,
            "message": "Demande d'affiliation envoyée avec succès",
            "request_id": request_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("request_affiliate_failed", user_id=user_id, product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la demande d'affiliation"
        )


@router.post("/products/{product_id}/review", response_model=dict)
async def create_product_review(
    product_id: str,
    review_data: ProductReviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Ajouter un avis sur un produit

    **Requis:**
    - Être connecté
    - 1 seul avis par produit par utilisateur

    **L'avis sera en attente d'approbation par admin**
    """
    user_id = current_user.get("id")

    try:
        # Vérifier produit existe
        product_result = supabase.table('products').select('id').eq('id', product_id).execute()

        if not product_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )

        # Vérifier pas déjà reviewé
        existing = supabase.table('product_reviews').select('id').eq('product_id', product_id).eq('user_id', user_id).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous avez déjà laissé un avis sur ce produit"
            )

        # Créer review
        review = {
            'product_id': product_id,
            'user_id': user_id,
            'rating': review_data.rating,
            'title': review_data.title,
            'comment': review_data.comment,
            'is_approved': False,  # En attente modération
            'created_at': datetime.utcnow().isoformat()
        }

        result = supabase.table('product_reviews').insert(review).execute()

        review_id = result.data[0]['id'] if result.data else None

        logger.info("product_review_created", user_id=user_id, product_id=product_id, review_id=review_id)

        return {
            "success": True,
            "message": "Avis soumis avec succès. Il sera publié après modération.",
            "review_id": review_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_product_review_failed", user_id=user_id, product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'avis"
        )
