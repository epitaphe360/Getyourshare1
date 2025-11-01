"""
Tests pour Content Studio Service

Tests couvrant:
- Génération d'images IA
- Templates visuels
- QR codes
- Watermarking
- Planification de posts
- A/B Testing
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from PIL import Image
import io

from backend.services.content_studio_service import (
    ContentStudioService,
    ContentType,
    SocialPlatform,
    TemplateCategory
)


class TestContentStudioService:
    """Tests du service Content Studio"""

    @pytest.fixture
    def content_studio(self):
        """Fixture service"""
        return ContentStudioService()

    # ========== Tests de génération IA ==========

    @pytest.mark.asyncio
    async def test_generate_image_demo_mode(self, content_studio):
        """Test: Génération image en mode démo"""
        content_studio.demo_mode = True

        result = await content_studio.generate_image_ai(
            prompt="Écouteurs Bluetooth modernes",
            style="realistic"
        )

        assert result["success"] is True
        assert result["demo_mode"] is True
        assert "image_url" in result

    @pytest.mark.asyncio
    async def test_generate_image_different_styles(self, content_studio):
        """Test: Différents styles d'images"""
        content_studio.demo_mode = True
        styles = ["realistic", "artistic", "cartoon", "minimalist"]

        for style in styles:
            result = await content_studio.generate_image_ai(
                prompt="Test product",
                style=style
            )
            assert result["success"] is True
            assert result["style"] == style

    @pytest.mark.asyncio
    async def test_generate_image_different_sizes(self, content_studio):
        """Test: Différentes tailles d'images"""
        content_studio.demo_mode = True
        sizes = ["1024x1024", "1792x1024", "1024x1792"]

        for size in sizes:
            result = await content_studio.generate_image_ai(
                prompt="Test",
                size=size
            )
            assert result["success"] is True

    # ========== Tests des templates ==========

    def test_get_all_templates(self, content_studio):
        """Test: Récupérer tous les templates"""
        templates = content_studio.get_templates()

        assert len(templates) > 0
        assert all("id" in t for t in templates)
        assert all("name" in t for t in templates)
        assert all("category" in t for t in templates)

    def test_get_templates_by_category(self, content_studio):
        """Test: Filtrer par catégorie"""
        templates = content_studio.get_templates(
            category=TemplateCategory.PRODUCT_SHOWCASE
        )

        assert all(t["category"] == TemplateCategory.PRODUCT_SHOWCASE for t in templates)

    def test_get_templates_by_content_type(self, content_studio):
        """Test: Filtrer par type de contenu"""
        templates = content_studio.get_templates(
            content_type=ContentType.STORY
        )

        assert all(t["content_type"] == ContentType.STORY for t in templates)

    def test_get_templates_by_platform(self, content_studio):
        """Test: Filtrer par plateforme"""
        templates = content_studio.get_templates(
            platform=SocialPlatform.INSTAGRAM
        )

        assert all(SocialPlatform.INSTAGRAM in t["platforms"] for t in templates)

    def test_template_structure(self, content_studio):
        """Test: Structure d'un template"""
        templates = content_studio.get_templates()
        template = templates[0]

        required_fields = ["id", "name", "category", "content_type", "platforms", "dimensions", "elements"]
        for field in required_fields:
            assert field in template

    def test_template_elements(self, content_studio):
        """Test: Éléments des templates"""
        templates = content_studio.get_templates()

        for template in templates:
            assert "elements" in template
            assert len(template["elements"]) > 0

            for element in template["elements"]:
                assert "type" in element

    # ========== Tests QR Code ==========

    def test_generate_qr_code_basic(self, content_studio):
        """Test: Génération QR code basique"""
        qr_code = content_studio.generate_qr_code(
            url="https://shareyoursales.com/aff/ABC123"
        )

        assert qr_code is not None
        assert qr_code.startswith("data:image/png;base64,")

    def test_generate_qr_code_styles(self, content_studio):
        """Test: Différents styles QR"""
        styles = ["modern", "rounded", "dots", "artistic"]

        for style in styles:
            qr_code = content_studio.generate_qr_code(
                url="https://example.com",
                style=style
            )
            assert qr_code is not None

    def test_generate_qr_code_colors(self, content_studio):
        """Test: QR codes colorés"""
        qr_code = content_studio.generate_qr_code(
            url="https://example.com",
            color="#FF6B9D",
            bg_color="#FFFFFF"
        )

        assert qr_code is not None

    def test_generate_qr_code_sizes(self, content_studio):
        """Test: Différentes tailles QR"""
        sizes = [128, 256, 512, 1024]

        for size in sizes:
            qr_code = content_studio.generate_qr_code(
                url="https://example.com",
                size=size
            )
            assert qr_code is not None

    # ========== Tests Watermark ==========

    def test_add_watermark_basic(self, content_studio, tmp_path):
        """Test: Ajout watermark basique"""
        # Créer une image test
        img = Image.new('RGB', (1080, 1080), color='white')
        img_path = tmp_path / "test.jpg"
        img.save(img_path)

        result = content_studio.add_watermark(
            image_path=str(img_path),
            watermark_text="@username"
        )

        assert result is not None
        assert "_watermarked" in result

    def test_watermark_positions(self, content_studio, tmp_path):
        """Test: Différentes positions watermark"""
        img = Image.new('RGB', (1080, 1080), color='white')
        img_path = tmp_path / "test.jpg"
        img.save(img_path)

        positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]

        for position in positions:
            result = content_studio.add_watermark(
                image_path=str(img_path),
                watermark_text="@test",
                position=position
            )
            assert result is not None

    def test_watermark_opacity(self, content_studio, tmp_path):
        """Test: Opacité watermark"""
        img = Image.new('RGB', (1080, 1080), color='white')
        img_path = tmp_path / "test.jpg"
        img.save(img_path)

        opacities = [0.3, 0.5, 0.7, 1.0]

        for opacity in opacities:
            result = content_studio.add_watermark(
                image_path=str(img_path),
                watermark_text="@test",
                opacity=opacity
            )
            assert result is not None

    # ========== Tests Planification ==========

    def test_schedule_post_single_platform(self, content_studio):
        """Test: Planifier post sur 1 plateforme"""
        result = content_studio.schedule_post(
            content={"text": "Test post"},
            platforms=[SocialPlatform.INSTAGRAM],
            scheduled_time=datetime.now() + timedelta(hours=1),
            user_id="user_123"
        )

        assert result["success"] is True
        assert "scheduled_id" in result

    def test_schedule_post_multiple_platforms(self, content_studio):
        """Test: Planifier sur plusieurs plateformes"""
        platforms = [
            SocialPlatform.INSTAGRAM,
            SocialPlatform.TIKTOK,
            SocialPlatform.FACEBOOK
        ]

        result = content_studio.schedule_post(
            content={"text": "Multi-platform post"},
            platforms=platforms,
            scheduled_time=datetime.now() + timedelta(days=1),
            user_id="user_123"
        )

        assert result["success"] is True
        assert len(result["platforms"]) == 3

    def test_schedule_post_content_structure(self, content_studio):
        """Test: Structure du contenu"""
        content = {
            "text": "Post text",
            "image_url": "https://example.com/image.jpg",
            "hashtags": ["#test", "#maroc"]
        }

        result = content_studio.schedule_post(
            content=content,
            platforms=[SocialPlatform.INSTAGRAM],
            scheduled_time=datetime.now() + timedelta(hours=2),
            user_id="user_123"
        )

        assert result["success"] is True

    # ========== Tests A/B Testing ==========

    def test_analyze_creative_performance(self, content_studio):
        """Test: Analyse A/B test"""
        result = content_studio.analyze_creative_performance(
            creative_id="cr_123",
            variant_a_id="var_a",
            variant_b_id="var_b"
        )

        assert "variant_a" in result
        assert "variant_b" in result
        assert "winner" in result
        assert "improvement_percentage" in result
        assert "recommendation" in result
        assert "insights" in result

    def test_ab_test_winner_determination(self, content_studio):
        """Test: Détermination du gagnant"""
        result = content_studio.analyze_creative_performance(
            "cr_1", "var_a", "var_b"
        )

        # Le gagnant devrait être A ou B
        assert result["winner"] in ["A", "B"]

    def test_ab_test_metrics(self, content_studio):
        """Test: Métriques A/B test"""
        result = content_studio.analyze_creative_performance(
            "cr_1", "var_a", "var_b"
        )

        # Les deux variantes doivent avoir des métriques
        for variant in ["variant_a", "variant_b"]:
            metrics = result[variant]["metrics"]
            assert "impressions" in metrics
            assert "clicks" in metrics
            assert "conversions" in metrics
            assert "ctr" in metrics

    def test_ab_test_insights(self, content_studio):
        """Test: Insights A/B test"""
        result = content_studio.analyze_creative_performance(
            "cr_1", "var_a", "var_b"
        )

        assert len(result["insights"]) > 0
        assert all(isinstance(insight, str) for insight in result["insights"])


