"""Services métier pour les demandes d'affiliation."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import HTTPException

from db_helpers import (
    get_user_by_id,
    get_influencer_by_user_id,
    get_merchant_by_user_id,
)
from supabase_client import supabase

from .schemas import AffiliationRequestCreate, AffiliationDecision

logger = logging.getLogger(__name__)

AFFILIATION_STATUS_APP_TO_DB = {
    "pending_approval": "pending",
    "active": "approved",
    "rejected": "rejected",
    "cancelled": "cancelled",
}

AFFILIATION_STATUS_DB_TO_APP = {db: app for app, db in AFFILIATION_STATUS_APP_TO_DB.items()}


def map_affiliation_status_to_db(app_status: Optional[str]) -> Optional[str]:
    return AFFILIATION_STATUS_APP_TO_DB.get(app_status) if app_status else None


def map_affiliation_status_to_app(db_status: Optional[str]) -> Optional[str]:
    return AFFILIATION_STATUS_DB_TO_APP.get(db_status, db_status)


def record_affiliation_history(
    *,
    request_id: str,
    old_status: Optional[str],
    new_status: str,
    changed_by: str,
    comment: Optional[str] = None,
) -> None:
    try:
        supabase.table("affiliation_request_history").insert(
            {
                "request_id": request_id,
                "old_status": old_status,
                "new_status": new_status,
                "changed_by": changed_by,
                "comment": comment,
                "created_at": datetime.utcnow().isoformat(),
            }
        ).execute()
    except Exception as history_error:  # pragma: no cover - logging only
        logger.warning("Unable to record affiliation history: %s", history_error)


def create_affiliation_request(user_id: str, request_data: AffiliationRequestCreate) -> Dict:
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if user["role"] != "influencer":
        raise HTTPException(status_code=403, detail="Influenceurs uniquement")

    influencer = get_influencer_by_user_id(user_id)
    if not influencer:
        raise HTTPException(status_code=404, detail="Profil influencer non trouvé")

    product_query = (
        supabase.table("products").select("*").eq("id", request_data.product_id).execute()
    )
    if not product_query.data:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    product = product_query.data[0]
    merchant_id = product.get("merchant_id")
    if not merchant_id:
        raise HTTPException(status_code=400, detail="Produit sans marchand associé")

    existing_query = (
        supabase.table("affiliation_requests")
        .select("*")
        .eq("influencer_id", influencer["id"])
        .eq("product_id", request_data.product_id)
        .execute()
    )

    stats_payload = request_data.stats or None

    if existing_query.data:
        existing_request = existing_query.data[0]
        existing_status_db = existing_request.get("status")
        existing_status_app = map_affiliation_status_to_app(existing_status_db)

        if existing_status_app == "pending_approval":
            raise HTTPException(
                status_code=400,
                detail="Vous avez déjà une demande en attente pour ce produit",
            )
        if existing_status_app == "active":
            raise HTTPException(
                status_code=400, detail="Vous avez déjà accès à ce produit"
            )

        allow_resubmit = existing_status_app == "cancelled"
        if existing_status_app == "rejected":
            timestamp_source = (
                existing_request.get("reviewed_at")
                or existing_request.get("updated_at")
                or existing_request.get("created_at")
            )
            reopened_at = None
            if timestamp_source:
                try:
                    reopened_at = datetime.fromisoformat(timestamp_source.replace("Z", "+00:00"))
                except ValueError:
                    reopened_at = None
            if reopened_at:
                if datetime.utcnow() - reopened_at.replace(tzinfo=None) >= timedelta(days=30):
                    allow_resubmit = True
            if not allow_resubmit:
                raise HTTPException(
                    status_code=400,
                    detail="Vous devez attendre 30 jours avant de redemander ce produit",
                )

        if allow_resubmit:
            update_result = (
                supabase.table("affiliation_requests")
                .update(
                    {
                        "status": "pending",
                        "message": request_data.message,
                        "influencer_stats": stats_payload,
                        "merchant_response": None,
                        "reviewed_at": None,
                        "reviewed_by": None,
                    }
                )
                .eq("id", existing_request["id"])
                .execute()
            )

            update_error = getattr(update_result, "error", None)
            if update_error:
                error_message = getattr(update_error, "message", str(update_error))
                raise HTTPException(status_code=500, detail=error_message)

            if not update_result.data:
                raise HTTPException(
                    status_code=500, detail="Impossible de mettre à jour la demande existante"
                )

            record_affiliation_history(
                request_id=existing_request["id"],
                old_status=existing_status_db,
                new_status="pending",
                changed_by=user_id,
                comment="Demande réactivée",
            )

            return {
                "success": True,
                "request_id": existing_request["id"],
                "status": map_affiliation_status_to_app("pending"),
                "message": "Demande renvoyée au marchand",
            }

    affiliation_data = {
        "influencer_id": influencer["id"],
        "product_id": request_data.product_id,
        "merchant_id": merchant_id,
        "message": request_data.message,
        "influencer_stats": stats_payload,
        "status": "pending",
    }

    result = supabase.table("affiliation_requests").insert(affiliation_data).execute()

    insert_error = getattr(result, "error", None)
    if insert_error:
        error_message = getattr(insert_error, "message", str(insert_error))
        if "duplicate key value" in error_message or "affiliation_requests_influencer_id_product_id_key" in error_message:
            raise HTTPException(status_code=400, detail="Vous avez déjà une demande pour ce produit")
        raise HTTPException(status_code=500, detail=error_message)

    if not result.data:
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la demande")

    request_id = result.data[0]["id"]

    record_affiliation_history(
        request_id=request_id,
        old_status=None,
        new_status="pending",
        changed_by=user_id,
        comment="Demande créée",
    )

    return {
        "success": True,
        "request_id": request_id,
        "status": map_affiliation_status_to_app("pending"),
        "message": "Demande envoyée au marchand avec succès",
    }


def list_influencer_requests(user_id: str, status: Optional[str]) -> List[Dict]:
    user = get_user_by_id(user_id)
    if not user or user["role"] != "influencer":
        raise HTTPException(status_code=403, detail="Influenceurs uniquement")

    influencer = get_influencer_by_user_id(user_id)
    if not influencer:
        raise HTTPException(status_code=404, detail="Profil influencer non trouvé")

    query = (
        supabase.table("influencer_affiliation_requests")
        .select("*")
        .eq("influencer_id", influencer["id"])
    )

    if status:
        db_status = map_affiliation_status_to_db(status)
        if not db_status:
            raise HTTPException(status_code=400, detail="Statut invalide")
        query = query.eq("status", db_status)

    result = query.order("created_at", desc=True).execute()

    requests: List[Dict] = []
    for row in result.data or []:
        requests.append(
            {
                "id": row.get("id"),
                "product_id": row.get("product_id"),
                "status": map_affiliation_status_to_app(row.get("status")),
                "message": row.get("message"),
                "merchant_response": row.get("merchant_response"),
                "created_at": row.get("created_at"),
                "reviewed_at": row.get("reviewed_at"),
                "product_name": row.get("product_name"),
                "product_description": row.get("product_description"),
                "product_price": row.get("product_price"),
                "commission_rate": row.get("commission_rate"),
                "merchant_company": row.get("merchant_company"),
            }
        )

    return requests


def cancel_affiliation_request(user_id: str, request_id: str) -> Dict:
    user = get_user_by_id(user_id)
    if not user or user["role"] != "influencer":
        raise HTTPException(status_code=403, detail="Influenceurs uniquement")

    influencer = get_influencer_by_user_id(user_id)
    if not influencer:
        raise HTTPException(status_code=404, detail="Profil influencer non trouvé")

    request_query = (
        supabase.table("affiliation_requests")
        .select("*")
        .eq("id", request_id)
        .eq("influencer_id", influencer["id"])
        .execute()
    )

    if not request_query.data:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    request_data = request_query.data[0]

    if request_data.get("status") != "pending":
        raise HTTPException(status_code=400, detail="Seules les demandes en attente peuvent être annulées")

    update_result = (
        supabase.table("affiliation_requests")
        .update({"status": "cancelled"})
        .eq("id", request_id)
        .eq("status", "pending")
        .execute()
    )

    update_error = getattr(update_result, "error", None)
    if update_error:
        error_message = getattr(update_error, "message", str(update_error))
        raise HTTPException(status_code=500, detail=error_message)

    if not update_result.data:
        raise HTTPException(status_code=400, detail="Impossible d'annuler cette demande")

    record_affiliation_history(
        request_id=request_id,
        old_status="pending",
        new_status="cancelled",
        changed_by=user_id,
        comment="Demande annulée par l'influenceur",
    )

    return {
        "success": True,
        "status": map_affiliation_status_to_app("cancelled"),
        "message": "Demande annulée avec succès",
    }


def list_merchant_requests(user_id: str, status: Optional[str]) -> List[Dict]:
    user = get_user_by_id(user_id)
    if not user or user["role"] != "merchant":
        raise HTTPException(status_code=403, detail="Marchands uniquement")

    merchant = get_merchant_by_user_id(user_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Profil marchand introuvable")

    query = (
        supabase.table("merchant_affiliation_requests")
        .select("*")
        .eq("merchant_id", merchant["id"])
    )

    if status and status != "all":
        db_status = map_affiliation_status_to_db(status)
        if not db_status:
            raise HTTPException(status_code=400, detail="Statut invalide")
        query = query.eq("status", db_status)

    result = query.order("created_at", desc=True).execute()

    requests: List[Dict] = []
    for row in result.data or []:
        requests.append(
            {
                "id": row.get("id"),
                "product_id": row.get("product_id"),
                "influencer_id": row.get("influencer_id"),
                "status": map_affiliation_status_to_app(row.get("status")),
                "message": row.get("message"),
                "merchant_response": row.get("merchant_response"),
                "created_at": row.get("created_at"),
                "reviewed_at": row.get("reviewed_at"),
                "influencer_email": row.get("influencer_email"),
                "influencer_name": row.get("influencer_name"),
                "influencer_avatar": row.get("influencer_avatar"),
                "product_name": row.get("product_name"),
                "commission_rate": row.get("commission_rate"),
                "product_price": row.get("product_price"),
                "followers_count": row.get("followers_count"),
                "engagement_rate": row.get("engagement_rate"),
                "platforms": row.get("platforms"),
            }
        )

    return requests


def approve_affiliation_request(
    user_id: str,
    request_id: str,
    decision: AffiliationDecision,
) -> Dict:
    user = get_user_by_id(user_id)
    if not user or user["role"] != "merchant":
        raise HTTPException(status_code=403, detail="Marchands uniquement")

    merchant = get_merchant_by_user_id(user_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Profil marchand introuvable")

    request_query = (
        supabase.table("affiliation_requests").select("*").eq("id", request_id).limit(1).execute()
    )

    if not request_query.data:
        raise HTTPException(status_code=404, detail="Demande introuvable")

    request_record = request_query.data[0]

    if request_record.get("merchant_id") != merchant["id"]:
        raise HTTPException(status_code=403, detail="Cette demande n'appartient pas à votre boutique")

    if request_record.get("status") != "pending":
        raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")

    update_result = (
        supabase.table("affiliation_requests")
        .update(
            {
                "status": "approved",
                "merchant_response": decision.merchant_response,
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewed_by": user_id,
            }
        )
        .eq("id", request_id)
        .eq("status", "pending")
        .execute()
    )

    update_error = getattr(update_result, "error", None)
    if update_error:
        error_message = getattr(update_error, "message", str(update_error))
        raise HTTPException(status_code=500, detail=error_message)

    if not update_result.data:
        raise HTTPException(status_code=400, detail="Impossible d'approuver cette demande")

    record_affiliation_history(
        request_id=request_id,
        old_status="pending",
        new_status="approved",
        changed_by=user_id,
        comment="Demande approuvée par le marchand",
    )

    link_query = (
        supabase.table("trackable_links")
        .select("id, unique_code, short_code, full_url")
        .eq("influencer_id", request_record.get("influencer_id"))
        .eq("product_id", request_record.get("product_id"))
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    tracking_link = None
    if link_query.data:
        link = link_query.data[0]
        code = link.get("short_code") or link.get("unique_code")
        if code:
            base_url = os.getenv("TRACKING_BASE_URL", "http://localhost:8001")
            tracking_link = {
                "id": link.get("id"),
                "short_code": code,
                "url": f"{base_url}/r/{code}",
            }

    return {
        "success": True,
        "message": "Demande approuvée avec succès",
        "status": map_affiliation_status_to_app("approved"),
        "tracking_link": tracking_link,
    }


def reject_affiliation_request(
    user_id: str,
    request_id: str,
    decision: AffiliationDecision,
) -> Dict:
    user = get_user_by_id(user_id)
    if not user or user["role"] != "merchant":
        raise HTTPException(status_code=403, detail="Marchands uniquement")

    if not decision.merchant_response or not decision.merchant_response.strip():
        raise HTTPException(status_code=400, detail="Merci de fournir une raison de refus")

    merchant = get_merchant_by_user_id(user_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Profil marchand introuvable")

    request_query = (
        supabase.table("affiliation_requests").select("*").eq("id", request_id).limit(1).execute()
    )

    if not request_query.data:
        raise HTTPException(status_code=404, detail="Demande introuvable")

    request_record = request_query.data[0]

    if request_record.get("merchant_id") != merchant["id"]:
        raise HTTPException(status_code=403, detail="Cette demande n'appartient pas à votre boutique")

    if request_record.get("status") != "pending":
        raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")

    update_result = (
        supabase.table("affiliation_requests")
        .update(
            {
                "status": "rejected",
                "merchant_response": decision.merchant_response.strip(),
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewed_by": user_id,
            }
        )
        .eq("id", request_id)
        .eq("status", "pending")
        .execute()
    )

    update_error = getattr(update_result, "error", None)
    if update_error:
        error_message = getattr(update_error, "message", str(update_error))
        raise HTTPException(status_code=500, detail=error_message)

    if not update_result.data:
        raise HTTPException(status_code=400, detail="Impossible de refuser cette demande")

    record_affiliation_history(
        request_id=request_id,
        old_status="pending",
        new_status="rejected",
        changed_by=user_id,
        comment="Demande refusée par le marchand",
    )

    return {
        "success": True,
        "status": map_affiliation_status_to_app("rejected"),
        "message": "Demande refusée",
    }


def get_affiliation_stats(user_id: str) -> Dict:
    user = get_user_by_id(user_id)
    if not user or user["role"] != "merchant":
        raise HTTPException(status_code=403, detail="Marchands uniquement")

    merchant = get_merchant_by_user_id(user_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Profil marchand introuvable")

    stats_query = (
        supabase.table("affiliation_requests_stats")
        .select("*")
        .eq("merchant_id", merchant["id"])
        .execute()
    )

    if stats_query.data:
        return stats_query.data[0]

    return {
        "total_requests": 0,
        "pending_requests": 0,
        "approved_requests": 0,
        "rejected_requests": 0,
        "approval_rate": 0,
        "avg_response_time_hours": 0,
    }
