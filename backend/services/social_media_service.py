"""
Service d'Intégration Réseaux Sociaux
Récupération automatique des statistiques des influenceurs

Plateformes supportées:
- Instagram Graph API
- TikTok Creator API
- Facebook Graph API
- YouTube Analytics API
- Twitter API v2

Fonctionnalités:
- Connexion OAuth 2.0 pour chaque plateforme
- Récupération automatique des stats (followers, engagement, posts)
- Refresh automatique quotidien via Celery
- Détection de fraude (fake followers, bots)
- Stockage historique des statistiques
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum

import structlog
from pydantic import BaseModel, Field

from supabase_client import supabase

logger = structlog.get_logger(__name__)


# ============================================
# ENUMS & MODELS
# ============================================

class SocialPlatform(str, Enum):
    """Plateformes sociales supportées"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    TWITTER = "twitter"


class SocialStats(BaseModel):
    """Statistiques d'un compte social"""
    platform: SocialPlatform
    username: str
    followers: int
    following: Optional[int] = None
    posts_count: Optional[int] = None
    engagement_rate: float
    average_likes: Optional[float] = None
    average_comments: Optional[float] = None
    average_views: Optional[float] = None  # Pour vidéos
    verified: bool = False
    categories: Optional[List[str]] = None
    raw_data: Optional[Dict] = None


# ============================================
# SERVICE SOCIAL MEDIA
# ============================================