# ========== Tests d'intégration ==========

class TestContentStudioIntegration:
    """Tests d'intégration Content Studio"""

    @pytest.mark.asyncio
    async def test_complete_content_creation_workflow(self):
        """Test: Workflow complet de création"""
        service = ContentStudioService()
        service.demo_mode = True

        # 1. Générer une image
        image_result = await service.generate_image_ai(
            prompt="Product image",
            style="realistic"
        )
        assert image_result["success"] is True

        # 2. Générer un QR code
        qr_code = service.generate_qr_code(
            url="https://shareyoursales.com/aff/123"
        )
        assert qr_code is not None

        # 3. Planifier un post
        schedule_result = service.schedule_post(
            content={
                "text": "Check out this product!",
                "image_url": image_result["image_url"]
            },
            platforms=[SocialPlatform.INSTAGRAM],
            scheduled_time=datetime.now() + timedelta(hours=1),
            user_id="user_123"
        )
        assert schedule_result["success"] is True

    def test_template_to_post_workflow(self):
        """Test: Template → Post planifié"""
        service = ContentStudioService()

        # 1. Récupérer un template
        templates = service.get_templates(
            category=TemplateCategory.PRODUCT_SHOWCASE
        )
        assert len(templates) > 0

        template = templates[0]

        # 2. Personnaliser (simulé)
        # En vrai, il y aurait un endpoint de rendu

        # 3. Planifier
        result = service.schedule_post(
            content={
                "text": "Product post",
                "template_id": template["id"]
            },
            platforms=[SocialPlatform.INSTAGRAM],
            scheduled_time=datetime.now() + timedelta(days=1),
            user_id="user_123"
        )

        assert result["success"] is True


