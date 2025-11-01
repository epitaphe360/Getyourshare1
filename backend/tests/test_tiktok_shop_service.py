"""
Tests pour TikTok Shop Service

Tests couvrant:
- Synchronisation de produits
- Récupération de statuts
- Tracking des commandes
- Analytics TikTok Lives
- Génération de scripts vidéos
- Trending products
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from backend.services.tiktok_shop_service import (
    TikTokShopService,
    TikTokProductStatus,
    TikTokOrderStatus
)


class TestTikTokShopService:
    """Tests du service TikTok Shop"""

    @pytest.fixture
    def tiktok_service(self):
        """Fixture pour créer une instance du service"""
        service = TikTokShopService()
        service.demo_mode = False
        service.app_key = "test_key"
        service.app_secret = "test_secret"
        service.shop_id = "test_shop"
        return service

    @pytest.fixture
    def demo_service(self):
        """Service en mode démo"""
        return TikTokShopService()

    # ========== Tests d'initialisation ==========

    def test_service_initialization(self):
        """Test: Service s'initialise correctement"""
        service = TikTokShopService()
        assert service is not None
        assert isinstance(service.demo_mode, bool)

    def test_demo_mode_without_keys(self):
        """Test: Mode démo si pas de clés"""
        service = TikTokShopService()
        service.app_key = ""
        service.app_secret = ""
        assert service.demo_mode is True

    # ========== Tests de signature ==========

    def test_generate_signature(self, tiktok_service):
        """Test: Génération de signature HMAC"""
        params = {
            "app_key": "test",
            "timestamp": 1234567890
        }

        signature = tiktok_service._generate_signature(params, "")

        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) == 64  # HMAC-SHA256 = 64 hex chars

    def test_signature_consistency(self, tiktok_service):
        """Test: Même params = même signature"""
        params = {"test": "value"}

        sig1 = tiktok_service._generate_signature(params)
        sig2 = tiktok_service._generate_signature(params)

        assert sig1 == sig2

    # ========== Tests de synchronisation produits ==========

    @pytest.mark.asyncio
    async def test_sync_product_demo_mode(self, demo_service):
        """Test: Sync produit en mode démo"""
        product_data = {
            "title": "Test Product",
            "description": "Test Description",
            "price": 299.99,
            "currency": "MAD",
            "stock": 100,
            "images": ["https://example.com/image.jpg"]
        }

        result = await demo_service.sync_product_to_tiktok(product_data)

        assert result["success"] is True
        assert "product_id" in result
        assert result["status"] == "APPROVED"
        assert result["demo_mode"] is True

    @pytest.mark.asyncio
    async def test_sync_product_with_video(self, demo_service):
        """Test: Sync produit avec vidéo"""
        product_data = {
            "title": "Product with Video",
            "price": 199.99,
            "currency": "MAD",
            "stock": 50,
            "images": ["https://example.com/img.jpg"],
            "video_url": "https://example.com/video.mp4"
        }

        result = await demo_service.sync_product_to_tiktok(product_data)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_sync_product_validation(self, demo_service):
        """Test: Validation données produit"""
        # Produit sans titre (devrait passer en demo mais échouer en prod)
        product_data = {
            "price": 100,
            "currency": "MAD"
        }

        # En mode demo, ça passe
        result = await demo_service.sync_product_to_tiktok(product_data)
        assert result["success"] is True

    # ========== Tests de statut produit ==========

    @pytest.mark.asyncio
    async def test_get_product_status_demo(self, demo_service):
        """Test: Récupérer statut produit"""
        result = await demo_service.get_product_status("tiktok_123")

        assert "product_id" in result
        assert "status" in result
        assert result["status"] == "APPROVED"
        assert "views" in result
        assert "likes" in result

    @pytest.mark.asyncio
    async def test_product_status_metrics(self, demo_service):
        """Test: Métriques du produit"""
        result = await demo_service.get_product_status("test_product")

        assert result["views"] > 0
        assert result["likes"] > 0
        assert result["shares"] > 0

    # ========== Tests des commandes ==========

    @pytest.mark.asyncio
    async def test_get_orders_demo(self, demo_service):
        """Test: Récupérer les commandes"""
        orders = await demo_service.get_orders()

        assert isinstance(orders, list)
        assert len(orders) > 0

        order = orders[0]
        assert "order_id" in order
        assert "product_name" in order
        assert "total_amount" in order
        assert "commission" in order
        assert "status" in order

    @pytest.mark.asyncio
    async def test_get_orders_with_date_filter(self, demo_service):
        """Test: Filtrer commandes par date"""
        start = datetime.now() - timedelta(days=30)
        end = datetime.now()

        orders = await demo_service.get_orders(
            start_date=start,
            end_date=end
        )

        assert isinstance(orders, list)

    @pytest.mark.asyncio
    async def test_get_orders_with_status_filter(self, demo_service):
        """Test: Filtrer par statut"""
        orders = await demo_service.get_orders(
            status=TikTokOrderStatus.COMPLETED
        )

        # En mode demo, retourne des données
        assert isinstance(orders, list)

    # ========== Tests des analytics TikTok Live ==========

    @pytest.mark.asyncio
    async def test_get_live_stream_stats(self, demo_service):
        """Test: Statistiques d'un live"""
        stats = await demo_service.get_live_stream_stats("live_123")

        assert "live_stream_id" in stats
        assert "status" in stats
        assert "viewers_peak" in stats
        assert "viewers_average" in stats
        assert "likes" in stats
        assert "sales_count" in stats
        assert "total_revenue" in stats

    @pytest.mark.asyncio
    async def test_live_stats_calculations(self, demo_service):
        """Test: Calculs des stats live"""
        stats = await demo_service.get_live_stream_stats("live_test")

        # Viewers peak devrait être >= average
        assert stats["viewers_peak"] >= stats["viewers_average"]

        # Revenue devrait être cohérent avec sales
        assert stats["total_revenue"] > 0
        assert stats["sales_count"] > 0

    # ========== Tests des analytics généraux ==========

    @pytest.mark.asyncio
    async def test_get_analytics(self, demo_service):
        """Test: Analytics sur période"""
        start = datetime.now() - timedelta(days=7)
        end = datetime.now()

        analytics = await demo_service.get_analytics(
            start_date=start,
            end_date=end
        )

        assert "summary" in analytics
        assert "daily_data" in analytics

        summary = analytics["summary"]
        assert "total_views" in summary
        assert "total_clicks" in summary
        assert "total_purchases" in summary
        assert "total_gmv" in summary

    @pytest.mark.asyncio
    async def test_analytics_daily_data(self, demo_service):
        """Test: Données quotidiennes"""
        start = datetime.now() - timedelta(days=7)
        end = datetime.now()

        analytics = await demo_service.get_analytics(start, end)
        daily = analytics["daily_data"]

        assert len(daily) == 7  # 7 jours

        for day in daily:
            assert "date" in day
            assert "views" in day
            assert "clicks" in day
            assert "purchases" in day
            assert "gmv" in day

    # ========== Tests de génération de scripts ==========

    def test_generate_video_script_review(self, demo_service):
        """Test: Générer script review"""
        product = {
            "name": "Écouteurs Bluetooth",
            "promo_code": "TIKTOK10"
        }

        script = demo_service.generate_video_script(product, "review")

        assert "hook" in script
        assert "scenes" in script
        assert "hashtags" in script
        assert "total_duration" in script
        assert script["style"] == "review"

    def test_generate_script_all_styles(self, demo_service):
        """Test: Tous les styles de scripts"""
        product = {"name": "Test Product"}
        styles = ["review", "unboxing", "tutorial"]

        for style in styles:
            script = demo_service.generate_video_script(product, style)
            assert script["style"] == style
            assert len(script["scenes"]) > 0

    def test_script_scene_structure(self, demo_service):
        """Test: Structure des scènes"""
        script = demo_service.generate_video_script(
            {"name": "Product"},
            "review"
        )

        for scene in script["scenes"]:
            assert "duration" in scene
            assert "action" in scene
            assert "text" in scene

    def test_script_duration_calculation(self, demo_service):
        """Test: Calcul durée totale"""
        script = demo_service.generate_video_script(
            {"name": "Test"},
            "tutorial"
        )

        # Calculer manuellement
        manual_total = sum(s["duration"] for s in script["scenes"])

        assert script["total_duration"] == manual_total

    # ========== Tests trending categories ==========

    def test_get_trending_categories(self, demo_service):
        """Test: Catégories tendance"""
        categories = demo_service.get_trending_products_categories()

        assert len(categories) > 0

        for cat in categories:
            assert "category" in cat
            assert "trending_score" in cat
            assert "avg_views" in cat
            assert "top_products" in cat
            assert 0 <= cat["trending_score"] <= 100

    def test_trending_categories_sorted(self, demo_service):
        """Test: Catégories triées par score"""
        categories = demo_service.get_trending_products_categories()

        scores = [cat["trending_score"] for cat in categories]

        # Devrait être trié décroissant
        assert scores == sorted(scores, reverse=True)

    # ========== Tests de validation ==========

    @pytest.mark.asyncio
    async def test_sync_product_missing_required_fields(self, demo_service):
        """Test: Champs requis manquants"""
        # En mode demo, accepte tout
        result = await demo_service.sync_product_to_tiktok({})

        # Demo mode devrait toujours réussir
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_product_id_status(self, demo_service):
        """Test: ID produit invalide"""
        # Devrait retourner un résultat même si ID invalide
        result = await demo_service.get_product_status("invalid_id")

        assert "product_id" in result


