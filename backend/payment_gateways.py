"""
Service de gestion des gateways de paiement marocains
Supporte: CMI, PayZen/Lyra, Société Générale Maroc

Auteur: ShareYourSales Platform
Date: 2025-10-23
"""

from typing import Dict, Optional, List
import requests
import hmac
import hashlib
import base64
import json
from datetime import datetime, timedelta
from supabase_client import supabase
import logging

logger = logging.getLogger(__name__)


class PaymentGatewayService:
    """Service unifié pour tous les gateways de paiement"""

    def __init__(self):
        self.gateways = {
            "cmi": CMIGateway(),
            "payzen": PayZenGateway(),
            "sg_maroc": SGMarocGateway(),
        }

    def create_payment(
        self,
        merchant_id: str,
        amount: float,
        description: str,
        invoice_id: Optional[str] = None,
        currency: str = "MAD",
    ) -> Dict:
        """
        Crée un paiement via le gateway configuré du merchant

        Args:
            merchant_id: ID du merchant
            amount: Montant (en MAD par défaut)
            description: Description du paiement
            invoice_id: ID de la facture (optionnel)
            currency: Devise (défaut: MAD)

        Returns:
            Dict avec payment_id, payment_url, status
        """

        try:
            # Récupérer config gateway du merchant
            merchant_result = (
                supabase.table("merchants")
                .select("payment_gateway, gateway_config, company_name, email")
                .eq("id", merchant_id)
                .single()
                .execute()
            )

            if not merchant_result.data:
                raise Exception(f"Merchant {merchant_id} not found")

            merchant = merchant_result.data
            gateway_type = merchant["payment_gateway"]
            gateway_config = merchant.get("gateway_config", {})

            logger.info(f"Creating payment for merchant {merchant_id} via {gateway_type}")

            # Si paiement manuel
            if gateway_type == "manual":
                return {
                    "success": True,
                    "payment_method": "manual",
                    "status": "pending_manual_payment",
                    "message": "Paiement manuel requis - facture sera envoyée",
                    "gateway": "manual",
                }

            # Vérifier que le gateway est supporté
            gateway = self.gateways.get(gateway_type)
            if not gateway:
                raise Exception(f"Gateway {gateway_type} not supported")

            # Créer paiement via le gateway
            result = gateway.create_payment(
                config=gateway_config,
                amount=amount,
                description=description,
                merchant_id=merchant_id,
                currency=currency,
            )

            # Enregistrer la transaction
            transaction_data = {
                "merchant_id": merchant_id,
                "invoice_id": invoice_id,
                "gateway": gateway_type,
                "transaction_id": result.get("transaction_id"),
                "order_id": result.get("order_id"),
                "amount": amount,
                "currency": currency,
                "status": "pending" if result.get("success") else "failed",
                "payment_url": result.get("payment_url"),
                "request_payload": result.get("request"),
                "response_payload": result.get("response"),
                "failure_reason": result.get("error") if not result.get("success") else None,
                "expires_at": result.get("expires_at"),
            }

            transaction_insert = (
                supabase.table("gateway_transactions").insert(transaction_data).execute()
            )

            result["db_transaction_id"] = (
                transaction_insert.data[0]["id"] if transaction_insert.data else None
            )

            logger.info(f"Payment created successfully: {result.get('transaction_id')}")

            return result

        except Exception as e:
            logger.error(f"Payment creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "gateway": gateway_type if "gateway_type" in locals() else "unknown",
            }

    def process_webhook(
        self,
        gateway_type: str,
        merchant_id: str,
        payload: Dict,
        headers: Dict,
        raw_body: str = None,
    ) -> Dict:
        """
        Traite un webhook reçu d'un gateway

        Args:
            gateway_type: Type de gateway (cmi, payzen, sg_maroc)
            merchant_id: ID du merchant
            payload: Payload JSON reçu
            headers: Headers HTTP
            raw_body: Corps brut de la requête (pour vérification signature)

        Returns:
            Dict avec status et informations de traitement
        """

        try:
            # Récupérer config gateway du merchant
            merchant_result = (
                supabase.table("merchants")
                .select("gateway_config")
                .eq("id", merchant_id)
                .single()
                .execute()
            )

            if not merchant_result.data:
                raise Exception(f"Merchant {merchant_id} not found")

            gateway_config = merchant_result.data.get("gateway_config", {})

            # Vérifier signature
            gateway = self.gateways.get(gateway_type)
            if not gateway:
                raise Exception(f"Gateway {gateway_type} not supported")

            signature_header = (
                headers.get("X-Signature")
                or headers.get("X-CMI-Signature")
                or headers.get("kr-hash")
            )
            signature_valid = gateway.verify_webhook(
                payload=raw_body or json.dumps(payload),
                signature=signature_header or "",
                secret=gateway_config.get(f"{gateway_type}_secret_key")
                or gateway_config.get(f"{gateway_type}_api_key", ""),
            )

            if not signature_valid:
                logger.warning(
                    f"Invalid webhook signature from {gateway_type} for merchant {merchant_id}"
                )
                return {"success": False, "error": "Invalid signature"}

            # Extraire informations de paiement
            payment_info = gateway.extract_payment_info(payload)

            # Mettre à jour transaction
            transaction_update = (
                supabase.table("gateway_transactions")
                .update(
                    {
                        "status": payment_info["status"],
                        "completed_at": (
                            datetime.now().isoformat()
                            if payment_info["status"] == "completed"
                            else None
                        ),
                        "webhook_payload": payload,
                        "signature": signature_header,
                    }
                )
                .eq("transaction_id", payment_info["transaction_id"])
                .execute()
            )

            # Si paiement réussi, mettre à jour facture
            if payment_info["status"] == "completed" and transaction_update.data:
                transaction = transaction_update.data[0]
                if transaction.get("invoice_id"):
                    supabase.table("platform_invoices").update(
                        {
                            "status": "paid",
                            "paid_at": datetime.now().isoformat(),
                            "payment_method": gateway_type,
                            "payment_reference": payment_info["transaction_id"],
                        }
                    ).eq("id", transaction["invoice_id"]).execute()

                    logger.info(f"Invoice {transaction['invoice_id']} marked as paid")

            return {
                "success": True,
                "status": payment_info["status"],
                "transaction_id": payment_info["transaction_id"],
                "amount": payment_info["amount"],
            }

        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"success": False, "error": str(e)}

    def get_transaction_status(self, transaction_id: str) -> Dict:
        """Récupère le statut d'une transaction"""

        try:
            result = (
                supabase.table("gateway_transactions")
                .select("*")
                .eq("id", transaction_id)
                .single()
                .execute()
            )

            if result.data:
                return {"success": True, "transaction": result.data}
            else:
                return {"success": False, "error": "Transaction not found"}

        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            return {"success": False, "error": str(e)}


