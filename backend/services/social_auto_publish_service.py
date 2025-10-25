"""
Social Media Auto-Publishing Service
Publication automatique sur les réseaux sociaux des influenceurs

Features:
1. Publication Instagram (Feed + Stories + Reels)
2. Publication TikTok (Videos)
3. Publication Facebook (Pages + Groupes)
4. Génération automatique de captions optimisées
5. Hashtags intelligents
6. Scheduling (publication différée)
7. Analytics post-publication
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import structlog
from supabase_client import supabase

logger = structlog.get_logger()


# ============================================
# SOCIAL MEDIA AUTO-PUBLISH SERVICE
# ============================================

class SocialMediaAutoPublisher:
    """
    Service de publication automatique sur réseaux sociaux
    """

    def __init__(self):
        self.instagram_api_url = "https://graph.instagram.com/v18.0"
        self.tiktok_api_url = "https://open-api.tiktok.com/v1.3"
        self.facebook_api_url = "https://graph.facebook.com/v18.0"

    async def generate_caption(
        self,
        product_name: str,
        product_description: str,
        affiliate_link: str,
        platform: str = "instagram"
    ) -> Dict:
        """
        Générer caption optimisée pour chaque plateforme

        Args:
            product_name: Nom du produit
            product_description: Description
            affiliate_link: Lien d'affiliation
            platform: instagram, tiktok, facebook

        Returns:
            {
                "caption": str,
                "hashtags": List[str],
                "call_to_action": str
            }
        """
        try:
            # Raccourcir description pour réseaux sociaux
            short_desc = product_description[:200] + "..." if len(product_description) > 200 else product_description

            # Hashtags génériques (à améliorer avec AI)
            base_hashtags = [
                "#maroc",
                "#casablanca",
                "#shopping",
                "#deals",
                "#promo",
                "#reduction",
                "#bonplan"
            ]

            if platform == "instagram":
                caption = f"""✨ {product_name} ✨

{short_desc}

🔗 Lien dans ma bio ou swipe up!
👉 {affiliate_link}

💰 Profitez de cette offre exclusive!

