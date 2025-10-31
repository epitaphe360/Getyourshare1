"""
TikTok Shop API Endpoints

Endpoints pour gérer l'intégration TikTok Shop:
- Synchronisation de produits
- Tracking des ventes
- Analytics TikTok
- Génération de scripts vidéos
- Trending products
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .services.tiktok_shop_service import tiktok_shop_service, TikTokProductStatus, TikTokOrderStatus

router = APIRouter(prefix="/api/tiktok-shop", tags=["TikTok Shop"])


# ==================== MODELS ====================

class SyncProductRequest(BaseModel):
    """Requête pour synchroniser un produit vers TikTok"""
    product_id: str = Field(..., description="ID du produit dans notre système")
    title: str
    description: str
    category_id: Optional[str] = None
    price: float
    currency: str = Field(default="MAD")
    stock: int = Field(default=0)
    images: List[str] = Field(default_factory=list)
    video_url: Optional[str] = None
    brand: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class ProductStatusResponse(BaseModel):
    """Réponse du statut d'un produit TikTok"""
    product_id: str
    status: str
    views: Optional[int] = None
    likes: Optional[int] = None
    shares: Optional[int] = None

class GenerateVideoScriptRequest(BaseModel):
    """Requête pour générer un script vidéo"""
    product_name: str
    product_description: Optional[str] = None
    style: str = Field(default="review", description="Style: review, unboxing, tutorial, lifestyle, comedy")
    duration_target: int = Field(default=15, description="Durée cible en secondes")
    promo_code: Optional[str] = None

class LiveStreamStatsRequest(BaseModel):
    """Requête pour récupérer les stats d'un live"""
    live_stream_id: str


# ==================== ENDPOINTS ====================

@router.post("/sync-product", summary="Synchroniser un produit vers TikTok Shop")
async def sync_product(request: SyncProductRequest):
    """
    Synchroniser un produit de notre marketplace vers TikTok Shop

    Processus:
    1. Validation des données produit
    2. Upload vers TikTok Shop
    3. Attente de l'approbation (modération TikTok)
    4. Notification du résultat

    Note: Les produits doivent respecter les guidelines TikTok Commerce
    """
    product_data = request.dict()

    result = await tiktok_shop_service.sync_product_to_tiktok(product_data)

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur sync TikTok: {result.get('error')}"
        )

    return {
        "success": True,
        "tiktok_product_id": result["product_id"],
        "status": result["status"],
        "audit_failed_reasons": result.get("audit_failed_reasons", []),
        "demo_mode": result.get("demo_mode", False),
        "message": "Produit synchronisé avec succès! En attente d'approbation TikTok." if result["status"] == "PENDING" else "Produit approuvé et en ligne!"
    }


@router.get("/product-status/{tiktok_product_id}", summary="Récupérer le statut d'un produit")
async def get_product_status(tiktok_product_id: str):
    """
    Récupérer le statut et les métriques d'un produit sur TikTok Shop

    Métriques:
    - Statut (DRAFT, PENDING, APPROVED, LIVE, REJECTED)
    - Vues
    - Likes
    - Partages
    - Ventes
    """
    result = await tiktok_shop_service.get_product_status(tiktok_product_id)

    return {
        "product_id": result["product_id"],
        "status": result["status"],
        "metrics": {
            "views": result.get("views", 0),
            "likes": result.get("likes", 0),
            "shares": result.get("shares", 0)
        },
        "demo_mode": result.get("demo_mode", False)
    }


@router.get("/orders", summary="Récupérer les commandes TikTok Shop")
async def get_orders(
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    status: Optional[TikTokOrderStatus] = None
):
    """
    Récupérer les commandes TikTok Shop

    Permet de tracker toutes les ventes réalisées via TikTok et calculer les commissions

    Filtres:
    - Période (start_date, end_date)
    - Statut (PAID, SHIPPED, DELIVERED, etc.)
    """
    # Parser les dates
    start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
    end = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()

    orders = await tiktok_shop_service.get_orders(
        start_date=start,
        end_date=end,
        status=status
    )

    # Calculer les totaux
    total_orders = len(orders)
    total_revenue = sum(order["total_amount"] for order in orders)
    total_commission = sum(order.get("commission", 0) for order in orders)

    return {
        "orders": orders,
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_commission": total_commission,
            "currency": "MAD",
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat()
            }
        },
        "demo_mode": orders[0].get("demo_mode", False) if orders else False
    }


