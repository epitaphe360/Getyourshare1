"""Router FastAPI pour le module d'affiliation."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from .schemas import AffiliationDecision, AffiliationRequestCreate
from . import service

router = APIRouter(tags=["Affiliation"], prefix="/api")


def get_token_payload() -> dict:
    """Dépendance qui sera surchargée par l'application principale."""

    raise RuntimeError("Dependency override required: inject verify_token")


@router.post("/affiliation/request")
async def create_affiliation_request(
    request_data: AffiliationRequestCreate,
    payload: dict = Depends(get_token_payload),
):
    return service.create_affiliation_request(payload["sub"], request_data)


@router.get("/influencer/affiliation-requests")
async def get_influencer_affiliation_requests(
    status: Optional[str] = Query(None, description="pending_approval|active|rejected|cancelled"),
    payload: dict = Depends(get_token_payload),
):
    return service.list_influencer_requests(payload["sub"], status)


@router.delete("/affiliation/request/{request_id}")
async def cancel_affiliation_request(
    request_id: str,
    payload: dict = Depends(get_token_payload),
):
    return service.cancel_affiliation_request(payload["sub"], request_id)


@router.get("/merchant/affiliation-requests")
async def get_merchant_affiliation_requests(
    status: Optional[str] = Query(None, description="pending_approval|active|rejected|cancelled|all"),
    payload: dict = Depends(get_token_payload),
):
    return service.list_merchant_requests(payload["sub"], status)


@router.post("/merchant/affiliation-requests/{request_id}/approve")
async def approve_affiliation_request(
    request_id: str,
    response_data: AffiliationDecision,
    payload: dict = Depends(get_token_payload),
):
    return service.approve_affiliation_request(payload["sub"], request_id, response_data)


@router.post("/merchant/affiliation-requests/{request_id}/reject")
async def reject_affiliation_request(
    request_id: str,
    response_data: AffiliationDecision,
    payload: dict = Depends(get_token_payload),
):
    return service.reject_affiliation_request(payload["sub"], request_id, response_data)


@router.get("/merchant/affiliation-requests/stats")
async def get_affiliation_requests_stats(payload: dict = Depends(get_token_payload)):
    return service.get_affiliation_stats(payload["sub"])
