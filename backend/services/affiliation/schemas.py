from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AffiliationRequestCreate(BaseModel):
    """Payload envoyé par un influenceur pour demander un lien."""

    product_id: str = Field(..., min_length=1)
    message: Optional[str] = Field(None, max_length=5000)
    stats: Optional[Dict[str, Any]] = None


class AffiliationDecision(BaseModel):
    """Réponse d'un marchand lors de l'approbation / refus."""

    merchant_response: Optional[str] = Field(None, max_length=2000)
