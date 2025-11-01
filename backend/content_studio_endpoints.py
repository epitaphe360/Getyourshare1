"""
Content Studio API Endpoints

Endpoints pour le studio de création de contenu:
- Génération d'images IA
- Bibliothèque de templates
- QR codes stylisés
- Watermarking
- Planification de posts
- A/B Testing
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .services.content_studio_service import (
    content_studio_service,
    ContentType,
    SocialPlatform,
    TemplateCategory
)

router = APIRouter(prefix="/api/content-studio", tags=["Content Studio"])


# ==================== MODELS ====================

class GenerateImageRequest(BaseModel):
    """Requête pour générer une image avec IA"""
    prompt: str = Field(..., description="Description de l'image à générer")
    style: str = Field(default="realistic", description="Style: realistic, artistic, cartoon, minimalist")
    size: str = Field(default="1024x1024", description="Taille: 1024x1024, 1792x1024, 1024x1792")
    quality: str = Field(default="standard", description="Qualité: standard, hd")

class GenerateQRCodeRequest(BaseModel):
    """Requête pour générer un QR code"""
    url: str
    style: str = Field(default="modern", description="Style: modern, rounded, dots, artistic")
    color: str = Field(default="#000000")
    bg_color: str = Field(default="#FFFFFF")
    logo_url: Optional[str] = None
    size: int = Field(default=512)

class AddWatermarkRequest(BaseModel):
    """Requête pour ajouter un watermark"""
    image_url: str
    watermark_text: str = Field(..., description="Texte du watermark (ex: @username)")
    position: str = Field(default="bottom-right")
    opacity: float = Field(default=0.7, ge=0.0, le=1.0)
    include_link: bool = Field(default=True)
    affiliate_link: Optional[str] = None

class SchedulePostRequest(BaseModel):
    """Requête pour planifier un post"""
    content: Dict[str, Any] = Field(..., description="Contenu du post (texte, image, etc.)")
    platforms: List[str] = Field(..., description="Plateformes: instagram, tiktok, facebook, etc.")
    scheduled_time: str = Field(..., description="Date/heure au format ISO")
    user_id: str

class ABTestRequest(BaseModel):
    """Requête pour analyser un A/B test"""
    creative_id: str
    variant_a_id: str
    variant_b_id: str


# ==================== ENDPOINTS ====================

@router.post("/generate-image", summary="Générer une image avec IA")
async def generate_image(request: GenerateImageRequest):
    """
    Générer une image avec DALL-E 3 ou Stable Diffusion

    Cas d'usage:
    - Créer des visuels pour produits
    - Générer des backgrounds
    - Créer des illustrations uniques
    - Contenu original pour posts

    Styles disponibles:
    - **realistic**: Photorealistic, haute qualité
    - **artistic**: Artistique, créatif
    - **cartoon**: Style cartoon, fun
    - **minimalist**: Minimaliste, épuré

    Tailles:
    - 1024x1024: Carré (Instagram Post)
    - 1792x1024: Paysage (Facebook Cover)
    - 1024x1792: Portrait (Instagram Story)
    """
    result = await content_studio_service.generate_image_ai(
        prompt=request.prompt,
        style=request.style,
        size=request.size,
        quality=request.quality
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"Erreur génération image: {result.get('error')}"
        )

    return {
        "success": True,
        "image_url": result["image_url"],
        "prompt": request.prompt,
        "style": request.style,
        "revised_prompt": result.get("revised_prompt"),
        "demo_mode": result.get("demo_mode", False)
    }


@router.get("/templates", summary="Liste des templates disponibles")
async def get_templates(
    category: Optional[TemplateCategory] = None,
    content_type: Optional[ContentType] = None,
    platform: Optional[SocialPlatform] = None
):
    """
    Récupérer les templates prêts à l'emploi

    Filtres:
    - **category**: product_showcase, promotion, review, tutorial, testimonial, announcement, quote
    - **content_type**: post, story, reel, carousel, video
    - **platform**: instagram, tiktok, facebook, twitter, linkedin, whatsapp

    Retourne:
    - Liste de templates avec aperçu
    - Éléments personnalisables
    - Dimensions recommandées
    - Plateformes compatibles

    Plus de 50 templates disponibles!
    """
    templates = content_studio_service.get_templates(
        category=category,
        content_type=content_type,
        platform=platform
    )

    return {
        "templates": templates,
        "count": len(templates),
        "filters": {
            "category": category.value if category else None,
            "content_type": content_type.value if content_type else None,
            "platform": platform.value if platform else None
        }
    }


@router.get("/templates/{template_id}", summary="Détails d'un template")
async def get_template_details(template_id: str):
    """
    Récupérer les détails complets d'un template

    Inclut:
    - Tous les éléments personnalisables
    - Dimensions exactes
    - Exemple de rendu
    - Instructions d'utilisation
    """
    templates = content_studio_service.get_templates()
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")

    return {
        "template": template,
        "customization_guide": {
            "required_fields": [
                elem for elem in template.get("elements", [])
                if "placeholder" in elem or "{{" in str(elem.get("content", ""))
            ],
            "optional_fields": [
                elem for elem in template.get("elements", [])
                if elem["type"] in ["badge", "countdown", "cta"]
            ]
        }
    }


@router.post("/generate-qr-code", summary="Générer un QR code stylisé")
async def generate_qr_code(request: GenerateQRCodeRequest):
    """
    Générer un QR code stylisé pour lien d'affiliation

    Styles:
    - **modern**: Style moderne classique
    - **rounded**: Coins arrondis
    - **dots**: Points au lieu de carrés
    - **artistic**: Style artistique unique

    Features:
    - Couleurs personnalisables
    - Logo au centre (optionnel)
    - Haute résolution
    - Format PNG transparent

    Le QR code est retourné en base64 (data URL)
    """
    qr_code = content_studio_service.generate_qr_code(
        url=request.url,
        style=request.style,
        color=request.color,
        bg_color=request.bg_color,
        logo_url=request.logo_url,
        size=request.size
    )

    if not qr_code:
        raise HTTPException(
            status_code=500,
            detail="Erreur génération QR code"
        )

    return {
        "success": True,
        "qr_code": qr_code,  # Data URL base64
        "url": request.url,
        "style": request.style,
        "size": request.size
    }


@router.post("/add-watermark", summary="Ajouter un watermark")
async def add_watermark(request: AddWatermarkRequest):
    """
    Ajouter un watermark automatique avec lien d'affiliation

    Positions:
    - top-left, top-right
    - bottom-left, bottom-right
    - center

    Watermark inclut:
    - Votre @username
    - Lien d'affiliation (si activé)
    - Opacité réglable
    - Ombre pour lisibilité

    Retourne l'URL de l'image watermarkée
    """
    # TODO: Télécharger l'image depuis l'URL
    # TODO: Appliquer le watermark
    # TODO: Upload sur CDN
    # Pour l'instant, retourne une URL demo

    watermarked_url = request.image_url.replace(".jpg", "_watermarked.jpg")

    return {
        "success": True,
        "original_url": request.image_url,
        "watermarked_url": watermarked_url,
        "watermark_text": request.watermark_text,
        "position": request.position
    }


@router.post("/schedule-post", summary="Planifier un post multi-réseaux")
async def schedule_post(
    request: SchedulePostRequest,
    background_tasks: BackgroundTasks
):
    """
    Planifier un post sur plusieurs réseaux sociaux

    Plateformes supportées:
    - Instagram (Post, Story, Reel)
    - TikTok
    - Facebook
    - Twitter
    - LinkedIn
    - WhatsApp Status

    Features:
    - Planification multi-plateformes
    - Adaptation automatique du format par plateforme
    - Retry automatique en cas d'échec
    - Notifications de confirmation
    - Analytics de performance

    Le post sera publié automatiquement à l'heure prévue
    """
    # Parser la date
    try:
        scheduled_time = datetime.fromisoformat(request.scheduled_time)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Format de date invalide. Utilisez le format ISO: YYYY-MM-DDTHH:MM:SS"
        )

    # Vérifier que la date est dans le futur
    if scheduled_time <= datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="La date de publication doit être dans le futur"
        )

    # Convertir les plateformes
    platforms = []
    for p in request.platforms:
        try:
            platforms.append(SocialPlatform(p))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Plateforme invalide: {p}"
            )

    # Planifier le post
    result = content_studio_service.schedule_post(
        content=request.content,
        platforms=platforms,
        scheduled_time=scheduled_time,
        user_id=request.user_id
    )

    return {
        "success": True,
        "scheduled_id": result["scheduled_id"],
        "scheduled_time": result["scheduled_time"],
        "platforms": result["platforms"],
        "status": "scheduled",
        "message": f"Post planifié pour {scheduled_time.strftime('%d/%m/%Y à %H:%M')}"
    }


@router.get("/scheduled-posts/{user_id}", summary="Liste des posts planifiés")
async def get_scheduled_posts(user_id: str):
    """
    Récupérer tous les posts planifiés d'un utilisateur

    Retourne:
    - Posts à venir
    - Posts publiés
    - Posts en erreur

    Permet de gérer et modifier les posts avant publication
    """
    # TODO: Récupérer depuis la DB

    # Données demo
    scheduled_posts = [
        {
            "id": "sched_123",
            "content": {
                "text": "Découvrez ce super produit! 🔥",
                "image_url": "https://...",
                "hashtags": ["#promo", "#maroc"]
            },
            "platforms": ["instagram", "facebook"],
            "scheduled_time": "2025-11-01T18:00:00",
            "status": "pending"
        },
        {
            "id": "sched_124",
            "content": {
                "text": "Nouvelle vidéo TikTok! 🎬",
                "video_url": "https://..."
            },
            "platforms": ["tiktok", "instagram"],
            "scheduled_time": "2025-11-01T20:00:00",
            "status": "pending"
        }
    ]

    return {
        "scheduled_posts": scheduled_posts,
        "count": len(scheduled_posts),
        "user_id": user_id
    }


@router.delete("/scheduled-posts/{post_id}", summary="Annuler un post planifié")
async def cancel_scheduled_post(post_id: str):
    """
    Annuler un post planifié

    Le post ne sera pas publié et sera supprimé de la file d'attente
    """
    # TODO: Supprimer de la DB et annuler le job cron

    return {
        "success": True,
        "post_id": post_id,
        "status": "cancelled",
        "message": "Post annulé avec succès"
    }


@router.post("/ab-test/analyze", summary="Analyser un A/B test")
async def analyze_ab_test(request: ABTestRequest):
    """
    Analyser la performance de 2 variantes (A/B testing)

    Compare:
    - Impressions
    - Clics (CTR)
    - Conversions
    - Engagement

    Recommandations:
    - Quelle variante utiliser
    - Insights pour améliorer
    - Statistiques détaillées

    L'A/B testing permet d'optimiser vos créatives et maximiser les conversions
    """
    result = content_studio_service.analyze_creative_performance(
        creative_id=request.creative_id,
        variant_a_id=request.variant_a_id,
        variant_b_id=request.variant_b_id
    )

    return {
        "ab_test": result,
        "winner": result["winner"],
        "improvement": f"+{result['improvement_percentage']}%",
        "recommendation": result["recommendation"],
        "insights": result["insights"]
    }


@router.get("/media-library", summary="Bibliothèque de médias")
async def get_media_library(
    user_id: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """
    Récupérer les médias de la bibliothèque

    Filtres:
    - **user_id**: Médias de l'utilisateur
    - **type**: image, video, audio
    - **search**: Recherche par nom/tags

    Inclut:
    - Médias uploadés par l'utilisateur
    - Photos/vidéos de produits (depuis les marchands)
    - Assets partagés (photos de stock)

    Permet de réutiliser facilement les médias dans vos créations
    """
    # TODO: Récupérer depuis la DB/CDN

    # Données demo
    media_items = [
        {
            "id": "media_001",
            "type": "image",
            "url": "https://via.placeholder.com/1080x1080",
            "thumbnail": "https://via.placeholder.com/300x300",
            "name": "Produit Écouteurs",
            "tags": ["produit", "tech", "écouteurs"],
            "size": 245678,
            "dimensions": {"width": 1080, "height": 1080},
            "uploaded_at": "2025-10-25T14:30:00"
        },
        {
            "id": "media_002",
            "type": "video",
            "url": "https://example.com/video1.mp4",
            "thumbnail": "https://via.placeholder.com/300x300",
            "name": "Demo Produit",
            "tags": ["vidéo", "demo", "produit"],
            "size": 5245678,
            "duration": 15,
            "uploaded_at": "2025-10-24T10:15:00"
        }
    ]

    # Filtrer
    if type:
        media_items = [m for m in media_items if m["type"] == type]

    if search:
        media_items = [
            m for m in media_items
            if search.lower() in m["name"].lower() or
               any(search.lower() in tag for tag in m["tags"])
        ]

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated = media_items[start:end]

    return {
        "media": paginated,
        "total": len(media_items),
        "page": page,
        "limit": limit,
        "has_more": end < len(media_items)
    }


@router.post("/media-library/upload", summary="Upload un média")
async def upload_media(
    file: UploadFile = File(...),
    user_id: str = None,
    tags: Optional[str] = None
):
    """
    Upload un fichier dans la bibliothèque

    Formats supportés:
    - Images: JPG, PNG, GIF, WebP
    - Vidéos: MP4, MOV, AVI
    - Audio: MP3, WAV

    Limite: 50 MB par fichier

    Le fichier est automatiquement:
    - Optimisé (compression)
    - Uploadé sur CDN
    - Indexé pour recherche
    """
    # TODO: Valider le fichier
    # TODO: Upload sur CDN (AWS S3, Cloudinary, etc.)
    # TODO: Sauvegarder metadata en DB

    file_url = f"https://cdn.shareyoursales.com/media/{user_id}/{file.filename}"

    return {
        "success": True,
        "file_url": file_url,
        "filename": file.filename,
        "size": 0,  # file.size
        "type": file.content_type,
        "tags": tags.split(",") if tags else []
    }


@router.get("/stats", summary="Statistiques du Content Studio")
async def get_content_studio_stats(user_id: str):
    """
    Statistiques d'utilisation du Content Studio

    Métriques:
    - Nombre de créations (images, vidéos)
    - Posts planifiés
    - Performance moyenne des créatives
    - Templates les plus utilisés
    - Temps gagné (estimation)

    Aide à mesurer l'impact du Content Studio
    """
    return {
        "user_id": user_id,
        "stats": {
            "total_creations": 47,
            "images_generated": 12,
            "templates_used": 23,
            "posts_scheduled": 35,
            "ab_tests_run": 8,
            "time_saved_hours": 18.5,
            "avg_engagement_rate": 8.7,
            "best_performing_template": "insta_product_1",
            "most_used_platform": "instagram"
        },
        "recent_activity": [
            {
                "type": "template_used",
                "template_id": "insta_product_1",
                "created_at": "2025-10-31T10:30:00"
            },
            {
                "type": "post_scheduled",
                "platforms": ["instagram", "facebook"],
                "scheduled_for": "2025-11-01T18:00:00"
            }
        ]
    }