# ========== Tests de performance ==========

class TestContentStudioPerformance:
    """Tests de performance"""

    def test_template_loading_performance(self):
        """Test: Chargement rapide des templates"""
        service = ContentStudioService()

        import time
        start = time.time()

        # Charger tous les templates
        templates = service.get_templates()

        elapsed = time.time() - start

        # Devrait être très rapide (< 10ms)
        assert elapsed < 0.01
        assert len(templates) > 0

    def test_qr_code_generation_performance(self):
        """Test: Génération QR rapide"""
        service = ContentStudioService()

        import time
        start = time.time()

        # Générer 10 QR codes
        for i in range(10):
            service.generate_qr_code(
                url=f"https://example.com/{i}"
            )

        elapsed = time.time() - start

        # 10 QR codes en moins d'1 seconde
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_concurrent_image_generation(self):
        """Test: Générations IA concurrentes"""
        service = ContentStudioService()
        service.demo_mode = True

        import asyncio
        import time

        start = time.time()

        # Générer 5 images en parallèle
        tasks = [
            service.generate_image_ai(f"Product {i}", "realistic")
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        elapsed = time.time() - start

        # Toutes devraient réussir
        assert all(r["success"] for r in results)

        # En mode demo, devrait être très rapide
        assert elapsed < 1.0
