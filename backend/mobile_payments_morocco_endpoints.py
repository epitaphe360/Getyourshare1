"""
Endpoints API pour Paiements Mobiles Marocains
Routes pour Cash Plus, Wafacash, Orange Money, inwi money, Maroc Telecom, CIH Mobile
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict
from pydantic import BaseModel, Field
from services.mobile_payment_morocco_service import (
    mobile_payment_service,
    MobilePayoutRequest,
    MobilePayoutResponse,
    MobilePaymentProvider,
    PayoutStatus
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mobile-payments-ma", tags=["Mobile Payments Morocco"])


# ============================================
# MODELS
# ============================================

class PayoutHistoryItem(BaseModel):
    """Historique de paiement"""
    payout_id: str
    amount: float
    phone_number: str
    provider: str
    status: str
    created_at: str
    completed_at: str = None


# ============================================
# ENDPOINTS
# ============================================

@router.get("/providers", summary="Liste des opérateurs supportés")
async def get_supported_providers() -> List[Dict]:
    """
    Récupère la liste des opérateurs de paiement mobile marocains supportés

    Returns:
        Liste des opérateurs avec détails (nom, logo, limites, fees)
    """
    return mobile_payment_service.get_supported_providers()


@router.post("/payout", summary="Initier un paiement mobile")
async def initiate_mobile_payout(
    request: MobilePayoutRequest
) -> MobilePayoutResponse:
    """
    Initier un paiement vers un compte mobile money marocain

    **Opérateurs supportés:**
    - Cash Plus (cash_plus)
    - Wafacash (wafacash)
    - Orange Money (orange_money)
    - inwi money (inwi_money)
    - Maroc Telecom Mobile Money (maroc_telecom)
    - CIH Mobile (cih_mobile)

    **Exemple de requête:**
    ```json
    {
        "user_id": "user_123",
        "amount": 500.0,
        "phone_number": "+212612345678",
        "provider": "cash_plus",
        "reference": "COMM-2024-001"
    }
    ```

    **Formats de numéro acceptés:**
    - +212612345678 (international)
    - 0612345678 (national)

    **Montants:**
    - Cash Plus / Wafacash / CIH: 10-10,000 MAD
    - Orange Money / inwi / Maroc Telecom: 5-5,000 MAD
    """
    try:
        # Valider le montant selon l'opérateur
        providers_info = mobile_payment_service.get_supported_providers()
        provider_info = next(
            (p for p in providers_info if p["id"] == request.provider),
            None
        )

        if not provider_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Opérateur non supporté: {request.provider}"
            )

        if request.amount < provider_info["min_amount"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Montant minimum pour {provider_info['name']}: {provider_info['min_amount']} MAD"
            )

        if request.amount > provider_info["max_amount"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Montant maximum pour {provider_info['name']}: {provider_info['max_amount']} MAD"
            )

        # Initier le paiement
        result = await mobile_payment_service.initiate_payout(request)

        if result.status == PayoutStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.message
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur paiement mobile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du paiement: {str(e)}"
        )


@router.get("/payout/{payout_id}/status", summary="Vérifier statut paiement")
async def check_payout_status(
    payout_id: str,
    provider: MobilePaymentProvider
) -> Dict:
    """
    Vérifier le statut d'un paiement mobile

    Args:
        payout_id: ID du paiement
        provider: Opérateur utilisé

    Returns:
        Statut actuel du paiement
    """
    try:
        status_result = await mobile_payment_service.check_payout_status(
            payout_id=payout_id,
            provider=provider
        )

        return {
            "payout_id": payout_id,
            "status": status_result,
            "message": "Statut récupéré avec succès"
        }

    except Exception as e:
        logger.error(f"Erreur vérification statut: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/user/{user_id}/history", summary="Historique paiements utilisateur")
async def get_user_payout_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0
) -> Dict:
    """
    Récupère l'historique des paiements mobiles d'un utilisateur

    Args:
        user_id: ID de l'utilisateur
        limit: Nombre de résultats (max 100)
        offset: Offset pour pagination

    Returns:
        Liste des paiements avec pagination
    """
    # TODO: Récupérer depuis la base de données
    # Pour démo, retourne un historique mock

    mock_history = [
        {
            "payout_id": "MOCK-CASHPLUS-1234567890",
            "amount": 500.0,
            "phone_number": "+212612345678",
            "provider": "cash_plus",
            "status": "completed",
            "created_at": "2025-01-15T10:30:00",
            "completed_at": "2025-01-15T10:30:05"
        },
        {
            "payout_id": "MOCK-ORANGE-1234567891",
            "amount": 250.0,
            "phone_number": "+212612345678",
            "provider": "orange_money",
            "status": "completed",
            "created_at": "2025-01-10T14:20:00",
            "completed_at": "2025-01-10T14:20:03"
        }
    ]

    return {
        "user_id": user_id,
        "total": len(mock_history),
        "limit": limit,
        "offset": offset,
        "payouts": mock_history[offset:offset + limit]
    }


@router.get("/stats", summary="Statistiques paiements mobiles")
async def get_mobile_payments_stats() -> Dict:
    """
    Statistiques globales des paiements mobiles

    Returns:
        Métriques clés (volume, montant total, par opérateur)
    """
    # TODO: Calculer depuis la base de données
    # Pour démo, retourne des stats mock

    return {
        "total_payouts": 1247,
        "total_amount": 456789.50,
        "success_rate": 99.2,
        "by_provider": {
            "cash_plus": {
                "count": 523,
                "amount": 198456.00,
                "percentage": 41.9
            },
            "wafacash": {
                "count": 312,
                "amount": 125678.00,
                "percentage": 25.0
            },
            "orange_money": {
                "count": 245,
                "amount": 89234.50,
                "percentage": 19.6
            },
            "inwi_money": {
                "count": 98,
                "amount": 28345.00,
                "percentage": 7.9
            },
            "maroc_telecom": {
                "count": 54,
                "amount": 12456.00,
                "percentage": 4.3
            },
            "cih_mobile": {
                "count": 15,
                "amount": 2620.00,
                "percentage": 1.2
            }
        },
        "average_payout": 366.24,
        "processing_time_avg_seconds": 3.2
    }


@router.post("/validate-phone", summary="Valider numéro marocain")
async def validate_moroccan_phone(
    phone_number: str,
    provider: MobilePaymentProvider
) -> Dict:
    """
    Valide qu'un numéro de téléphone marocain est compatible avec un opérateur

    Args:
        phone_number: Numéro à valider
        provider: Opérateur cible

    Returns:
        Résultat de validation avec détails
    """
    import re

    # Pattern numéro marocain
    pattern = r"^(?:\+212|0)[5-7]\d{8}$"

    if not re.match(pattern, phone_number):
        return {
            "valid": False,
            "message": "Format de numéro invalide. Formats acceptés: +212612345678 ou 0612345678",
            "provider_compatible": False
        }

    # Normaliser le numéro
    normalized = phone_number
    if phone_number.startswith("0"):
        normalized = "+212" + phone_number[1:]

    # Vérifier compatibilité avec opérateur
    operator_prefixes = {
        MobilePaymentProvider.ORANGE_MONEY: ["+2126"],  # Orange
        MobilePaymentProvider.INWI_MONEY: ["+2127", "+2128"],  # inwi
        MobilePaymentProvider.MAROC_TELECOM: ["+2125"],  # Maroc Telecom
    }

    # Cash Plus, Wafacash, CIH acceptent tous les numéros
    universal_providers = [
        MobilePaymentProvider.CASH_PLUS,
        MobilePaymentProvider.WAFACASH,
        MobilePaymentProvider.CIH_MOBILE
    ]

    if provider in universal_providers:
        return {
            "valid": True,
            "normalized": normalized,
            "message": f"{provider.value} accepte tous les numéros marocains",
            "provider_compatible": True
        }

    # Vérifier préfixe pour opérateurs spécifiques
    if provider in operator_prefixes:
        prefixes = operator_prefixes[provider]
        compatible = any(normalized.startswith(p) for p in prefixes)

        if compatible:
            return {
                "valid": True,
                "normalized": normalized,
                "message": f"Numéro compatible avec {provider.value}",
                "provider_compatible": True
            }
        else:
            return {
                "valid": True,
                "normalized": normalized,
                "message": f"Numéro valide mais incompatible avec {provider.value}",
                "provider_compatible": False,
                "suggestion": "Utilisez Cash Plus ou Wafacash pour ce numéro"
            }

    return {
        "valid": True,
        "normalized": normalized,
        "provider_compatible": True
    }


# ============================================
# WEBHOOKS (pour notifications des opérateurs)
# ============================================

@router.post("/webhook/{provider}", summary="Webhook opérateur")
async def mobile_payment_webhook(
    provider: MobilePaymentProvider,
    payload: Dict
):
    """
    Endpoint pour recevoir les webhooks des opérateurs de paiement

    Chaque opérateur peut envoyer des notifications de statut ici

    Args:
        provider: Opérateur qui envoie la notification
        payload: Données de la notification
    """
    logger.info(f"Webhook reçu de {provider}: {payload}")

    # TODO: Traiter la notification et mettre à jour le statut en DB

    return {
        "received": True,
        "provider": provider,
        "message": "Webhook traité avec succès"
    }
