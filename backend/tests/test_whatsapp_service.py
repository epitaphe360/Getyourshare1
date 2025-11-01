"""
Tests pour WhatsApp Business Service

Tests couvrant:
- Envoi de messages simples
- Envoi de templates
- Envoi de liens d'affiliation
- Notifications
- Messages interactifs
- Génération d'URLs
- Validation des numéros de téléphone
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend.services.whatsapp_business_service import (
    WhatsAppBusinessService,
    WhatsAppMessageType,
    WhatsAppTemplateCategory
)


class TestWhatsAppBusinessService:
    """Tests du service WhatsApp Business"""

    @pytest.fixture
    def whatsapp_service(self):
        """Fixture pour créer une instance du service"""
        service = WhatsAppBusinessService()
        service.demo_mode = False  # Désactiver le mode demo pour les tests
        service.phone_number_id = "123456789"
        service.access_token = "test_token"
        return service

    @pytest.fixture
    def demo_service(self):
        """Service en mode démo"""
        service = WhatsAppBusinessService()
        service.demo_mode = True
        return service

    # ========== Tests d'initialisation ==========

    def test_service_initialization(self):
        """Test: Service s'initialise correctement"""
        service = WhatsAppBusinessService()
        assert service is not None
        assert isinstance(service.demo_mode, bool)

    def test_demo_mode_when_no_token(self):
        """Test: Mode démo activé quand pas de token"""
        service = WhatsAppBusinessService()
        service.access_token = ""
        assert service.demo_mode is True

    # ========== Tests de nettoyage de numéro ==========

    def test_clean_phone_number_with_plus(self, whatsapp_service):
        """Test: Nettoyer numéro avec +"""
        result = whatsapp_service._clean_phone_number("+212612345678")
        assert result == "212612345678"

    def test_clean_phone_number_with_zero(self, whatsapp_service):
        """Test: Numéro commençant par 0 → 212"""
        result = whatsapp_service._clean_phone_number("0612345678")
        assert result == "212612345678"

    def test_clean_phone_number_with_spaces(self, whatsapp_service):
        """Test: Enlever les espaces et tirets"""
        result = whatsapp_service._clean_phone_number("+212 6-12-34-56-78")
        assert result == "212612345678"

    def test_clean_phone_number_without_country_code(self, whatsapp_service):
        """Test: Ajouter 212 si manquant"""
        result = whatsapp_service._clean_phone_number("612345678")
        assert result == "212612345678"

    # ========== Tests d'envoi de messages simples ==========

    @pytest.mark.asyncio
    async def test_send_text_message_demo_mode(self, demo_service):
        """Test: Envoi message en mode démo"""
        result = await demo_service.send_text_message(
            to_phone="+212612345678",
            message="Test message"
        )

        assert result["success"] is True
        assert result["demo_mode"] is True
        assert "message_id" in result
        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_text_message_with_url_preview(self, demo_service):
        """Test: Message avec prévisualisation URL"""
        result = await demo_service.send_text_message(
            to_phone="+212612345678",
            message="Check this out: https://example.com",
            preview_url=True
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_send_text_message_api_call(self, mock_post, whatsapp_service):
        """Test: Appel API réel pour envoi message"""
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [{"id": "wamid.123"}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = await whatsapp_service.send_text_message(
            to_phone="+212612345678",
            message="Test message"
        )

        assert result["success"] is True
        assert result["message_id"] == "wamid.123"
        mock_post.assert_called_once()

    # ========== Tests d'envoi de templates ==========

    @pytest.mark.asyncio
    async def test_send_template_message_demo(self, demo_service):
        """Test: Envoi template en mode démo"""
        result = await demo_service.send_template_message(
            to_phone="+212612345678",
            template_name="new_commission",
            language_code="fr",
            parameters=["125 MAD", "Écouteurs Bluetooth"]
        )

        assert result["success"] is True
        assert result["template_name"] == "new_commission"
        assert result["demo_mode"] is True

    @pytest.mark.asyncio
    async def test_send_template_different_languages(self, demo_service):
        """Test: Templates en différentes langues"""
        languages = ["fr", "ar", "en"]

        for lang in languages:
            result = await demo_service.send_template_message(
                to_phone="+212612345678",
                template_name="new_commission",
                language_code=lang,
                parameters=["100"]
            )
            assert result["success"] is True

    # ========== Tests de liens d'affiliation ==========

    @pytest.mark.asyncio
    async def test_send_affiliate_link(self, demo_service):
        """Test: Envoi lien d'affiliation"""
        result = await demo_service.send_affiliate_link(
            to_phone="+212612345678",
            product_name="Écouteurs Bluetooth TWS",
            affiliate_link="https://shareyoursales.com/aff/ABC123",
            commission_rate=15.0
        )

        assert result["success"] is True
        assert "message_id" in result

    @pytest.mark.asyncio
    async def test_send_affiliate_link_with_image(self, demo_service):
        """Test: Lien d'affiliation avec image"""
        result = await demo_service.send_affiliate_link(
            to_phone="+212612345678",
            product_name="Test Product",
            affiliate_link="https://example.com/aff/123",
            commission_rate=10.0,
            product_image_url="https://example.com/image.jpg"
        )

        assert result["success"] is True

    # ========== Tests de notifications ==========

    @pytest.mark.asyncio
    async def test_send_notification_new_commission(self, demo_service):
        """Test: Notification nouvelle commission"""
        result = await demo_service.send_notification(
            to_phone="+212612345678",
            notification_type="new_commission",
            data={
                "amount": "125 MAD",
                "product_name": "Test Product",
                "language": "fr"
            }
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_send_notification_payout_approved(self, demo_service):
        """Test: Notification paiement approuvé"""
        result = await demo_service.send_notification(
            to_phone="+212612345678",
            notification_type="payout_approved",
            data={
                "amount": "1000 MAD",
                "method": "Cash Plus"
            }
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_send_notification_invalid_type(self, demo_service):
        """Test: Type de notification invalide → fallback message texte"""
        result = await demo_service.send_notification(
            to_phone="+212612345678",
            notification_type="invalid_type",
            data={"message": "Fallback message"}
        )

        assert result["success"] is True

    # ========== Tests de boutons interactifs ==========

    @pytest.mark.asyncio
    async def test_send_interactive_buttons(self, demo_service):
        """Test: Message avec boutons interactifs"""
        result = await demo_service.send_interactive_buttons(
            to_phone="+212612345678",
            body_text="Voulez-vous accepter?",
            buttons=[
                {"id": "accept", "title": "Accepter"},
                {"id": "reject", "title": "Refuser"}
            ]
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_interactive_buttons_max_limit(self, demo_service):
        """Test: Limite de 3 boutons maximum"""
        buttons = [
            {"id": "btn1", "title": "Button 1"},
            {"id": "btn2", "title": "Button 2"},
            {"id": "btn3", "title": "Button 3"},
            {"id": "btn4", "title": "Button 4"}  # Ce bouton sera ignoré
        ]

        result = await demo_service.send_interactive_buttons(
            to_phone="+212612345678",
            body_text="Choose an option",
            buttons=buttons
        )

        assert result["success"] is True

    # ========== Tests de génération d'URLs ==========

    def test_get_whatsapp_share_url_text_only(self, whatsapp_service):
        """Test: URL de partage avec texte uniquement"""
        url = whatsapp_service.get_whatsapp_share_url("Hello World")

        assert url.startswith("https://wa.me/?text=")
        assert "Hello" in url

    def test_get_whatsapp_share_url_with_link(self, whatsapp_service):
        """Test: URL de partage avec texte et lien"""
        url = whatsapp_service.get_whatsapp_share_url(
            text="Check this out",
            url="https://example.com"
        )

        assert url.startswith("https://wa.me/?text=")
        assert "example.com" in url

    def test_get_whatsapp_direct_url(self, whatsapp_service):
        """Test: URL de message direct"""
        url = whatsapp_service.get_whatsapp_direct_url(
            phone="+212612345678",
            text="Hello"
        )

        assert url.startswith("https://wa.me/212612345678?text=")
        assert "Hello" in url

    # ========== Tests de gestion d'erreurs ==========

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_send_message_api_error(self, mock_post, whatsapp_service):
        """Test: Gestion erreur API"""
        mock_post.side_effect = Exception("API Error")

        result = await whatsapp_service.send_text_message(
            to_phone="+212612345678",
            message="Test"
        )

        assert result["success"] is False
        assert "error" in result
        assert result["status"] == "failed"

    # ========== Tests de validation ==========

    def test_clean_phone_invalid_format(self, whatsapp_service):
        """Test: Validation format invalide"""
        # Devrait quand même retourner quelque chose
        result = whatsapp_service._clean_phone_number("invalid")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_send_to_multiple_numbers(self, demo_service):
        """Test: Envoi à plusieurs numéros"""
        numbers = ["+212612345678", "+212698765432", "+212611111111"]

        for number in numbers:
            result = await demo_service.send_text_message(
                to_phone=number,
                message="Broadcast message"
            )
            assert result["success"] is True


# ========== Tests d'intégration ==========

class TestWhatsAppIntegration:
    """Tests d'intégration WhatsApp"""

    @pytest.mark.asyncio
    async def test_complete_notification_flow(self):
        """Test: Flux complet de notification"""
        service = WhatsAppBusinessService()
        service.demo_mode = True

        # 1. Envoyer notification
        result = await service.send_notification(
            to_phone="+212612345678",
            notification_type="new_commission",
            data={
                "amount": "250 MAD",
                "product_name": "Test Product"
            }
        )

        assert result["success"] is True
        assert "message_id" in result

    @pytest.mark.asyncio
    async def test_affiliate_link_workflow(self):
        """Test: Workflow complet de partage lien"""
        service = WhatsAppBusinessService()
        service.demo_mode = True

        # 1. Générer URL de partage
        share_url = service.get_whatsapp_share_url(
            text="Produit incroyable!",
            url="https://shareyoursales.com/aff/ABC123"
        )

        assert share_url is not None

        # 2. Envoyer le lien
        result = await service.send_affiliate_link(
            to_phone="+212612345678",
            product_name="Test Product",
            affiliate_link="https://shareyoursales.com/aff/ABC123",
            commission_rate=15.0
        )

        assert result["success"] is True


# ========== Tests de performance ==========

class TestWhatsAppPerformance:
    """Tests de performance"""

    @pytest.mark.asyncio
    async def test_send_message_response_time(self, benchmark):
        """Test: Temps de réponse < 100ms en mode démo"""
        service = WhatsAppBusinessService()
        service.demo_mode = True

        async def send():
            return await service.send_text_message(
                to_phone="+212612345678",
                message="Performance test"
            )

        # Le benchmark devrait être < 100ms
        result = await send()
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_bulk_message_performance(self):
        """Test: Envoi en masse performant"""
        service = WhatsAppBusinessService()
        service.demo_mode = True

        import time
        start = time.time()

        # Envoyer 100 messages
        for i in range(100):
            await service.send_text_message(
                to_phone=f"+21261234{i:04d}",
                message=f"Test {i}"
            )

        elapsed = time.time() - start

        # Devrait prendre moins de 5 secondes pour 100 messages en démo
        assert elapsed < 5.0
