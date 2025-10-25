"""
API Endpoints pour l'intégration des réseaux sociaux

Permet aux influenceurs de:
- Connecter leurs comptes sociaux (Instagram, TikTok, Facebook, etc.)
- Voir leurs statistiques automatiquement récupérées
- Synchroniser manuellement leurs données
- Déconnecter leurs comptes

Workflow OAuth:
1. Frontend redirige vers l'URL d'autorisation de la plateforme
2. Plateforme redirige vers /callback avec code d'autorisation
3. Backend échange le code contre un access_token
4. Backend sauvegarde la connexion et récupère les stats initiales
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
import structlog
from enum import Enum

from services.social_media_service import (
    SocialMediaService,
    SocialPlatform,
    SocialStats,
    ConnectionStatus
)
from auth import get_current_user  # Fonction d'authentification JWT

router = APIRouter(prefix="/api/social-media", tags=["Social Media"])
logger = structlog.get_logger()

# ============================================
# MODÈLES PYDANTIC
# ============================================

class PlatformEnum(str, Enum):
    """Plateformes supportées"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class ConnectInstagramRequest(BaseModel):
    """Requête pour connecter Instagram"""
    instagram_user_id: str = Field(..., description="ID utilisateur Instagram")
    access_token: str = Field(..., description="Short-lived access token from OAuth")


class ConnectTikTokRequest(BaseModel):
    """Requête pour connecter TikTok"""
    authorization_code: str = Field(..., description="Authorization code from OAuth callback")
    redirect_uri: str = Field(..., description="Redirect URI used in OAuth flow")


class ConnectFacebookRequest(BaseModel):
    """Requête pour connecter Facebook"""
    facebook_user_id: str = Field(..., description="ID utilisateur Facebook")
    access_token: str = Field(..., description="Facebook access token")
    page_id: Optional[str] = Field(None, description="ID de la page Facebook (optionnel)")


class SyncStatsRequest(BaseModel):
    """Requête pour synchroniser manuellement"""
    platforms: Optional[List[PlatformEnum]] = Field(None, description="Plateformes à synchroniser (toutes si vide)")


class ConnectionResponse(BaseModel):
    """Réponse avec info de connexion"""
    id: str
    platform: str
    platform_username: str
    platform_display_name: Optional[str]
    profile_picture_url: Optional[str]
    connection_status: str
    connected_at: datetime
    last_synced_at: Optional[datetime]
    token_expires_at: Optional[datetime]
    days_until_expiry: Optional[int]


class StatsResponse(BaseModel):
    """Réponse avec statistiques"""
    platform: str
    followers_count: int
    following_count: Optional[int]
    engagement_rate: float
    total_posts: int
    average_likes_per_post: float
    average_comments_per_post: float
    followers_growth: Optional[int]
    synced_at: datetime


class SyncLogResponse(BaseModel):
    """Réponse avec log de synchronisation"""
    id: str
    platform: str
    sync_type: str
    sync_status: str
    stats_fetched: bool
    posts_fetched: int
    error_message: Optional[str]
    duration_ms: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]


class DashboardStatsResponse(BaseModel):
    """Statistiques agrégées pour le dashboard"""
    total_followers: int
    total_platforms: int
    avg_engagement_rate: float
    total_posts: int
    connections: List[ConnectionResponse]
    latest_stats: List[StatsResponse]
    last_sync: Optional[datetime]


# ============================================
# ENDPOINTS - CONNEXION DES COMPTES
# ============================================

