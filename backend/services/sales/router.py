"""
Router FastAPI pour les endpoints de vente.
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, EmailStr, validator

from .service import SalesService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sales", tags=["Sales"])


# Modèles Pydantic
class CreateSaleRequest(BaseModel):
    """Requête de création de vente."""
    link_id: UUID = Field(..., description="ID du lien tracké utilisé")
    product_id: UUID = Field(..., description="ID du produit vendu")
    influencer_id: UUID = Field(..., description="ID de l'influenceur")
    merchant_id: UUID = Field(..., description="ID du merchant")
    amount: float = Field(..., gt=0, description="Montant de la vente (doit être > 0)")
    currency: str = Field(default="EUR", description="Devise")
    quantity: int = Field(default=1, gt=0, description="Quantité (doit être > 0)")
    customer_email: Optional[EmailStr] = Field(None, description="Email du client")
    customer_name: Optional[str] = Field(None, max_length=255, description="Nom du client")
    payment_status: str = Field(default="pending", description="Statut de paiement")
    status: str = Field(default="completed", description="Statut de la vente")
    
    @validator("status")
    def validate_status(cls, v):
        allowed = ["pending", "completed", "refunded", "cancelled"]
        if v not in allowed:
            raise ValueError(f"Statut doit être l'un de: {', '.join(allowed)}")
        return v
    
    @validator("payment_status")
    def validate_payment_status(cls, v):
        allowed = ["pending", "paid"]
        if v not in allowed:
            raise ValueError(f"Statut de paiement doit être l'un de: {', '.join(allowed)}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "link_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "product_id": "e5f6g7h8-i9j0-k1l2-m3n4-o5p6q7r8s9t0",
                "influencer_id": "i9j0k1l2-m3n4-o5p6-q7r8-s9t0u1v2w3x4",
                "merchant_id": "m3n4o5p6-q7r8-s9t0-u1v2-w3x4y5z6a7b8",
                "amount": 199.90,
                "currency": "EUR",
                "quantity": 1,
                "customer_email": "client@example.com",
                "customer_name": "Jean Dupont",
                "payment_status": "pending",
                "status": "completed"
            }
        }


class SaleResponse(BaseModel):
    """Réponse après création/récupération de vente."""
    id: UUID
    link_id: Optional[UUID]
    product_id: Optional[UUID]
    influencer_id: Optional[UUID]
    merchant_id: Optional[UUID]
    amount: float
    currency: str
    quantity: int
    influencer_commission: float
    platform_commission: float
    merchant_revenue: float
    status: str
    payment_status: str
    customer_email: Optional[str]
    customer_name: Optional[str]
    sale_timestamp: str
    created_at: str
    
    class Config:
        from_attributes = True


class UpdateSaleStatusRequest(BaseModel):
    """Requête de mise à jour du statut d'une vente."""
    status: str = Field(..., description="Nouveau statut")
    payment_status: Optional[str] = Field(None, description="Nouveau statut de paiement")
    
    @validator("status")
    def validate_status(cls, v):
        allowed = ["pending", "completed", "refunded", "cancelled"]
        if v not in allowed:
            raise ValueError(f"Statut doit être l'un de: {', '.join(allowed)}")
        return v
    
    @validator("payment_status")
    def validate_payment_status(cls, v):
        if v is not None:
            allowed = ["pending", "paid"]
            if v not in allowed:
                raise ValueError(f"Statut de paiement doit être l'un de: {', '.join(allowed)}")
        return v


# Dépendance pour obtenir le service
def get_sales_service() -> SalesService:
    """Retourne une instance du service de ventes."""
    return SalesService()


# Endpoints
@router.post(
    "",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une vente",
    description="Crée une nouvelle vente via la fonction transactionnelle create_sale_transaction"
)
async def create_sale(
    request: CreateSaleRequest,
    service: SalesService = Depends(get_sales_service)
):
    """
    Crée une vente complète avec commission, met à jour tous les compteurs.
    
    Cette route appelle la fonction PL/pgSQL `create_sale_transaction` qui garantit
    l'atomicité de toutes les opérations (création vente, commission, mise à jour métriques).
    """
    try:
        sale = await service.create_sale(
            link_id=request.link_id,
            product_id=request.product_id,
            influencer_id=request.influencer_id,
            merchant_id=request.merchant_id,
            amount=request.amount,
            currency=request.currency,
            quantity=request.quantity,
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            payment_status=request.payment_status,
            status=request.status
        )
        return sale
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
    "/{sale_id}",
    response_model=SaleResponse,
    summary="Récupérer une vente",
    description="Récupère les détails d'une vente par son ID"
)
async def get_sale(
    sale_id: UUID,
    service: SalesService = Depends(get_sales_service)
):
    """Récupère une vente par son ID."""
    sale = await service.get_sale_by_id(sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vente {sale_id} introuvable"
        )
    return sale


@router.get(
    "/influencer/{influencer_id}",
    response_model=list[SaleResponse],
    summary="Récupérer les ventes d'un influenceur",
    description="Liste toutes les ventes générées par un influenceur"
)
async def get_influencer_sales(
    influencer_id: UUID,
    limit: int = 50,
    offset: int = 0,
    service: SalesService = Depends(get_sales_service)
):
    """Récupère les ventes d'un influenceur avec pagination."""
    sales = await service.get_sales_by_influencer(influencer_id, limit, offset)
    return sales


@router.get(
    "/merchant/{merchant_id}",
    response_model=list[SaleResponse],
    summary="Récupérer les ventes d'un merchant",
    description="Liste toutes les ventes d'un merchant"
)
async def get_merchant_sales(
    merchant_id: UUID,
    limit: int = 50,
    offset: int = 0,
    service: SalesService = Depends(get_sales_service)
):
    """Récupère les ventes d'un merchant avec pagination."""
    sales = await service.get_sales_by_merchant(merchant_id, limit, offset)
    return sales


@router.patch(
    "/{sale_id}/status",
    response_model=SaleResponse,
    summary="Mettre à jour le statut d'une vente",
    description="Change le statut d'une vente (completed, refunded, cancelled, etc.)"
)
async def update_sale_status(
    sale_id: UUID,
    request: UpdateSaleStatusRequest,
    service: SalesService = Depends(get_sales_service)
):
    """Met à jour le statut d'une vente."""
    sale = await service.update_sale_status(
        sale_id=sale_id,
        status=request.status,
        payment_status=request.payment_status
    )
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vente {sale_id} introuvable"
        )
    return sale