# ========== Tests d'intégration ==========

class TestTikTokIntegration:
    """Tests d'intégration TikTok"""

    @pytest.mark.asyncio
    async def test_complete_product_workflow(self):
        """Test: Workflow complet produit"""
        service = TikTokShopService()
        service.demo_mode = True

        # 1. Sync produit
        product = {
            "title": "Test Product",
            "price": 199.99,
            "currency": "MAD",
            "stock": 50,
            "images": ["https://example.com/img.jpg"]
        }

        sync_result = await service.sync_product_to_tiktok(product)
        assert sync_result["success"] is True

        # 2. Vérifier statut
        product_id = sync_result["product_id"]
        status = await service.get_product_status(product_id)
        assert status["product_id"] == product_id

        # 3. Générer script vidéo
        script = service.generate_video_script(
            {"name": product["title"]},
            "review"
        )
        assert script is not None

    @pytest.mark.asyncio
    async def test_analytics_workflow(self):
        """Test: Workflow analytics complet"""
        service = TikTokShopService()
        service.demo_mode = True

        # 1. Obtenir analytics
        analytics = await service.get_analytics(
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now()
        )

        assert analytics["summary"]["total_views"] > 0

        # 2. Stats d'un live
        live_stats = await service.get_live_stream_stats("live_123")
        assert live_stats["sales_count"] > 0


# ========== Tests de performance ==========

class TestTikTokPerformance:
    """Tests de performance"""

    @pytest.mark.asyncio
    async def test_sync_multiple_products_performance(self):
        """Test: Sync de plusieurs produits"""
        service = TikTokShopService()
        service.demo_mode = True

        import time
        start = time.time()

        # Sync 50 produits
        for i in range(50):
            await service.sync_product_to_tiktok({
                "title": f"Product {i}",
                "price": 100 + i,
                "currency": "MAD",
                "stock": 10
            })

        elapsed = time.time() - start

        # Devrait prendre moins de 2 secondes en mode demo
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_analytics_query_performance(self):
        """Test: Performance requête analytics"""
        service = TikTokShopService()
        service.demo_mode = True

        import time
        start = time.time()

        await service.get_analytics(
            start_date=datetime.now() - timedelta(days=90),
            end_date=datetime.now()
        )

        elapsed = time.time() - start

        # Devrait être rapide même pour 90 jours
        assert elapsed < 1.0
