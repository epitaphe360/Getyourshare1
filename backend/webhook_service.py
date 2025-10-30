"""
Service Webhook - Réception des ventes depuis les plateformes e-commerce
Supporte Shopify, WooCommerce, Stripe, etc.
"""

from fastapi import Request, HTTPException
from supabase_client import supabase
from datetime import datetime
from typing import Dict, Optional
import hmac
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class WebhookService:
    """Service de gestion des webhooks e-commerce"""

    def __init__(self):
        self.supabase = supabase

    # ============================================
    # 1. SHOPIFY WEBHOOKS
    # ============================================

    async def process_shopify_webhook(self, request: Request, merchant_id: str) -> Dict:
        """
        Traite un webhook Shopify (order/create)

        Documentation Shopify:
        https://shopify.dev/docs/api/admin-rest/2024-01/resources/webhook
        """
        try:
            # 1. Récupérer le body et les headers
            body = await request.body()
            headers = dict(request.headers)

            # 2. Vérifier la signature HMAC (sécurité)
            is_valid = await self._verify_shopify_signature(
                body=body,
                hmac_header=headers.get("x-shopify-hmac-sha256", ""),
                merchant_id=merchant_id,
            )

            if not is_valid:
                logger.warning("⚠️ Signature Shopify invalide")
                return await self._log_webhook(
                    source="shopify",
                    merchant_id=merchant_id,
                    event_type="order.created",
                    payload=json.loads(body),
                    headers=headers,
                    status="failed",
                    error="Invalid HMAC signature",
                )

            # 3. Parser les données de la commande
            order_data = json.loads(body)

            # 4. Extraire les informations clés
            order_id = str(order_data.get("id"))
            order_number = order_data.get("order_number")
            total_price = float(order_data.get("total_price", 0))
            currency = order_data.get("currency", "EUR")
            customer_email = order_data.get("email", "")

            # 5. Chercher l'attribution (cookie/UTM dans note_attributes)
            attribution = await self._find_attribution_shopify(order_data)

            if not attribution:
                logger.warning(f"⚠️ Pas d'attribution pour commande Shopify #{order_number}")
                return await self._log_webhook(
                    source="shopify",
                    merchant_id=merchant_id,
                    event_type="order.created",
                    payload=order_data,
                    headers=headers,
                    status="ignored",
                    error="No attribution found",
                )

            # 6. Récupérer les infos du merchant
            merchant = await self._get_merchant(merchant_id)
            influencer_commission_rate = merchant.get("influencer_commission_rate", 10.0)
            platform_commission_rate = merchant.get("platform_commission_rate", 5.0)

            # 7. Calculer les commissions
            influencer_commission = total_price * (influencer_commission_rate / 100)
            platform_commission = total_price * (platform_commission_rate / 100)
            merchant_revenue = total_price - influencer_commission - platform_commission

            # 8. Créer la vente dans la BDD
            sale_data = {
                "merchant_id": merchant_id,
                "influencer_id": attribution["influencer_id"],
                "link_id": attribution.get("link_id"),
                "click_id": attribution.get("click_id"),
                "product_id": None,  # Shopify peut avoir plusieurs produits
                "amount": total_price,
                "currency": currency,
                "influencer_commission": influencer_commission,
                "platform_commission": platform_commission,
                "merchant_revenue": merchant_revenue,
                "status": "pending",  # En attente validation (14 jours)
                "payment_status": "pending",
                "external_order_id": order_id,
                "external_order_number": order_number,
                "customer_email": customer_email,
                "metadata": {"source": "shopify", "order_data": order_data},
                "created_at": datetime.now().isoformat(),
            }

            sale_result = supabase.table("sales").insert(sale_data).execute()
            sale_id = sale_result.data[0]["id"]

            # 9. Incrémenter les conversions du lien
            if attribution.get("link_id"):
                await self._increment_link_conversion(
                    link_id=attribution["link_id"], revenue=total_price
                )

            # 10. Envoyer notification à l'influenceur
            await self._notify_influencer_sale(
                influencer_id=attribution["influencer_id"],
                amount=total_price,
                commission=influencer_commission,
            )

            # 11. Logger le webhook comme traité
            await self._log_webhook(
                source="shopify",
                merchant_id=merchant_id,
                event_type="order.created",
                payload=order_data,
                headers=headers,
                status="processed",
                sale_id=sale_id,
            )

            logger.info(
                f"✅ Vente Shopify créée: {sale_id} - {total_price}€ - Commande #{order_number}"
            )

            return {
                "success": True,
                "sale_id": sale_id,
                "amount": total_price,
                "commission": influencer_commission,
                "influencer_id": attribution["influencer_id"],
            }

        except Exception as e:
            logger.error(f"Erreur webhook Shopify: {e}")
            return {"success": False, "error": str(e)}

    async def _verify_shopify_signature(
        self, body: bytes, hmac_header: str, merchant_id: str
    ) -> bool:
        """Vérifie la signature HMAC du webhook Shopify"""
        try:
            # Récupérer le secret Shopify du merchant
            merchant = await self._get_merchant(merchant_id)
            shopify_secret = merchant.get("shopify_webhook_secret")

            if not shopify_secret:
                logger.warning("⚠️ Pas de secret Shopify configuré")
                return False  # En dev, on pourrait retourner True

            # Calculer le HMAC
            calculated_hmac = hmac.new(
                shopify_secret.encode("utf-8"), body, hashlib.sha256
            ).hexdigest()

            # Comparer avec le header
            return hmac.compare_digest(calculated_hmac, hmac_header)

        except Exception as e:
            logger.error(f"Erreur vérification HMAC: {e}")
            return False

    async def _find_attribution_shopify(self, order_data: Dict) -> Optional[Dict]:
        """
        Trouve l'attribution depuis les données Shopify
        Cherche dans: note_attributes, customer tags, UTM parameters
        """
        try:
            # Méthode 1: Note attributes (si influenceur a ajouté tracking_code)
            note_attributes = order_data.get("note_attributes", [])
            for attr in note_attributes:
                if attr.get("name") == "tracking_code":
                    short_code = attr.get("value")
                    return await self._get_attribution_from_code(short_code)

            # Méthode 2: Landing site (si contient notre short_code)
            landing_site = order_data.get("landing_site", "")
            if "/r/" in landing_site:
                short_code = landing_site.split("/r/")[-1].split("?")[0]
                return await self._get_attribution_from_code(short_code)

            # Méthode 3: Referring site
            referring_site = order_data.get("referring_site", "")
            if "tracknow.io" in referring_site or "localhost:8000" in referring_site:
                # Extraire le code
                if "/r/" in referring_site:
                    short_code = referring_site.split("/r/")[-1].split("?")[0]
                    return await self._get_attribution_from_code(short_code)

            # Méthode 4: UTM source (si = influencer_id)
            utm_source = order_data.get("source_name", "")
            if utm_source.startswith("influencer_"):
                influencer_id = utm_source.replace("influencer_", "")
                return {"influencer_id": influencer_id}

            return None

        except Exception as e:
            logger.error(f"Erreur attribution Shopify: {e}")
            return None

    async def _get_attribution_from_code(self, short_code: str) -> Optional[Dict]:
        """Récupère l'attribution depuis un short_code"""
        try:
            link = (
                supabase.table("tracking_links").select("*").eq("short_code", short_code).execute()
            )

            if not link.data:
                return None

            link_data = link.data[0]

            return {"influencer_id": link_data["influencer_id"], "link_id": link_data["id"]}
        except Exception as e:
            logger.error(f"Erreur récupération attribution: {e}")
            return None

    # ============================================
    # 2. WOOCOMMERCE WEBHOOKS
    # ============================================

    async def process_woocommerce_webhook(self, request: Request, merchant_id: str) -> Dict:
        """
        Traite un webhook WooCommerce (order.created)

        Documentation WooCommerce:
        https://woocommerce.github.io/woocommerce-rest-api-docs/
        """
        try:
            body = await request.body()
            headers = dict(request.headers)
            order_data = json.loads(body)

            # Similaire à Shopify mais structure différente
            order_id = str(order_data.get("id"))
            total = float(order_data.get("total", 0))
            currency = order_data.get("currency", "EUR")

            # Attribution depuis meta_data
            attribution = await self._find_attribution_woocommerce(order_data)

            if not attribution:
                return await self._log_webhook(
                    source="woocommerce",
                    merchant_id=merchant_id,
                    event_type="order.created",
                    payload=order_data,
                    headers=headers,
                    status="ignored",
                    error="No attribution found",
                )

            # Créer la vente (code similaire à Shopify)
            merchant = await self._get_merchant(merchant_id)
            influencer_commission = total * (merchant.get("influencer_commission_rate", 10.0) / 100)
            platform_commission = total * (merchant.get("platform_commission_rate", 5.0) / 100)

            sale_data = {
                "merchant_id": merchant_id,
                "influencer_id": attribution["influencer_id"],
                "link_id": attribution.get("link_id"),
                "amount": total,
                "currency": currency,
                "influencer_commission": influencer_commission,
                "platform_commission": platform_commission,
                "merchant_revenue": total - influencer_commission - platform_commission,
                "status": "pending",
                "external_order_id": order_id,
                "metadata": {"source": "woocommerce", "order_data": order_data},
                "created_at": datetime.now().isoformat(),
            }

            sale_result = supabase.table("sales").insert(sale_data).execute()
            sale_id = sale_result.data[0]["id"]

            await self._log_webhook(
                source="woocommerce",
                merchant_id=merchant_id,
                event_type="order.created",
                payload=order_data,
                headers=headers,
                status="processed",
                sale_id=sale_id,
            )

            logger.info(f"✅ Vente WooCommerce créée: {sale_id} - {total}€")

            return {"success": True, "sale_id": sale_id, "amount": total}

        except Exception as e:
            logger.error(f"Erreur webhook WooCommerce: {e}")
            return {"success": False, "error": str(e)}

    async def _find_attribution_woocommerce(self, order_data: Dict) -> Optional[Dict]:
        """Trouve l'attribution dans les meta_data WooCommerce"""
        try:
            meta_data = order_data.get("meta_data", [])

            for meta in meta_data:
                if meta.get("key") == "_tracking_code":
                    short_code = meta.get("value")
                    return await self._get_attribution_from_code(short_code)

            return None
        except Exception as e:
            logger.error(f"Erreur attribution WooCommerce: {e}")
            return None

    # ============================================
    # 3. TIKTOK SHOP WEBHOOKS
    # ============================================

    async def process_tiktok_webhook(self, request: Request, merchant_id: str) -> Dict:
        """
        Traite un webhook TikTok Shop (order placed)

        Documentation TikTok Shop:
        https://partner.tiktokshop.com/docv2/page/650a99c4b1a23902bebbb651

        Events supportés:
        - ORDER_STATUS_CHANGE (order placed)
        - ORDER_PAID
        """
        try:
            body = await request.body()
            headers = dict(request.headers)

            # Parser le payload TikTok
            webhook_data = json.loads(body)

            # TikTok utilise une structure imbriquée
            event_type = webhook_data.get("type")  # ORDER_STATUS_CHANGE
            timestamp = webhook_data.get("timestamp")
            data = webhook_data.get("data", {})

            # Vérifier la signature (sécurité TikTok)
            is_valid = await self._verify_tiktok_signature(
                body=body, signature=headers.get("x-tiktok-signature", ""), merchant_id=merchant_id
            )

            if not is_valid:
                logger.warning("⚠️ Signature TikTok invalide")
                return await self._log_webhook(
                    source="tiktok_shop",
                    merchant_id=merchant_id,
                    event_type=event_type,
                    payload=webhook_data,
                    headers=headers,
                    status="failed",
                    error="Invalid signature",
                )

            # Extraire les données de la commande
            order_id = str(data.get("order_id"))
            order_status = data.get("order_status")  # 100 = placed, 111 = awaiting payment, etc.

            # Ne traiter que les commandes payées
            if order_status not in [111, 112, 121]:  # Statuts "payé" TikTok
                return await self._log_webhook(
                    source="tiktok_shop",
                    merchant_id=merchant_id,
                    event_type=event_type,
                    payload=webhook_data,
                    headers=headers,
                    status="ignored",
                    error=f"Order status {order_status} not paid yet",
                )

            # Récupérer les détails de paiement
            payment_info = data.get("payment", {})
            total_amount = (
                float(payment_info.get("total_amount", 0)) / 100
            )  # TikTok envoie en centimes
            currency = payment_info.get("currency", "USD")

            # Infos client
            buyer_info = data.get("buyer_info", {})
            customer_email = buyer_info.get("email", "")
            customer_name = buyer_info.get("name", "")

            # Chercher l'attribution
            attribution = await self._find_attribution_tiktok(data)

            if not attribution:
                logger.warning(f"⚠️ Pas d'attribution pour commande TikTok #{order_id}")
                return await self._log_webhook(
                    source="tiktok_shop",
                    merchant_id=merchant_id,
                    event_type=event_type,
                    payload=webhook_data,
                    headers=headers,
                    status="ignored",
                    error="No attribution found",
                )

            # Récupérer les infos du merchant
            merchant = await self._get_merchant(merchant_id)
            influencer_commission_rate = merchant.get("influencer_commission_rate", 10.0)
            platform_commission_rate = merchant.get("platform_commission_rate", 5.0)

            # Calculer les commissions
            influencer_commission = total_amount * (influencer_commission_rate / 100)
            platform_commission = total_amount * (platform_commission_rate / 100)
            merchant_revenue = total_amount - influencer_commission - platform_commission

            # Créer la vente dans la BDD
            sale_data = {
                "merchant_id": merchant_id,
                "influencer_id": attribution["influencer_id"],
                "link_id": attribution.get("link_id"),
                "click_id": attribution.get("click_id"),
                "product_id": None,  # TikTok peut avoir plusieurs produits
                "amount": total_amount,
                "currency": currency,
                "influencer_commission": influencer_commission,
                "platform_commission": platform_commission,
                "merchant_revenue": merchant_revenue,
                "status": "pending",  # En attente validation (14 jours)
                "payment_status": "pending",
                "external_order_id": order_id,
                "external_order_number": order_id,  # TikTok n'a pas de order_number séparé
                "customer_email": customer_email,
                "metadata": {
                    "source": "tiktok_shop",
                    "order_status": order_status,
                    "customer_name": customer_name,
                    "order_data": data,
                },
                "created_at": datetime.now().isoformat(),
            }

            sale_result = supabase.table("sales").insert(sale_data).execute()
            sale_id = sale_result.data[0]["id"]

            # Incrémenter les conversions du lien
            if attribution.get("link_id"):
                await self._increment_link_conversion(
                    link_id=attribution["link_id"], revenue=total_amount
                )

            # Envoyer notification à l'influenceur
            await self._notify_influencer_sale(
                influencer_id=attribution["influencer_id"],
                amount=total_amount,
                commission=influencer_commission,
            )

            # Logger le webhook comme traité
            await self._log_webhook(
                source="tiktok_shop",
                merchant_id=merchant_id,
                event_type=event_type,
                payload=webhook_data,
                headers=headers,
                status="processed",
                sale_id=sale_id,
            )

            logger.info(
                f"✅ Vente TikTok Shop créée: {sale_id} - {total_amount}{currency} - Order #{order_id}"
            )

            return {
                "success": True,
                "sale_id": sale_id,
                "amount": total_amount,
                "commission": influencer_commission,
                "influencer_id": attribution["influencer_id"],
            }

        except Exception as e:
            logger.error(f"Erreur webhook TikTok Shop: {e}")
            return {"success": False, "error": str(e)}

    async def _verify_tiktok_signature(self, body: bytes, signature: str, merchant_id: str) -> bool:
        """
        Vérifie la signature du webhook TikTok Shop

        TikTok utilise HMAC-SHA256 avec:
        - App Secret comme clé
        - Body complet comme message
        """
        try:
            # Récupérer le App Secret du merchant
            merchant = await self._get_merchant(merchant_id)
            tiktok_secret = merchant.get("tiktok_app_secret")

            if not tiktok_secret:
                logger.warning("⚠️ Pas de TikTok App Secret configuré")
                return False  # En dev, on pourrait retourner True

            # Calculer le HMAC
            calculated_signature = hmac.new(
                tiktok_secret.encode("utf-8"), body, hashlib.sha256
            ).hexdigest()

            # Comparer avec le header
            return hmac.compare_digest(calculated_signature, signature)

        except Exception as e:
            logger.error(f"Erreur vérification signature TikTok: {e}")
            return False

    async def _find_attribution_tiktok(self, order_data: Dict) -> Optional[Dict]:
        """
        Trouve l'attribution depuis les données TikTok Shop

        TikTok Shop envoie:
        - creator_info: Infos du créateur TikTok
        - promotion_info: Infos de promotion
        - Paramètres UTM dans tracking_info
        """
        try:
            # Méthode 1: Creator info (si commande via TikTok Live ou Creator Marketplace)
            creator_info = order_data.get("creator_info", {})
            if creator_info:
                creator_id = creator_info.get("creator_id")
                # Mapper creator_id TikTok → influencer_id
                # Vous devez stocker cette relation dans la BDD
                influencer = await self._get_influencer_by_tiktok_id(creator_id)
                if influencer:
                    return {"influencer_id": influencer["id"], "source": "tiktok_creator"}

            # Méthode 2: Promotion info (code promo)
            promotion_info = order_data.get("promotion_info", {})
            for promo in promotion_info:
                promo_code = promo.get("promotion_code", "")
                # Si le code promo contient un tracking_code
                if promo_code:
                    attribution = await self._get_attribution_from_code(promo_code)
                    if attribution:
                        return attribution

            # Méthode 3: Tracking info (UTM parameters)
            tracking_info = order_data.get("tracking_info", {})
            utm_source = tracking_info.get("utm_source", "")
            utm_campaign = tracking_info.get("utm_campaign", "")

            # Si utm_source = notre short_code
            if utm_source:
                attribution = await self._get_attribution_from_code(utm_source)
                if attribution:
                    return attribution

            # Si utm_campaign = notre short_code
            if utm_campaign:
                attribution = await self._get_attribution_from_code(utm_campaign)
                if attribution:
                    return attribution

            # Méthode 4: Order note (notes de commande)
            order_note = order_data.get("buyer_message", "")
            if "TRACK:" in order_note:
                # Format: "TRACK:ABC12345"
                short_code = order_note.split("TRACK:")[1].split()[0]
                return await self._get_attribution_from_code(short_code)

            return None

        except Exception as e:
            logger.error(f"Erreur attribution TikTok: {e}")
            return None

    async def _get_influencer_by_tiktok_id(self, tiktok_creator_id: str) -> Optional[Dict]:
        """Récupère un influenceur par son TikTok Creator ID"""
        try:
            # Chercher dans la table influencers
            # Vous devez avoir une colonne tiktok_creator_id
            result = (
                supabase.table("influencers")
                .select("*")
                .eq("tiktok_creator_id", tiktok_creator_id)
                .execute()
            )

            return result.data[0] if result.data else None
        except:
            return None

    # ============================================
    # 3. HELPERS
    # ============================================

    async def _get_merchant(self, merchant_id: str) -> Dict:
        """Récupère les infos d'un merchant"""
        try:
            result = supabase.table("merchants").select("*").eq("id", merchant_id).execute()
            return result.data[0] if result.data else {}
        except:
            return {}

    async def _increment_link_conversion(self, link_id: str, revenue: float):
        """Incrémente les conversions d'un lien"""
        try:
            link = (
                supabase.table("tracking_links")
                .select("conversions, revenue")
                .eq("id", link_id)
                .execute()
            )

            if link.data:
                current_conversions = int(link.data[0].get("conversions", 0))
                current_revenue = float(link.data[0].get("revenue", 0))

                supabase.table("tracking_links").update(
                    {"conversions": current_conversions + 1, "revenue": current_revenue + revenue}
                ).eq("id", link_id).execute()
        except Exception as e:
            logger.error(f"Erreur incrémentation conversion: {e}")

    async def _notify_influencer_sale(self, influencer_id: str, amount: float, commission: float):
        """Envoie une notification à l'influenceur"""
        try:
            # Récupérer le user_id de l'influenceur
            influencer = (
                supabase.table("influencers").select("user_id").eq("id", influencer_id).execute()
            )

            if not influencer.data:
                return

            user_id = influencer.data[0]["user_id"]

            # Créer la notification
            notification_data = {
                "user_id": user_id,
                "type": "sale",
                "title": "🎉 Nouvelle vente !",
                "message": f"Vous avez généré une vente de {amount}€. Commission: {commission}€ (validation dans 14 jours)",
                "is_read": False,
                "metadata": {"amount": amount, "commission": commission},
                "created_at": datetime.now().isoformat(),
            }

            supabase.table("notifications").insert(notification_data).execute()

            logger.info(f"📧 Notification envoyée à influenceur {influencer_id}")

        except Exception as e:
            logger.error(f"Erreur notification: {e}")

    async def _log_webhook(
        self,
        source: str,
        merchant_id: str,
        event_type: str,
        payload: Dict,
        headers: Dict,
        status: str,
        error: str = None,
        sale_id: str = None,
    ) -> Dict:
        """Enregistre le webhook dans les logs"""
        try:
            log_data = {
                "source": source,
                "merchant_id": merchant_id,
                "event_type": event_type,
                "payload": payload,
                "headers": headers,
                "status": status,
                "error_message": error,
                "sale_id": sale_id,
                "processed_at": datetime.now().isoformat() if status == "processed" else None,
                "received_at": datetime.now().isoformat(),
            }

            result = supabase.table("webhook_logs").insert(log_data).execute()
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Erreur log webhook: {e}")
            return {}


# Instance globale
webhook_service = WebhookService()