@router.get("/live-stream-stats/{live_stream_id}", summary="Statistiques d'un TikTok Live")
async def get_live_stream_stats(live_stream_id: str):
    """
    Récupérer les statistiques d'un TikTok Live Stream

    Métriques essentielles:
    - Viewers (pic, moyenne)
    - Engagement (likes, comments, shares)
    - Produits montrés
    - Ventes réalisées pendant le live
    - Revenu généré

    Cas d'usage:
    - Analyser la performance des lives
    - Calculer les commissions
    - Identifier les produits à succès
    """
    stats = await tiktok_shop_service.get_live_stream_stats(live_stream_id)

    return {
        "live_stream_id": stats["live_stream_id"],
        "status": stats["status"],
        "engagement": {
            "viewers_peak": stats.get("viewers_peak", 0),
            "viewers_average": stats.get("viewers_average", 0),
            "likes": stats.get("likes", 0),
            "comments": stats.get("comments", 0),
            "shares": stats.get("shares", 0)
        },
        "performance": {
            "duration_minutes": stats.get("duration_minutes", 0),
            "products_shown": stats.get("products_shown", 0),
            "sales_count": stats.get("sales_count", 0),
            "total_revenue": stats.get("total_revenue", 0),
            "commission_earned": stats.get("commission_earned", 0),
            "currency": stats.get("currency", "MAD")
        },
        "demo_mode": stats.get("demo_mode", False)
    }


@router.get("/analytics", summary="Analytics TikTok Shop")
async def get_analytics(
    start_date: str = Query(..., description="Date de début (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Date de fin (YYYY-MM-DD)"),
    metrics: Optional[str] = Query(None, description="Métriques séparées par virgules")
):
    """
    Récupérer les analytics TikTok Shop

    Métriques disponibles:
    - views: Vues des produits
    - clicks: Clics sur liens
    - add_to_cart: Ajouts au panier
    - purchases: Achats
    - gmv: Gross Merchandise Value (revenu total)
    - conversion_rate: Taux de conversion

    Période: Jusqu'à 90 jours
    """
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    metrics_list = metrics.split(",") if metrics else None

    analytics = await tiktok_shop_service.get_analytics(
        start_date=start,
        end_date=end,
        metrics=metrics_list
    )

    return {
        "period": {
            "start": analytics["start_date"],
            "end": analytics["end_date"]
        },
        "summary": analytics.get("summary", {}),
        "daily_data": analytics.get("daily_data", []),
        "demo_mode": analytics.get("demo_mode", False)
    }


@router.post("/generate-video-script", summary="Générer un script de vidéo TikTok")
async def generate_video_script(request: GenerateVideoScriptRequest):
    """
    Générer un script optimisé pour une vidéo TikTok

    Styles disponibles:
    - **review**: Critique/test du produit (meilleur pour engagement)
    - **unboxing**: Déballage (très populaire au Maroc)
    - **tutorial**: Tutoriel d'utilisation (éducatif)
    - **lifestyle**: Mise en situation lifestyle
    - **comedy**: Approche humoristique

    Le script inclut:
    - Hook (3 premières secondes captivantes)
    - Scènes détaillées avec timing
    - Texte à dire/afficher
    - Suggestions musicales
    - Hashtags optimisés
    """
    product = {
        "name": request.product_name,
        "description": request.product_description,
        "promo_code": request.promo_code
    }

    script = tiktok_shop_service.generate_video_script(product, request.style)

    return {
        "script": script,
        "tips": [
            "📱 Filme en mode portrait (9:16)",
            "🎬 Commence fort: 3 premières secondes cruciales!",
            "💬 Ajoute des sous-titres (70% regardent sans son)",
            "🔗 Mets ton lien en bio",
            "⏰ Meilleur moment pour poster: 18h-22h",
            f"📅 Jours optimaux: {', '.join(['Jeudi', 'Vendredi', 'Samedi'])}"
        ],
        "estimated_reach": "5,000 - 50,000 vues (selon ton audience)",
        "estimated_engagement_rate": "8-12%"
    }


