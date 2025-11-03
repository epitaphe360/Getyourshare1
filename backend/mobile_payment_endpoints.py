"""
Mobile Payment Endpoints
Endpoints pour les paiements mobiles instantanés au Maroc
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from mobile_payment_service import (
    MobilePaymentService,
    PayoutRequest,
    PayoutResponse,
    PaymentAccount,
    MobilePaymentProvider,
    PaymentStatus
)
from auth import get_current_user
# from db_helpers import log_user_activity, get_user_balance  # TODO: Implémenter dans db_helpers
from supabase_client import supabase

router = APIRouter(prefix="/api/mobile-payments", tags=["Mobile Payments"])

# Initialiser le service
payment_service = MobilePaymentService()

# ============================================
# ENDPOINTS
# ============================================

@router.post("/request-payout", response_model=PayoutResponse)
async def request_payout(
    request: PayoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Demande un paiement mobile instantané

    Exemples:

    CashPlus:
    ```json
    {
        "user_id": "user_123",
        "amount": 150.00,
        "provider": "cashplus",
        "phone_number": "+212612345678",
        "notes": "Commission du mois de janvier"
    }
    ```

    Orange Money:
    ```json
    {
        "user_id": "user_123",
        "amount": 50.00,
        "provider": "orange_money",
        "phone_number": "+212712345678"
    }
    ```

    Flux:
    1. Vérifie le solde disponible
    2. Vérifie le montant minimum
    3. Calcule les frais
    4. Traite le paiement
    5. Met à jour le solde
    6. Envoie notification
    """

    try:
        # Sécurité: vérifier que l'user_id correspond au current_user
        if request.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez demander un paiement que pour votre propre compte"
            )

        # Vérifier le solde disponible
        user_balance = await get_user_balance(current_user["id"])
        if user_balance < request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solde insuffisant. Disponible: {user_balance} MAD, Demandé: {request.amount} MAD"
            )

        # Calculer les frais
        fee = payment_service.calculate_fee(request.amount, request.provider)
        net_amount = request.amount - fee

        # Traiter le payout
        payout_response = await payment_service.process_payout(request)

        # Enregistrer dans la DB
        payout_record = {
            "user_id": request.user_id,
            "amount": request.amount,
            "fee": fee,
            "net_amount": net_amount,
            "provider": request.provider,
            "phone_number": request.phone_number,
            "status": payout_response.status,
            "payout_id": payout_response.payout_id,
            "transaction_id": payout_response.transaction_id,
            "created_at": datetime.now().isoformat(),
            "notes": request.notes
        }

        # Insérer dans Supabase
        result = supabase.table("payouts").insert(payout_record).execute()

        # Si le payout est accepté, déduire du solde
        if payout_response.status in [PaymentStatus.PROCESSING, PaymentStatus.COMPLETED]:
            # Mettre à jour le solde de l'utilisateur
            supabase.table("users").update({
                "balance": user_balance - request.amount
            }).eq("id", current_user["id"]).execute()

        # Logger l'activité
        await log_user_activity(
            user_id=current_user["id"],
            action="payout_requested",
            details={
                "amount": request.amount,
                "provider": request.provider,
                "payout_id": payout_response.payout_id
            }
        )

        return payout_response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement du paiement: {str(e)}"
        )


@router.get("/providers", response_model=List[dict])
async def get_supported_providers(
    current_user: dict = Depends(get_current_user)
):
    """
    Liste tous les providers de paiement mobile supportés

    Retourne les infos sur:
    - Montants minimum
    - Frais
    - Temps de traitement
    - Opérateurs compatibles
    """

    return payment_service.get_supported_providers()


