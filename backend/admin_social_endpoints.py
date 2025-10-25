"""
Admin Social Media Dashboard Endpoints
Gestion des publications sociales admin (publicité plateforme)

Endpoints:
- POST /api/admin/social/posts - Créer un post
- POST /api/admin/social/posts/{id}/publish - Publier sur réseaux sociaux
- GET /api/admin/social/posts - Liste des posts
- GET /api/admin/social/posts/{id} - Détail d'un post
- PATCH /api/admin/social/posts/{id} - Modifier un post
- DELETE /api/admin/social/posts/{id} - Supprimer un post
- POST /api/admin/social/posts/{id}/schedule - Programmer une publication
- GET /api/admin/social/templates - Templates de posts
- POST /api/admin/social/templates - Créer un template
- GET /api/admin/social/analytics - Analytics globales
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
import structlog
import re

from auth import get_current_admin
from supabase_client import supabase
from services.social_auto_publish_service import auto_publisher

router = APIRouter(prefix="/api/admin/social", tags=["Admin Social Media"])
logger = structlog.get_logger()


# ============================================
# PYDANTIC MODELS
# ============================================

class CreateAdminPostRequest(BaseModel):
    """Créer un post admin"""
    title: Optional[str] = Field(None, max_length=500)
    caption: str = Field(..., min_length=10, description="Caption du post")
    media_urls: List[str] = Field(default=[], description="URLs des médias (images/vidéos)")
    media_type: str = Field(default="image", pattern="^(image|video|carousel|text)$")
    cta_text: Optional[str] = Field(None, max_length=255, description="Texte du call-to-action")
    cta_url: Optional[HttpUrl] = Field(None, description="URL du call-to-action")
    hashtags: List[str] = Field(default=[], description="Liste de hashtags")
    campaign_type: str = Field(
        default="general",
        pattern="^(general|app_launch|new_feature|merchant_recruitment|influencer_recruitment|seasonal_promo|user_testimonial|milestone_celebration|contest)$"
    )
    template_id: Optional[str] = Field(None, description="ID du template utilisé")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Lancement ShareYourSales",
                "caption": "🚀 La plateforme qui connecte influenceurs et marchands au Maroc est enfin là!",
                "media_urls": ["https://example.com/image.jpg"],
                "media_type": "image",
                "cta_text": "Télécharger maintenant!",
                "cta_url": "https://shareyoursales.ma",
                "hashtags": ["#ShareYourSales", "#MarocDigital", "#Influenceurs"],
                "campaign_type": "app_launch"
            }
        }


class PublishPostRequest(BaseModel):
    """Publier un post sur les réseaux sociaux"""
    platforms: List[str] = Field(..., description="Plateformes (instagram, facebook, tiktok, twitter, linkedin)")
    publish_now: bool = Field(default=True, description="Publier immédiatement ou programmer")
    scheduled_for: Optional[datetime] = Field(None, description="Date/heure de publication programmée")

    class Config:
        json_schema_extra = {
            "example": {
                "platforms": ["instagram", "facebook", "linkedin"],
                "publish_now": True
            }
        }


class UpdateAdminPostRequest(BaseModel):
    """Mettre à jour un post"""
    title: Optional[str] = None
    caption: Optional[str] = None
    media_urls: Optional[List[str]] = None
    cta_text: Optional[str] = None
    cta_url: Optional[HttpUrl] = None
    hashtags: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(draft|scheduled|published|failed|archived)$")


class CreateTemplateRequest(BaseModel):
    """Créer un template de post"""
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    category: str = Field(default="general")
    caption_template: str = Field(..., min_length=10, description="Template avec variables {{var}}")
    suggested_hashtags: List[str] = Field(default=[])
    suggested_cta_text: Optional[str] = None
    suggested_cta_url: Optional[str] = None
    example_media_url: Optional[str] = None
    media_type: str = Field(default="image")


# ============================================
# ADMIN SOCIAL POSTS ENDPOINTS
# ============================================

@router.post("/posts", response_model=dict, status_code=201)
async def create_admin_post(
    post_data: CreateAdminPostRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Créer un post pour promouvoir la plateforme

    **Types de campagne:**
    - general: Post général
    - app_launch: Lancement app
    - new_feature: Nouvelle fonctionnalité
    - merchant_recruitment: Recrutement marchands
    - influencer_recruitment: Recrutement influenceurs
    - seasonal_promo: Promotion saisonnière
    - user_testimonial: Témoignage utilisateur
    - milestone_celebration: Célébration d'un jalon
    - contest: Concours

    **Returns:**
    - Post créé en brouillon
    - Peut être publié ensuite via /publish
    """
    admin_id = current_admin.get("id")

    try:
        # Si un template est utilisé, incrémenter son usage
        if post_data.template_id:
            supabase.rpc('increment_template_usage', {'template_id': post_data.template_id}).execute()

        # Préparer les données du post
        post_dict = {
            'created_by': admin_id,
            'title': post_data.title,
            'caption': post_data.caption,
            'media_urls': post_data.media_urls,
            'media_type': post_data.media_type,
            'cta_text': post_data.cta_text,
            'cta_url': str(post_data.cta_url) if post_data.cta_url else None,
            'hashtags': post_data.hashtags,
            'campaign_type': post_data.campaign_type,
            'platforms': {},
            'status': 'draft',
            'created_at': datetime.utcnow().isoformat()
        }

        # Créer le post
        result = supabase.table('admin_social_posts').insert(post_dict).execute()

        if not result.data:
            raise Exception("Failed to create admin post")

        post = result.data[0]

        logger.info("admin_post_created",
                   admin_id=admin_id,
                   post_id=post['id'],
                   campaign_type=post_data.campaign_type)

        return {
            "success": True,
            "message": "Post créé avec succès",
            "post": post
        }

    except Exception as e:
        logger.error("create_admin_post_failed", admin_id=admin_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du post"
        )


