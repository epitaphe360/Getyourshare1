"""
API Endpoints 2FA - Two-Factor Authentication
Gestion authentification à deux facteurs

Endpoints:
- POST /api/2fa/setup - Configurer 2FA
- POST /api/2fa/enable - Activer 2FA (après vérification code)
- POST /api/2fa/disable - Désactiver 2FA
- POST /api/2fa/verify - Vérifier code 2FA (login)
- POST /api/2fa/send-email-code - Envoyer code par email
- GET /api/2fa/status - Statut 2FA utilisateur
- POST /api/2fa/regenerate-backup-codes - Régénérer codes backup
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
import structlog

from auth import get_current_user
from services.twofa_service import twofa_service, TwoFactorSetup

router = APIRouter(prefix="/api/2fa", tags=["2FA"])
logger = structlog.get_logger()


# ============================================
# PYDANTIC MODELS
# ============================================

class Setup2FARequest(BaseModel):
    """Request pour setup 2FA"""
    method: str = Field(default="totp", pattern="^(totp|email)$", description="Méthode: totp ou email")

    class Config:
        json_schema_extra = {
            "example": {
                "method": "totp"
            }
        }


class Enable2FARequest(BaseModel):
    """Request pour activer 2FA"""
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$", description="Code à 6 chiffres")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class Verify2FARequest(BaseModel):
    """Request pour vérifier code 2FA"""
    code: str = Field(..., min_length=6, description="Code 2FA (6 chiffres) ou backup code (12 chiffres)")
    method: str = Field(default="totp", pattern="^(totp|email|backup)$", description="Méthode de vérification")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456",
                "method": "totp"
            }
        }


class TwoFAStatusResponse(BaseModel):
    """Statut 2FA"""
    enabled: bool
    method: Optional[str] = None
    backup_codes_remaining: int = 0
    enabled_at: Optional[str] = None


class TwoFASetupResponse(BaseModel):
    """Response setup 2FA"""
    success: bool
    message: str
    secret: Optional[str] = None
    qr_code_url: Optional[str] = None
    backup_codes: Optional[List[str]] = None
    manual_entry_key: Optional[str] = None


# ============================================
# ENDPOINTS
# ============================================

@router.post("/setup", response_model=TwoFASetupResponse, status_code=201)
async def setup_2fa(
    request: Setup2FARequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Configurer 2FA pour l'utilisateur

    **Étapes:**
    1. Appeler cet endpoint pour obtenir QR code et backup codes
    2. Scanner le QR code avec Google Authenticator / Authy
    3. Sauvegarder les backup codes en lieu sûr
    4. Appeler `/enable` avec un code pour activer

    **Méthodes:**
    - `totp`: Application authenticator (recommandé)
    - `email`: Code par email (moins sécurisé)

    **Returns:**
    - QR code (data URI)
    - Secret pour saisie manuelle
    - 10 backup codes (IMPORTANT: sauvegarder!)
    """
    user_id = current_user.get("id")
    user_email = current_user.get("email")

    try:
        # Vérifier si 2FA déjà activé
        status_2fa = await twofa_service.get_2fa_status(user_id)

        if status_2fa.get("enabled"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA déjà activé. Désactivez d'abord pour reconfigurer."
            )

        # Setup 2FA
        setup_data = await twofa_service.setup_2fa(
            user_id=user_id,
            user_email=user_email,
            method=request.method
        )

        logger.info("2fa_setup_completed", user_id=user_id, method=request.method)

        return TwoFASetupResponse(
            success=True,
            message="2FA configuré. Scannez le QR code et activez avec un code.",
            secret=setup_data.secret,
            qr_code_url=setup_data.qr_code_url,
            backup_codes=setup_data.backup_codes,
            manual_entry_key=setup_data.manual_entry_key
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("2fa_setup_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la configuration 2FA"
        )


@router.post("/enable", response_model=dict)
async def enable_2fa(
    request: Enable2FARequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Activer 2FA après configuration

    **Requis:**
    - Code généré par votre application authenticator
    - Ou code reçu par email

    **Important:**
    Une fois activé, vous devrez fournir un code 2FA à chaque connexion.
    Sauvegardez vos backup codes!
    """
    user_id = current_user.get("id")

    try:
        success = await twofa_service.enable_2fa(user_id, request.code)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code invalide. Vérifiez votre application authenticator."
            )

        logger.info("2fa_enabled", user_id=user_id)

        return {
            "success": True,
            "message": "2FA activé avec succès! Vous devrez fournir un code à chaque connexion.",
            "enabled": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("2fa_enable_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'activation 2FA"
        )


@router.post("/disable", response_model=dict)
async def disable_2fa(
    request: Verify2FARequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Désactiver 2FA

    **Requis:**
    - Code 2FA valide (pour confirmation)

    **Attention:**
    Désactiver 2FA réduit la sécurité de votre compte.
    """
    user_id = current_user.get("id")

    try:
        # Vérifier code avant désactivation (sécurité)
        is_valid = await twofa_service.verify_2fa(user_id, request.code, request.method)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code 2FA invalide"
            )

        # Désactiver
        success = await twofa_service.disable_2fa(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la désactivation"
            )

        logger.info("2fa_disabled", user_id=user_id)

        return {
            "success": True,
            "message": "2FA désactivé. Votre compte est maintenant moins sécurisé.",
            "enabled": False
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("2fa_disable_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la désactivation 2FA"
        )


@router.post("/verify", response_model=dict)
async def verify_2fa(
    request: Verify2FARequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifier code 2FA

    **Méthodes:**
    - `totp`: Code de l'app authenticator (6 chiffres)
    - `email`: Code reçu par email (6 chiffres)
    - `backup`: Backup code (format: XXXX-XXXX-XXXX)

    **Utilisé lors du login après mot de passe.**
    """
    user_id = current_user.get("id")

    try:
        is_valid = await twofa_service.verify_2fa(
            user_id=user_id,
            code=request.code,
            method=request.method
        )

        if not is_valid:
            logger.warning("2fa_verification_failed", user_id=user_id, method=request.method)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_code",
                    "message": "Code 2FA invalide ou expiré",
                    "method": request.method
                }
            )

        logger.info("2fa_verified", user_id=user_id, method=request.method)

        return {
            "success": True,
            "verified": True,
            "message": "Code 2FA valide",
            "method": request.method
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("2fa_verify_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la vérification 2FA"
        )


@router.post("/send-email-code", response_model=dict)
async def send_email_code(current_user: dict = Depends(get_current_user)):
    """
    Envoyer code 2FA par email

    **Utilisé si:**
    - Vous avez perdu votre téléphone
    - Application authenticator non disponible

    **Code valide pendant 5 minutes.**
    """
    user_id = current_user.get("id")
    user_email = current_user.get("email")

    try:
        # Vérifier que 2FA est activé
        status_2fa = await twofa_service.get_2fa_status(user_id)

        if not status_2fa.get("enabled"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA non activé"
            )

        # Envoyer code
        success = await twofa_service.send_email_code(user_id, user_email)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de l'envoi du code"
            )

        logger.info("2fa_email_code_sent", user_id=user_id)

        return {
            "success": True,
            "message": f"Code 2FA envoyé à {user_email}. Valide pendant 5 minutes.",
            "email": user_email,
            "expires_in_seconds": 300
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("2fa_send_email_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'envoi du code"
        )


@router.get("/status", response_model=TwoFAStatusResponse)
async def get_2fa_status(current_user: dict = Depends(get_current_user)):
    """
    Obtenir le statut 2FA de l'utilisateur

    **Returns:**
    - enabled: 2FA activé ou non
    - method: totp ou email
    - backup_codes_remaining: Nombre de codes backup restants
    - enabled_at: Date d'activation
    """
    user_id = current_user.get("id")

    try:
        status_data = await twofa_service.get_2fa_status(user_id)

        return TwoFAStatusResponse(**status_data)

    except Exception as e:
        logger.error("get_2fa_status_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du statut 2FA"
        )


@router.post("/regenerate-backup-codes", response_model=dict)
async def regenerate_backup_codes(
    request: Verify2FARequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Régénérer les backup codes

    **Requis:**
    - Code 2FA valide (sécurité)

    **Attention:**
    Les anciens backup codes seront invalidés!
    Sauvegardez les nouveaux codes en lieu sûr.
    """
    user_id = current_user.get("id")

    try:
        # Vérifier code
        is_valid = await twofa_service.verify_2fa(user_id, request.code, request.method)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code 2FA invalide"
            )

        # Générer nouveaux codes
        new_codes = twofa_service.generate_backup_codes()
        hashed_codes = [twofa_service.hash_backup_code(code) for code in new_codes]

        # Sauvegarder en DB
        from supabase_client import supabase
        from datetime import datetime

        supabase.table('user_2fa').update({
            'backup_codes': hashed_codes,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('user_id', user_id).execute()

        logger.info("backup_codes_regenerated", user_id=user_id)

        return {
            "success": True,
            "message": "Nouveaux backup codes générés. SAUVEGARDEZ-LES!",
            "backup_codes": new_codes,
            "count": len(new_codes)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("regenerate_backup_codes_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la régénération des backup codes"
        )