@router.post("/verify-phone")
async def verify_phone_number(
    phone: str,
    provider: MobilePaymentProvider,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifie si un numéro de téléphone est compatible avec un provider

    Exemple: Un numéro Orange ne peut pas utiliser MT Cash
    """

    result = await payment_service.verify_phone_number(phone, provider)
    return result


@router.post("/save-payment-account", response_model=PaymentAccount)
async def save_payment_account(
    provider: MobilePaymentProvider,
    phone_number: str,
    account_name: str,
    is_default: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Enregistre un compte de paiement mobile pour utilisation future

    Permet aux utilisateurs de sauvegarder leurs comptes préférés
    """

    try:
        # Vérifier d'abord si le numéro est valide
        verification = await payment_service.verify_phone_number(phone_number, provider)

        if not verification["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=verification.get("message", "Numéro invalide")
            )

        # Si is_default, retirer le default des autres comptes
        if is_default:
            supabase.table("payment_accounts").update({
                "is_default": False
            }).eq("user_id", current_user["id"]).execute()

        # Créer le compte
        account_data = {
            "user_id": current_user["id"],
            "provider": provider,
            "phone_number": phone_number,
            "account_name": account_name,
            "is_default": is_default,
            "is_verified": False,  # À vérifier avec un code SMS
            "created_at": datetime.now().isoformat()
        }

        result = supabase.table("payment_accounts").insert(account_data).execute()

        if result.data:
            account = PaymentAccount(**result.data[0])
            return account
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de l'enregistrement du compte"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/my-payment-accounts", response_model=List[dict])
async def get_my_payment_accounts(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère tous les comptes de paiement enregistrés par l'utilisateur
    """

    try:
        result = supabase.table("payment_accounts").select("*").eq(
            "user_id", current_user["id"]
        ).execute()

        return result.data if result.data else []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/payout-history")
async def get_payout_history(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Historique des payouts de l'utilisateur
    """

    try:
        result = supabase.table("payouts").select("*").eq(
            "user_id", current_user["id"]
        ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()

        return {
            "payouts": result.data if result.data else [],
            "count": len(result.data) if result.data else 0,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/payout-status/{payout_id}")
async def get_payout_status(
    payout_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifie le statut d'un payout spécifique
    """

    try:
        # Récupérer de la DB
        result = supabase.table("payouts").select("*").eq(
            "payout_id", payout_id
        ).eq("user_id", current_user["id"]).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payout non trouvé"
            )

        payout = result.data

        # Vérifier le statut en temps réel si nécessaire
        if payout["status"] == PaymentStatus.PROCESSING:
            live_status = await payment_service.get_payout_status(
                payout_id,
                payout["provider"]
            )

            # Mettre à jour si le statut a changé
            if live_status != payout["status"]:
                supabase.table("payouts").update({
                    "status": live_status,
                    "updated_at": datetime.now().isoformat()
                }).eq("payout_id", payout_id).execute()

                payout["status"] = live_status

        return payout

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/calculate-fee")
async def calculate_payout_fee(
    amount: float,
    provider: MobilePaymentProvider,
    current_user: dict = Depends(get_current_user)
):
    """
    Calcule les frais pour un montant et provider donnés

    Utile pour afficher le net amount avant confirmation
    """

    fee = payment_service.calculate_fee(amount, provider)
    net_amount = amount - fee

    return {
        "amount": amount,
        "fee": fee,
        "fee_percentage": payment_service.provider_fees.get(provider, 2.0),
        "net_amount": net_amount,
        "provider": provider,
        "currency": "MAD"
    }


@router.get("/stats")
async def get_payment_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Statistiques de paiement pour l'utilisateur
    """

    try:
        # Récupérer tous les payouts de l'utilisateur
        result = supabase.table("payouts").select("*").eq(
            "user_id", current_user["id"]
        ).execute()

        payouts = result.data if result.data else []

        # Calculer les stats
        total_payouts = len(payouts)
        total_amount = sum(p.get("amount", 0) for p in payouts)
        total_fees = sum(p.get("fee", 0) for p in payouts)

        completed = [p for p in payouts if p.get("status") == PaymentStatus.COMPLETED]
        pending = [p for p in payouts if p.get("status") == PaymentStatus.PENDING]
        failed = [p for p in payouts if p.get("status") == PaymentStatus.FAILED]

        # Provider préféré
        provider_counts = {}
        for p in payouts:
            provider = p.get("provider", "unknown")
            provider_counts[provider] = provider_counts.get(provider, 0) + 1

        favorite_provider = max(provider_counts, key=provider_counts.get) if provider_counts else None

        return {
            "total_payouts": total_payouts,
            "total_amount": total_amount,
            "total_fees": total_fees,
            "net_received": total_amount - total_fees,
            "completed_count": len(completed),
            "pending_count": len(pending),
            "failed_count": len(failed),
            "favorite_provider": favorite_provider,
            "average_payout": total_amount / total_payouts if total_payouts > 0 else 0,
            "currency": "MAD"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )
