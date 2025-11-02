"""
============================================
ENDPOINTS API MODÉRATION ADMINISTRATEUR
Gestion de la queue de modération des produits
============================================
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

from auth import get_current_user, role_checker
from moderation_service import moderate_product, ModerationStats

# Configuration Supabase
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("⚠️ Warning: Supabase not configured for moderation")
    supabase = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

router = APIRouter(prefix="/api/admin/moderation", tags=["Admin Moderation"])

# ============================================
# PYDANTIC MODELS
# ============================================

class ModerationReviewRequest(BaseModel):
    """Request pour réviser un produit"""
    moderation_id: str
    decision: str  # 'approve' ou 'reject'
    comment: Optional[str] = None
    
    @validator('decision')
    def validate_decision(cls, v):
        if v not in ['approve', 'reject']:
            raise ValueError("Decision must be 'approve' or 'reject'")
        return v

class BulkModerationRequest(BaseModel):
    """Request pour approuver/rejeter plusieurs produits"""
    moderation_ids: List[str]
    decision: str
    comment: Optional[str] = None
    
    @validator('decision')
    def validate_decision(cls, v):
        if v not in ['approve', 'reject']:
            raise ValueError("Decision must be 'approve' or 'reject'")
        return v

# ============================================
# ENDPOINTS ADMIN
# ============================================

@router.get("/pending")
async def get_pending_moderation(
    limit: int = 50,
    offset: int = 0,
    risk_level: Optional[str] = None,
    current_user: dict = Depends(role_checker(["admin"]))
):
    """
    Liste des produits en attente de modération
    Accessible uniquement aux admins
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        # Construire la requête
        query = supabase.from_("v_pending_moderation").select("*")
        
        # Filtrer par risk_level si fourni
        if risk_level:
            query = query.eq("ai_risk_level", risk_level)
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        # Exécuter
        response = query.execute()
        
        # Compter le total
        count_response = supabase.from_("moderation_queue")\
            .select("id", count="exact")\
            .eq("status", "pending")\
            .execute()
        
        return {
            "data": response.data or [],
            "total": count_response.count or 0,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        print(f"❌ Error fetching pending moderation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_moderation_stats(
    period: str = "today",  # today, week, month, all
    current_user: dict = Depends(role_checker(["admin"]))
):
    """
    Statistiques de modération
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        # Déterminer la date de début selon la période
        if period == "today":
            date_filter = "created_at >= CURRENT_DATE"
        elif period == "week":
            date_filter = "created_at >= CURRENT_DATE - INTERVAL '7 days'"
        elif period == "month":
            date_filter = "created_at >= CURRENT_DATE - INTERVAL '30 days'"
        else:
            date_filter = "1=1"  # All time
        
        # Stats globales
        stats_response = supabase.from_("moderation_queue")\
            .select("status, ai_decision, ai_risk_level, ai_confidence")\
            .execute()
        
        data = stats_response.data or []
        
        # Calculer les stats
        total = len(data)
        pending = len([x for x in data if x["status"] == "pending"])
        approved = len([x for x in data if x["status"] == "approved"])
        rejected = len([x for x in data if x["status"] == "rejected"])
        
        # Par risk level
        by_risk = {}
        for item in data:
            risk = item.get("ai_risk_level", "unknown")
            by_risk[risk] = by_risk.get(risk, 0) + 1
        
        # Confidence moyenne
        confidences = [x.get("ai_confidence", 0) for x in data if x.get("ai_confidence")]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "period": period,
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "approval_rate": approved / max(total, 1),
            "by_risk_level": by_risk,
            "avg_ai_confidence": round(avg_confidence, 2),
            "needs_review": pending
        }
        
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review")
async def review_moderation(
    request: ModerationReviewRequest = Body(...),
    current_user: dict = Depends(role_checker(["admin"]))
):
    """
    Approuver ou rejeter un produit en modération
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        admin_user_id = current_user.get("id")
        
        if request.decision == "approve":
            # Appeler la fonction SQL pour approuver
            response = supabase.rpc(
                "approve_moderation",
                {
                    "p_moderation_id": request.moderation_id,
                    "p_admin_user_id": admin_user_id,
                    "p_comment": request.comment
                }
            ).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Moderation not found or already reviewed")
            
            # Si approuvé, créer le produit dans la table products
            # (TODO: implémenter la création automatique du produit)
            
            return {
                "success": True,
                "decision": "approved",
                "message": "Produit approuvé avec succès"
            }
            
        else:  # reject
            response = supabase.rpc(
                "reject_moderation",
                {
                    "p_moderation_id": request.moderation_id,
                    "p_admin_user_id": admin_user_id,
                    "p_comment": request.comment or "Rejeté par l'admin"
                }
            ).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Moderation not found or already reviewed")
            
            # TODO: Notifier le merchant du rejet
            
            return {
                "success": True,
                "decision": "rejected",
                "message": "Produit rejeté"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error reviewing moderation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-review")
async def bulk_review_moderation(
    request: BulkModerationRequest = Body(...),
    current_user: dict = Depends(role_checker(["admin"]))
):
    """
    Approuver ou rejeter plusieurs produits en une fois
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        admin_user_id = current_user.get("id")
        results = {
            "success": [],
            "failed": []
        }
        
        for moderation_id in request.moderation_ids:
            try:
                if request.decision == "approve":
                    supabase.rpc(
                        "approve_moderation",
                        {
                            "p_moderation_id": moderation_id,
                            "p_admin_user_id": admin_user_id,
                            "p_comment": request.comment
                        }
                    ).execute()
                else:
                    supabase.rpc(
                        "reject_moderation",
                        {
                            "p_moderation_id": moderation_id,
                            "p_admin_user_id": admin_user_id,
                            "p_comment": request.comment or "Rejeté en masse"
                        }
                    ).execute()
                
                results["success"].append(moderation_id)
                
            except Exception as e:
                results["failed"].append({
                    "moderation_id": moderation_id,
                    "error": str(e)
                })
        
        return {
            "processed": len(request.moderation_ids),
            "succeeded": len(results["success"]),
            "failed": len(results["failed"]),
            "results": results
        }
        
    except Exception as e:
        print(f"❌ Error in bulk review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{moderation_id}")
async def get_moderation_details(
    moderation_id: str,
    current_user: dict = Depends(role_checker(["admin"]))
):
    """
    Détails complets d'un produit en modération
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        # Récupérer la modération
        moderation_response = supabase.from_("moderation_queue")\
            .select("""
                *,
                merchants(company_name, email, phone),
                users(email, full_name)
            """)\
            .eq("id", moderation_id)\
            .single()\
            .execute()
        
        if not moderation_response.data:
            raise HTTPException(status_code=404, detail="Moderation not found")
        
        # Récupérer l'historique
        history_response = supabase.from_("moderation_history")\
            .select("*")\
            .eq("moderation_id", moderation_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return {
            "moderation": moderation_response.data,
            "history": history_response.data or []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching moderation details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchant/{merchant_id}")
async def get_merchant_moderation_history(
    merchant_id: str,
    limit: int = 20,
    current_user: dict = Depends(role_checker(["admin"]))
):
    """
    Historique de modération d'un merchant spécifique
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        response = supabase.from_("moderation_queue")\
            .select("*")\
            .eq("merchant_id", merchant_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        data = response.data or []
        
        # Stats du merchant
        total = len(data)
        approved = len([x for x in data if x["status"] == "approved"])
        rejected = len([x for x in data if x["status"] == "rejected"])
        pending = len([x for x in data if x["status"] == "pending"])
        
        return {
            "merchant_id": merchant_id,
            "history": data,
            "stats": {
                "total": total,
                "approved": approved,
                "rejected": rejected,
                "pending": pending,
                "rejection_rate": rejected / max(total, 1)
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching merchant history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ENDPOINTS MERCHANT (voir leur propre statut)
# ============================================

@router.get("/my-pending")
async def get_my_pending_products(
    current_user: dict = Depends(get_current_user)
):
    """
    Permet aux merchants de voir leurs produits en attente de modération
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    if current_user.get("role") != "merchant":
        raise HTTPException(status_code=403, detail="Only merchants can access this endpoint")
    
    try:
        user_id = current_user.get("id")
        
        response = supabase.from_("moderation_queue")\
            .select("id, product_name, status, ai_risk_level, ai_reason, created_at")\
            .eq("user_id", user_id)\
            .eq("status", "pending")\
            .order("created_at", desc=True)\
            .execute()
        
        return {
            "pending_products": response.data or [],
            "count": len(response.data or [])
        }
        
    except Exception as e:
        print(f"❌ Error fetching merchant pending: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# WEBHOOK / TEST
# ============================================

@router.post("/test-moderation")
async def test_moderation_service(
    product_name: str = Body(...),
    description: str = Body(...),
    current_user: dict = Depends(role_checker(["admin"]))
):
    """
    Endpoint de test pour essayer la modération IA sans créer de produit
    """
    try:
        result = await moderate_product(
            product_name=product_name,
            description=description,
            use_ai=True
        )
        
        return {
            "test_result": result,
            "message": "Test de modération effectué avec succès"
        }
        
    except Exception as e:
        print(f"❌ Error in test moderation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
