# Backend - Endpoints Collaboration

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib

collaboration_router = APIRouter(prefix="/api/collaborations", tags=["collaborations"])

# ============================================
# MODELS
# ============================================

class CollaborationRequest(BaseModel):
    influencer_id: str
    product_id: str
    commission_rate: float
    message: Optional[str] = None

class CounterOffer(BaseModel):
    counter_commission: float
    message: Optional[str] = None

class RejectRequest(BaseModel):
    reason: Optional[str] = None

class ContractSignature(BaseModel):
    signature: str  # Hash de la signature électronique

# ============================================
# ENDPOINTS
# ============================================

@collaboration_router.post("/requests")
async def create_collaboration_request(
    data: CollaborationRequest,
    payload: dict = Depends(verify_token)
):
    """
    Créer une demande de collaboration
    Marchand → Influenceur pour promouvoir un produit
    """
    merchant_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Appeler la fonction SQL
        result = supabase.rpc(
            "create_collaboration_request",
            {
                "p_merchant_id": merchant_id,
                "p_influencer_id": data.influencer_id,
                "p_product_id": data.product_id,
                "p_commission_rate": data.commission_rate,
                "p_message": data.message
            }
        ).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        request_data = result.data[0]
        
        return {
            "success": True,
            "message": "Demande envoyée avec succès",
            "request_id": request_data["request_id"],
            "status": request_data["status"],
            "expires_at": request_data["expires_at"]
        }
        
    except Exception as e:
        error_msg = str(e)
        if "existe déjà" in error_msg:
            raise HTTPException(status_code=409, detail="Une demande existe déjà pour ce produit")
        elif "Produit non trouvé" in error_msg:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        raise HTTPException(status_code=500, detail=error_msg)


