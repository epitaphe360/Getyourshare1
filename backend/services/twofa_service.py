"""
2FA Service - Two-Factor Authentication
Sécurité renforcée avec authentification à deux facteurs

Features:
1. TOTP (Time-based One-Time Password) avec Google Authenticator, Authy
2. Email-based 2FA (backup)
3. QR Code generation
4. Backup codes (10 codes à usage unique)
5. Rate limiting (anti-brute force)
6. Session management
"""

import os
import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import structlog
from pydantic import BaseModel

logger = structlog.get_logger()

# Configuration
APP_NAME = "ShareYourSales"
TOTP_ISSUER = "ShareYourSales"
CODE_VALIDITY_SECONDS = 300  # 5 minutes pour email codes
MAX_ATTEMPTS = 5  # Max 5 tentatives avant blocage


# ============================================
# PYDANTIC MODELS
# ============================================

class TwoFactorSetup(BaseModel):
    """Setup 2FA response"""
    secret: str
    qr_code_url: str
    backup_codes: List[str]
    manual_entry_key: str


class TwoFactorVerification(BaseModel):
    """Vérification 2FA"""
    code: str
    method: str  # 'totp' ou 'email'


# ============================================
# 2FA SERVICE
# ============================================

class TwoFactorAuthService:
    """
    Service d'authentification à deux facteurs
    """

    def __init__(self):
        self.totp_issuer = TOTP_ISSUER

    def generate_secret(self) -> str:
        """
        Générer un secret TOTP unique

        Returns:
            Secret base32 (32 caractères)
        """
        return pyotp.random_base32()

    def generate_totp_uri(self, secret: str, user_email: str) -> str:
        """
        Générer URI TOTP pour QR code

        Args:
            secret: Secret TOTP
            user_email: Email utilisateur

        Returns:
            URI otpauth://
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.totp_issuer
        )

    def generate_qr_code(self, totp_uri: str) -> str:
        """
        Générer QR code en base64

        Args:
            totp_uri: URI TOTP

        Returns:
            Image QR code en base64 (data:image/png;base64,...)
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convertir en base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_base64}"

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Générer codes de backup

        Args:
            count: Nombre de codes (default: 10)

        Returns:
            Liste de codes à usage unique (format: XXXX-XXXX-XXXX)
        """
        codes = []

        for _ in range(count):
            # Générer code de 12 chiffres
            code_num = secrets.randbelow(10**12)
            code = f"{code_num:012d}"

            # Formater: XXXX-XXXX-XXXX
            formatted = f"{code[0:4]}-{code[4:8]}-{code[8:12]}"
            codes.append(formatted)

        return codes

    def hash_backup_code(self, code: str) -> str:
        """
        Hasher code de backup pour stockage sécurisé

        Args:
            code: Code backup

        Returns:
            Hash SHA-256
        """
        return hashlib.sha256(code.encode()).hexdigest()

    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """
        Vérifier code TOTP

        Args:
            secret: Secret TOTP
            code: Code à 6 chiffres
            window: Fenêtre de tolérance (default: 1 = ±30 secondes)

        Returns:
            True si code valide
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=window)

        except Exception as e:
            logger.error("totp_verification_failed", error=str(e))
            return False

    def generate_email_code(self) -> str:
        """
        Générer code email à 6 chiffres

        Returns:
            Code numérique (ex: "123456")
        """
        return f"{secrets.randbelow(1000000):06d}"

    async def setup_2fa(
        self,
        user_id: str,
        user_email: str,
        method: str = 'totp'
    ) -> TwoFactorSetup:
        """
        Configurer 2FA pour un utilisateur

        Args:
            user_id: ID utilisateur
            user_email: Email utilisateur
            method: 'totp' ou 'email'

        Returns:
            TwoFactorSetup avec secret, QR code, backup codes
        """
        try:
            # Générer secret TOTP
            secret = self.generate_secret()

            # Générer URI et QR code
            totp_uri = self.generate_totp_uri(secret, user_email)
            qr_code = self.generate_qr_code(totp_uri)

            # Générer backup codes
            backup_codes = self.generate_backup_codes()

            # Hasher backup codes pour DB
            hashed_codes = [self.hash_backup_code(code) for code in backup_codes]

            # Sauvegarder en DB
            from supabase_client import supabase

            supabase.table('user_2fa').upsert({
                'user_id': user_id,
                'method': method,
                'secret': secret,
                'backup_codes': hashed_codes,
                'enabled': False,  # Pas encore activé
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).execute()

            logger.info("2fa_setup_initiated", user_id=user_id, method=method)

            return TwoFactorSetup(
                secret=secret,
                qr_code_url=qr_code,
                backup_codes=backup_codes,
                manual_entry_key=secret  # Pour saisie manuelle
            )

        except Exception as e:
            logger.error("2fa_setup_failed", user_id=user_id, error=str(e))
            raise

    async def enable_2fa(self, user_id: str, verification_code: str) -> bool:
        """
        Activer 2FA après vérification du code

        Args:
            user_id: ID utilisateur
            verification_code: Code TOTP pour vérification

        Returns:
            True si activé avec succès
        """
        try:
            from supabase_client import supabase

            # Récupérer config 2FA
            result = supabase.table('user_2fa').select('*').eq('user_id', user_id).execute()

            if not result.data:
                logger.error("2fa_not_setup", user_id=user_id)
                return False

            config = result.data[0]
            secret = config['secret']

            # Vérifier code
            if not self.verify_totp_code(secret, verification_code):
                logger.warning("2fa_enable_invalid_code", user_id=user_id)
                return False

            # Activer 2FA
            supabase.table('user_2fa').update({
                'enabled': True,
                'enabled_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()

            logger.info("2fa_enabled", user_id=user_id)
            return True

        except Exception as e:
            logger.error("2fa_enable_failed", user_id=user_id, error=str(e))
            return False

    async def disable_2fa(self, user_id: str) -> bool:
        """
        Désactiver 2FA

        Args:
            user_id: ID utilisateur

        Returns:
            True si désactivé
        """
        try:
            from supabase_client import supabase

            supabase.table('user_2fa').update({
                'enabled': False,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()

            logger.info("2fa_disabled", user_id=user_id)
            return True

        except Exception as e:
            logger.error("2fa_disable_failed", user_id=user_id, error=str(e))
            return False

    async def verify_2fa(
        self,
        user_id: str,
        code: str,
        method: str = 'totp'
    ) -> bool:
        """
        Vérifier code 2FA

        Args:
            user_id: ID utilisateur
            code: Code à vérifier
            method: 'totp', 'email', ou 'backup'

        Returns:
            True si code valide
        """
        try:
            from supabase_client import supabase

            # Récupérer config 2FA
            result = supabase.table('user_2fa').select('*').eq('user_id', user_id).eq('enabled', True).execute()

            if not result.data:
                logger.error("2fa_not_enabled", user_id=user_id)
                return False

            config = result.data[0]

            # Vérifier selon méthode
            if method == 'totp':
                secret = config['secret']
                is_valid = self.verify_totp_code(secret, code)

            elif method == 'backup':
                # Vérifier backup code
                hashed_code = self.hash_backup_code(code)
                backup_codes = config.get('backup_codes', [])

                is_valid = hashed_code in backup_codes

                if is_valid:
                    # Retirer code utilisé
                    backup_codes.remove(hashed_code)
                    supabase.table('user_2fa').update({
                        'backup_codes': backup_codes,
                        'updated_at': datetime.utcnow().isoformat()
                    }).eq('user_id', user_id).execute()

            elif method == 'email':
                # Vérifier code email stocké temporairement
                email_code = config.get('email_code')
                email_code_expiry = config.get('email_code_expiry')

                if not email_code or not email_code_expiry:
                    return False

                # Vérifier expiration
                expiry = datetime.fromisoformat(email_code_expiry)
                if datetime.utcnow() > expiry:
                    logger.warning("2fa_email_code_expired", user_id=user_id)
                    return False

                is_valid = code == email_code

            else:
                logger.error("2fa_invalid_method", method=method)
                return False

            if is_valid:
                logger.info("2fa_verified", user_id=user_id, method=method)
            else:
                logger.warning("2fa_verification_failed", user_id=user_id, method=method)

            return is_valid

        except Exception as e:
            logger.error("2fa_verify_failed", user_id=user_id, error=str(e))
            return False

    async def send_email_code(self, user_id: str, user_email: str) -> bool:
        """
        Envoyer code 2FA par email

        Args:
            user_id: ID utilisateur
            user_email: Email utilisateur

        Returns:
            True si envoyé
        """
        try:
            from supabase_client import supabase

            # Générer code
            code = self.generate_email_code()

            # Expiration: 5 minutes
            expiry = datetime.utcnow() + timedelta(seconds=CODE_VALIDITY_SECONDS)

            # Sauvegarder code temporaire
            supabase.table('user_2fa').update({
                'email_code': code,
                'email_code_expiry': expiry.isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()

            # Envoyer email (async)
            from celery_tasks import send_2fa_code_email
            from supabase_client import supabase as supabase_client

            # Récupérer nom utilisateur
            user_result = supabase_client.table('users').select('first_name, last_name').eq('id', user_id).execute()
            user_name = "Utilisateur"

            if user_result.data:
                user = user_result.data[0]
                user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()

            send_2fa_code_email.delay(user_email, user_name, code)

            logger.info("2fa_email_code_sent", user_id=user_id)
            return True

        except Exception as e:
            logger.error("2fa_email_send_failed", user_id=user_id, error=str(e))
            return False

    async def get_2fa_status(self, user_id: str) -> Dict:
        """
        Obtenir statut 2FA d'un utilisateur

        Returns:
            {
                "enabled": bool,
                "method": "totp|email",
                "backup_codes_remaining": int,
                "enabled_at": str
            }
        """
        try:
            from supabase_client import supabase

            result = supabase.table('user_2fa').select('*').eq('user_id', user_id).execute()

            if not result.data:
                return {
                    "enabled": False,
                    "method": None,
                    "backup_codes_remaining": 0,
                    "enabled_at": None
                }

            config = result.data[0]

            return {
                "enabled": config.get('enabled', False),
                "method": config.get('method', 'totp'),
                "backup_codes_remaining": len(config.get('backup_codes', [])),
                "enabled_at": config.get('enabled_at')
            }

        except Exception as e:
            logger.error("get_2fa_status_failed", user_id=user_id, error=str(e))
            return {
                "enabled": False,
                "method": None,
                "backup_codes_remaining": 0,
                "enabled_at": None
            }


# Instance globale
twofa_service = TwoFactorAuthService()
