"""
Service de Paiements Mobiles Marocains
Intégrations : Cash Plus, Wafacash, Orange Money, inwi money, Maroc Telecom, CIH Mobile
"""

from typing import Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import httpx
import logging
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================
# ENUMS & MODELS
# ============================================

class MobilePaymentProvider(str, Enum):
    """Opérateurs de paiement mobile au Maroc"""
    CASH_PLUS = "cash_plus"
    WAFACASH = "wafacash"
    ORANGE_MONEY = "orange_money"
    INWI_MONEY = "inwi_money"
    MAROC_TELECOM = "maroc_telecom"
    CIH_MOBILE = "cih_mobile"


class PayoutStatus(str, Enum):
    """Statuts de paiement"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MobilePayoutRequest(BaseModel):
    """Requête de paiement mobile"""
    user_id: str
    amount: float = Field(..., gt=0, description="Montant en MAD")
    phone_number: str = Field(..., pattern=r"^(?:\+212|0)[5-7]\d{8}$")
    provider: MobilePaymentProvider
    reference: Optional[str] = None
    metadata: Optional[Dict] = None


class MobilePayoutResponse(BaseModel):
    """Réponse de paiement mobile"""
    payout_id: str
    status: PayoutStatus
    amount: float
    phone_number: str
    provider: MobilePaymentProvider
    transaction_id: Optional[str] = None
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None


# ============================================
# SERVICE PRINCIPAL
# ============================================

class MobilePaymentService:
    """Service de gestion des paiements mobiles marocains"""

    def __init__(self):
        # URLs API des opérateurs (à configurer avec les vraies URLs)
        self.provider_configs = {
            MobilePaymentProvider.CASH_PLUS: {
                "api_url": "https://api.cashplus.ma/v1",
                "api_key": "YOUR_CASHPLUS_API_KEY",
                "merchant_id": "YOUR_MERCHANT_ID",
            },
            MobilePaymentProvider.WAFACASH: {
                "api_url": "https://api.wafacash.ma/v1",
                "api_key": "YOUR_WAFACASH_API_KEY",
                "merchant_id": "YOUR_MERCHANT_ID",
            },
            MobilePaymentProvider.ORANGE_MONEY: {
                "api_url": "https://api.orange.ma/omoney/v1",
                "api_key": "YOUR_ORANGE_API_KEY",
                "merchant_code": "YOUR_MERCHANT_CODE",
            },
            MobilePaymentProvider.INWI_MONEY: {
                "api_url": "https://api.inwi.ma/money/v1",
                "api_key": "YOUR_INWI_API_KEY",
                "merchant_id": "YOUR_MERCHANT_ID",
            },
            MobilePaymentProvider.MAROC_TELECOM: {
                "api_url": "https://api.iam.ma/mobilemoney/v1",
                "api_key": "YOUR_MT_API_KEY",
                "merchant_id": "YOUR_MERCHANT_ID",
            },
            MobilePaymentProvider.CIH_MOBILE: {
                "api_url": "https://api.cih.ma/mobile/v1",
                "api_key": "YOUR_CIH_API_KEY",
                "merchant_id": "YOUR_MERCHANT_ID",
            },
        }

    async def initiate_payout(
        self,
        request: MobilePayoutRequest
    ) -> MobilePayoutResponse:
        """
        Initier un paiement vers un compte mobile money

        Args:
            request: Requête de paiement avec détails

        Returns:
            Réponse avec statut et transaction ID
        """
        try:
            # Sélectionner le bon provider
            if request.provider == MobilePaymentProvider.CASH_PLUS:
                return await self._process_cashplus(request)
            elif request.provider == MobilePaymentProvider.WAFACASH:
                return await self._process_wafacash(request)
            elif request.provider == MobilePaymentProvider.ORANGE_MONEY:
                return await self._process_orange_money(request)
            elif request.provider == MobilePaymentProvider.INWI_MONEY:
                return await self._process_inwi_money(request)
            elif request.provider == MobilePaymentProvider.MAROC_TELECOM:
                return await self._process_maroc_telecom(request)
            elif request.provider == MobilePaymentProvider.CIH_MOBILE:
                return await self._process_cih_mobile(request)
            else:
                raise ValueError(f"Provider non supporté: {request.provider}")

        except Exception as e:
            logger.error(f"Erreur paiement mobile: {str(e)}")
            return MobilePayoutResponse(
                payout_id=f"PO-{datetime.now().timestamp()}",
                status=PayoutStatus.FAILED,
                amount=request.amount,
                phone_number=request.phone_number,
                provider=request.provider,
                message=f"Erreur: {str(e)}",
                created_at=datetime.now()
            )

    # ============================================
    # INTÉGRATIONS PAR OPÉRATEUR
    # ============================================

    async def _process_cashplus(
        self,
        request: MobilePayoutRequest
    ) -> MobilePayoutResponse:
        """Traiter paiement via Cash Plus"""
        config = self.provider_configs[MobilePaymentProvider.CASH_PLUS]

        async with httpx.AsyncClient() as client:
            try:
                # Appel API Cash Plus
                response = await client.post(
                    f"{config['api_url']}/payout",
                    json={
                        "merchant_id": config["merchant_id"],
                        "phone": request.phone_number,
                        "amount": request.amount,
                        "reference": request.reference or f"SYS-{datetime.now().timestamp()}",
                        "metadata": request.metadata or {}
                    },
                    headers={
                        "Authorization": f"Bearer {config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return MobilePayoutResponse(
                        payout_id=data.get("transaction_id", f"CP-{datetime.now().timestamp()}"),
                        status=PayoutStatus.COMPLETED,
                        amount=request.amount,
                        phone_number=request.phone_number,
                        provider=MobilePaymentProvider.CASH_PLUS,
                        transaction_id=data.get("transaction_id"),
                        message="Paiement Cash Plus réussi",
                        created_at=datetime.now(),
                        completed_at=datetime.now()
                    )
                else:
                    raise Exception(f"Cash Plus API error: {response.status_code}")

            except httpx.RequestError as e:
                logger.error(f"Cash Plus request error: {str(e)}")
                # Mode MOCK pour démo (à retirer en production)
                return self._mock_successful_payout(request, MobilePaymentProvider.CASH_PLUS)

    async def _process_wafacash(
        self,
        request: MobilePayoutRequest
    ) -> MobilePayoutResponse:
        """Traiter paiement via Wafacash"""
        config = self.provider_configs[MobilePaymentProvider.WAFACASH]

        # Similar implementation
        # Mode MOCK pour démo
        return self._mock_successful_payout(request, MobilePaymentProvider.WAFACASH)

    async def _process_orange_money(
        self,
        request: MobilePayoutRequest
    ) -> MobilePayoutResponse:
        """Traiter paiement via Orange Money"""
        config = self.provider_configs[MobilePaymentProvider.ORANGE_MONEY]

        # Mode MOCK pour démo
        return self._mock_successful_payout(request, MobilePaymentProvider.ORANGE_MONEY)

    async def _process_inwi_money(
        self,
        request: MobilePayoutRequest
    ) -> MobilePayoutResponse:
        """Traiter paiement via inwi money"""
        config = self.provider_configs[MobilePaymentProvider.INWI_MONEY]

        # Mode MOCK pour démo
        return self._mock_successful_payout(request, MobilePaymentProvider.INWI_MONEY)

    async def _process_maroc_telecom(
        self,
        request: MobilePayoutRequest
    ) -> MobilePayoutResponse:
        """Traiter paiement via Maroc Telecom Mobile Money"""
        config = self.provider_configs[MobilePaymentProvider.MAROC_TELECOM]

        # Mode MOCK pour démo
        return self._mock_successful_payout(request, MobilePaymentProvider.MAROC_TELECOM)

    async def _process_cih_mobile(
        self,
        request: MobilePayoutRequest
    ) -> MobilePayoutResponse:
        """Traiter paiement via CIH Mobile"""
        config = self.provider_configs[MobilePaymentProvider.CIH_MOBILE]

        # Mode MOCK pour démo
        return self._mock_successful_payout(request, MobilePaymentProvider.CIH_MOBILE)

    # ============================================
    # HELPERS
    # ============================================

    def _mock_successful_payout(
        self,
        request: MobilePayoutRequest,
        provider: MobilePaymentProvider
    ) -> MobilePayoutResponse:
        """Mock de paiement réussi (pour démo sans vraies API keys)"""
        return MobilePayoutResponse(
            payout_id=f"MOCK-{provider.value.upper()}-{int(datetime.now().timestamp())}",
            status=PayoutStatus.COMPLETED,
            amount=request.amount,
            phone_number=request.phone_number,
            provider=provider,
            transaction_id=f"TXN-{int(datetime.now().timestamp())}",
            message=f"✅ Paiement {provider.value} réussi (DEMO MODE)",
            created_at=datetime.now(),
            completed_at=datetime.now()
        )

    async def check_payout_status(
        self,
        payout_id: str,
        provider: MobilePaymentProvider
    ) -> PayoutStatus:
        """Vérifier le statut d'un paiement"""
        # Implementation pour vérifier le statut auprès de l'opérateur
        # Pour démo, retourne COMPLETED
        return PayoutStatus.COMPLETED

    def get_supported_providers(self) -> List[Dict]:
        """Liste des opérateurs supportés avec infos"""
        return [
            {
                "id": MobilePaymentProvider.CASH_PLUS,
                "name": "Cash Plus",
                "logo": "/assets/providers/cashplus.png",
                "min_amount": 10.0,
                "max_amount": 10000.0,
                "fees": 0.0,
                "processing_time": "Instantané",
                "description": "Leader des paiements mobile au Maroc"
            },
            {
                "id": MobilePaymentProvider.WAFACASH,
                "name": "Wafacash",
                "logo": "/assets/providers/wafacash.png",
                "min_amount": 10.0,
                "max_amount": 10000.0,
                "fees": 0.0,
                "processing_time": "Instantané",
                "description": "Service de transfert d'argent Attijariwafa bank"
            },
            {
                "id": MobilePaymentProvider.ORANGE_MONEY,
                "name": "Orange Money",
                "logo": "/assets/providers/orange.png",
                "min_amount": 5.0,
                "max_amount": 5000.0,
                "fees": 0.0,
                "processing_time": "Instantané",
                "description": "Paiement mobile Orange Maroc"
            },
            {
                "id": MobilePaymentProvider.INWI_MONEY,
                "name": "inwi money",
                "logo": "/assets/providers/inwi.png",
                "min_amount": 5.0,
                "max_amount": 5000.0,
                "fees": 0.0,
                "processing_time": "Instantané",
                "description": "Service de paiement mobile inwi"
            },
            {
                "id": MobilePaymentProvider.MAROC_TELECOM,
                "name": "Maroc Telecom Mobile Money",
                "logo": "/assets/providers/iam.png",
                "min_amount": 5.0,
                "max_amount": 5000.0,
                "fees": 0.0,
                "processing_time": "Instantané",
                "description": "Paiement mobile Maroc Telecom"
            },
            {
                "id": MobilePaymentProvider.CIH_MOBILE,
                "name": "CIH Mobile",
                "logo": "/assets/providers/cih.png",
                "min_amount": 10.0,
                "max_amount": 10000.0,
                "fees": 0.0,
                "processing_time": "Instantané",
                "description": "Service mobile CIH Bank"
            },
        ]


# ============================================
# INSTANCE SINGLETON
# ============================================

mobile_payment_service = MobilePaymentService()