class CMIGateway:
    """Gateway CMI (Centre Monétique Interbancaire)"""

    BASE_URL = "https://payment.cmi.co.ma/api/v1"

    def create_payment(
        self, config: Dict, amount: float, description: str, merchant_id: str, currency: str = "MAD"
    ) -> Dict:
        """Crée un paiement via CMI"""

        order_id = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}-{merchant_id[:8]}"

        payload = {
            "amount": int(amount * 100),  # Convertir en centimes
            "currency": currency,
            "merchant_id": config.get("cmi_merchant_id"),
            "store_key": config.get("cmi_store_key"),
            "terminal_id": config.get("cmi_terminal_id"),
            "order_id": order_id,
            "description": description,
            "callback_url": f"https://yourdomain.com/api/webhook/cmi/{merchant_id}",
            "return_url": f"https://yourdomain.com/payment/return",
            "cancel_url": f"https://yourdomain.com/payment/cancel",
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.get('cmi_api_key')}",
        }

        try:
            logger.info(f"CMI payment request: {order_id}")

            response = requests.post(
                f"{self.BASE_URL}/payments/create", json=payload, headers=headers, timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Calculer date d'expiration (24h)
            expires_at = datetime.now() + timedelta(hours=24)

            return {
                "success": True,
                "transaction_id": data.get("payment_id"),
                "order_id": order_id,
                "payment_url": data.get("payment_url"),
                "status": "pending",
                "gateway": "cmi",
                "expires_at": expires_at.isoformat(),
                "request": payload,
                "response": data,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"CMI API error: {e}")
            return {"success": False, "error": f"CMI API error: {str(e)}", "gateway": "cmi"}
        except Exception as e:
            logger.error(f"CMI payment creation failed: {e}")
            return {"success": False, "error": str(e), "gateway": "cmi"}

    def verify_webhook(self, payload: str, signature: str, secret: str) -> bool:
        """Vérifie la signature webhook CMI (HMAC-SHA256)"""

        if not signature or not secret:
            return False

        try:
            # CMI utilise HMAC-SHA256
            if isinstance(payload, dict):
                message = json.dumps(payload, separators=(",", ":"), sort_keys=True)
            else:
                message = payload

            expected_signature = hmac.new(
                secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            logger.error(f"CMI signature verification failed: {e}")
            return False

    def extract_payment_info(self, payload: Dict) -> Dict:
        """Extrait les informations de paiement du webhook CMI"""

        return {
            "transaction_id": payload.get("payment_id"),
            "status": "completed" if payload.get("status") == "completed" else "failed",
            "amount": float(payload.get("amount", 0)) / 100,  # Convertir centimes en MAD
            "currency": payload.get("currency", "MAD"),
            "paid_at": payload.get("paid_at"),
        }


class PayZenGateway:
    """Gateway PayZen / Lyra"""

    BASE_URL = "https://api.payzen.eu/api-payment/V4"

    def create_payment(
        self, config: Dict, amount: float, description: str, merchant_id: str, currency: str = "MAD"
    ) -> Dict:
        """Crée un paiement via PayZen"""

        order_id = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}-{merchant_id[:8]}"

        payload = {
            "amount": int(amount * 100),  # Centimes
            "currency": currency,
            "orderId": order_id,
            "customer": {
                "reference": merchant_id,
                "email": config.get("merchant_email", "merchant@example.ma"),
            },
            "transactionOptions": {"cardOptions": {"paymentSource": "EC"}},
            "formAction": "PAYMENT",
            "ipnTargetUrl": f"https://yourdomain.com/api/webhook/payzen/{merchant_id}",
            "metadata": {"description": description},
        }

        # Basic Auth: shop_id:api_key en base64
        auth_string = f"{config.get('payzen_shop_id')}:{config.get('payzen_api_key')}"
        auth_header = base64.b64encode(auth_string.encode()).decode()

        headers = {"Content-Type": "application/json", "Authorization": f"Basic {auth_header}"}

        try:
            logger.info(f"PayZen payment request: {order_id}")

            response = requests.post(
                f"{self.BASE_URL}/Charge/CreatePayment", json=payload, headers=headers, timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get("status") == "SUCCESS":
                # PayZen renvoie un formToken à utiliser dans leur widget JS
                expires_at = datetime.now() + timedelta(hours=24)

                return {
                    "success": True,
                    "transaction_id": data["answer"]["orderId"],
                    "order_id": order_id,
                    "form_token": data["answer"]["formToken"],
                    "payment_url": f"https://secure.payzen.eu/vads-payment/{data['answer']['formToken']}",
                    "status": "pending",
                    "gateway": "payzen",
                    "expires_at": expires_at.isoformat(),
                    "request": payload,
                    "response": data,
                }
            else:
                return {
                    "success": False,
                    "error": data.get("answer", {}).get("errorMessage", "Payment creation failed"),
                    "gateway": "payzen",
                    "response": data,
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"PayZen API error: {e}")
            return {"success": False, "error": f"PayZen API error: {str(e)}", "gateway": "payzen"}
        except Exception as e:
            logger.error(f"PayZen payment creation failed: {e}")
            return {"success": False, "error": str(e), "gateway": "payzen"}

    def verify_webhook(self, payload: str, signature: str, secret: str) -> bool:
        """Vérifie la signature webhook PayZen (SHA256)"""

        if not signature or not secret:
            return False

        try:
            # PayZen utilise SHA256(payload + secret)
            expected_signature = hashlib.sha256(f"{payload}{secret}".encode("utf-8")).hexdigest()

            return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            logger.error(f"PayZen signature verification failed: {e}")
            return False

    def extract_payment_info(self, payload: Dict) -> Dict:
        """Extrait les informations de paiement du webhook PayZen"""

        kr_answer = payload.get("kr-answer", {})
        order_details = kr_answer.get("orderDetails", {})
        transactions = kr_answer.get("transactions", [])

        # Premier transaction
        transaction = transactions[0] if transactions else {}

        status_map = {
            "PAID": "completed",
            "CAPTURED": "completed",
            "REFUSED": "failed",
            "CANCELLED": "failed",
        }

        return {
            "transaction_id": order_details.get("orderId"),
            "status": status_map.get(kr_answer.get("orderStatus"), "failed"),
            "amount": float(order_details.get("orderTotalAmount", 0)) / 100,
            "currency": order_details.get("orderCurrency", "MAD"),
            "paid_at": transaction.get("creationDate"),
        }


class SGMarocGateway:
    """Gateway Société Générale Maroc - e-Payment"""

    BASE_URL = "https://epayment.sg.ma/api/v2"

    def __init__(self):
        self.access_tokens = {}  # Cache des tokens par config

    def _get_access_token(self, config: Dict) -> str:
        """Obtient un access token OAuth2 (avec cache)"""

        config_key = config.get("sg_api_username")

        # Vérifier cache
        if config_key in self.access_tokens:
            token_data = self.access_tokens[config_key]
            if datetime.now() < token_data["expires_at"]:
                return token_data["token"]

        # Demander nouveau token
        try:
            auth_url = f"{self.BASE_URL}/oauth/token"
            payload = {
                "grant_type": "client_credentials",
                "client_id": config.get("sg_api_username"),
                "client_secret": config.get("sg_api_password"),
            }

            response = requests.post(auth_url, data=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Stocker dans cache
            self.access_tokens[config_key] = {
                "token": data["access_token"],
                "expires_at": datetime.now() + timedelta(seconds=data["expires_in"] - 60),
            }

            return data["access_token"]

        except Exception as e:
            logger.error(f"SG Maroc token request failed: {e}")
            raise

    def create_payment(
        self, config: Dict, amount: float, description: str, merchant_id: str, currency: str = "MAD"
    ) -> Dict:
        """Crée un paiement via SG Maroc"""

        order_id = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}-{merchant_id[:8]}"

        try:
            access_token = self._get_access_token(config)

            payload = {
                "merchantCode": config.get("sg_merchant_code"),
                "terminalId": config.get("sg_terminal_id"),
                "amount": f"{amount:.2f}",
                "currency": currency,
                "orderId": order_id,
                "description": description,
                "returnUrl": "https://yourdomain.com/payment/return",
                "cancelUrl": "https://yourdomain.com/payment/cancel",
                "ipnUrl": f"https://yourdomain.com/api/webhook/sg/{merchant_id}",
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }

            logger.info(f"SG Maroc payment request: {order_id}")

            response = requests.post(
                f"{self.BASE_URL}/payment/init", json=payload, headers=headers, timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                expires_at = datetime.now() + timedelta(hours=24)

                return {
                    "success": True,
                    "transaction_id": data["transactionId"],
                    "order_id": order_id,
                    "payment_url": data["paymentUrl"],
                    "status": "pending",
                    "gateway": "sg_maroc",
                    "expires_at": expires_at.isoformat(),
                    "request": payload,
                    "response": data,
                }
            else:
                return {
                    "success": False,
                    "error": data.get("error", "Payment creation failed"),
                    "gateway": "sg_maroc",
                    "response": data,
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"SG Maroc API error: {e}")
            return {
                "success": False,
                "error": f"SG Maroc API error: {str(e)}",
                "gateway": "sg_maroc",
            }
        except Exception as e:
            logger.error(f"SG Maroc payment creation failed: {e}")
            return {"success": False, "error": str(e), "gateway": "sg_maroc"}

    def verify_webhook(self, payload: str, signature: str, secret: str) -> bool:
        """Vérifie la signature webhook SG Maroc (HMAC-SHA256 Base64)"""

        if not signature or not secret:
            return False

        try:
            # SG Maroc: construire message (ordre alphabétique)
            if isinstance(payload, str):
                payload = json.loads(payload)

            sorted_keys = sorted(payload.keys())
            message = "".join(str(payload[key]) for key in sorted_keys)

            # HMAC-SHA256 en Base64
            expected_signature = hmac.new(
                secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
            ).digest()

            expected_signature_b64 = base64.b64encode(expected_signature).decode()

            return hmac.compare_digest(expected_signature_b64, signature)

        except Exception as e:
            logger.error(f"SG Maroc signature verification failed: {e}")
            return False

    def extract_payment_info(self, payload: Dict) -> Dict:
        """Extrait les informations de paiement du webhook SG Maroc"""

        status_map = {
            "SUCCESS": "completed",
            "COMPLETED": "completed",
            "FAILED": "failed",
            "REFUSED": "failed",
            "CANCELLED": "failed",
        }

        return {
            "transaction_id": payload.get("transactionId"),
            "status": status_map.get(payload.get("status"), "failed"),
            "amount": float(payload.get("amount", "0")),
            "currency": payload.get("currency", "MAD"),
            "paid_at": payload.get("paymentDate"),
        }


# Instance globale
payment_gateway_service = PaymentGatewayService()
