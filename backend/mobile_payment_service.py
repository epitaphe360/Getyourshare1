"""
Mobile Payment Service pour le Maroc
Intégrations: CashPlus, Orange Money, Maroc Telecom Cash, Wafacash
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import httpx
import hashlib
import hmac
import os

# ============================================
# MODELS
# ============================================

class MobilePaymentProvider(str, Enum):
    CASHPLUS = "cashplus"
    ORANGE_MONEY = "orange_money"
    MAROC_TELECOM_CASH = "mt_cash"
    WAFACASH = "wafacash"
    PAYZONE = "payzone"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PayoutRequest(BaseModel):
    user_id: str
    amount: float = Field(..., gt=0, description="Montant en MAD")
    provider: MobilePaymentProvider
    phone_number: str = Field(..., pattern=r"^(\+212|0)[5-7][0-9]{8}$")
    reference: Optional[str] = None
    notes: Optional[str] = None

class PayoutResponse(BaseModel):
    payout_id: str
    status: PaymentStatus
    amount: float
    provider: MobilePaymentProvider
    phone_number: str
    transaction_id: Optional[str] = None
    created_at: datetime
    estimated_completion: str
    qr_code_url: Optional[str] = None  # Pour retrait en magasin

class PaymentAccount(BaseModel):
    user_id: str
    provider: MobilePaymentProvider
    phone_number: str
    account_name: str
    is_verified: bool = False
    is_default: bool = False
    created_at: datetime = datetime.now()

# ============================================
# MOBILE PAYMENT SERVICE
# ============================================

class MobilePaymentService:
    """Service de paiement mobile pour le Maroc"""

    def __init__(self):
        # Credentials (à stocker dans .env en production)
        self.cashplus_api_key = os.getenv("CASHPLUS_API_KEY")
        self.cashplus_secret = os.getenv("CASHPLUS_SECRET")
        self.cashplus_merchant_id = os.getenv("CASHPLUS_MERCHANT_ID")

        self.orange_money_api_key = os.getenv("ORANGE_MONEY_API_KEY")
        self.orange_money_secret = os.getenv("ORANGE_MONEY_SECRET")

        self.mt_cash_api_key = os.getenv("MT_CASH_API_KEY")
        self.mt_cash_merchant_id = os.getenv("MT_CASH_MERCHANT_ID")

        # Minimum payout amounts (en MAD)
        self.min_payout_amounts = {
            MobilePaymentProvider.CASHPLUS: 50.0,
            MobilePaymentProvider.ORANGE_MONEY: 10.0,
            MobilePaymentProvider.MAROC_TELECOM_CASH: 10.0,
            MobilePaymentProvider.WAFACASH: 100.0,
            MobilePaymentProvider.PAYZONE: 50.0
        }

        # Fees par provider (%)
        self.provider_fees = {
            MobilePaymentProvider.CASHPLUS: 1.5,  # 1.5% de frais
            MobilePaymentProvider.ORANGE_MONEY: 2.0,
            MobilePaymentProvider.MAROC_TELECOM_CASH: 2.0,
            MobilePaymentProvider.WAFACASH: 3.0,
            MobilePaymentProvider.PAYZONE: 2.5
        }

    async def process_payout(self, request: PayoutRequest) -> PayoutResponse:
        """
        Traite un paiement vers un compte mobile

        Flux:
        1. Vérifier le solde de l'utilisateur
        2. Vérifier le montant minimum
        3. Appeler l'API du provider
        4. Enregistrer la transaction
        5. Notifier l'utilisateur
        """

        # Vérifier le montant minimum
        min_amount = self.min_payout_amounts.get(request.provider, 100.0)
        if request.amount < min_amount:
            raise ValueError(f"Montant minimum pour {request.provider}: {min_amount} MAD")

        # Calculer les frais
        fee = self.calculate_fee(request.amount, request.provider)
        net_amount = request.amount - fee

        # Router vers le bon provider
        if request.provider == MobilePaymentProvider.CASHPLUS:
            result = await self._process_cashplus_payout(request, net_amount)
        elif request.provider == MobilePaymentProvider.ORANGE_MONEY:
            result = await self._process_orange_money_payout(request, net_amount)
        elif request.provider == MobilePaymentProvider.MAROC_TELECOM_CASH:
            result = await self._process_mt_cash_payout(request, net_amount)
        else:
            result = await self._process_generic_payout(request, net_amount)

        return result

    async def _process_cashplus_payout(self, request: PayoutRequest, net_amount: float) -> PayoutResponse:
        """
        Intégration CashPlus API
        Docs: https://www.cashplus.ma/api-docs
        """

        try:
            # Générer un ID unique pour la transaction
            payout_id = f"payout_{datetime.now().timestamp()}_{request.user_id}"

            # Préparer la requête CashPlus
            payload = {
                "merchant_id": self.cashplus_merchant_id,
                "amount": net_amount,
                "phone": request.phone_number,
                "reference": payout_id,
                "callback_url": f"{os.getenv('API_BASE_URL')}/api/webhooks/cashplus"
            }

            # Générer la signature HMAC
            signature = self._generate_cashplus_signature(payload)
            payload["signature"] = signature

            # Appeler l'API CashPlus
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.cashplus.ma/v1/payouts",
                    headers={
                        "Authorization": f"Bearer {self.cashplus_api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()

                    return PayoutResponse(
                        payout_id=payout_id,
                        status=PaymentStatus.PROCESSING,
                        amount=request.amount,
                        provider=MobilePaymentProvider.CASHPLUS,
                        phone_number=request.phone_number,
                        transaction_id=data.get("transaction_id"),
                        created_at=datetime.now(),
                        estimated_completion="Instantané (1-5 minutes)",
                        qr_code_url=data.get("qr_code_url")  # Pour retrait en agence
                    )
                else:
                    # Gestion d'erreur
                    return PayoutResponse(
                        payout_id=payout_id,
                        status=PaymentStatus.FAILED,
                        amount=request.amount,
                        provider=MobilePaymentProvider.CASHPLUS,
                        phone_number=request.phone_number,
                        created_at=datetime.now(),
                        estimated_completion="Échec"
                    )

        except Exception as e:
            print(f"CashPlus API Error: {e}")
            # Fallback: créer une transaction manuelle
            return await self._create_manual_payout(request, net_amount)

    async def _process_orange_money_payout(self, request: PayoutRequest, net_amount: float) -> PayoutResponse:
        """
        Intégration Orange Money API
        """

        try:
            payout_id = f"payout_om_{datetime.now().timestamp()}_{request.user_id}"

            # Orange Money utilise OAuth2
            access_token = await self._get_orange_money_token()

            payload = {
                "amount": {
                    "value": net_amount,
                    "currency": "MAD"
                },
                "recipient": {
                    "phone_number": request.phone_number
                },
                "reference": payout_id
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.orange.com/orange-money-webpay/ma/v1/payouts",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )

                if response.status_code in [200, 201]:
                    data = response.json()

                    return PayoutResponse(
                        payout_id=payout_id,
                        status=PaymentStatus.PROCESSING,
                        amount=request.amount,
                        provider=MobilePaymentProvider.ORANGE_MONEY,
                        phone_number=request.phone_number,
                        transaction_id=data.get("transaction_id"),
                        created_at=datetime.now(),
                        estimated_completion="Instantané (1-3 minutes)"
                    )
                else:
                    return await self._create_manual_payout(request, net_amount)

        except Exception as e:
            print(f"Orange Money API Error: {e}")
            return await self._create_manual_payout(request, net_amount)

    async def _process_mt_cash_payout(self, request: PayoutRequest, net_amount: float) -> PayoutResponse:
        """
        Intégration Maroc Telecom Cash API
        """

        try:
            payout_id = f"payout_mt_{datetime.now().timestamp()}_{request.user_id}"

            payload = {
                "merchant_id": self.mt_cash_merchant_id,
                "amount": net_amount,
                "msisdn": request.phone_number,
                "transaction_ref": payout_id
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.iam.ma/mtcash/v1/transfer",
                    headers={
                        "X-API-KEY": self.mt_cash_api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()

                    return PayoutResponse(
                        payout_id=payout_id,
                        status=PaymentStatus.PROCESSING,
                        amount=request.amount,
                        provider=MobilePaymentProvider.MAROC_TELECOM_CASH,
                        phone_number=request.phone_number,
                        transaction_id=data.get("transaction_id"),
                        created_at=datetime.now(),
                        estimated_completion="Instantané (1-3 minutes)"
                    )
                else:
                    return await self._create_manual_payout(request, net_amount)

        except Exception as e:
            print(f"MT Cash API Error: {e}")
            return await self._create_manual_payout(request, net_amount)

    async def _process_generic_payout(self, request: PayoutRequest, net_amount: float) -> PayoutResponse:
        """Payout générique pour providers sans intégration directe"""
        return await self._create_manual_payout(request, net_amount)

    async def _create_manual_payout(self, request: PayoutRequest, net_amount: float) -> PayoutResponse:
        """
        Crée un payout manuel (à traiter par l'admin)
        Utilisé en fallback ou pour providers sans API
        """

        payout_id = f"manual_{datetime.now().timestamp()}_{request.user_id}"

        return PayoutResponse(
            payout_id=payout_id,
            status=PaymentStatus.PENDING,
            amount=request.amount,
            provider=request.provider,
            phone_number=request.phone_number,
            created_at=datetime.now(),
            estimated_completion="24-48 heures (traitement manuel)"
        )

    def calculate_fee(self, amount: float, provider: MobilePaymentProvider) -> float:
        """Calcule les frais de transaction"""
        fee_percentage = self.provider_fees.get(provider, 2.0)
        return round(amount * (fee_percentage / 100), 2)

    def _generate_cashplus_signature(self, payload: dict) -> str:
        """Génère la signature HMAC pour CashPlus"""
        message = f"{payload['merchant_id']}{payload['amount']}{payload['phone']}{payload['reference']}"
        signature = hmac.new(
            self.cashplus_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def _get_orange_money_token(self) -> str:
        """Récupère un token OAuth2 pour Orange Money"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.orange.com/oauth/v3/token",
                    headers={
                        "Authorization": f"Basic {self.orange_money_api_key}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={
                        "grant_type": "client_credentials"
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["access_token"]
                else:
                    raise Exception("Failed to get Orange Money token")

        except Exception as e:
            print(f"Error getting Orange Money token: {e}")
            return ""

    async def verify_phone_number(self, phone: str, provider: MobilePaymentProvider) -> Dict[str, Any]:
        """
        Vérifie si un numéro de téléphone est valide pour un provider

        Retourne:
        - valid: bool
        - account_name: str (si disponible)
        - operator: str
        """

        # Validation du format
        if not phone.startswith(("+212", "0")):
            return {"valid": False, "error": "Numéro marocain requis"}

        # Détection de l'opérateur
        if phone.startswith(("+2126", "06")):
            operator = "Maroc Telecom"
        elif phone.startswith(("+2127", "07")):
            operator = "Orange"
        elif phone.startswith(("+2125", "05")):
            operator = "INWI"
        else:
            operator = "Unknown"

        # Vérifier la compatibilité provider/operator
        compatible = True
        if provider == MobilePaymentProvider.ORANGE_MONEY and operator != "Orange":
            compatible = False
        elif provider == MobilePaymentProvider.MAROC_TELECOM_CASH and operator != "Maroc Telecom":
            compatible = False

        return {
            "valid": compatible,
            "operator": operator,
            "provider": provider,
            "compatible": compatible,
            "message": "Numéro valide" if compatible else f"Ce numéro n'est pas compatible avec {provider}"
        }

    async def get_payout_status(self, payout_id: str, provider: MobilePaymentProvider) -> PaymentStatus:
        """
        Vérifie le statut d'un payout

        À implémenter avec les webhooks des providers
        """

        # À implémenter avec la DB + webhooks
        return PaymentStatus.PROCESSING

    def get_supported_providers(self) -> List[Dict[str, Any]]:
        """Retourne la liste des providers supportés avec leurs infos"""

        return [
            {
                "provider": MobilePaymentProvider.CASHPLUS,
                "name": "CashPlus",
                "logo": "https://www.cashplus.ma/logo.png",
                "min_amount": 50.0,
                "fee_percentage": 1.5,
                "processing_time": "Instantané (1-5 min)",
                "supported_operators": ["Tous"],
                "has_qr_code": True,
                "description": "Retrait instantané dans +10,000 points CashPlus"
            },
            {
                "provider": MobilePaymentProvider.ORANGE_MONEY,
                "name": "Orange Money",
                "logo": "https://www.orange.ma/logo.png",
                "min_amount": 10.0,
                "fee_percentage": 2.0,
                "processing_time": "Instantané (1-3 min)",
                "supported_operators": ["Orange"],
                "has_qr_code": False,
                "description": "Paiement direct sur votre compte Orange Money"
            },
            {
                "provider": MobilePaymentProvider.MAROC_TELECOM_CASH,
                "name": "MT Cash",
                "logo": "https://www.iam.ma/logo.png",
                "min_amount": 10.0,
                "fee_percentage": 2.0,
                "processing_time": "Instantané (1-3 min)",
                "supported_operators": ["Maroc Telecom"],
                "has_qr_code": False,
                "description": "Paiement direct sur votre compte MT Cash"
            },
            {
                "provider": MobilePaymentProvider.WAFACASH,
                "name": "WafaCash",
                "logo": "https://www.wafacash.ma/logo.png",
                "min_amount": 100.0,
                "fee_percentage": 3.0,
                "processing_time": "24-48 heures",
                "supported_operators": ["Tous"],
                "has_qr_code": True,
                "description": "Retrait en agence WafaCash"
            }
        ]