@router.post("/posts/{post_id}/publish", response_model=dict)
async def publish_admin_post(
    post_id: str,
    publish_data: PublishPostRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Publier un post sur les réseaux sociaux

    **Process:**
    1. Récupérer le post
    2. Vérifier qu'il est en brouillon
    3. Publier sur les plateformes sélectionnées
    4. Mettre à jour le statut

    **Plateformes supportées:**
    - instagram: Page Instagram officielle
    - facebook: Page Facebook officielle
    - tiktok: Compte TikTok officiel
    - twitter: Compte Twitter officiel (TODO)
    - linkedin: Page LinkedIn entreprise (TODO)

    **Returns:**
    - Résultat de publication par plateforme
    """
    admin_id = current_admin.get("id")

    try:
        # Récupérer le post
        post_result = supabase.table('admin_social_posts').select('*').eq('id', post_id).execute()

        if not post_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post non trouvé"
            )

        post = post_result.data[0]

        # Vérifier le statut
        if post['status'] == 'published':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce post a déjà été publié"
            )

        # Si publication programmée
        if not publish_data.publish_now and publish_data.scheduled_for:
            # Mettre à jour avec date de programmation
            supabase.table('admin_social_posts').update({
                'status': 'scheduled',
                'scheduled_for': publish_data.scheduled_for.isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', post_id).execute()

            logger.info("admin_post_scheduled", post_id=post_id, scheduled_for=publish_data.scheduled_for)

            return {
                "success": True,
                "message": f"Post programmé pour le {publish_data.scheduled_for}",
                "scheduled_for": publish_data.scheduled_for.isoformat()
            }

        # Publication immédiate
        # Préparer la caption complète avec hashtags
        full_caption = post['caption']
        if post.get('hashtags'):
            full_caption += "\n\n" + " ".join([f"#{tag.lstrip('#')}" for tag in post['hashtags']])

        if post.get('cta_text') and post.get('cta_url'):
            full_caption += f"\n\n👉 {post['cta_text']}\n{post['cta_url']}"

        # Préparer les médias
        media_urls = {
            "default": post['media_urls'][0] if post.get('media_urls') else "https://via.placeholder.com/1080x1080"
        }

        # Ajouter média spécifique par plateforme si disponible
        for i, platform in enumerate(publish_data.platforms):
            if i < len(post.get('media_urls', [])):
                media_urls[platform] = post['media_urls'][i]
            else:
                media_urls[platform] = media_urls["default"]

        # Publier sur toutes les plateformes
        # Note: Pour l'admin, on utilise les comptes officiels de la plateforme
        # Il faut avoir configuré les tokens d'accès dans social_media_accounts pour un user "platform_admin"

        # Récupérer l'ID du compte admin plateforme (celui qui a les tokens des comptes officiels)
        platform_admin_result = supabase.table('users').select('id').eq('role', 'admin').eq('email', 'admin@shareyoursales.ma').execute()

        if not platform_admin_result.data:
            # Fallback: utiliser l'admin actuel (il doit avoir connecté les comptes sociaux)
            platform_admin_id = admin_id
        else:
            platform_admin_id = platform_admin_result.data[0]['id']

        # Publier
        publication_results = {
            "published": [],
            "failed": []
        }

        for platform in publish_data.platforms:
            try:
                # Générer caption_data format
                caption_data = {
                    "caption": post['caption'],
                    "full_text": full_caption,
                    "hashtags": post.get('hashtags', []),
                    "call_to_action": post.get('cta_text', '')
                }

                # Publier selon la plateforme
                if platform == "instagram":
                    result = await auto_publisher.publish_to_instagram(
                        user_id=platform_admin_id,
                        product_id=None,  # Post admin, pas de produit
                        affiliate_link=post.get('cta_url', ''),
                        image_url=media_urls.get('instagram', media_urls['default']),
                        caption_data=caption_data,
                        post_type='feed'
                    )

                elif platform == "facebook":
                    result = await auto_publisher.publish_to_facebook(
                        user_id=platform_admin_id,
                        product_id=None,
                        affiliate_link=post.get('cta_url', ''),
                        image_url=media_urls.get('facebook', media_urls['default']),
                        caption_data=caption_data,
                        target_type='page'
                    )

                elif platform == "tiktok":
                    result = await auto_publisher.publish_to_tiktok(
                        user_id=platform_admin_id,
                        product_id=None,
                        affiliate_link=post.get('cta_url', ''),
                        video_url=media_urls.get('tiktok', media_urls['default']),
                        caption_data=caption_data
                    )

                else:
                    # Plateforme non supportée pour l'instant
                    result = {
                        "success": False,
                        "error": f"Plateforme {platform} non encore supportée",
                        "platform": platform
                    }

                if result.get("success"):
                    publication_results["published"].append(result)
                else:
                    publication_results["failed"].append(result)

            except Exception as e:
                logger.error("platform_publish_failed", platform=platform, error=str(e))
                publication_results["failed"].append({
                    "platform": platform,
                    "error": str(e)
                })

        # Mettre à jour le post avec les résultats
        platforms_status = {}
        for pub in publication_results["published"]:
            platforms_status[pub['platform']] = {
                "post_id": pub.get('post_id'),
                "url": pub.get('url'),
                "status": "published",
                "published_at": datetime.utcnow().isoformat()
            }

        for fail in publication_results["failed"]:
            platforms_status[fail['platform']] = {
                "status": "failed",
                "error": fail.get('error')
            }

        # Update post
        supabase.table('admin_social_posts').update({
            'status': 'published' if len(publication_results["published"]) > 0 else 'failed',
            'platforms': platforms_status,
            'published_at': datetime.utcnow().isoformat() if len(publication_results["published"]) > 0 else None,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', post_id).execute()

        logger.info("admin_post_published",
                   post_id=post_id,
                   admin_id=admin_id,
                   published=len(publication_results["published"]),
                   failed=len(publication_results["failed"]))

        return {
            "success": len(publication_results["published"]) > 0,
            "message": f"Post publié sur {len(publication_results['published'])} plateformes",
            "published": publication_results["published"],
            "failed": publication_results["failed"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("publish_admin_post_failed", post_id=post_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la publication"
        )


@router.get("/posts", response_model=dict)
async def get_admin_posts(
    page: int = 1,
    limit: int = 20,
    status_filter: Optional[str] = None,
    campaign_type: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Liste de tous les posts admin

    **Filters:**
    - status: draft, scheduled, published, failed, archived
    - campaign_type: general, app_launch, new_feature, etc.

    **Returns:**
    - Liste des posts avec infos créateur
    """
    try:
        offset = (page - 1) * limit

        query = supabase.table('v_admin_social_posts_summary').select('*', count='exact')

        if status_filter:
            query = query.eq('status', status_filter)

        if campaign_type:
            query = query.eq('campaign_type', campaign_type)

        query = query.order('created_at', desc=True).range(offset, offset + limit - 1)

        result = query.execute()

        return {
            "success": True,
            "posts": result.data or [],
            "total": result.count or 0,
            "page": page,
            "limit": limit,
            "total_pages": ((result.count or 0) + limit - 1) // limit
        }

    except Exception as e:
        logger.error("get_admin_posts_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des posts"
        )


@router.get("/posts/{post_id}", response_model=dict)
async def get_admin_post_detail(
    post_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Détail d'un post admin

    **Returns:**
    - Post complet
    - Statut de publication par plateforme
    - Analytics si disponibles
    """
    try:
        result = supabase.table('admin_social_posts').select('*').eq('id', post_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post non trouvé"
            )

        post = result.data[0]

        # Enrichir avec info créateur
        if post.get('created_by'):
            creator_result = supabase.table('users').select('id, email, first_name, last_name').eq('id', post['created_by']).execute()
            if creator_result.data:
                post['creator'] = creator_result.data[0]

        return {
            "success": True,
            "post": post
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_admin_post_detail_failed", post_id=post_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du post"
        )


@router.patch("/posts/{post_id}", response_model=dict)
async def update_admin_post(
    post_id: str,
    update_data: UpdateAdminPostRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Modifier un post admin

    **Limitations:**
    - Cannot modify published posts (use archive first)
    """
    try:
        # Vérifier que le post existe
        post_result = supabase.table('admin_social_posts').select('*').eq('id', post_id).execute()

        if not post_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post non trouvé"
            )

        post = post_result.data[0]

        # Ne pas modifier un post publié (sauf pour changer le statut en archived)
        if post['status'] == 'published' and update_data.status != 'archived':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de modifier un post publié. Archivez-le d'abord."
            )

        # Préparer update
        update_dict = {
            'updated_at': datetime.utcnow().isoformat()
        }

        if update_data.title is not None:
            update_dict['title'] = update_data.title

        if update_data.caption is not None:
            update_dict['caption'] = update_data.caption

        if update_data.media_urls is not None:
            update_dict['media_urls'] = update_data.media_urls

        if update_data.cta_text is not None:
            update_dict['cta_text'] = update_data.cta_text

        if update_data.cta_url is not None:
            update_dict['cta_url'] = str(update_data.cta_url)

        if update_data.hashtags is not None:
            update_dict['hashtags'] = update_data.hashtags

        if update_data.status is not None:
            update_dict['status'] = update_data.status

        # Update
        result = supabase.table('admin_social_posts').update(update_dict).eq('id', post_id).execute()

        logger.info("admin_post_updated", post_id=post_id, admin_id=current_admin.get('id'))

        return {
            "success": True,
            "message": "Post mis à jour avec succès",
            "post": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_admin_post_failed", post_id=post_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du post"
        )


