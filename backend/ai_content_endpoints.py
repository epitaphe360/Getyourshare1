"""
AI Content Generator Endpoints
Endpoints pour la génération de contenu IA multi-plateforme
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from ai_content_generator import (
    AIContentGeneratorService,
    TrendingTopicsAnalyzer,
    ContentRequest,
    GeneratedContent,
    TrendingTopic,
    SocialPlatform,
    ContentType
)
from auth import get_current_user
from db_helpers import log_user_activity

router = APIRouter(prefix="/api/ai-content", tags=["AI Content Generator"])

# Initialiser le service
content_generator = AIContentGeneratorService()
trends_analyzer = TrendingTopicsAnalyzer()

# ============================================
# ENDPOINTS
# ============================================

@router.post("/generate", response_model=GeneratedContent)
async def generate_content(
    request: ContentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Génère du contenu optimisé pour une plateforme sociale spécifique

    Exemples de requêtes:

    TikTok Script:
    ```json
    {
        "platform": "tiktok",
        "content_type": "video_script",
        "product_name": "Huile d'Argan Bio",
        "product_description": "Huile 100% naturelle pour cheveux et peau",
        "target_audience": "Femmes 18-35 ans",
        "tone": "engaging",
        "language": "fr",
        "duration_seconds": 30
    }
    ```

    Instagram Carousel:
    ```json
    {
        "platform": "instagram",
        "content_type": "carousel",
        "product_name": "Formation Marketing Digital",
        "product_description": "Cours complet pour devenir expert en marketing",
        "target_audience": "Entrepreneurs et étudiants",
        "tone": "professional",
        "language": "fr"
    }
    ```
    """

    try:
        # Vérifier les quotas de l'utilisateur (selon son plan)
        user_plan = current_user.get("subscription_plan", "free")

        # Limites par plan
        daily_limits = {
            "free": 3,
            "starter": 10,
            "pro": 50,
            "enterprise": 999
        }

        # Vérifier si l'utilisateur a atteint sa limite (à implémenter avec Redis)
        # Pour l'instant, on laisse passer

        # Générer le contenu
        generated_content = await content_generator.generate_content(request)

        # Logger l'activité
        await log_user_activity(
            user_id=current_user["id"],
            action="ai_content_generated",
            details={
                "platform": request.platform,
                "content_type": request.content_type,
                "product": request.product_name
            }
        )

        return generated_content

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de contenu: {str(e)}"
        )


@router.get("/trending-topics", response_model=List[TrendingTopic])
async def get_trending_topics(
    region: str = "MA",
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les sujets tendances pour une région

    Paramètres:
    - region: Code pays (MA, FR, US, etc.)
    - category: Catégorie optionnelle (fashion, food, tech, beauty)
    """

    try:
        trends = await trends_analyzer.get_morocco_trends()

        # Filtrer par catégorie si spécifié
        if category:
            trends = [t for t in trends if t.category == category]

        return trends

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des tendances: {str(e)}"
        )


@router.post("/analyze-trend-fit")
async def analyze_trend_fit(
    content: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyse si un contenu correspond aux tendances actuelles

    Retourne un score de 0 à 100
    """

    try:
        trends = await trends_analyzer.get_morocco_trends()
        score = await trends_analyzer.analyze_content_trend_fit(content, trends)

        return {
            "trend_fit_score": score,
            "matching_trends": [
                t.keyword for t in trends
                if t.keyword.lower() in content.lower()
            ],
            "recommendation": "Excellent match !" if score > 70 else "Ajoutez plus de mots-clés tendances"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


@router.get("/templates")
async def get_content_templates(
    platform: SocialPlatform,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère des templates prêts à l'emploi pour une plateforme
    """

    templates = {
        "tiktok": [
            {
                "name": "Unboxing Viral",
                "structure": "Hook (produit mystère) → Déballage → Réaction → Lien promo",
                "estimated_engagement": 85
            },
            {
                "name": "Avant/Après",
                "structure": "Problème → Solution (produit) → Résultat → Témoignage",
                "estimated_engagement": 78
            },
            {
                "name": "POV Trending",
                "structure": "POV: Tu découvres [produit] → Détails → Bénéfices → CTA",
                "estimated_engagement": 82
            }
        ],
        "instagram": [
            {
                "name": "Carousel Éducatif",
                "structure": "10 slides: Titre → 8 conseils → Témoignage → CTA",
                "estimated_engagement": 75
            },
            {
                "name": "Reel Transformation",
                "structure": "Avant → Processus → Après → Lien produit",
                "estimated_engagement": 80
            }
        ],
        "youtube_shorts": [
            {
                "name": "Tutorial Express",
                "structure": "Problème → Solution en 3 étapes → Résultat → Abonne-toi",
                "estimated_engagement": 72
            }
        ]
    }

    return {
        "platform": platform,
        "templates": templates.get(platform, []),
        "count": len(templates.get(platform, []))
    }


@router.post("/batch-generate")
async def batch_generate_content(
    product_name: str,
    product_description: str,
    target_audience: str,
    platforms: List[SocialPlatform],
    current_user: dict = Depends(get_current_user)
):
    """
    Génère du contenu pour plusieurs plateformes en une seule requête

    Gain de temps énorme pour les influenceurs !
    """

    try:
        results = []

        for platform in platforms:
            # Déterminer le type de contenu par défaut par plateforme
            content_type_map = {
                SocialPlatform.TIKTOK: ContentType.VIDEO_SCRIPT,
                SocialPlatform.INSTAGRAM: ContentType.REEL_SCRIPT,
                SocialPlatform.YOUTUBE_SHORTS: ContentType.VIDEO_SCRIPT,
                SocialPlatform.FACEBOOK: ContentType.POST_CAPTION
            }

            request = ContentRequest(
                platform=platform,
                content_type=content_type_map.get(platform, ContentType.POST_CAPTION),
                product_name=product_name,
                product_description=product_description,
                target_audience=target_audience,
                tone="engaging",
                language="fr"
            )

            content = await content_generator.generate_content(request)
            results.append(content)

        return {
            "batch_id": f"batch_{datetime.now().timestamp()}",
            "generated_count": len(results),
            "contents": results,
            "total_estimated_engagement": sum(c.estimated_engagement for c in results) / len(results)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération en batch: {str(e)}"
        )


@router.get("/usage-stats")
async def get_usage_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Statistiques d'utilisation du générateur IA pour l'utilisateur
    """

    user_plan = current_user.get("subscription_plan", "free")

    # À implémenter avec Redis pour tracking en temps réel
    daily_limits = {
        "free": 3,
        "starter": 10,
        "pro": 50,
        "enterprise": 999
    }

    return {
        "user_id": current_user["id"],
        "plan": user_plan,
        "daily_limit": daily_limits.get(user_plan, 3),
        "used_today": 0,  # À récupérer de Redis
        "remaining_today": daily_limits.get(user_plan, 3),
        "total_generated": 0,  # À récupérer de la DB
        "favorite_platform": "tiktok",  # À calculer
        "average_engagement": 78.5  # À calculer
    }
