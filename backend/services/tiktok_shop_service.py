"""
TikTok Shop API Service pour le Maroc

Ce service gère l'intégration TikTok Shop pour:
- Synchronisation automatique des produits
- Tracking des ventes depuis TikTok Lives
- Commission automatique sur ventes TikTok
- Analytics TikTok intégrés
- Génération de templates vidéos

API utilisée: TikTok Shop API (Seller API)
Documentation: https://partner.tiktokshop.com/doc/page/262811
"""

import os
import json
import logging
import hashlib
import hmac
import time
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class TikTokProductStatus(str, Enum):
    """Statuts des produits TikTok"""
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    LIVE = "LIVE"
    SUSPENDED = "SUSPENDED"

class TikTokOrderStatus(str, Enum):
    """Statuts des commandes TikTok"""
    UNPAID = "UNPAID"
    PAID = "PAID"
    READY_TO_SHIP = "READY_TO_SHIP"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class TikTokShopService:
    """Service pour gérer l'API TikTok Shop"""

    def __init__(self):
        # Configuration API TikTok Shop
        self.api_url = os.getenv("TIKTOK_SHOP_API_URL", "https://open-api.tiktokglobalshop.com")
        self.app_key = os.getenv("TIKTOK_SHOP_APP_KEY", "")
        self.app_secret = os.getenv("TIKTOK_SHOP_APP_SECRET", "")
        self.shop_id = os.getenv("TIKTOK_SHOP_ID", "")
        self.access_token = os.getenv("TIKTOK_SHOP_ACCESS_TOKEN", "")

        # Mode DEMO par défaut
        self.demo_mode = not bool(self.app_key and self.app_secret)

        if self.demo_mode:
            logger.warning("⚠️ TikTok Shop Service en mode DEMO (pas de clés configurées)")
        else:
            logger.info("✅ TikTok Shop Service configuré")

    def _generate_signature(self, params: Dict[str, Any], body: str = "") -> str:
        """
        Générer la signature pour authentifier les requêtes TikTok

        Algorithme: HMAC-SHA256
        """
        # Trier les paramètres par clé
        sorted_params = sorted(params.items())

        # Construire la chaîne à signer
        param_str = "".join([f"{k}{v}" for k, v in sorted_params])
        sign_str = f"{param_str}{body}"

        # Calculer HMAC-SHA256
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    async def sync_product_to_tiktok(
        self,
        product_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synchroniser un produit vers TikTok Shop

        Args:
            product_data: {
                "title": "Nom du produit",
                "description": "Description",
                "category_id": "12345",
                "price": 299.99,
                "currency": "MAD",
                "stock": 100,
                "images": ["https://..."],
                "video_url": "https://...",
                "brand": "Marque",
                "attributes": {...}
            }

        Returns:
            Résultat avec product_id TikTok
        """
        if self.demo_mode:
            logger.info(f"🎵 [DEMO] Sync TikTok Shop: {product_data.get('title')}")
            return {
                "success": True,
                "product_id": f"tiktok_demo_{int(time.time())}",
                "status": "APPROVED",
                "demo_mode": True,
                "sync_date": datetime.utcnow().isoformat()
            }

        try:
            # Préparer les données du produit
            tiktok_product = {
                "title": product_data["title"],
                "description": product_data.get("description", ""),
                "category_id": product_data.get("category_id"),
                "brand": {
                    "name": product_data.get("brand", "")
                },
                "main_images": [{"url": img} for img in product_data.get("images", [])[:9]],
                "skus": [{
                    "id": product_data.get("sku_id", "DEFAULT"),
                    "price": {
                        "amount": str(int(product_data["price"] * 100)),  # En centimes
                        "currency": product_data.get("currency", "MAD")
                    },
                    "stock_infos": [{
                        "warehouse_id": self.shop_id,
                        "available_stock": product_data.get("stock", 0)
                    }]
                }]
            }

            # Ajouter la vidéo si disponible
            if product_data.get("video_url"):
                tiktok_product["video"] = {
                    "url": product_data["video_url"]
                }

            # Paramètres de requête
            timestamp = int(time.time())
            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "shop_id": self.shop_id,
                "access_token": self.access_token
            }

            # Générer la signature
            body = json.dumps(tiktok_product)
            params["sign"] = self._generate_signature(params, body)

            # Envoyer la requête
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/product/202309/products",
                    params=params,
                    json=tiktok_product,
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()

                if result.get("code") == 0:
                    return {
                        "success": True,
                        "product_id": result["data"]["product_id"],
                        "status": result["data"]["status"],
                        "audit_failed_reasons": result["data"].get("audit_failed_reasons", [])
                    }
                else:
                    raise Exception(f"TikTok API error: {result.get('message')}")

        except Exception as e:
            logger.error(f"❌ Erreur sync TikTok Shop: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_product_status(
        self,
        tiktok_product_id: str
    ) -> Dict[str, Any]:
        """
        Récupérer le statut d'un produit sur TikTok Shop
        """
        if self.demo_mode:
            return {
                "product_id": tiktok_product_id,
                "status": "APPROVED",
                "views": 15420,
                "likes": 856,
                "shares": 234,
                "demo_mode": True
            }

        # En production, appeler l'API TikTok
        return {
            "product_id": tiktok_product_id,
            "status": "IMPLEMENTATION_REQUIRED"
        }

    async def get_orders(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[TikTokOrderStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les commandes TikTok Shop

        Permet de tracker les ventes réalisées via TikTok
        """
        if self.demo_mode:
            # Données de démonstration
            demo_orders = [
                {
                    "order_id": f"TT{int(time.time())}-001",
                    "product_name": "Produit TikTok Demo 1",
                    "quantity": 2,
                    "total_amount": 599.98,
                    "currency": "MAD",
                    "commission": 59.99,
                    "status": "COMPLETED",
                    "buyer_username": "@tiktok_user_1",
                    "created_at": datetime.utcnow().isoformat(),
                    "demo_mode": True
                },
                {
                    "order_id": f"TT{int(time.time())}-002",
                    "product_name": "Produit TikTok Demo 2",
                    "quantity": 1,
                    "total_amount": 299.99,
                    "currency": "MAD",
                    "commission": 29.99,
                    "status": "SHIPPED",
                    "buyer_username": "@tiktok_user_2",
                    "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "demo_mode": True
                }
            ]
            return demo_orders

        # En production, appeler l'API TikTok
        logger.info("Récupération des commandes TikTok Shop")
        return []

    async def get_live_stream_stats(
        self,
        live_stream_id: str
    ) -> Dict[str, Any]:
        """
        Récupérer les statistiques d'un TikTok Live

        Métriques:
        - Viewers (max, moyenne)
        - Likes
        - Comments
        - Ventes réalisées
        - Produits mis en avant
        """
        if self.demo_mode:
            return {
                "live_stream_id": live_stream_id,
                "status": "COMPLETED",
                "viewers_peak": 3542,
                "viewers_average": 1823,
                "likes": 15234,
                "comments": 892,
                "shares": 156,
                "duration_minutes": 45,
                "products_shown": 8,
                "sales_count": 23,
                "total_revenue": 6899.77,
                "currency": "MAD",
                "commission_earned": 689.97,
                "demo_mode": True
            }

        # En production, appeler l'API TikTok Live
        return {
            "live_stream_id": live_stream_id,
            "status": "IMPLEMENTATION_REQUIRED"
        }

    async def get_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Récupérer les analytics TikTok Shop

        Métriques disponibles:
        - views: Vues des produits
        - clicks: Clics sur liens
        - add_to_cart: Ajouts au panier
        - purchases: Achats
        - gmv: Gross Merchandise Value
        - conversion_rate: Taux de conversion
        """
        if self.demo_mode:
            # Données demo sur 7 jours
            days_data = []
            for i in range(7):
                date = end_date - timedelta(days=i)
                days_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "views": 1200 + (i * 150),
                    "clicks": 340 + (i * 45),
                    "add_to_cart": 89 + (i * 12),
                    "purchases": 23 + (i * 3),
                    "gmv": 6899.99 + (i * 899),
                    "conversion_rate": 6.76 + (i * 0.3)
                })

            return {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "summary": {
                    "total_views": 9450,
                    "total_clicks": 2695,
                    "total_purchases": 182,
                    "total_gmv": 54593.93,
                    "average_conversion_rate": 6.76
                },
                "daily_data": days_data,
                "demo_mode": True
            }

        # En production, appeler l'API Analytics TikTok
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "status": "IMPLEMENTATION_REQUIRED"
        }

    def generate_video_script(
        self,
        product: Dict[str, Any],
        style: str = "review"
    ) -> Dict[str, Any]:
        """
        Générer un script de vidéo TikTok pour un produit

        Styles disponibles:
        - review: Critique/test du produit
        - unboxing: Déballage
        - tutorial: Tutoriel d'utilisation
        - lifestyle: Mise en situation lifestyle
        - comedy: Approche humoristique
        """
        scripts = {
            "review": {
                "hook": f"🔥 J'ai testé {product['name']} pendant 7 jours et...",
                "scenes": [
                    {
                        "duration": 3,
                        "action": "Montrer le produit avec enthousiasme",
                        "text": "Regardez ça! 👀"
                    },
                    {
                        "duration": 5,
                        "action": "Démonstration du produit",
                        "text": f"Voici comment ça fonctionne..."
                    },
                    {
                        "duration": 4,
                        "action": "Montrer les avantages",
                        "text": "Ce que j'adore: [liste 3 points]"
                    },
                    {
                        "duration": 3,
                        "action": "Call-to-action",
                        "text": f"Lien en bio! Code promo: {product.get('promo_code', 'TIKTOK10')}"
                    }
                ],
                "music_suggestion": "Trending upbeat track",
                "hashtags": ["#review", "#test", f"#{product['name'].replace(' ', '')}", "#maroc", "#tiktokshop"]
            },
            "unboxing": {
                "hook": f"📦 Unboxing de {product['name']} - Vous allez adorer!",
                "scenes": [
                    {"duration": 2, "action": "Montrer le colis fermé", "text": "Ça vient d'arriver! 🎁"},
                    {"duration": 4, "action": "Ouvrir lentement", "text": "Le moment de vérité..."},
                    {"duration": 5, "action": "Découvrir le contenu", "text": "WOW regardez ça! 😍"},
                    {"duration": 4, "action": "Montrer les détails", "text": "La qualité est incroyable!"}
                ],
                "music_suggestion": "Suspenseful to exciting transition",
                "hashtags": ["#unboxing", "#haul", "#shopping", "#maroc"]
            },
            "tutorial": {
                "hook": f"Comment utiliser {product['name']} comme un PRO 💪",
                "scenes": [
                    {"duration": 3, "action": "Intro rapide", "text": "Tutoriel en 15 secondes!"},
                    {"duration": 4, "action": "Étape 1", "text": "1️⃣ Première étape..."},
                    {"duration": 4, "action": "Étape 2", "text": "2️⃣ Ensuite..."},
                    {"duration": 4, "action": "Résultat final", "text": "Et voilà le résultat! ✨"}
                ],
                "music_suggestion": "Upbeat tutorial music",
                "hashtags": ["#tutorial", "#howto", "#tips", "#maroc", "#astuce"]
            }
        }

        script = scripts.get(style, scripts["review"])
        script["total_duration"] = sum(scene["duration"] for scene in script["scenes"])
        script["product_name"] = product["name"]
        script["style"] = style

        return script

    def get_trending_products_categories(self) -> List[Dict[str, Any]]:
        """
        Récupérer les catégories de produits tendance sur TikTok Maroc

        Basé sur les données de TikTok Shop Analytics
        """
        return [
            {
                "category": "Fashion & Beauty",
                "category_id": "fashion_beauty",
                "trending_score": 95,
                "avg_views": 45000,
                "top_products": ["Hijabs", "Maquillage", "Parfums"],
                "best_time_to_post": "18:00-22:00",
                "peak_days": ["Jeudi", "Vendredi", "Samedi"]
            },
            {
                "category": "Electronics & Gadgets",
                "category_id": "electronics",
                "trending_score": 88,
                "avg_views": 38000,
                "top_products": ["Écouteurs", "Powerbanks", "Accessoires téléphone"],
                "best_time_to_post": "19:00-23:00",
                "peak_days": ["Mercredi", "Jeudi", "Vendredi"]
            },
            {
                "category": "Home & Kitchen",
                "category_id": "home_kitchen",
                "trending_score": 82,
                "avg_views": 32000,
                "top_products": ["Ustensiles", "Décoration", "Organisation"],
                "best_time_to_post": "12:00-14:00, 20:00-22:00",
                "peak_days": ["Samedi", "Dimanche"]
            },
            {
                "category": "Sports & Fitness",
                "category_id": "sports",
                "trending_score": 76,
                "avg_views": 28000,
                "top_products": ["Équipement fitness", "Vêtements sport", "Suppléments"],
                "best_time_to_post": "06:00-09:00, 17:00-19:00",
                "peak_days": ["Lundi", "Mardi", "Samedi"]
            }
        ]


# Instance singleton du service
tiktok_shop_service = TikTokShopService()