@collaboration_router.get("/requests/received")
async def get_received_requests(
    status: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """
    Récupérer les demandes reçues (pour influenceur)
    """
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("collaboration_requests") \
            .select("""
                *,
                merchant:merchant_id (
                    id,
                    first_name,
                    last_name,
                    email,
                    company_name
                ),
                product:product_id (
                    id,
                    name,
                    price,
                    image_url
                )
            """) \
            .eq("influencer_id", influencer_id) \
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "requests": result.data,
            "total": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collaboration_router.get("/requests/sent")
async def get_sent_requests(
    status: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """
    Récupérer les demandes envoyées (pour marchand)
    """
    merchant_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("collaboration_requests") \
            .select("""
                *,
                influencer:influencer_id (
                    id,
                    first_name,
                    last_name,
                    email,
                    username
                ),
                product:product_id (
                    id,
                    name,
                    price,
                    image_url
                ),
                affiliate_link:affiliate_link_id (
                    id,
                    code,
                    clicks,
                    conversions
                )
            """) \
            .eq("merchant_id", merchant_id) \
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "requests": result.data,
            "total": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collaboration_router.put("/requests/{request_id}/accept")
async def accept_request(
    request_id: str,
    payload: dict = Depends(verify_token)
):
    """
    Accepter une demande de collaboration (influenceur)
    """
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "accept_collaboration_request",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Demande acceptée ! Vous devez maintenant signer le contrat."
        }
        
    except Exception as e:
        error_msg = str(e)
        if "non valide" in error_msg or "déjà traitée" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@collaboration_router.put("/requests/{request_id}/reject")
async def reject_request(
    request_id: str,
    data: RejectRequest,
    payload: dict = Depends(verify_token)
):
    """
    Refuser une demande de collaboration (influenceur)
    """
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "reject_collaboration_request",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id,
                "p_reason": data.reason
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Demande refusée"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collaboration_router.put("/requests/{request_id}/counter-offer")
async def counter_offer(
    request_id: str,
    data: CounterOffer,
    payload: dict = Depends(verify_token)
):
    """
    Faire une contre-offre sur la commission (influenceur)
    """
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "counter_offer_collaboration",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id,
                "p_counter_commission": data.counter_commission,
                "p_message": data.message
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Contre-offre envoyée au marchand"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collaboration_router.post("/requests/{request_id}/sign-contract")
async def sign_contract(
    request_id: str,
    data: ContractSignature,
    payload: dict = Depends(verify_token)
):
    """
    Signer le contrat de collaboration
    """
    user_id = payload.get("user_id")
    user_role = payload.get("role", "merchant")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Accepter le contrat
        result = supabase.rpc(
            "accept_contract",
            {
                "p_request_id": request_id,
                "p_user_id": user_id,
                "p_user_role": user_role,
                "p_signature": data.signature
            }
        ).execute()
        
        # Si c'est l'influenceur qui signe (dernière signature),
        # générer automatiquement le lien d'affiliation
        if user_role == "influencer":
            link_result = supabase.rpc(
                "generate_affiliate_link_from_collaboration",
                {"p_request_id": request_id}
            ).execute()
            
            link_id = link_result.data if link_result.data else None
            
            return {
                "success": True,
                "message": "Contrat signé ! Votre lien d'affiliation a été généré.",
                "affiliate_link_id": link_id
            }
        
        return {
            "success": True,
            "message": "Contrat signé avec succès"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collaboration_router.get("/requests/{request_id}")
async def get_request_details(
    request_id: str,
    payload: dict = Depends(verify_token)
):
    """
    Récupérer les détails d'une demande
    """
    user_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.table("collaboration_requests") \
            .select("""
                *,
                merchant:merchant_id (
                    id,
                    first_name,
                    last_name,
                    email,
                    company_name
                ),
                influencer:influencer_id (
                    id,
                    first_name,
                    last_name,
                    email,
                    username
                ),
                product:product_id (
                    id,
                    name,
                    price,
                    description,
                    image_url
                ),
                affiliate_link:affiliate_link_id (
                    id,
                    code,
                    clicks,
                    conversions,
                    total_sales,
                    total_commission
                )
            """) \
            .eq("id", request_id) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        # Vérifier que l'utilisateur est impliqué
        request_data = result.data
        if user_id not in [request_data["merchant_id"], request_data["influencer_id"]]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Marquer comme vue par l'influenceur
        if user_id == request_data["influencer_id"] and not request_data.get("viewed_by_influencer"):
            supabase.table("collaboration_requests") \
                .update({
                    "viewed_by_influencer": True,
                    "viewed_at": datetime.now().isoformat()
                }) \
                .eq("id", request_id) \
                .execute()
        
        # Récupérer l'historique
        history = supabase.table("collaboration_history") \
            .select("*") \
            .eq("collaboration_request_id", request_id) \
            .order("created_at", desc=False) \
            .execute()
        
        return {
            "success": True,
            "request": request_data,
            "history": history.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@collaboration_router.get("/requests/{request_id}/contract")
async def get_contract_terms(request_id: str):
    """
    Récupérer les termes du contrat
    """
    return {
        "success": True,
        "contract": {
            "version": "v1.0",
            "terms": [
                {
                    "title": "1. Respect Éthique",
                    "content": "L'influenceur s'engage à promouvoir le produit de manière éthique et honnête, sans fausses déclarations."
                },
                {
                    "title": "2. Transparence",
                    "content": "L'influenceur doit clairement indiquer qu'il s'agit d'un partenariat commercial (#ad, #sponsored)."
                },
                {
                    "title": "3. Commission",
                    "content": "La commission convenue sera versée pour chaque vente générée via le lien d'affiliation."
                },
                {
                    "title": "4. Durée",
                    "content": "Le contrat est valable pour 12 mois, renouvelable par accord mutuel."
                },
                {
                    "title": "5. Résiliation",
                    "content": "Chaque partie peut résilier avec un préavis de 30 jours."
                },
                {
                    "title": "6. Propriété Intellectuelle",
                    "content": "Le marchand conserve tous les droits sur le produit. L'influenceur conserve ses droits sur son contenu."
                },
                {
                    "title": "7. Confidentialité",
                    "content": "Les termes financiers de cet accord sont confidentiels."
                },
                {
                    "title": "8. Conformité Légale",
                    "content": "Les deux parties s'engagent à respecter toutes les lois applicables."
                }
            ]
        }
    }

# ============================================
# COMMENTAIRES
# ============================================
"""
Endpoints de collaboration Marchand-Influenceur

Flow complet:
1. Marchand envoie demande → POST /requests
2. Influenceur voit demandes → GET /requests/received
3. Influenceur accepte/refuse/contre-offre → PUT /requests/{id}/accept|reject|counter-offer
4. Les deux signent le contrat → POST /requests/{id}/sign-contract
5. Lien d'affiliation généré automatiquement
6. Marchand suit le statut → GET /requests/sent
"""