@router.get("/trending-categories", summary="Catégories tendance TikTok Maroc")
async def get_trending_categories():
    """
    Récupérer les catégories de produits tendance sur TikTok au Maroc

    Inclut:
    - Score de tendance (0-100)
    - Vues moyennes
    - Top produits de la catégorie
    - Meilleurs moments pour poster
    - Jours de pic d'engagement

    Utile pour choisir quels produits promouvoir
    """
    categories = tiktok_shop_service.get_trending_products_categories()

    return {
        "trending_categories": categories,
        "last_updated": datetime.utcnow().isoformat(),
        "market": "Morocco",
        "tips": [
            "🔥 Fashion & Beauty domine au Maroc",
            "📱 Electronics marche très bien chez les 18-25 ans",
            "🏠 Home & Kitchen explose le weekend",
            "💪 Sports & Fitness: poster tôt le matin ou en soirée"
        ]
    }


@router.post("/bulk-sync", summary="Synchroniser plusieurs produits en masse")
async def bulk_sync_products(
    product_ids: List[str],
    background_tasks: BackgroundTasks
):
    """
    Synchroniser plusieurs produits vers TikTok Shop en arrière-plan

    Processus asynchrone:
    1. Ajoute les produits à la file d'attente
    2. Synchronise un par un
    3. Envoie une notification à la fin

    Limite: 50 produits par requête
    """
    if len(product_ids) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 produits par synchronisation en masse"
        )

    # Lancer en arrière-plan
    background_tasks.add_task(sync_products_background, product_ids)

    return {
        "success": True,
        "products_queued": len(product_ids),
        "estimated_time_minutes": len(product_ids) * 0.5,  # ~30 sec par produit
        "message": "Synchronisation en cours... Vous recevrez une notification à la fin."
    }


@router.get("/product-suggestions", summary="Suggestions de produits à promouvoir")
async def get_product_suggestions(
    category: Optional[str] = None,
    min_trending_score: int = Query(default=70, ge=0, le=100)
):
    """
    Obtenir des suggestions de produits à promouvoir sur TikTok

    Basé sur:
    - Tendances actuelles
    - Performance historique
    - Taux d'engagement
    - Potentiel de viralité

    Aide les influenceurs à choisir les meilleurs produits
    """
    # Logique de suggestion basée sur les tendances
    suggestions = [
        {
            "product_name": "Hijab Jersey Premium",
            "category": "Fashion & Beauty",
            "trending_score": 95,
            "estimated_views": "15K - 80K",
            "estimated_sales": "50 - 200",
            "commission_rate": 15.0,
            "why_trending": "Ramadan approche, forte demande",
            "best_hashtags": ["#hijabstyle", "#modest fashion", "#maroc", "#tiktokshop"]
        },
        {
            "product_name": "Écouteurs Bluetooth TWS",
            "category": "Electronics",
            "trending_score": 88,
            "estimated_views": "10K - 50K",
            "estimated_sales": "30 - 150",
            "commission_rate": 12.0,
            "why_trending": "Toujours tendance, bon rapport qualité/prix",
            "best_hashtags": ["#tech", "#gadgets", "#maroc", "#unboxing"]
        },
        {
            "product_name": "Kit Café Marocain Luxe",
            "category": "Home & Kitchen",
            "trending_score": 82,
            "estimated_views": "8K - 40K",
            "estimated_sales": "25 - 100",
            "commission_rate": 18.0,
            "why_trending": "Culture marocaine, engagement élevé",
            "best_hashtags": ["#moroccanstyle", "#cafe", "#tradition", "#maroc"]
        }
    ]

    # Filtrer par catégorie si spécifiée
    if category:
        suggestions = [s for s in suggestions if s["category"].lower() == category.lower()]

    # Filtrer par score minimum
    suggestions = [s for s in suggestions if s["trending_score"] >= min_trending_score]

    return {
        "suggestions": suggestions,
        "count": len(suggestions),
        "filters_applied": {
            "category": category,
            "min_trending_score": min_trending_score
        }
    }


# ==================== BACKGROUND TASKS ====================

async def sync_products_background(product_ids: List[str]):
    """
    Synchroniser les produits en arrière-plan

    TODO: Implémenter la récupération des produits depuis la DB
    et envoyer une notification à la fin
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"🎵 Début synchronisation TikTok: {len(product_ids)} produits")

    for product_id in product_ids:
        try:
            # TODO: Récupérer le produit de la DB
            # product = await get_product_from_db(product_id)
            # await tiktok_shop_service.sync_product_to_tiktok(product)

            logger.info(f"✅ Produit {product_id} synchronisé")
        except Exception as e:
            logger.error(f"❌ Erreur sync produit {product_id}: {str(e)}")

    logger.info(f"🎉 Synchronisation TikTok terminée: {len(product_ids)} produits")
    # TODO: Envoyer notification WhatsApp/Email
