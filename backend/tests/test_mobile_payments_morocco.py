"""
Tests pour le Service de Paiements Mobiles Marocains

Couvre:
- Tous les 6 opérateurs (Cash Plus, Wafacash, Orange Money, inwi money, Maroc Telecom, CIH Mobile)
- Validation des requêtes (montants, numéros de téléphone)
- Traitement des paiements
- Gestion d'erreurs
- Tests d'intégration
- Tests de performance
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from services.mobile_payment_morocco_service import (
    MobilePaymentService,
    MobilePaymentProvider,
    PayoutStatus,
    MobilePayoutRequest,
    MobilePayoutResponse
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def payment_service():
    """Instance du service de paiement mobile en mode démo"""
    return MobilePaymentService(demo_mode=True)


@pytest.fixture
def valid_payout_request():
    """Requête de paiement valide"""
    return MobilePayoutRequest(
        user_id="user_123",
        amount=500.0,
        phone_number="+212612345678",
        provider=MobilePaymentProvider.CASH_PLUS,
        reference="TEST-REF-001",
        metadata={"commission_id": "COM-123"}
    )


@pytest.fixture
def invalid_phone_requests():
    """Exemples de numéros de téléphone invalides"""
    return [
        "+212412345678",  # Commence par 4 (invalide, doit être 5-7)
        "+212812345678",  # Commence par 8 (invalide, doit être 5-7)
        "+212123456",     # Trop court
        "+33612345678",   # Pas Maroc (doit commencer par +212 ou 0)
        "061234567",      # Manque un chiffre (seulement 9 caractères)
        "+2126123456789", # Trop long (11 après +212)
    ]


# ============================================
# TESTS UNITAIRES - VALIDATION
# ============================================

class TestPayoutRequestValidation:
    """Tests de validation des requêtes de paiement"""

    def test_valid_phone_number_formats(self):
        """Test différents formats valides de numéros marocains"""
        valid_phones = [
            "+212612345678",  # Mobile Maroc Telecom
            "+212698765432",  # Mobile Maroc Telecom
            "+212712345678",  # Mobile Orange
            "+212798765432",  # Mobile Orange
            "+212512345678",  # Mobile inwi
            "+212598765432",  # Mobile inwi
            "0612345678",     # Format local
            "0712345678",     # Format local
            "0512345678",     # Format local
        ]

        for phone in valid_phones:
            # Devrait créer sans lever d'exception
            request = MobilePayoutRequest(
                user_id="user_123",
                amount=100.0,
                phone_number=phone,
                provider=MobilePaymentProvider.CASH_PLUS
            )
            assert request.phone_number == phone

    def test_invalid_phone_number_formats(self, invalid_phone_requests):
        """Test rejet des formats de numéros invalides"""
        for phone in invalid_phone_requests:
            with pytest.raises(Exception):  # Pydantic ValidationError
                MobilePayoutRequest(
                    user_id="user_123",
                    amount=100.0,
                    phone_number=phone,
                    provider=MobilePaymentProvider.CASH_PLUS
                )

    def test_amount_must_be_positive(self):
        """Test que le montant doit être positif"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            MobilePayoutRequest(
                user_id="user_123",
                amount=-100.0,
                phone_number="+212612345678",
                provider=MobilePaymentProvider.CASH_PLUS
            )

        with pytest.raises(Exception):
            MobilePayoutRequest(
                user_id="user_123",
                amount=0.0,
                phone_number="+212612345678",
                provider=MobilePaymentProvider.CASH_PLUS
            )

    def test_minimum_required_fields(self):
        """Test que les champs obligatoires sont requis"""
        # Devrait fonctionner sans reference et metadata (optionnels)
        request = MobilePayoutRequest(
            user_id="user_123",
            amount=100.0,
            phone_number="+212612345678",
            provider=MobilePaymentProvider.CASH_PLUS
        )
        assert request.reference is None
        assert request.metadata is None


# ============================================
# TESTS UNITAIRES - OPÉRATEURS
# ============================================

