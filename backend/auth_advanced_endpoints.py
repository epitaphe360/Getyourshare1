"""
Endpoints d'authentification avancés
- Réinitialisation de mot de passe
- Vérification d'email
- 2FA (Two-Factor Authentication)
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime, timedelta
from typing import Optional
import secrets
import pyotp
import qrcode
from io import BytesIO
import base64
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/auth", tags=["Authentication Advanced"])
limiter = Limiter(key_func=get_remote_address)

# Store temporaire pour les tokens (en production, utiliser Redis ou DB)
PASSWORD_RESET_TOKENS = {}
EMAIL_VERIFICATION_TOKENS = {}
TWO_FA_SECRETS = {}

# ============================================
# MODELS
# ============================================

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: constr(min_length=32, max_length=256)
    new_password: constr(min_length=8, max_length=128)

class EmailVerification(BaseModel):
    token: constr(min_length=32, max_length=256)

class TwoFactorSetup(BaseModel):
    pass

class TwoFactorVerify(BaseModel):
    code: constr(min_length=6, max_length=6, pattern="^[0-9]{6}$")

class TwoFactorDisable(BaseModel):
    password: str
    code: constr(min_length=6, max_length=6, pattern="^[0-9]{6}$")

# ============================================
# PASSWORD RESET ENDPOINTS
# ============================================

@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(request: Request, data: PasswordResetRequest):
    """
    Demander une réinitialisation de mot de passe
    Envoie un email avec un lien de réinitialisation
    """
    email = data.email
    
    # Générer un token unique
    token = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=1)
    
    # Stocker le token
    PASSWORD_RESET_TOKENS[token] = {
        "email": email,
        "expires_at": expiration,
        "used": False
    }
    
    # TODO: Envoyer email avec le lien
    # reset_link = f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"
    # await send_password_reset_email(email, reset_link)
    
    return {
        "message": "Si cet email existe, un lien de réinitialisation a été envoyé",
        "success": True,
        # En dev uniquement - retirer en production
        "dev_token": token if os.getenv("DEBUG") == "True" else None
    }

@router.post("/reset-password")
@limiter.limit("5/hour")
async def reset_password(request: Request, data: PasswordReset):
    """
    Réinitialiser le mot de passe avec un token valide
    """
    token = data.token
    
    # Vérifier que le token existe
    if token not in PASSWORD_RESET_TOKENS:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    
    token_data = PASSWORD_RESET_TOKENS[token]
    
    # Vérifier l'expiration
    if datetime.utcnow() > token_data["expires_at"]:
        del PASSWORD_RESET_TOKENS[token]
        raise HTTPException(status_code=400, detail="Token expiré")
    
    # Vérifier que le token n'a pas déjà été utilisé
    if token_data["used"]:
        raise HTTPException(status_code=400, detail="Token déjà utilisé")
    
    # Marquer comme utilisé
    token_data["used"] = True
    
    # TODO: Mettre à jour le mot de passe dans la DB
    # user = get_user_by_email(token_data["email"])
    # update_user_password(user.id, hash_password(data.new_password))
    
    # Nettoyer le token
    del PASSWORD_RESET_TOKENS[token]
    
    return {
        "message": "Mot de passe réinitialisé avec succès",
        "success": True
    }

# ============================================
# EMAIL VERIFICATION ENDPOINTS
# ============================================

@router.post("/verify-email")
async def verify_email(data: EmailVerification):
    """
    Vérifier l'adresse email avec un token
    """
    token = data.token
    
    # Vérifier que le token existe
    if token not in EMAIL_VERIFICATION_TOKENS:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    
    token_data = EMAIL_VERIFICATION_TOKENS[token]
    
    # Vérifier l'expiration
    if datetime.utcnow() > token_data["expires_at"]:
        del EMAIL_VERIFICATION_TOKENS[token]
        raise HTTPException(status_code=400, detail="Token expiré")
    
    # TODO: Marquer l'email comme vérifié dans la DB
    # user = get_user_by_email(token_data["email"])
    # update_user_email_verified(user.id, True)
    
    # Nettoyer le token
    del EMAIL_VERIFICATION_TOKENS[token]
    
    return {
        "message": "Email vérifié avec succès",
        "success": True
    }

@router.post("/resend-verification")
@limiter.limit("3/hour")
async def resend_verification(request: Request, data: PasswordResetRequest):
    """
    Renvoyer l'email de vérification
    """
    email = data.email
    
    # Générer un nouveau token
    token = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    # Stocker le token
    EMAIL_VERIFICATION_TOKENS[token] = {
        "email": email,
        "expires_at": expiration
    }
    
    # TODO: Envoyer email avec le lien
    # verification_link = f"{os.getenv('FRONTEND_URL')}/verify-email?token={token}"
    # await send_verification_email(email, verification_link)
    
    return {
        "message": "Email de vérification envoyé",
        "success": True,
        # En dev uniquement
        "dev_token": token if os.getenv("DEBUG") == "True" else None
    }

# ============================================
# 2FA (TWO-FACTOR AUTHENTICATION) ENDPOINTS
# ============================================

@router.post("/2fa/setup")
async def setup_2fa(user_id: str):  # TODO: Récupérer user_id depuis le token JWT
    """
    Configurer l'authentification à deux facteurs
    Retourne un QR code à scanner avec Google Authenticator
    """
    # Générer un secret unique pour l'utilisateur
    secret = pyotp.random_base32()
    
    # Stocker le secret (en attente de validation)
    TWO_FA_SECRETS[user_id] = {
        "secret": secret,
        "enabled": False,
        "backup_codes": [secrets.token_hex(4) for _ in range(10)]
    }
    
    # Générer le QR code
    app_name = "ShareYourSales"
    user_email = f"user_{user_id}@shareyoursales.ma"  # TODO: Récupérer le vrai email
    
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email,
        issuer_name=app_name
    )
    
    # Créer le QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir en base64 pour l'affichage
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "message": "2FA setup initiated",
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "backup_codes": TWO_FA_SECRETS[user_id]["backup_codes"],
        "manual_entry": secret
    }

@router.post("/2fa/verify")
async def verify_2fa(user_id: str, data: TwoFactorVerify):  # TODO: user_id depuis JWT
    """
    Vérifier le code 2FA et activer la fonctionnalité
    """
    if user_id not in TWO_FA_SECRETS:
        raise HTTPException(status_code=400, detail="2FA non configuré")
    
    secret = TWO_FA_SECRETS[user_id]["secret"]
    totp = pyotp.TOTP(secret)
    
    # Vérifier le code
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Code invalide")
    
    # Activer 2FA
    TWO_FA_SECRETS[user_id]["enabled"] = True
    
    # TODO: Sauvegarder dans la DB
    # update_user_2fa_status(user_id, True, secret)
    
    return {
        "message": "2FA activé avec succès",
        "success": True,
        "backup_codes": TWO_FA_SECRETS[user_id]["backup_codes"]
    }

@router.post("/2fa/disable")
async def disable_2fa(user_id: str, data: TwoFactorDisable):  # TODO: user_id depuis JWT
    """
    Désactiver l'authentification à deux facteurs
    Nécessite le mot de passe et un code 2FA valide
    """
    if user_id not in TWO_FA_SECRETS:
        raise HTTPException(status_code=400, detail="2FA non configuré")
    
    # TODO: Vérifier le mot de passe
    # user = get_user_by_id(user_id)
    # if not verify_password(data.password, user.password_hash):
    #     raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    
    # Vérifier le code 2FA
    secret = TWO_FA_SECRETS[user_id]["secret"]
    totp = pyotp.TOTP(secret)
    
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Code 2FA invalide")
    
    # Désactiver 2FA
    del TWO_FA_SECRETS[user_id]
    
    # TODO: Mettre à jour dans la DB
    # update_user_2fa_status(user_id, False, None)
    
    return {
        "message": "2FA désactivé avec succès",
        "success": True
    }

@router.post("/2fa/verify-login")
async def verify_2fa_login(user_id: str, data: TwoFactorVerify):
    """
    Vérifier le code 2FA lors de la connexion
    """
    if user_id not in TWO_FA_SECRETS or not TWO_FA_SECRETS[user_id]["enabled"]:
        raise HTTPException(status_code=400, detail="2FA non activé")
    
    secret = TWO_FA_SECRETS[user_id]["secret"]
    totp = pyotp.TOTP(secret)
    
    # Vérifier le code ou backup code
    if totp.verify(data.code, valid_window=1):
        return {
            "message": "Code valide",
            "success": True
        }
    
    # Vérifier si c'est un backup code
    if data.code in TWO_FA_SECRETS[user_id]["backup_codes"]:
        # Supprimer le backup code utilisé
        TWO_FA_SECRETS[user_id]["backup_codes"].remove(data.code)
        
        return {
            "message": "Backup code valide",
            "success": True,
            "warning": "Ce code de secours ne peut être utilisé qu'une seule fois"
        }
    
    raise HTTPException(status_code=400, detail="Code invalide")

# ============================================
# UTILITY ENDPOINTS
# ============================================

@router.get("/check-email/{email}")
async def check_email_availability(email: str):
    """
    Vérifier si un email est disponible
    """
    # TODO: Vérifier dans la DB
    # user = get_user_by_email(email)
    # available = user is None
    
    return {
        "email": email,
        "available": True,  # Mock
        "suggestions": [
            f"{email.split('@')[0]}.pro@{email.split('@')[1]}",
            f"{email.split('@')[0]}_ma@{email.split('@')[1]}"
        ]
    }

@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """
    Vérifier si un nom d'utilisateur est disponible
    """
    # TODO: Vérifier dans la DB
    # user = get_user_by_username(username)
    # available = user is None
    
    return {
        "username": username,
        "available": True,  # Mock
        "suggestions": [
            f"{username}_ma",
            f"{username}_pro",
            f"{username}2024"
        ]
    }