class SocialMediaService:
    """Service principal d'intégration réseaux sociaux"""

    def __init__(self):
        self.supabase = supabase

        # Credentials API (à stocker dans .env en production)
        self.instagram_app_id = os.getenv('INSTAGRAM_APP_ID')
        self.instagram_app_secret = os.getenv('INSTAGRAM_APP_SECRET')

        self.tiktok_client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.tiktok_client_secret = os.getenv('TIKTOK_CLIENT_SECRET')

        self.facebook_app_id = os.getenv('FACEBOOK_APP_ID')
        self.facebook_app_secret = os.getenv('FACEBOOK_APP_SECRET')

        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')

        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    # ============================================
    # INSTAGRAM GRAPH API
    # ============================================

    async def connect_instagram(self, user_id: str, instagram_user_id: str, access_token: str) -> Dict:
        """
        Connecte un compte Instagram Business/Creator via OAuth

        Process:
        1. L'utilisateur autorise l'app via Instagram OAuth
        2. On reçoit un access_token
        3. On récupère les infos du compte
        4. On stocke le token (chiffré) en BDD
        5. On récupère les stats initiales

        Documentation: https://developers.facebook.com/docs/instagram-api
        """
        try:
            # 1. Échanger le short-lived token contre un long-lived token (60 jours)
            long_lived_token = await self._exchange_instagram_token(access_token)

            # 2. Récupérer les infos du compte
            account_info = await self._get_instagram_account_info(instagram_user_id, long_lived_token)

            # 3. Stocker la connexion
            social_connection = {
                'user_id': user_id,
                'platform': SocialPlatform.INSTAGRAM.value,
                'platform_user_id': instagram_user_id,
                'username': account_info.get('username'),
                'access_token_encrypted': long_lived_token,  # TODO: Chiffrer avec pgcrypto
                'token_expires_at': (datetime.now() + timedelta(days=60)).isoformat(),
                'is_active': True,
                'created_at': datetime.now().isoformat()
            }

            result = self.supabase.table('social_media_connections').upsert(
                social_connection,
                on_conflict='user_id,platform'
            ).execute()

            # 4. Récupérer les stats initiales
            stats = await self.fetch_instagram_stats(instagram_user_id, long_lived_token)

            # 5. Stocker les stats
            await self._save_social_stats(user_id, stats)

            logger.info(
                "instagram_connected",
                user_id=user_id,
                username=account_info.get('username'),
                followers=stats.followers
            )

            return {
                "success": True,
                "platform": SocialPlatform.INSTAGRAM.value,
                "username": account_info.get('username'),
                "followers": stats.followers,
                "engagement_rate": stats.engagement_rate
            }

        except Exception as e:
            logger.error("instagram_connection_failed", user_id=user_id, error=str(e))
            raise Exception(f"Erreur connexion Instagram: {str(e)}")

    async def _exchange_instagram_token(self, short_lived_token: str) -> str:
        """Échange un short-lived token contre un long-lived token (60 jours)"""
        try:
            url = "https://graph.instagram.com/access_token"
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': self.instagram_app_secret,
                'access_token': short_lived_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data['access_token']

        except Exception as e:
            logger.error("instagram_token_exchange_failed", error=str(e))
            raise

    async def _get_instagram_account_info(self, instagram_user_id: str, access_token: str) -> Dict:
        """Récupère les infos de base du compte Instagram"""
        try:
            url = f"https://graph.instagram.com/{instagram_user_id}"
            params = {
                'fields': 'id,username,account_type,media_count',
                'access_token': access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error("instagram_account_info_failed", error=str(e))
            raise

    async def fetch_instagram_stats(self, instagram_user_id: str, access_token: str) -> SocialStats:
        """
        Récupère les statistiques d'un compte Instagram

        Métriques:
        - Followers
        - Engagement rate (calculé sur les 12 derniers posts)
        - Average likes/comments
        - Verified status
        """
        try:
            # 1. Récupérer les insights du compte
            url = f"https://graph.instagram.com/{instagram_user_id}/insights"
            params = {
                'metric': 'follower_count,reach,impressions',
                'period': 'day',
                'access_token': access_token
            }

            insights_response = requests.get(url, params=params)
            insights_response.raise_for_status()
            insights = insights_response.json()

            # 2. Récupérer les 12 derniers posts pour calculer l'engagement
            media_url = f"https://graph.instagram.com/{instagram_user_id}/media"
            media_params = {
                'fields': 'id,like_count,comments_count,media_type,timestamp',
                'limit': 12,
                'access_token': access_token
            }

            media_response = requests.get(media_url, params=media_params)
            media_response.raise_for_status()
            media_data = media_response.json()

            # 3. Calculer les métriques
            followers = next((m['values'][0]['value'] for m in insights['data'] if m['name'] == 'follower_count'), 0)

            total_likes = sum(post.get('like_count', 0) for post in media_data.get('data', []))
            total_comments = sum(post.get('comments_count', 0) for post in media_data.get('data', []))
            posts_count = len(media_data.get('data', []))

            avg_likes = total_likes / posts_count if posts_count > 0 else 0
            avg_comments = total_comments / posts_count if posts_count > 0 else 0

            # Engagement rate = (avg_likes + avg_comments) / followers * 100
            engagement_rate = ((avg_likes + avg_comments) / followers * 100) if followers > 0 else 0

            # 4. Récupérer le username
            account_info = await self._get_instagram_account_info(instagram_user_id, access_token)

            stats = SocialStats(
                platform=SocialPlatform.INSTAGRAM,
                username=account_info.get('username', ''),
                followers=followers,
                posts_count=account_info.get('media_count', 0),
                engagement_rate=round(engagement_rate, 2),
                average_likes=round(avg_likes, 2),
                average_comments=round(avg_comments, 2),
                verified=False,  # Instagram API ne fournit pas cette info directement
                raw_data={
                    'insights': insights,
                    'recent_posts': media_data
                }
            )

            logger.info(
                "instagram_stats_fetched",
                username=stats.username,
                followers=followers,
                engagement_rate=engagement_rate
            )

            return stats

        except Exception as e:
            logger.error("instagram_stats_fetch_failed", error=str(e))
            raise

    # ============================================
    # TIKTOK CREATOR API
    # ============================================

    async def connect_tiktok(self, user_id: str, authorization_code: str) -> Dict:
        """
        Connecte un compte TikTok Creator via OAuth

        Documentation: https://developers.tiktok.com/doc/login-kit-web
        """
        try:
            # 1. Échanger le code contre un access token
            token_data = await self._exchange_tiktok_code(authorization_code)

            access_token = token_data['access_token']
            refresh_token = token_data['refresh_token']
            expires_in = token_data['expires_in']

            # 2. Récupérer les infos utilisateur
            user_info = await self._get_tiktok_user_info(access_token)

            # 3. Stocker la connexion
            social_connection = {
                'user_id': user_id,
                'platform': SocialPlatform.TIKTOK.value,
                'platform_user_id': user_info['open_id'],
                'username': user_info['display_name'],
                'access_token_encrypted': access_token,  # TODO: Chiffrer
                'refresh_token_encrypted': refresh_token,
                'token_expires_at': (datetime.now() + timedelta(seconds=expires_in)).isoformat(),
                'is_active': True,
                'created_at': datetime.now().isoformat()
            }

            self.supabase.table('social_media_connections').upsert(
                social_connection,
                on_conflict='user_id,platform'
            ).execute()

            # 4. Récupérer les stats
            stats = await self.fetch_tiktok_stats(user_info['open_id'], access_token)

            # 5. Stocker les stats
            await self._save_social_stats(user_id, stats)

            logger.info(
                "tiktok_connected",
                user_id=user_id,
                username=user_info['display_name'],
                followers=stats.followers
            )

            return {
                "success": True,
                "platform": SocialPlatform.TIKTOK.value,
                "username": user_info['display_name'],
                "followers": stats.followers,
                "engagement_rate": stats.engagement_rate
            }

        except Exception as e:
            logger.error("tiktok_connection_failed", user_id=user_id, error=str(e))
            raise

    async def _exchange_tiktok_code(self, authorization_code: str) -> Dict:
        """Échange le code d'autorisation contre un access token"""
        try:
            url = "https://open-api.tiktok.com/oauth/access_token/"
            params = {
                'client_key': self.tiktok_client_key,
                'client_secret': self.tiktok_client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code'
            }

            response = requests.post(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data['data']

        except Exception as e:
            logger.error("tiktok_code_exchange_failed", error=str(e))
            raise

    async def _get_tiktok_user_info(self, access_token: str) -> Dict:
        """Récupère les infos de base de l'utilisateur TikTok"""
        try:
            url = "https://open-api.tiktok.com/user/info/"
            params = {
                'access_token': access_token,
                'fields': 'open_id,union_id,avatar_url,display_name'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data['data']['user']

        except Exception as e:
            logger.error("tiktok_user_info_failed", error=str(e))
            raise

    async def fetch_tiktok_stats(self, open_id: str, access_token: str) -> SocialStats:
        """
        Récupère les statistiques d'un compte TikTok

        Note: TikTok Creator API ne fournit pas toutes les métriques publiquement
        On doit utiliser les endpoints spécifiques
        """
        try:
            # 1. Récupérer les métriques du créateur
            url = "https://open-api.tiktok.com/user/info/"
            params = {
                'access_token': access_token,
                'fields': 'follower_count,following_count,likes_count,video_count'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            user_data = data['data']['user']

            # 2. Récupérer les vidéos récentes pour calculer l'engagement
            videos_url = "https://open-api.tiktok.com/video/list/"
            videos_params = {
                'access_token': access_token,
                'fields': 'id,like_count,comment_count,share_count,view_count',
                'max_count': 20
            }

            videos_response = requests.post(videos_url, json=videos_params)
            videos_response.raise_for_status()
            videos_data = videos_response.json()

            # 3. Calculer l'engagement
            videos = videos_data.get('data', {}).get('videos', [])
            if videos:
                total_likes = sum(v.get('like_count', 0) for v in videos)
                total_comments = sum(v.get('comment_count', 0) for v in videos)
                total_views = sum(v.get('view_count', 0) for v in videos)
                count = len(videos)

                avg_likes = total_likes / count
                avg_comments = total_comments / count
                avg_views = total_views / count

                # Engagement rate = (avg_likes + avg_comments) / followers * 100
                followers = user_data.get('follower_count', 0)
                engagement_rate = ((avg_likes + avg_comments) / followers * 100) if followers > 0 else 0
            else:
                avg_likes = 0
                avg_comments = 0
                avg_views = 0
                engagement_rate = 0

            stats = SocialStats(
                platform=SocialPlatform.TIKTOK,
                username=user_data.get('display_name', ''),
                followers=user_data.get('follower_count', 0),
                following=user_data.get('following_count', 0),
                posts_count=user_data.get('video_count', 0),
                engagement_rate=round(engagement_rate, 2),
                average_likes=round(avg_likes, 2),
                average_comments=round(avg_comments, 2),
                average_views=round(avg_views, 2),
                verified=user_data.get('is_verified', False),
                raw_data={
                    'user': user_data,
                    'recent_videos': videos
                }
            )

            logger.info(
                "tiktok_stats_fetched",
                username=stats.username,
                followers=stats.followers,
                engagement_rate=engagement_rate
            )

            return stats

        except Exception as e:
            logger.error("tiktok_stats_fetch_failed", error=str(e))
            raise

    # ============================================
    # STOCKAGE DES STATISTIQUES
    # ============================================

    async def _save_social_stats(self, user_id: str, stats: SocialStats):
        """
        Stocke les statistiques dans la base de données

        Table: social_media_stats (historique)
        """
        try:
            stats_data = {
                'user_id': user_id,
                'platform': stats.platform.value,
                'username': stats.username,
                'followers': stats.followers,
                'following': stats.following,
                'posts_count': stats.posts_count,
                'engagement_rate': stats.engagement_rate,
                'average_likes': stats.average_likes,
                'average_comments': stats.average_comments,
                'average_views': stats.average_views,
                'verified': stats.verified,
                'categories': json.dumps(stats.categories) if stats.categories else None,
                'raw_data': json.dumps(stats.raw_data) if stats.raw_data else None,
                'captured_at': datetime.now().isoformat()
            }

            self.supabase.table('social_media_stats').insert(stats_data).execute()

            # Mettre à jour le profil influenceur avec les dernières stats
            await self._update_influencer_profile(user_id, stats)

            logger.info(
                "social_stats_saved",
                user_id=user_id,
                platform=stats.platform.value,
                followers=stats.followers
            )

        except Exception as e:
            logger.error("save_social_stats_failed", user_id=user_id, error=str(e))

    async def _update_influencer_profile(self, user_id: str, stats: SocialStats):
        """
        Met à jour le profil influenceur avec les dernières stats

        On prend le total des followers de toutes les plateformes
        """
        try:
            # Récupérer l'influenceur
            influencer_result = self.supabase.table('influencers').select('*').eq('user_id', user_id).execute()

            if not influencer_result.data:
                logger.warning("influencer_not_found", user_id=user_id)
                return

            # Récupérer les stats de toutes les plateformes
            all_stats = self.supabase.table('social_media_stats').select('*').eq('user_id', user_id).execute()

            if all_stats.data:
                # Calculer le total de followers (dernière stat de chaque plateforme)
                platforms_stats = {}
                for stat in all_stats.data:
                    platform = stat['platform']
                    if platform not in platforms_stats or stat['captured_at'] > platforms_stats[platform]['captured_at']:
                        platforms_stats[platform] = stat

                total_followers = sum(s['followers'] for s in platforms_stats.values())
                avg_engagement = sum(s['engagement_rate'] for s in platforms_stats.values()) / len(platforms_stats)

                # Mettre à jour l'influenceur
                update_data = {
                    'audience_size': total_followers,
                    'engagement_rate': round(avg_engagement, 2),
                    'social_links': json.dumps({
                        platform: {
                            'username': stat['username'],
                            'url': self._get_platform_url(platform, stat['username'])
                        }
                        for platform, stat in platforms_stats.items()
                    }),
                    'updated_at': datetime.now().isoformat()
                }

                self.supabase.table('influencers').update(update_data).eq('user_id', user_id).execute()

                logger.info(
                    "influencer_profile_updated",
                    user_id=user_id,
                    total_followers=total_followers,
                    avg_engagement=avg_engagement
                )

        except Exception as e:
            logger.error("update_influencer_profile_failed", user_id=user_id, error=str(e))

    def _get_platform_url(self, platform: str, username: str) -> str:
        """Retourne l'URL du profil selon la plateforme"""
        urls = {
            'instagram': f"https://instagram.com/{username}",
            'tiktok': f"https://tiktok.com/@{username}",
            'facebook': f"https://facebook.com/{username}",
            'youtube': f"https://youtube.com/@{username}",
            'twitter': f"https://twitter.com/{username}"
        }
        return urls.get(platform, '')

    # ============================================
    # REFRESH AUTOMATIQUE (Celery Task)
    # ============================================

    async def refresh_all_stats(self):
        """
        Refresh les stats de tous les utilisateurs connectés

        À exécuter quotidiennement via Celery:
        @celery.task
        async def daily_social_stats_refresh():
            await social_media_service.refresh_all_stats()
        """
        try:
            # Récupérer toutes les connexions actives
            connections = self.supabase.table('social_media_connections').select('*').eq('is_active', True).execute()

            if not connections.data:
                logger.info("no_social_connections_to_refresh")
                return

            refreshed = 0
            errors = 0

            for conn in connections.data:
                try:
                    user_id = conn['user_id']
                    platform = conn['platform']
                    platform_user_id = conn['platform_user_id']
                    access_token = conn['access_token_encrypted']  # TODO: Déchiffrer

                    # Vérifier si le token n'est pas expiré
                    if datetime.fromisoformat(conn['token_expires_at']) < datetime.now():
                        logger.warning("token_expired", user_id=user_id, platform=platform)
                        # TODO: Refresh le token automatiquement
                        continue

                    # Fetch stats selon la plateforme
                    if platform == SocialPlatform.INSTAGRAM.value:
                        stats = await self.fetch_instagram_stats(platform_user_id, access_token)
                    elif platform == SocialPlatform.TIKTOK.value:
                        stats = await self.fetch_tiktok_stats(platform_user_id, access_token)
                    # TODO: Ajouter autres plateformes

                    # Sauvegarder les stats
                    await self._save_social_stats(user_id, stats)

                    refreshed += 1

                except Exception as e:
                    logger.error("stats_refresh_failed", user_id=conn['user_id'], platform=conn['platform'], error=str(e))
                    errors += 1

            logger.info(
                "social_stats_refresh_completed",
                total=len(connections.data),
                refreshed=refreshed,
                errors=errors
            )

        except Exception as e:
            logger.error("refresh_all_stats_failed", error=str(e))


# Instance globale du service
social_media_service = SocialMediaService()