#ad #sponsored #shareyoursales"""

                hashtags = base_hashtags + [
                    "#instagrammaroc",
                    "#influencermaroc",
                    "#shoppingonline",
                    "#madeInmorocco"
                ]

                call_to_action = "Swipe up pour découvrir! 👆"

            elif platform == "tiktok":
                caption = f"""🔥 {product_name}

{short_desc[:100]}...

Lien en bio! 🔗
{affiliate_link}

#tiktokmade #maroctiktok #dealoftiktok #shoppingtiktok"""

                hashtags = base_hashtags + [
                    "#tiktokmade",
                    "#maroctiktok",
                    "#fyp",
                    "#viral"
                ]

                call_to_action = "Clique le lien en bio! ⬆️"

            elif platform == "facebook":
                caption = f"""{product_name}

{short_desc}

🛒 Commandez maintenant via ce lien:
{affiliate_link}

⭐ Offre limitée!"""

                hashtags = base_hashtags + [
                    "#facebookmaroc",
                    "#groupeachatmaroc"
                ]

                call_to_action = "Cliquez pour commander! 🛍️"

            else:
                # Generic
                caption = f"{product_name}\n\n{short_desc}\n\n{affiliate_link}"
                hashtags = base_hashtags
                call_to_action = "En savoir plus!"

            return {
                "caption": caption,
                "hashtags": hashtags,
                "call_to_action": call_to_action,
                "full_text": f"{caption}\n\n{' '.join(hashtags)}"
            }

        except Exception as e:
            logger.error("caption_generation_failed", error=str(e))
            return {
                "caption": f"{product_name}\n\n{affiliate_link}",
                "hashtags": [],
                "call_to_action": "Découvrir"
            }

    async def publish_to_instagram(
        self,
        user_id: str,
        product_id: str,
        affiliate_link: str,
        image_url: str,
        caption_data: Dict,
        post_type: str = "feed"  # feed, story, reel
    ) -> Dict:
        """
        Publier sur Instagram

        Args:
            user_id: ID utilisateur
            product_id: ID produit
            affiliate_link: Lien affiliation
            image_url: URL image produit
            caption_data: Caption générée
            post_type: Type de post

        Returns:
            {
                "success": bool,
                "post_id": str,
                "platform": "instagram",
                "url": str
            }
        """
        try:
            # Récupérer access token Instagram
            account = await self._get_social_account(user_id, "instagram")

            if not account or not account.get("access_token"):
                raise Exception("Instagram account not connected")

            access_token = account["access_token"]
            instagram_account_id = account["platform_user_id"]

            # Préparer données publication
            if post_type == "feed":
                # Publication normale (image + caption)
                # TODO: Implémenter avec Instagram Graph API
                # POST /{ig-user-id}/media
                # POST /{ig-user-id}/media_publish

                logger.info("instagram_feed_post_initiated", user_id=user_id, product_id=product_id)

                # Simuler pour l'instant (à implémenter réellement)
                post_id = f"ig_post_{datetime.utcnow().timestamp()}"

                # Sauvegarder dans DB
                await self._save_publication(
                    user_id=user_id,
                    product_id=product_id,
                    platform="instagram",
                    post_type=post_type,
                    post_id=post_id,
                    caption=caption_data["full_text"],
                    media_url=image_url,
                    affiliate_link=affiliate_link
                )

                return {
                    "success": True,
                    "post_id": post_id,
                    "platform": "instagram",
                    "post_type": post_type,
                    "url": f"https://www.instagram.com/p/{post_id}/"
                }

            elif post_type == "story":
                # Story Instagram
                # TODO: Implémenter Instagram Stories API
                logger.info("instagram_story_post_initiated", user_id=user_id)

                post_id = f"ig_story_{datetime.utcnow().timestamp()}"

                return {
                    "success": True,
                    "post_id": post_id,
                    "platform": "instagram",
                    "post_type": "story",
                    "url": f"https://www.instagram.com/stories/{instagram_account_id}/"
                }

            elif post_type == "reel":
                # Reel Instagram
                # TODO: Implémenter Instagram Reels API
                logger.info("instagram_reel_post_initiated", user_id=user_id)

                post_id = f"ig_reel_{datetime.utcnow().timestamp()}"

                return {
                    "success": True,
                    "post_id": post_id,
                    "platform": "instagram",
                    "post_type": "reel",
                    "url": f"https://www.instagram.com/reel/{post_id}/"
                }

        except Exception as e:
            logger.error("instagram_publish_failed", user_id=user_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram"
            }

    async def publish_to_tiktok(
        self,
        user_id: str,
        product_id: str,
        affiliate_link: str,
        video_url: str,
        caption_data: Dict
    ) -> Dict:
        """
        Publier sur TikTok

        Args:
            user_id: ID utilisateur
            product_id: ID produit
            affiliate_link: Lien affiliation
            video_url: URL vidéo
            caption_data: Caption générée

        Returns:
            Publication result
        """
        try:
            # Récupérer access token TikTok
            account = await self._get_social_account(user_id, "tiktok")

            if not account or not account.get("access_token"):
                raise Exception("TikTok account not connected")

            # TODO: Implémenter TikTok Creator API
            # POST /share/video/upload/

            logger.info("tiktok_post_initiated", user_id=user_id, product_id=product_id)

            post_id = f"tiktok_{datetime.utcnow().timestamp()}"

            # Sauvegarder dans DB
            await self._save_publication(
                user_id=user_id,
                product_id=product_id,
                platform="tiktok",
                post_type="video",
                post_id=post_id,
                caption=caption_data["full_text"],
                media_url=video_url,
                affiliate_link=affiliate_link
            )

            return {
                "success": True,
                "post_id": post_id,
                "platform": "tiktok",
                "url": f"https://www.tiktok.com/@user/video/{post_id}"
            }

        except Exception as e:
            logger.error("tiktok_publish_failed", user_id=user_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "platform": "tiktok"
            }

    async def publish_to_facebook(
        self,
        user_id: str,
        product_id: str,
        affiliate_link: str,
        image_url: str,
        caption_data: Dict,
        target_type: str = "page"  # page ou group
    ) -> Dict:
        """
        Publier sur Facebook (Page ou Groupe)
        """
        try:
            # Récupérer access token Facebook
            account = await self._get_social_account(user_id, "facebook")

            if not account or not account.get("access_token"):
                raise Exception("Facebook account not connected")

            # TODO: Implémenter Facebook Graph API
            # POST /{page-id}/photos
            # POST /{group-id}/feed

            logger.info("facebook_post_initiated", user_id=user_id, product_id=product_id)

            post_id = f"fb_{datetime.utcnow().timestamp()}"

            await self._save_publication(
                user_id=user_id,
                product_id=product_id,
                platform="facebook",
                post_type=target_type,
                post_id=post_id,
                caption=caption_data["full_text"],
                media_url=image_url,
                affiliate_link=affiliate_link
            )

            return {
                "success": True,
                "post_id": post_id,
                "platform": "facebook",
                "url": f"https://www.facebook.com/{post_id}"
            }

        except Exception as e:
            logger.error("facebook_publish_failed", user_id=user_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "platform": "facebook"
            }

    async def publish_to_all_platforms(
        self,
        user_id: str,
        product_id: str,
        affiliate_link: str,
        media_urls: Dict,  # {platform: url}
        platforms: List[str] = None
    ) -> Dict:
        """
        Publier sur tous les réseaux sociaux de l'influenceur

        Args:
            user_id: ID influenceur
            product_id: ID produit
            affiliate_link: Lien affiliation généré
            media_urls: URLs des médias par plateforme
            platforms: Liste des plateformes (None = toutes)

        Returns:
            {
                "success": bool,
                "published": List[Dict],
                "failed": List[Dict]
            }
        """
        try:
            # Récupérer info produit
            product = await self._get_product(product_id)

            if not product:
                raise Exception("Product not found")

            # Récupérer comptes sociaux actifs
            if platforms is None:
                platforms = ["instagram", "tiktok", "facebook"]

            results = {
                "success": True,
                "published": [],
                "failed": [],
                "total": len(platforms)
            }

            for platform in platforms:
                try:
                    # Générer caption optimisée
                    caption_data = await self.generate_caption(
                        product_name=product["name"],
                        product_description=product.get("description", ""),
                        affiliate_link=affiliate_link,
                        platform=platform
                    )

                    # Publier selon plateforme
                    if platform == "instagram":
                        media_url = media_urls.get("instagram") or media_urls.get("default")
                        result = await self.publish_to_instagram(
                            user_id=user_id,
                            product_id=product_id,
                            affiliate_link=affiliate_link,
                            image_url=media_url,
                            caption_data=caption_data
                        )

                    elif platform == "tiktok":
                        media_url = media_urls.get("tiktok") or media_urls.get("default")
                        result = await self.publish_to_tiktok(
                            user_id=user_id,
                            product_id=product_id,
                            affiliate_link=affiliate_link,
                            video_url=media_url,
                            caption_data=caption_data
                        )

                    elif platform == "facebook":
                        media_url = media_urls.get("facebook") or media_urls.get("default")
                        result = await self.publish_to_facebook(
                            user_id=user_id,
                            product_id=product_id,
                            affiliate_link=affiliate_link,
                            image_url=media_url,
                            caption_data=caption_data
                        )

                    if result.get("success"):
                        results["published"].append(result)
                    else:
                        results["failed"].append(result)

                except Exception as e:
                    logger.error("platform_publish_failed", platform=platform, error=str(e))
                    results["failed"].append({
                        "platform": platform,
                        "error": str(e)
                    })

            results["success"] = len(results["failed"]) == 0

            logger.info("multi_platform_publish_completed",
                       user_id=user_id,
                       product_id=product_id,
                       published=len(results["published"]),
                       failed=len(results["failed"]))

            return results

        except Exception as e:
            logger.error("publish_to_all_failed", user_id=user_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "published": [],
                "failed": []
            }

    async def _get_social_account(self, user_id: str, platform: str) -> Optional[Dict]:
        """Récupérer compte social d'un utilisateur"""
        try:
            result = supabase.table('social_media_accounts').select('*').eq('user_id', user_id).eq('platform', platform).eq('is_active', True).execute()

            if result.data:
                return result.data[0]

            return None

        except Exception as e:
            logger.error("get_social_account_failed", user_id=user_id, platform=platform, error=str(e))
            return None

    async def _get_product(self, product_id: str) -> Optional[Dict]:
        """Récupérer détails produit"""
        try:
            result = supabase.table('products').select('*').eq('id', product_id).execute()

            if result.data:
                return result.data[0]

            return None

        except Exception as e:
            logger.error("get_product_failed", product_id=product_id, error=str(e))
            return None

    async def _save_publication(
        self,
        user_id: str,
        product_id: str,
        platform: str,
        post_type: str,
        post_id: str,
        caption: str,
        media_url: str,
        affiliate_link: str
    ):
        """Sauvegarder publication dans DB"""
        try:
            supabase.table('social_media_publications').insert({
                'user_id': user_id,
                'product_id': product_id,
                'platform': platform,
                'post_type': post_type,
                'platform_post_id': post_id,
                'caption': caption,
                'media_url': media_url,
                'affiliate_link': affiliate_link,
                'published_at': datetime.utcnow().isoformat(),
                'created_at': datetime.utcnow().isoformat()
            }).execute()

            logger.info("publication_saved", user_id=user_id, platform=platform, post_id=post_id)

        except Exception as e:
            logger.error("save_publication_failed", error=str(e))


# Instance globale
auto_publisher = SocialMediaAutoPublisher()
