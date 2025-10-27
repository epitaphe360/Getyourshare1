"""
Router FastAPI pour les endpoints de paiement et commissions.
"""

import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator

from .service import PaymentsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/commissions", tags=["Payments & Commissions"])


# Modèles Pydantic
class ApproveCommissionRequest(BaseModel):
    """Requête d'approbation/changement de statut de commission."""
    status: str = Field(..., description="Nouveau statut de la commission")
    
    @validator("status")
    def validate_status(cls, v):
        allowed = ["pending", "approved", "paid", "rejected"]
        if v not in allowed:
            raise ValueError(f"Statut doit être l'un de: {', '.join(allowed)}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved"
            }
        }


class BatchApproveRequest(BaseModel):
    """Requête d'approbation en lot."""
    commission_ids: List[UUID] = Field(..., description="Liste des IDs de commissions")
    status: str = Field(default="approved", description="Statut à appliquer")
    
    @validator("status")
    def validate_status(cls, v):
        allowed = ["approved", "paid", "rejected"]
        if v not in allowed:
            raise ValueError(f"Statut doit être l'un de: {', '.join(allowed)}")
        return v


class CommissionResponse(BaseModel):
    """Réponse après récupération de commission."""
    id: UUID
    sale_id: Optional[UUID]
    influencer_id: UUID
    amount: float
    currency: str
    status: str
    payment_method: Optional[str]
    transaction_id: Optional[str]
    paid_at: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class CommissionSummaryResponse(BaseModel):
    """Résumé des commissions d'un influenceur."""
    influencer_id: UUID
    pending_total: float
    approved_total: float
    paid_total: float
    total_earnings: float


class BatchApproveResponse(BaseModel):
    """Réponse après approbation en lot."""
    success_count: int
    failed_count: int
    success: List[str]
    failed: List[dict]


# Dépendance pour obtenir le service
def get_payments_service() -> PaymentsService:
    """Retourne une instance du service de paiements."""
    return PaymentsService()


# Endpoints
@router.post(
    "/{commission_id}/approve",
    response_model=dict,
    summary="Approuver/changer le statut d'une commission",
    description="Gère les transitions de statut via approve_payout_transaction"
)
async def approve_commission(
    commission_id: UUID,
    request: ApproveCommissionRequest,
    service: PaymentsService = Depends(get_payments_service)
):
    """
    Change le statut d'une commission en appelant approve_payout_transaction.
    
    Transitions autorisées:
    - pending → approved
    - approved → paid
    - approved → rejected
    - approved → pending (annulation)
    """
    try:
        success = await service.approve_commission(commission_id, request.status)
        return {
            "success": success,
            "commission_id": str(commission_id),
            "new_status": request.status,
            "message": f"Commission {commission_id} mise à jour avec succès"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{commission_id}",
    response_model=CommissionResponse,
    summary="Récupérer une commission",
    description="Récupère les détails d'une commission par son ID"
)
async def get_commission(
    commission_id: UUID,
    service: PaymentsService = Depends(get_payments_service)
):
    """Récupère une commission par son ID."""
    commission = await service.get_commission_by_id(commission_id)
    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commission {commission_id} introuvable"
        )
    return commission


@router.get(
    "",
    response_model=List[CommissionResponse],
    summary="Récupérer les commissions par statut",
    description="Liste les commissions filtrées par statut avec pagination"
)
async def get_commissions_by_status(
    status_filter: str = "pending",
    limit: int = 50,
    offset: int = 0,
    service: PaymentsService = Depends(get_payments_service)
):
    """Récupère les commissions par statut."""
    commissions = await service.get_commissions_by_status(status_filter, limit, offset)
    return commissions


@router.get(
    "/influencer/{influencer_id}",
    response_model=List[CommissionResponse],
    summary="Récupérer les commissions d'un influenceur",
    description="Liste toutes les commissions d'un influenceur"
)
async def get_influencer_commissions(
    influencer_id: UUID,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    service: PaymentsService = Depends(get_payments_service)
):
    """Récupère les commissions d'un influenceur avec pagination."""
    commissions = await service.get_commissions_by_influencer(
        influencer_id, status_filter, limit, offset
    )
    return commissions


@router.get(
    "/influencer/{influencer_id}/summary",
    response_model=CommissionSummaryResponse,
    summary="Résumé des commissions d'un influenceur",
    description="Retourne les totaux pending, approved et paid"
)
async def get_influencer_commission_summary(
    influencer_id: UUID,
    service: PaymentsService = Depends(get_payments_service)
):
    """Résumé des commissions d'un influenceur."""
    pending = await service.get_pending_commissions_total(influencer_id)
    approved = await service.get_approved_commissions_total(influencer_id)
    
    # Récupérer le total paid depuis les commissions
    result = await service.get_commissions_by_influencer(influencer_id, "paid", limit=1000)
    paid = sum(float(c.get("amount", 0)) for c in result)
    
    return {
        "influencer_id": influencer_id,
        "pending_total": pending,
        "approved_total": approved,
        "paid_total": paid,
        "total_earnings": pending + approved + paid
    }


@router.post(
    "/batch/approve",
    response_model=BatchApproveResponse,
    summary="Approuver plusieurs commissions en lot",
    description="Applique un statut à plusieurs commissions simultanément"
)
async def batch_approve_commissions(
    request: BatchApproveRequest,
    service: PaymentsService = Depends(get_payments_service)
):
    """
    Approuve plusieurs commissions en lot.
    Utile pour les paiements groupés mensuels.
    """
    result = await service.batch_approve_commissions(
        request.commission_ids,
        request.status
    )
    return result


@router.post(
    "/{commission_id}/pay",
    response_model=dict,
    summary="Marquer une commission comme payée",
    description="Raccourci pour passer au statut 'paid' directement"
)
async def pay_commission(
    commission_id: UUID,
    service: PaymentsService = Depends(get_payments_service)
):
    """
    Marque une commission comme payée.
    La commission doit être au statut 'approved'.
    """
    try:
        success = await service.approve_commission(commission_id, "paid")
        return {
            "success": success,
            "commission_id": str(commission_id),
            "status": "paid",
            "message": f"Commission {commission_id} marquée comme payée"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{commission_id}/reject",
    response_model=dict,
    summary="Rejeter une commission",
    description="Raccourci pour passer au statut 'rejected'"
)
async def reject_commission(
    commission_id: UUID,
    service: PaymentsService = Depends(get_payments_service)
):
    """
    Rejette une commission.
    Libère le montant si la commission était approuvée.
    """
    try:
        success = await service.approve_commission(commission_id, "rejected")
        return {
            "success": success,
            "commission_id": str(commission_id),
            "status": "rejected",
            "message": f"Commission {commission_id} rejetée"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