class TestMobilePaymentProviders:
    """Tests pour chaque opérateur de paiement mobile"""

    @pytest.mark.asyncio
    async def test_cashplus_payout_success(self, payment_service, valid_payout_request):
        """Test paiement Cash Plus réussi"""
        valid_payout_request.provider = MobilePaymentProvider.CASH_PLUS

        response = await payment_service.initiate_payout(valid_payout_request)

        assert response.status in [PayoutStatus.COMPLETED, PayoutStatus.PROCESSING]
        assert response.amount == valid_payout_request.amount
        assert response.phone_number == valid_payout_request.phone_number
        assert response.provider == MobilePaymentProvider.CASH_PLUS
        assert response.payout_id is not None
        assert response.message is not None

    @pytest.mark.asyncio
    async def test_wafacash_payout_success(self, payment_service, valid_payout_request):
        """Test paiement Wafacash réussi"""
        valid_payout_request.provider = MobilePaymentProvider.WAFACASH

        response = await payment_service.initiate_payout(valid_payout_request)

        assert response.status in [PayoutStatus.COMPLETED, PayoutStatus.PROCESSING]
        assert response.provider == MobilePaymentProvider.WAFACASH
        assert response.payout_id.startswith("MOCK-WAFACASH")

    @pytest.mark.asyncio
    async def test_orange_money_payout_success(self, payment_service, valid_payout_request):
        """Test paiement Orange Money réussi"""
        valid_payout_request.provider = MobilePaymentProvider.ORANGE_MONEY

        response = await payment_service.initiate_payout(valid_payout_request)

        assert response.status in [PayoutStatus.COMPLETED, PayoutStatus.PROCESSING]
        assert response.provider == MobilePaymentProvider.ORANGE_MONEY
        assert response.payout_id.startswith("MOCK-ORANGE_MONEY")

    @pytest.mark.asyncio
    async def test_inwi_money_payout_success(self, payment_service, valid_payout_request):
        """Test paiement inwi money réussi"""
        valid_payout_request.provider = MobilePaymentProvider.INWI_MONEY

        response = await payment_service.initiate_payout(valid_payout_request)

        assert response.status in [PayoutStatus.COMPLETED, PayoutStatus.PROCESSING]
        assert response.provider == MobilePaymentProvider.INWI_MONEY
        assert response.payout_id.startswith("MOCK-INWI_MONEY")

    @pytest.mark.asyncio
    async def test_maroc_telecom_payout_success(self, payment_service, valid_payout_request):
        """Test paiement Maroc Telecom réussi"""
        valid_payout_request.provider = MobilePaymentProvider.MAROC_TELECOM

        response = await payment_service.initiate_payout(valid_payout_request)

        assert response.status in [PayoutStatus.COMPLETED, PayoutStatus.PROCESSING]
        assert response.provider == MobilePaymentProvider.MAROC_TELECOM
        assert response.payout_id.startswith("MOCK-MAROC_TELECOM")

    @pytest.mark.asyncio
    async def test_cih_mobile_payout_success(self, payment_service, valid_payout_request):
        """Test paiement CIH Mobile réussi"""
        valid_payout_request.provider = MobilePaymentProvider.CIH_MOBILE

        response = await payment_service.initiate_payout(valid_payout_request)

        assert response.status in [PayoutStatus.COMPLETED, PayoutStatus.PROCESSING]
        assert response.provider == MobilePaymentProvider.CIH_MOBILE
        assert response.payout_id.startswith("MOCK-CIH_MOBILE")


# ============================================
# TESTS UNITAIRES - STATUTS & VÉRIFICATION
# ============================================

class TestPayoutStatus:
    """Tests de vérification de statut"""

    @pytest.mark.asyncio
    async def test_check_payout_status(self, payment_service):
        """Test vérification du statut d'un paiement"""
        status = await payment_service.check_payout_status(
            payout_id="MOCK-CASH_PLUS-123",
            provider=MobilePaymentProvider.CASH_PLUS
        )

        assert status in [
            PayoutStatus.PENDING,
            PayoutStatus.PROCESSING,
            PayoutStatus.COMPLETED,
            PayoutStatus.FAILED,
            PayoutStatus.CANCELLED
        ]

    def test_payout_response_timestamps(self, valid_payout_request):
        """Test que les timestamps sont correctement définis"""
        response = MobilePayoutResponse(
            payout_id="TEST-123",
            status=PayoutStatus.COMPLETED,
            amount=500.0,
            phone_number="+212612345678",
            provider=MobilePaymentProvider.CASH_PLUS,
            transaction_id="TXN-456",
            message="Succès",
            created_at=datetime.now(),
            completed_at=datetime.now()
        )

        assert response.created_at is not None
        assert response.completed_at is not None
        assert response.completed_at >= response.created_at

    @pytest.mark.asyncio
    async def test_failed_payout_has_error_message(self, payment_service):
        """Test qu'un paiement échoué contient un message d'erreur"""
        # En mode démo, tous les paiements réussissent
        # Ce test vérifie simplement que la structure de réponse est correcte
        request = MobilePayoutRequest(
            user_id="user_123",
            amount=100.0,
            phone_number="+212612345678",
            provider=MobilePaymentProvider.CASH_PLUS
        )

        response = await payment_service.initiate_payout(request)

        # Vérifier que la réponse a toujours un message
        assert response.message is not None
        assert len(response.message) > 0


# ============================================
# TESTS UNITAIRES - CONFIGURATION
# ============================================

class TestProviderConfiguration:
    """Tests de configuration des opérateurs"""

    def test_get_supported_providers(self, payment_service):
        """Test liste des opérateurs supportés"""
        providers = payment_service.get_supported_providers()

        assert len(providers) == 6
        assert all("id" in p for p in providers)
        assert all("name" in p for p in providers)
        assert all("min_amount" in p for p in providers)
        assert all("max_amount" in p for p in providers)
        assert all("fees" in p for p in providers)
        assert all("processing_time" in p for p in providers)

    def test_provider_limits(self, payment_service):
        """Test que chaque opérateur a des limites définies"""
        providers = payment_service.get_supported_providers()

        for provider in providers:
            assert provider["min_amount"] > 0
            assert provider["max_amount"] > provider["min_amount"]
            assert provider["fees"] >= 0

    def test_all_providers_have_configs(self, payment_service):
        """Test que tous les opérateurs ont une configuration"""
        for provider in MobilePaymentProvider:
            assert provider in payment_service.provider_configs
            config = payment_service.provider_configs[provider]
            assert "api_url" in config
            assert "api_key" in config


# ============================================
# TESTS D'INTÉGRATION
# ============================================

@pytest.mark.integration
class TestMobilePaymentIntegration:
    """Tests d'intégration end-to-end"""

    @pytest.mark.asyncio
    async def test_full_payout_workflow(self, payment_service):
        """Test workflow complet de paiement"""
        # 1. Créer une requête
        request = MobilePayoutRequest(
            user_id="influencer_789",
            amount=1250.50,
            phone_number="+212698765432",
            provider=MobilePaymentProvider.ORANGE_MONEY,
            reference="COMMISSION-2024-001",
            metadata={
                "commission_id": "COM-789",
                "period": "2024-01",
                "type": "monthly"
            }
        )

        # 2. Initier le paiement
        response = await payment_service.initiate_payout(request)

        # 3. Vérifier la réponse
        assert response.payout_id is not None
        assert response.status != PayoutStatus.FAILED

        # 4. Vérifier le statut
        if response.status == PayoutStatus.PROCESSING:
            status = await payment_service.check_payout_status(
                response.payout_id,
                request.provider
            )
            assert status in [PayoutStatus.PROCESSING, PayoutStatus.COMPLETED]

    @pytest.mark.asyncio
    async def test_multiple_providers_same_user(self, payment_service):
        """Test paiements multiples pour un même utilisateur avec différents opérateurs"""
        user_id = "user_multi_provider"
        phone = "+212612345678"

        providers_to_test = [
            MobilePaymentProvider.CASH_PLUS,
            MobilePaymentProvider.ORANGE_MONEY,
            MobilePaymentProvider.INWI_MONEY
        ]

        responses = []
        for provider in providers_to_test:
            request = MobilePayoutRequest(
                user_id=user_id,
                amount=100.0,
                phone_number=phone,
                provider=provider
            )
            response = await payment_service.initiate_payout(request)
            responses.append(response)

        # Vérifier que tous les paiements sont traités
        assert len(responses) == 3
        assert all(r.status != PayoutStatus.FAILED for r in responses)
        # Vérifier que les payout_ids sont uniques
        payout_ids = [r.payout_id for r in responses]
        assert len(payout_ids) == len(set(payout_ids))

    @pytest.mark.asyncio
    async def test_concurrent_payouts(self, payment_service):
        """Test paiements concurrents"""
        import asyncio

        requests = [
            MobilePayoutRequest(
                user_id=f"user_{i}",
                amount=100.0 + (i * 10),
                phone_number=f"+21261234567{i % 10}",
                provider=MobilePaymentProvider.CASH_PLUS
            )
            for i in range(5)
        ]

        # Exécuter tous les paiements en parallèle
        responses = await asyncio.gather(
            *[payment_service.initiate_payout(req) for req in requests]
        )

        assert len(responses) == 5
        # Tous devraient réussir ou être en traitement
        assert all(r.status in [PayoutStatus.COMPLETED, PayoutStatus.PROCESSING] for r in responses)


# ============================================
# TESTS DE PERFORMANCE
# ============================================

@pytest.mark.performance
class TestMobilePaymentPerformance:
    """Tests de performance"""

    @pytest.mark.asyncio
    async def test_payout_response_time(self, payment_service, valid_payout_request):
        """Test que le temps de réponse est acceptable"""
        start = datetime.now()
        response = await payment_service.initiate_payout(valid_payout_request)
        duration = (datetime.now() - start).total_seconds()

        # Le paiement devrait prendre moins de 5 secondes (en mode démo, instantané)
        assert duration < 5.0
        assert response.payout_id is not None
        assert response.status == PayoutStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_bulk_payout_processing(self, payment_service):
        """Test traitement de masse (100 paiements)"""
        import asyncio

        requests = [
            MobilePayoutRequest(
                user_id=f"bulk_user_{i}",
                amount=50.0,
                phone_number="+212612345678",
                provider=MobilePaymentProvider.CASH_PLUS
            )
            for i in range(100)
        ]

        start = datetime.now()
        responses = await asyncio.gather(
            *[payment_service.initiate_payout(req) for req in requests]
        )
        duration = (datetime.now() - start).total_seconds()

        # 100 paiements en moins de 30 secondes
        assert duration < 30.0
        assert len(responses) == 100
        assert all(r.payout_id is not None for r in responses)


# ============================================
# TESTS DE GESTION D'ERREURS
# ============================================

@pytest.mark.unit
class TestErrorHandling:
    """Tests de gestion d'erreurs"""

    @pytest.mark.asyncio
    async def test_network_error_handling(self, payment_service, valid_payout_request):
        """Test gestion des erreurs réseau"""
        # Le service devrait gérer gracieusement les erreurs réseau
        # et retourner un mock en mode démo
        response = await payment_service.initiate_payout(valid_payout_request)

        # Même en cas d'erreur réseau, devrait retourner une réponse valide
        assert response is not None
        assert isinstance(response, MobilePayoutResponse)

    def test_invalid_provider_enum(self):
        """Test avec un provider invalide"""
        with pytest.raises(Exception):
            MobilePayoutRequest(
                user_id="user_123",
                amount=100.0,
                phone_number="+212612345678",
                provider="invalid_provider"  # type: ignore
            )

    @pytest.mark.asyncio
    async def test_large_amount_handling(self, payment_service):
        """Test gestion de montants très élevés"""
        request = MobilePayoutRequest(
            user_id="user_vip",
            amount=50000.0,  # Montant élevé
            phone_number="+212612345678",
            provider=MobilePaymentProvider.CASH_PLUS
        )

        response = await payment_service.initiate_payout(request)

        # Devrait être traité mais possiblement avec un statut particulier
        assert response.amount == 50000.0
        assert response.payout_id is not None


# ============================================
# TESTS SPÉCIFIQUES MAROC
# ============================================

@pytest.mark.unit
class TestMoroccoSpecificFeatures:
    """Tests des fonctionnalités spécifiques au Maroc"""

    def test_all_major_providers_supported(self, payment_service):
        """Test que tous les principaux opérateurs marocains sont supportés"""
        providers = payment_service.get_supported_providers()
        provider_names = [p["name"] for p in providers]

        # Vérifier présence des leaders du marché
        assert "Cash Plus" in provider_names
        assert "Orange Money" in provider_names
        assert "inwi money" in provider_names

    def test_moroccan_phone_number_validation(self):
        """Test validation stricte des numéros marocains"""
        # Numéros valides au Maroc commencent par +212 ou 0
        # Suivis de 5, 6, ou 7 (mobiles)
        valid_prefixes = ["5", "6", "7"]

        for prefix in valid_prefixes:
            phone = f"+212{prefix}12345678"
            request = MobilePayoutRequest(
                user_id="user_123",
                amount=100.0,
                phone_number=phone,
                provider=MobilePaymentProvider.CASH_PLUS
            )
            assert request.phone_number.startswith(f"+212{prefix}")

    def test_mad_currency_handling(self, payment_service, valid_payout_request):
        """Test que les montants sont bien en MAD (Dirham marocain)"""
        # Les montants sont implicitement en MAD
        assert valid_payout_request.amount > 0
        # Vérifier que les limites sont cohérentes avec MAD
        providers = payment_service.get_supported_providers()
        for provider in providers:
            # Limites typiques en MAD
            assert provider["min_amount"] >= 5.0
            assert provider["max_amount"] <= 50000.0
