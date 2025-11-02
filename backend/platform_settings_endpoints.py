"""
Endpoints pour la gestion des paramètres de plateforme (Admin uniquement)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from supabase_client import get_supabase_client
from auth import verify_token

router = APIRouter(prefix="/api/admin/platform-settings", tags=["Platform Settings"])

# ============================================
# MODÈLES PYDANTIC
# ============================================

class PlatformSettingsResponse(BaseModel):
    """Réponse avec les paramètres de plateforme"""
    id: str
    min_payout_amount: float
    payout_frequency: str
    payout_day: Optional[str]
    validation_delay_days: int
    platform_commission_rate: float
    auto_payout_enabled: bool
    created_at: str
    updated_at: str
    updated_by: Optional[str]

class PlatformSettingsUpdate(BaseModel):
    """Modèle pour mise à jour des paramètres"""
    min_payout_amount: Optional[float] = Field(None, ge=10, le=1000, description="Montant minimum de retrait (10€ - 1000€)")
    payout_frequency: Optional[str] = Field(None, pattern="^(daily|weekly|biweekly|monthly)$")
    payout_day: Optional[str] = Field(None, pattern="^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$")
    validation_delay_days: Optional[int] = Field(None, ge=0, le=90, description="Délai de validation (0-90 jours)")
    platform_commission_rate: Optional[float] = Field(None, ge=0, le=50, description="Commission plateforme (0-50%)")
    auto_payout_enabled: Optional[bool] = None

# ============================================
# ENDPOINTS
# ============================================

@router.get("", response_model=PlatformSettingsResponse, summary="Obtenir les paramètres de plateforme")
async def get_platform_settings(user: dict = Depends(verify_token)):
    """
    Récupère les paramètres globaux de la plateforme.
    Accessible uniquement aux admins.
    """
    # Vérifier que l'utilisateur est admin
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    
    try:
        supabase = get_supabase_client()
        
        # Récupérer les paramètres (il n'y a qu'une seule ligne)
        response = supabase.table("platform_settings") \
            .select("*") \
            .limit(1) \
            .execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paramètres de plateforme non trouvés. Veuillez exécuter le script SQL d'initialisation."
            )
        
        settings = response.data[0]
        
        return PlatformSettingsResponse(
            id=settings["id"],
            min_payout_amount=float(settings["min_payout_amount"]),
            payout_frequency=settings["payout_frequency"],
            payout_day=settings.get("payout_day"),
            validation_delay_days=settings["validation_delay_days"],
            platform_commission_rate=float(settings["platform_commission_rate"]),
            auto_payout_enabled=settings["auto_payout_enabled"],
            created_at=settings["created_at"],
            updated_at=settings["updated_at"],
            updated_by=settings.get("updated_by")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des paramètres: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des paramètres: {str(e)}"
        )


@router.post("", response_model=PlatformSettingsResponse, summary="Mettre à jour les paramètres")
async def update_platform_settings(
    updates: PlatformSettingsUpdate,
    user: dict = Depends(verify_token)
):
    """
    Met à jour les paramètres globaux de la plateforme.
    Accessible uniquement aux admins.
    
    **Validations:**
    - min_payout_amount: 10€ - 1000€
    - payout_frequency: daily, weekly, biweekly, monthly
    - payout_day: lundi à dimanche
    - validation_delay_days: 0 - 90 jours
    - platform_commission_rate: 0% - 50%
    """
    # Vérifier que l'utilisateur est admin
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    
    try:
        supabase = get_supabase_client()
        
        # Construire l'objet de mise à jour (seulement les champs fournis)
        update_data = {}
        if updates.min_payout_amount is not None:
            update_data["min_payout_amount"] = updates.min_payout_amount
        if updates.payout_frequency is not None:
            update_data["payout_frequency"] = updates.payout_frequency
        if updates.payout_day is not None:
            update_data["payout_day"] = updates.payout_day
        if updates.validation_delay_days is not None:
            update_data["validation_delay_days"] = updates.validation_delay_days
        if updates.platform_commission_rate is not None:
            update_data["platform_commission_rate"] = updates.platform_commission_rate
        if updates.auto_payout_enabled is not None:
            update_data["auto_payout_enabled"] = updates.auto_payout_enabled
        
        # Ajouter l'ID de l'admin qui fait la modification
        update_data["updated_by"] = user["id"]
        
        if not update_data or update_data == {"updated_by": user["id"]}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucune modification fournie"
            )
        
        # Récupérer d'abord l'ID du settings (il n'y a qu'une ligne)
        response = supabase.table("platform_settings") \
            .select("id") \
            .limit(1) \
            .execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paramètres de plateforme non trouvés"
            )
        
        settings_id = response.data[0]["id"]
        
        # Mettre à jour les paramètres
        update_response = supabase.table("platform_settings") \
            .update(update_data) \
            .eq("id", settings_id) \
            .execute()
        
        if not update_response.data or len(update_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la mise à jour des paramètres"
            )
        
        updated_settings = update_response.data[0]
        
        print(f"✅ Paramètres de plateforme mis à jour par l'admin {user['email']}")
        
        return PlatformSettingsResponse(
            id=updated_settings["id"],
            min_payout_amount=float(updated_settings["min_payout_amount"]),
            payout_frequency=updated_settings["payout_frequency"],
            payout_day=updated_settings.get("payout_day"),
            validation_delay_days=updated_settings["validation_delay_days"],
            platform_commission_rate=float(updated_settings["platform_commission_rate"]),
            auto_payout_enabled=updated_settings["auto_payout_enabled"],
            created_at=updated_settings["created_at"],
            updated_at=updated_settings["updated_at"],
            updated_by=updated_settings.get("updated_by")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour des paramètres: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )


@router.get("/public/min-payout", summary="Obtenir le montant minimum de retrait (public)")
async def get_min_payout_public():
    """
    Endpoint public pour obtenir uniquement le montant minimum de retrait.
    Utilisé par les influenceurs pour connaître le seuil de paiement.
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("platform_settings") \
            .select("min_payout_amount") \
            .limit(1) \
            .execute()
        
        if not response.data or len(response.data) == 0:
            # Valeur par défaut si non configuré
            return {"min_payout_amount": 50.00}
        
        return {
            "min_payout_amount": float(response.data[0]["min_payout_amount"])
        }
    
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du min payout: {str(e)}")
        # Retourner valeur par défaut en cas d'erreur
        return {"min_payout_amount": 50.00}