@router.delete("/posts/{post_id}", response_model=dict)
async def delete_admin_post(
    post_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Supprimer un post admin

    **Note:** On archive plutôt que de supprimer réellement
    """
    try:
        # Vérifier existence
        post_result = supabase.table('admin_social_posts').select('*').eq('id', post_id).execute()

        if not post_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post non trouvé"
            )

        # Archiver au lieu de supprimer
        supabase.table('admin_social_posts').update({
            'status': 'archived',
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', post_id).execute()

        logger.info("admin_post_archived", post_id=post_id, admin_id=current_admin.get('id'))

        return {
            "success": True,
            "message": "Post archivé avec succès"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_admin_post_failed", post_id=post_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression du post"
        )


# ============================================
# TEMPLATES ENDPOINTS
# ============================================

@router.get("/templates", response_model=dict)
async def get_post_templates(
    category: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Récupérer les templates de posts

    **Returns:**
    - Templates avec variables {{variable}}
    - Hashtags suggérés
    - CTA suggéré
    """
    try:
        query = supabase.table('admin_social_post_templates').select('*').eq('is_active', True)

        if category:
            query = query.eq('category', category)

        query = query.order('usage_count', desc=True)

        result = query.execute()

        return {
            "success": True,
            "templates": result.data or []
        }

    except Exception as e:
        logger.error("get_templates_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des templates"
        )


@router.post("/templates", response_model=dict, status_code=201)
async def create_post_template(
    template_data: CreateTemplateRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Créer un nouveau template de post

    **Variables disponibles:**
    - {{app_name}}, {{app_url}}
    - {{user_name}}, {{user_role}}
    - {{commission}}, {{influencer_count}}
    - {{feature_name}}, {{feature_description}}
    - {{testimonial_text}}
    - {{metric_1}}, {{metric_2}}, {{metric_3}}
    - {{season}}, {{promo_description}}, {{end_date}}
    - {{prize_description}}, {{draw_date}}
    - {{milestone_number}}, {{milestone_type}}
    - etc.
    """
    try:
        template_dict = {
            'name': template_data.name,
            'description': template_data.description,
            'category': template_data.category,
            'caption_template': template_data.caption_template,
            'suggested_hashtags': template_data.suggested_hashtags,
            'suggested_cta_text': template_data.suggested_cta_text,
            'suggested_cta_url': template_data.suggested_cta_url,
            'example_media_url': template_data.example_media_url,
            'media_type': template_data.media_type,
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }

        result = supabase.table('admin_social_post_templates').insert(template_dict).execute()

        logger.info("template_created", admin_id=current_admin.get('id'), template_name=template_data.name)

        return {
            "success": True,
            "message": "Template créé avec succès",
            "template": result.data[0] if result.data else None
        }

    except Exception as e:
        logger.error("create_template_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du template"
        )


# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@router.get("/analytics", response_model=dict)
async def get_admin_social_analytics(current_admin: dict = Depends(get_current_admin)):
    """
    Analytics des publications admin

    **Returns:**
    - Total posts publiés
    - Engagement global (vues, likes, commentaires, partages, clics)
    - Performance par plateforme
    - Performance par type de campagne
    - Taux d'engagement
    """
    try:
        # Stats globales depuis la vue
        global_stats_result = supabase.table('v_admin_social_analytics').select('*').execute()

        if global_stats_result.data:
            global_stats = global_stats_result.data[0]
        else:
            global_stats = {}

        # Stats par plateforme (parser le JSONB platforms)
        # TODO: Améliorer avec requête PostgREST avancée

        # Stats par type de campagne
        campaign_stats = {}
        campaign_types = ['general', 'app_launch', 'new_feature', 'merchant_recruitment', 'influencer_recruitment', 'seasonal_promo', 'user_testimonial', 'milestone_celebration', 'contest']

        for ctype in campaign_types:
            ctype_result = supabase.table('admin_social_posts').select('*', count='exact').eq('campaign_type', ctype).eq('status', 'published').execute()
            campaign_stats[ctype] = ctype_result.count or 0

        return {
            "success": True,
            "global_stats": global_stats,
            "by_campaign_type": campaign_stats
        }

    except Exception as e:
        logger.error("get_analytics_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des analytics"
        )