@router.post("/connect/instagram", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def connect_instagram(
    request_data: ConnectInstagramRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Connecter un compte Instagram

    Workflow:
    1. Frontend obtient short-lived token via Instagram OAuth
    2. Frontend envoie le token à cet endpoint
    3. Backend échange contre long-lived token (60 jours)
    4. Backend sauvegarde la connexion et récupère les stats

    Permissions requises: instagram_basic, instagram_manage_insights
    """
    service = SocialMediaService()

    try:
        result = await service.connect_instagram(
            user_id=current_user["id"],
            instagram_user_id=request_data.instagram_user_id,
            access_token=request_data.access_token
        )

        logger.info("instagram_connected", user_id=current_user["id"], username=result.get("username"))

        return ConnectionResponse(
            id=result["connection_id"],
            platform="instagram",
            platform_username=result["username"],
            platform_display_name=result.get("display_name"),
            profile_picture_url=result.get("profile_picture"),
            connection_status="active",
            connected_at=result["connected_at"],
            last_synced_at=result.get("last_synced_at"),
            token_expires_at=result.get("token_expires_at"),
            days_until_expiry=None
        )

    except ValueError as e:
        logger.warning("instagram_connection_failed", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("instagram_connection_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de la connexion Instagram")


@router.post("/connect/tiktok", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def connect_tiktok(
    request_data: ConnectTikTokRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Connecter un compte TikTok

    Workflow OAuth TikTok:
    1. Frontend redirige vers: https://www.tiktok.com/auth/authorize/
    2. TikTok redirige vers callback avec authorization_code
    3. Frontend envoie le code à cet endpoint
    4. Backend échange contre access_token
    """
    service = SocialMediaService()

    try:
        result = await service.connect_tiktok(
            user_id=current_user["id"],
            authorization_code=request_data.authorization_code
        )

        logger.info("tiktok_connected", user_id=current_user["id"], username=result.get("username"))

        return ConnectionResponse(
            id=result["connection_id"],
            platform="tiktok",
            platform_username=result["username"],
            platform_display_name=result.get("display_name"),
            profile_picture_url=result.get("profile_picture"),
            connection_status="active",
            connected_at=result["connected_at"],
            last_synced_at=result.get("last_synced_at"),
            token_expires_at=result.get("token_expires_at"),
            days_until_expiry=None
        )

    except ValueError as e:
        logger.warning("tiktok_connection_failed", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("tiktok_connection_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de la connexion TikTok")


@router.post("/connect/facebook", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def connect_facebook(
    request_data: ConnectFacebookRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Connecter un compte Facebook ou une page Facebook

    Permissions requises:
    - pages_read_engagement
    - pages_show_list
    - instagram_basic (si connecté à Instagram)
    """
    service = SocialMediaService()

    try:
        # Pas encore implémenté dans social_media_service.py
        # TODO: Implémenter service.connect_facebook()
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Connexion Facebook en cours de développement"
        )

    except Exception as e:
        logger.error("facebook_connection_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS - GESTION DES CONNEXIONS
# ============================================

@router.get("/connections", response_model=List[ConnectionResponse])
async def get_connections(
    platform: Optional[PlatformEnum] = Query(None, description="Filtrer par plateforme"),
    status_filter: Optional[str] = Query(None, description="Filtrer par statut (active, expired, error)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer toutes les connexions de l'utilisateur
    """
    service = SocialMediaService()

    try:
        connections = await service.get_user_connections(
            user_id=current_user["id"],
            platform=platform.value if platform else None,
            status_filter=status_filter
        )

        response = []
        for conn in connections:
            # Calculer jours avant expiration
            days_until_expiry = None
            if conn.get("token_expires_at"):
                expires = conn["token_expires_at"]
                if isinstance(expires, str):
                    expires = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                delta = expires - datetime.now()
                days_until_expiry = max(0, delta.days)

            response.append(ConnectionResponse(
                id=conn["id"],
                platform=conn["platform"],
                platform_username=conn["platform_username"],
                platform_display_name=conn.get("platform_display_name"),
                profile_picture_url=conn.get("profile_picture_url"),
                connection_status=conn["connection_status"],
                connected_at=conn["connected_at"],
                last_synced_at=conn.get("last_synced_at"),
                token_expires_at=conn.get("token_expires_at"),
                days_until_expiry=days_until_expiry
            ))

        return response

    except Exception as e:
        logger.error("get_connections_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_platform(
    connection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Déconnecter un compte social

    Supprime la connexion et toutes les données associées (stats, posts)
    """
    service = SocialMediaService()

    try:
        await service.disconnect_platform(
            connection_id=connection_id,
            user_id=current_user["id"]
        )

        logger.info("platform_disconnected", user_id=current_user["id"], connection_id=connection_id)
        return None

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("disconnect_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/connections/{connection_id}/status")
async def check_connection_status(
    connection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifier le statut d'une connexion (active, expired, error)
    """
    service = SocialMediaService()

    try:
        status_info = await service.check_connection_status(
            connection_id=connection_id,
            user_id=current_user["id"]
        )

        return {
            "connection_id": connection_id,
            "status": status_info["status"],
            "is_active": status_info["is_active"],
            "token_expires_at": status_info.get("token_expires_at"),
            "days_until_expiry": status_info.get("days_until_expiry"),
            "last_error": status_info.get("last_error"),
            "last_synced_at": status_info.get("last_synced_at")
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("check_status_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS - SYNCHRONISATION DES STATS
# ============================================

@router.post("/sync", response_model=List[SyncLogResponse])
async def sync_stats_manual(
    request_data: Optional[SyncStatsRequest] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Synchroniser manuellement les statistiques

    Par défaut, synchronise toutes les plateformes connectées.
    Peut être limité à certaines plateformes via le body.
    """
    service = SocialMediaService()

    try:
        platforms = [p.value for p in request_data.platforms] if request_data and request_data.platforms else None

        results = await service.sync_all_user_stats(
            user_id=current_user["id"],
            platforms=platforms
        )

        logger.info("manual_sync_completed", user_id=current_user["id"], platforms=platforms, results_count=len(results))

        response = []
        for result in results:
            response.append(SyncLogResponse(
                id=result["log_id"],
                platform=result["platform"],
                sync_type="manual",
                sync_status=result["status"],
                stats_fetched=result.get("stats_fetched", False),
                posts_fetched=result.get("posts_fetched", 0),
                error_message=result.get("error"),
                duration_ms=result.get("duration_ms"),
                started_at=result["started_at"],
                completed_at=result.get("completed_at")
            ))

        return response

    except Exception as e:
        logger.error("manual_sync_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats", response_model=List[StatsResponse])
async def get_latest_stats(
    platform: Optional[PlatformEnum] = Query(None, description="Filtrer par plateforme"),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer les dernières statistiques de l'utilisateur

    Retourne les stats les plus récentes pour chaque plateforme connectée
    """
    service = SocialMediaService()

    try:
        stats = await service.get_latest_stats(
            user_id=current_user["id"],
            platform=platform.value if platform else None
        )

        response = []
        for stat in stats:
            response.append(StatsResponse(
                platform=stat["platform"],
                followers_count=stat["followers_count"],
                following_count=stat.get("following_count"),
                engagement_rate=stat["engagement_rate"],
                total_posts=stat["total_posts"],
                average_likes_per_post=stat["average_likes_per_post"],
                average_comments_per_post=stat["average_comments_per_post"],
                followers_growth=stat.get("followers_growth"),
                synced_at=stat["synced_at"]
            ))

        return response

    except Exception as e:
        logger.error("get_stats_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats/history", response_model=List[StatsResponse])
async def get_stats_history(
    platform: PlatformEnum = Query(..., description="Plateforme"),
    days: int = Query(30, ge=1, le=365, description="Nombre de jours d'historique"),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer l'historique des statistiques

    Utile pour afficher des graphiques d'évolution
    """
    service = SocialMediaService()

    try:
        stats = await service.get_stats_history(
            user_id=current_user["id"],
            platform=platform.value,
            days=days
        )

        response = []
        for stat in stats:
            response.append(StatsResponse(
                platform=stat["platform"],
                followers_count=stat["followers_count"],
                following_count=stat.get("following_count"),
                engagement_rate=stat["engagement_rate"],
                total_posts=stat["total_posts"],
                average_likes_per_post=stat["average_likes_per_post"],
                average_comments_per_post=stat["average_comments_per_post"],
                followers_growth=stat.get("followers_growth"),
                synced_at=stat["synced_at"]
            ))

        return response

    except Exception as e:
        logger.error("get_history_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS - PUBLICATIONS
# ============================================

@router.get("/posts/top")
async def get_top_posts(
    platform: Optional[PlatformEnum] = Query(None, description="Filtrer par plateforme"),
    limit: int = Query(10, ge=1, le=50, description="Nombre de posts"),
    sort_by: str = Query("engagement_rate", description="Tri (engagement_rate, likes_count, views_count)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer les posts les plus performants

    Utile pour afficher un portfolio ou analyser les contenus les plus engageants
    """
    service = SocialMediaService()

    try:
        posts = await service.get_top_posts(
            user_id=current_user["id"],
            platform=platform.value if platform else None,
            limit=limit,
            sort_by=sort_by
        )

        return {
            "total": len(posts),
            "posts": posts
        }

    except Exception as e:
        logger.error("get_top_posts_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS - DASHBOARD & ANALYTICS
# ============================================

@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer toutes les statistiques pour le dashboard influenceur

    Retourne:
    - Total de followers (toutes plateformes)
    - Nombre de plateformes connectées
    - Taux d'engagement moyen
    - Total de posts
    - Détails de chaque connexion
    - Dernières stats par plateforme
    """
    service = SocialMediaService()

    try:
        # Récupérer connexions
        connections = await service.get_user_connections(user_id=current_user["id"])

        # Récupérer dernières stats
        latest_stats = await service.get_latest_stats(user_id=current_user["id"])

        # Calculer agrégats
        total_followers = sum(stat["followers_count"] for stat in latest_stats)
        total_platforms = len(connections)
        avg_engagement = sum(stat["engagement_rate"] for stat in latest_stats) / len(latest_stats) if latest_stats else 0
        total_posts = sum(stat["total_posts"] for stat in latest_stats)
        last_sync = max((stat["synced_at"] for stat in latest_stats), default=None)

        # Formater réponse
        connections_response = []
        for conn in connections:
            days_until_expiry = None
            if conn.get("token_expires_at"):
                expires = conn["token_expires_at"]
                if isinstance(expires, str):
                    expires = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                delta = expires - datetime.now()
                days_until_expiry = max(0, delta.days)

            connections_response.append(ConnectionResponse(
                id=conn["id"],
                platform=conn["platform"],
                platform_username=conn["platform_username"],
                platform_display_name=conn.get("platform_display_name"),
                profile_picture_url=conn.get("profile_picture_url"),
                connection_status=conn["connection_status"],
                connected_at=conn["connected_at"],
                last_synced_at=conn.get("last_synced_at"),
                token_expires_at=conn.get("token_expires_at"),
                days_until_expiry=days_until_expiry
            ))

        stats_response = []
        for stat in latest_stats:
            stats_response.append(StatsResponse(
                platform=stat["platform"],
                followers_count=stat["followers_count"],
                following_count=stat.get("following_count"),
                engagement_rate=stat["engagement_rate"],
                total_posts=stat["total_posts"],
                average_likes_per_post=stat["average_likes_per_post"],
                average_comments_per_post=stat["average_comments_per_post"],
                followers_growth=stat.get("followers_growth"),
                synced_at=stat["synced_at"]
            ))

        return DashboardStatsResponse(
            total_followers=total_followers,
            total_platforms=total_platforms,
            avg_engagement_rate=round(avg_engagement, 2),
            total_posts=total_posts,
            connections=connections_response,
            latest_stats=stats_response,
            last_sync=last_sync
        )

    except Exception as e:
        logger.error("dashboard_error", user_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS - ADMIN & MAINTENANCE
# ============================================

@router.post("/admin/refresh-tokens", dependencies=[Depends(get_current_user)])
async def admin_refresh_expiring_tokens(
    days_before: int = Query(7, ge=1, le=30, description="Jours avant expiration"),
    current_user: dict = Depends(get_current_user)
):
    """
    (ADMIN) Rafraîchir tous les tokens expirant bientôt

    Parcourt toutes les connexions expirant dans X jours et tente de rafraîchir
    """
    # Vérifier que l'utilisateur est admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès réservé aux administrateurs")

    service = SocialMediaService()

    try:
        results = await service.refresh_expiring_tokens(days_before=days_before)

        logger.info("admin_token_refresh", admin_id=current_user["id"], results_count=len(results))

        return {
            "refreshed_count": len([r for r in results if r["success"]]),
            "failed_count": len([r for r in results if not r["success"]]),
            "details": results
        }

    except Exception as e:
        logger.error("admin_refresh_error", admin_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/admin/sync-logs", dependencies=[Depends(get_current_user)])
async def admin_get_sync_logs(
    user_id: Optional[str] = Query(None, description="Filtrer par utilisateur"),
    platform: Optional[PlatformEnum] = Query(None, description="Filtrer par plateforme"),
    status_filter: Optional[str] = Query(None, description="Filtrer par statut"),
    limit: int = Query(50, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """
    (ADMIN) Récupérer les logs de synchronisation

    Utile pour le debugging et le monitoring
    """
    # Vérifier que l'utilisateur est admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès réservé aux administrateurs")

    service = SocialMediaService()

    try:
        logs = await service.get_sync_logs(
            user_id=user_id,
            platform=platform.value if platform else None,
            status_filter=status_filter,
            limit=limit
        )

        return {
            "total": len(logs),
            "logs": logs
        }

    except Exception as e:
        logger.error("admin_logs_error", admin_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS - WEBHOOKS (FUTURS)
# ============================================

@router.post("/webhooks/instagram")
async def instagram_webhook(request: Request):
    """
    Webhook Instagram pour recevoir les notifications en temps réel

    Permet de recevoir des mises à jour automatiques quand:
    - Un nouveau post est publié
    - Les stats changent significativement

    Nécessite la configuration dans Facebook Developer Console
    """
    # TODO: Implémenter la vérification de signature Instagram
    # TODO: Traiter les événements Instagram

    return {"status": "not_implemented"}


@router.get("/webhooks/instagram")
async def instagram_webhook_verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """
    Vérification du webhook Instagram

    Instagram envoie cette requête pour vérifier que le webhook est légitime
    """
    # TODO: Vérifier le verify_token
    VERIFY_TOKEN = "your-verify-token"  # À stocker en variable d'environnement

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("instagram_webhook_verified")
        return int(hub_challenge)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid verify token")


# ============================================
# DOCUMENTATION OPENAPI
# ============================================

# Ajouter des exemples de réponses pour la documentation
router.get("/connections", response_model=List[ConnectionResponse]).__doc__ += """
Exemple de réponse:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "platform": "instagram",
    "platform_username": "marie_fitness",
    "platform_display_name": "Marie | Fitness Coach",
    "profile_picture_url": "https://...",
    "connection_status": "active",
    "connected_at": "2025-01-15T10:30:00Z",
    "last_synced_at": "2025-01-20T08:00:00Z",
    "token_expires_at": "2025-03-15T10:30:00Z",
    "days_until_expiry": 54
  }
]
```
"""
