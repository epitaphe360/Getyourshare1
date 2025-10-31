"""
WhatsApp Business API Service pour le Maroc

Ce service gère l'intégration WhatsApp Business pour:
- Notifications transactionnelles
- Partage de liens d'affiliation
- Messagerie influenceur-marchand
- Support client
- Catalogues produits

API utilisée: WhatsApp Business API (Meta)
Documentation: https://developers.facebook.com/docs/whatsapp/business-platform
"""

import os
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class WhatsAppMessageType(str, Enum):
    """Types de messages WhatsApp"""
    TEXT = "text"
    TEMPLATE = "template"
    IMAGE = "image"
    DOCUMENT = "document"
    INTERACTIVE = "interactive"
    LOCATION = "location"

class WhatsAppTemplateCategory(str, Enum):
    """Catégories de templates WhatsApp"""
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    AUTHENTICATION = "authentication"
    UTILITY = "utility"

class WhatsAppBusinessService:
    """Service pour gérer l'API WhatsApp Business"""

    def __init__(self):
        # Configuration API WhatsApp Business
        self.api_url = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v18.0")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")

        # Mode DEMO par défaut (si pas de token configuré)
        self.demo_mode = not bool(self.access_token)

        if self.demo_mode:
            logger.warning("⚠️ WhatsApp Business Service en mode DEMO (pas de token configuré)")
        else:
            logger.info("✅ WhatsApp Business Service configuré")

    async def send_text_message(
        self,
        to_phone: str,
        message: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """
        Envoyer un message texte simple

        Args:
            to_phone: Numéro de téléphone au format international (+212...)
            message: Contenu du message
            preview_url: Activer l'aperçu des liens

        Returns:
            Résultat de l'envoi avec message_id
        """
        if self.demo_mode:
            logger.info(f"📱 [DEMO] WhatsApp vers {to_phone}: {message[:50]}...")
            return {
                "success": True,
                "message_id": f"wamid.demo_{datetime.utcnow().timestamp()}",
                "status": "sent",
                "demo_mode": True
            }

        try:
            # Nettoyer le numéro de téléphone
            clean_phone = self._clean_phone_number(to_phone)

            # Construire le payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "text",
                "text": {
                    "preview_url": preview_url,
                    "body": message
                }
            }

            # Envoyer via l'API WhatsApp
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "status": "sent",
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur envoi WhatsApp: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    async def send_template_message(
        self,
        to_phone: str,
        template_name: str,
        language_code: str = "fr",
        parameters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Envoyer un message template (pré-approuvé par Meta)

        Templates communs:
        - new_commission: Nouvelle commission gagnée
        - payout_approved: Paiement approuvé
        - new_sale: Nouvelle vente réalisée
        - welcome_influencer: Bienvenue influenceur

        Args:
            to_phone: Numéro de téléphone
            template_name: Nom du template
            language_code: Code langue (fr, ar, en)
            parameters: Paramètres du template ({{1}}, {{2}}, etc.)
        """
        if self.demo_mode:
            logger.info(f"📱 [DEMO] Template WhatsApp '{template_name}' vers {to_phone}")
            return {
                "success": True,
                "message_id": f"wamid.demo_template_{datetime.utcnow().timestamp()}",
                "status": "sent",
                "demo_mode": True,
                "template_name": template_name
            }

        try:
            clean_phone = self._clean_phone_number(to_phone)

            # Construire les paramètres du template
            components = []
            if parameters:
                components.append({
                    "type": "body",
                    "parameters": [{"type": "text", "text": param} for param in parameters]
                })

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code},
                    "components": components
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "status": "sent",
                    "template_name": template_name
                }

        except Exception as e:
            logger.error(f"❌ Erreur envoi template WhatsApp: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    async def send_affiliate_link(
        self,
        to_phone: str,
        product_name: str,
        affiliate_link: str,
        commission_rate: float,
        product_image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envoyer un lien d'affiliation avec aperçu du produit

        Format optimisé pour le partage WhatsApp
        """
        message = f"""🎉 *{product_name}*

💰 Commission: {commission_rate}%

🔗 Ton lien d'affiliation:
{affiliate_link}

Partage ce lien sur tes réseaux sociaux et gagne de l'argent à chaque vente! 🚀"""

        return await self.send_text_message(to_phone, message, preview_url=True)

    async def send_notification(
        self,
        to_phone: str,
        notification_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envoyer une notification transactionnelle

        Types supportés:
        - new_commission: Nouvelle commission
        - payout_approved: Paiement approuvé
        - new_sale: Nouvelle vente
        - new_message: Nouveau message
        """
        templates = {
            "new_commission": lambda d: (
                "new_commission",
                [d.get("amount", "0"), d.get("product_name", "Produit")]
            ),
            "payout_approved": lambda d: (
                "payout_approved",
                [d.get("amount", "0"), d.get("method", "Compte bancaire")]
            ),
            "new_sale": lambda d: (
                "new_sale",
                [d.get("product_name", "Produit"), d.get("commission", "0")]
            ),
            "new_message": lambda d: (
                "new_message",
                [d.get("sender_name", "Un utilisateur")]
            )
        }

        if notification_type in templates:
            template_name, params = templates[notification_type](data)
            return await self.send_template_message(
                to_phone,
                template_name,
                language_code=data.get("language", "fr"),
                parameters=params
            )
        else:
            # Fallback: message texte simple
            return await self.send_text_message(to_phone, data.get("message", "Notification"))

    async def send_interactive_buttons(
        self,
        to_phone: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envoyer un message avec boutons interactifs

        Exemple:
        buttons = [
            {"id": "accept", "title": "Accepter"},
            {"id": "reject", "title": "Refuser"}
        ]
        """
        if self.demo_mode:
            logger.info(f"📱 [DEMO] Boutons WhatsApp vers {to_phone}: {len(buttons)} boutons")
            return {
                "success": True,
                "message_id": f"wamid.demo_interactive_{datetime.utcnow().timestamp()}",
                "status": "sent",
                "demo_mode": True
            }

        try:
            clean_phone = self._clean_phone_number(to_phone)

            # Construire les boutons (max 3)
            action_buttons = [
                {
                    "type": "reply",
                    "reply": {
                        "id": btn["id"],
                        "title": btn["title"][:20]  # Max 20 caractères
                    }
                }
                for btn in buttons[:3]  # WhatsApp limite à 3 boutons
            ]

            interactive_data = {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": action_buttons}
            }

            if header_text:
                interactive_data["header"] = {"type": "text", "text": header_text}
            if footer_text:
                interactive_data["footer"] = {"text": footer_text}

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "interactive",
                "interactive": interactive_data
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "status": "sent"
                }

        except Exception as e:
            logger.error(f"❌ Erreur envoi boutons WhatsApp: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    async def create_product_catalog(
        self,
        catalog_name: str,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Créer/mettre à jour un catalogue produits WhatsApp Business

        Args:
            catalog_name: Nom du catalogue
            products: Liste de produits [{name, price, image_url, description}]
        """
        if self.demo_mode:
            logger.info(f"📱 [DEMO] Catalogue WhatsApp '{catalog_name}': {len(products)} produits")
            return {
                "success": True,
                "catalog_id": f"catalog_demo_{datetime.utcnow().timestamp()}",
                "products_count": len(products),
                "demo_mode": True
            }

        # En production, utiliser l'API Catalog
        # https://developers.facebook.com/docs/whatsapp/business-management-api/manage-catalogs

        logger.info(f"Création catalogue WhatsApp: {catalog_name} avec {len(products)} produits")
        return {
            "success": True,
            "catalog_id": "implementation_required",
            "products_count": len(products),
            "note": "Implémentation complète nécessite API Catalog de Meta"
        }

    def _clean_phone_number(self, phone: str) -> str:
        """
        Nettoyer et formater le numéro de téléphone pour WhatsApp

        WhatsApp attend: numéro sans '+', sans espaces, sans tirets
        Exemple: 212612345678
        """
        # Enlever tous les caractères non-numériques sauf le +
        clean = ''.join(c for c in phone if c.isdigit() or c == '+')

        # Enlever le + du début si présent
        if clean.startswith('+'):
            clean = clean[1:]

        # Si commence par 0, remplacer par 212 (code Maroc)
        if clean.startswith('0'):
            clean = '212' + clean[1:]

        # Si ne commence pas par 212, ajouter 212
        if not clean.startswith('212'):
            clean = '212' + clean

        return clean

    def get_whatsapp_share_url(self, text: str, url: Optional[str] = None) -> str:
        """
        Générer une URL de partage WhatsApp

        Ouvre WhatsApp avec le message pré-rempli
        Fonctionne sur mobile et desktop
        """
        message = text
        if url:
            message += f"\n\n{url}"

        # Encoder pour URL
        from urllib.parse import quote
        encoded_message = quote(message)

        return f"https://wa.me/?text={encoded_message}"

    def get_whatsapp_direct_url(self, phone: str, text: str) -> str:
        """
        Générer une URL pour envoyer un message direct à un numéro

        Utile pour support client
        """
        clean_phone = self._clean_phone_number(phone)
        from urllib.parse import quote
        encoded_text = quote(text)

        return f"https://wa.me/{clean_phone}?text={encoded_text}"


# Instance singleton du service
whatsapp_service = WhatsAppBusinessService()
