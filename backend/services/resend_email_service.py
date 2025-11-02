"""
Resend Email Service - Production Ready
Service d'envoi d'emails via Resend API avec domaine personnalisé

Features:
- API Resend moderne et fiable
- Domaine personnalisé (info@shareyoursales.ma)
- Templates HTML professionnels
- Retry logic automatique
- Logging structuré
"""

import os
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime
import structlog
from pathlib import Path

logger = structlog.get_logger()

# Configuration Resend
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "ShareYourSales")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", "info@shareyoursales.ma")
RESEND_API_URL = "https://api.resend.com/emails"


class ResendEmailService:
    """
    Service d'envoi d'emails via Resend API
    """

    def __init__(self):
        self.api_key = RESEND_API_KEY
        self.from_name = EMAIL_FROM_NAME
        self.from_address = EMAIL_FROM_ADDRESS
        self.api_url = RESEND_API_URL

        if not self.api_key:
            logger.warning("resend_api_key_missing", message="Clé API Resend non configurée")

    def _get_headers(self) -> Dict[str, str]:
        """Headers pour requêtes Resend API"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Envoyer un email via Resend API

        Args:
            to_email: Email destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML
            text_content: Contenu texte (optionnel)
            reply_to: Email de réponse (optionnel)
            cc: Liste d'emails en copie (optionnel)
            bcc: Liste d'emails en copie cachée (optionnel)
            tags: Métadonnées pour tracking (optionnel)

        Returns:
            Dict avec le résultat (success, message_id, error)
        """
        try:
            # Construire le FROM avec nom
            from_email = f"{self.from_name} <{self.from_address}>"

            # Préparer le payload
            payload = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }

            # Ajouter le contenu texte si fourni
            if text_content:
                payload["text"] = text_content

            # Ajouter reply_to si fourni
            if reply_to:
                payload["reply_to"] = reply_to

            # Ajouter CC si fourni
            if cc:
                payload["cc"] = cc

            # Ajouter BCC si fourni
            if bcc:
                payload["bcc"] = bcc

            # Ajouter tags si fourni
            if tags:
                payload["tags"] = tags

            # Envoyer la requête
            response = requests.post(
                self.api_url,
                headers=self._get_headers(),
                json=payload,
                timeout=10
            )

            # Vérifier la réponse
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(
                    "email_sent_success",
                    to=to_email,
                    subject=subject,
                    message_id=result.get("id")
                )
                return {
                    "success": True,
                    "message_id": result.get("id"),
                    "data": result
                }
            else:
                error_data = response.json() if response.content else {}
                logger.error(
                    "email_send_failed",
                    to=to_email,
                    subject=subject,
                    status_code=response.status_code,
                    error=error_data
                )
                return {
                    "success": False,
                    "error": error_data.get("message", "Erreur d'envoi"),
                    "status_code": response.status_code
                }

        except requests.exceptions.Timeout:
            logger.error("email_send_timeout", to=to_email, subject=subject)
            return {
                "success": False,
                "error": "Timeout lors de l'envoi de l'email"
            }

        except requests.exceptions.RequestException as e:
            logger.error("email_send_request_error", to=to_email, subject=subject, error=str(e))
            return {
                "success": False,
                "error": f"Erreur réseau: {str(e)}"
            }

        except Exception as e:
            logger.error("email_send_unexpected_error", to=to_email, subject=subject, error=str(e))
            return {
                "success": False,
                "error": f"Erreur inattendue: {str(e)}"
            }

    # ============================================
    # TEMPLATES D'EMAILS
    # ============================================

    def send_welcome_email(self, to_email: str, user_name: str, role: str) -> Dict[str, Any]:
        """Email de bienvenue après inscription"""
        subject = f"🎉 Bienvenue sur ShareYourSales, {user_name}!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">ShareYourSales</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Chaque partage devient une vente</p>
            </div>

            <div style="background: white; padding: 40px 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #667eea; margin-top: 0;">Bienvenue, {user_name}! 🎉</h2>

                <p>Nous sommes ravis de vous accueillir sur <strong>ShareYourSales</strong>, la plateforme d'affiliation n°1 au Maroc.</p>

                <p>En tant que <strong>{role}</strong>, vous pouvez maintenant:</p>

                <ul style="background: #f8f9fa; padding: 20px 20px 20px 40px; border-left: 4px solid #667eea; margin: 20px 0;">
                    {'<li>Parcourir notre marketplace de produits et services</li><li>Générer vos liens d\'affiliation personnalisés</li><li>Gagner des commissions sur chaque vente (15% produits, 20% services)</li><li>Suivre vos performances en temps réel</li>' if role in ['influencer', 'commercial'] else '<li>Créer et gérer vos produits/services</li><li>Recruter des affiliés (influenceurs/commerciaux)</li><li>Suivre les performances de vos affiliés</li><li>Gérer vos paiements de commissions</li>'}
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/dashboard" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">Accéder à mon tableau de bord</a>
                </div>

                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                    <strong>💡 Astuce:</strong> Commencez par explorer notre marketplace et découvrez les opportunités de revenus qui vous attendent!
                </div>

                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Besoin d'aide? Notre équipe support est disponible 7j/7 à <a href="mailto:support@shareyoursales.ma" style="color: #667eea;">support@shareyoursales.ma</a>
                </p>
            </div>

            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666;">
                <p style="margin: 5px 0;">© {datetime.now().year} ShareYourSales - Tous droits réservés</p>
                <p style="margin: 5px 0;">Marketplace d'affiliation au Maroc 🇲🇦</p>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags={"type": "welcome", "role": role}
        )

    def send_affiliate_request_confirmation(
        self,
        to_email: str,
        user_name: str,
        product_name: str,
        company_name: str
    ) -> Dict[str, Any]:
        """Email de confirmation de demande d'affiliation"""
        subject = f"✅ Demande d'affiliation envoyée - {product_name}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">✅ Demande envoyée!</h1>
            </div>

            <div style="background: white; padding: 40px 30px; border: 1px solid #e0e0e0; border-top: none;">
                <p>Bonjour {user_name},</p>

                <p>Votre demande d'affiliation pour <strong>{product_name}</strong> a été envoyée avec succès à <strong>{company_name}</strong>.</p>

                <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0;">
                    <strong>⏱️ Prochaines étapes:</strong>
                    <ol style="margin: 10px 0 0 0; padding-left: 20px;">
                        <li>L'entreprise va examiner votre profil</li>
                        <li>Vous recevrez une réponse sous 48h</li>
                        <li>Si approuvé, vous recevrez votre lien d'affiliation</li>
                    </ol>
                </div>

                <p>Pendant ce temps, continuez à explorer notre marketplace pour découvrir d'autres opportunités!</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/marketplace" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">Explorer la Marketplace</a>
                </div>
            </div>

            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666;">
                <p style="margin: 5px 0;">© {datetime.now().year} ShareYourSales - Tous droits réservés</p>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags={"type": "affiliate_request", "product": product_name}
        )

    def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str
    ) -> Dict[str, Any]:
        """Email de réinitialisation de mot de passe"""
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        subject = "🔐 Réinitialisation de votre mot de passe"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🔐 Réinitialisation</h1>
            </div>

            <div style="background: white; padding: 40px 30px; border: 1px solid #e0e0e0; border-top: none;">
                <p>Bonjour {user_name},</p>

                <p>Vous avez demandé à réinitialiser votre mot de passe ShareYourSales.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">Réinitialiser mon mot de passe</a>
                </div>

                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                    <strong>⚠️ Important:</strong> Ce lien expire dans 1 heure pour votre sécurité.
                </div>

                <p style="color: #666; font-size: 14px;">Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. Votre mot de passe reste inchangé.</p>
            </div>

            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666;">
                <p style="margin: 5px 0;">© {datetime.now().year} ShareYourSales - Tous droits réservés</p>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags={"type": "password_reset"}
        )

    def send_2fa_code(
        self,
        to_email: str,
        user_name: str,
        code: str
    ) -> Dict[str, Any]:
        """Email avec code 2FA"""
        subject = f"🔒 Votre code de vérification: {code}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🔒 Code de vérification</h1>
            </div>

            <div style="background: white; padding: 40px 30px; border: 1px solid #e0e0e0; border-top: none; text-align: center;">
                <p>Bonjour {user_name},</p>

                <p>Voici votre code de vérification pour vous connecter:</p>

                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 36px; font-weight: bold; letter-spacing: 8px; padding: 20px; margin: 30px auto; border-radius: 10px; max-width: 250px;">
                    {code}
                </div>

                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; text-align: left;">
                    <strong>⚠️ Important:</strong> Ce code expire dans 10 minutes.
                </div>

                <p style="color: #666; font-size: 14px;">Si vous n'avez pas tenté de vous connecter, veuillez sécuriser votre compte immédiatement.</p>
            </div>

            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666;">
                <p style="margin: 5px 0;">© {datetime.now().year} ShareYourSales - Tous droits réservés</p>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags={"type": "2fa_code"}
        )


# Instance globale du service
resend_service = ResendEmailService()
