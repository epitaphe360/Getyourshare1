"""
Service de gestion des ventes.
Contient la logique métier pour la création et la gestion des ventes.
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class SalesService:
    """Service pour gérer les ventes et appeler les fonctions transactionnelles."""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def create_sale(
        self,
        link_id: UUID,
        product_id: UUID,
        influencer_id: UUID,
        merchant_id: UUID,
        amount: float,
        currency: str = "EUR",
        quantity: int = 1,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
        payment_status: str = "pending",
        status: str = "completed",
    ) -> dict:
        """
        Crée une vente en appelant la fonction PL/pgSQL create_sale_transaction.

        Args:
            link_id: ID du lien tracké
            product_id: ID du produit
            influencer_id: ID de l'influenceur
            merchant_id: ID du merchant
            amount: Montant de la vente
            currency: Devise (défaut: EUR)
            quantity: Quantité (défaut: 1)
            customer_email: Email du client (optionnel)
            customer_name: Nom du client (optionnel)
            payment_status: Statut de paiement (défaut: pending)
            status: Statut de la vente (défaut: completed)

        Returns:
            dict: Enregistrement de la vente créée

        Raises:
            ValueError: Si les paramètres sont invalides
            RuntimeError: Si l'appel à la fonction PL/pgSQL échoue
        """
        try:
            logger.info(f"Création vente: product={product_id}, amount={amount}")

            # Appel de la fonction PL/pgSQL create_sale_transaction via RPC
            result = self.supabase.rpc(
                "create_sale_transaction",
                {
                    "p_link_id": str(link_id),
                    "p_product_id": str(product_id),
                    "p_influencer_id": str(influencer_id),
                    "p_merchant_id": str(merchant_id),
                    "p_amount": amount,
                    "p_currency": currency,
                    "p_quantity": quantity,
                    "p_customer_email": customer_email,
                    "p_customer_name": customer_name,
                    "p_payment_status": payment_status,
                    "p_status": status,
                },
            ).execute()

            if not result.data:
                raise RuntimeError("La fonction create_sale_transaction n'a retourné aucune donnée")

            sale = result.data
            logger.info(f"Vente créée avec succès: sale_id={sale.get('id')}")

            return sale

        except Exception as e:
            logger.error(f"Erreur lors de la création de la vente: {str(e)}")
            # Parser l'erreur PostgreSQL pour renvoyer un message plus clair
            error_msg = str(e)
            if "Le montant de la vente doit être supérieur à 0" in error_msg:
                raise ValueError("Le montant de la vente doit être supérieur à 0")
            elif "La quantité doit être positive" in error_msg:
                raise ValueError("La quantité doit être positive")
            elif "introuvable" in error_msg:
                raise ValueError(f"Ressource introuvable: {error_msg}")
            elif "ne correspond pas" in error_msg:
                raise ValueError(f"Incohérence des données: {error_msg}")
            else:
                raise RuntimeError(f"Erreur lors de la création de la vente: {error_msg}")

    async def get_sale_by_id(self, sale_id: UUID) -> Optional[dict]:
        """
        Récupère une vente par son ID.

        Args:
            sale_id: ID de la vente

        Returns:
            dict ou None: La vente si trouvée
        """
        try:
            result = self.supabase.table("sales").select("*").eq("id", str(sale_id)).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la vente {sale_id}: {str(e)}")
            return None

    async def get_sales_by_influencer(
        self, influencer_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[dict]:
        """
        Récupère les ventes d'un influenceur.

        Args:
            influencer_id: ID de l'influenceur
            limit: Nombre max de résultats
            offset: Offset pour la pagination

        Returns:
            list[dict]: Liste des ventes
        """
        try:
            result = (
                self.supabase.table("sales")
                .select("*")
                .eq("influencer_id", str(influencer_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des ventes: {str(e)}")
            return []

    async def get_sales_by_merchant(
        self, merchant_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[dict]:
        """
        Récupère les ventes d'un merchant.

        Args:
            merchant_id: ID du merchant
            limit: Nombre max de résultats
            offset: Offset pour la pagination

        Returns:
            list[dict]: Liste des ventes
        """
        try:
            result = (
                self.supabase.table("sales")
                .select("*")
                .eq("merchant_id", str(merchant_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des ventes: {str(e)}")
            return []

    async def update_sale_status(
        self, sale_id: UUID, status: str, payment_status: Optional[str] = None
    ) -> Optional[dict]:
        """
        Met à jour le statut d'une vente.

        Args:
            sale_id: ID de la vente
            status: Nouveau statut ('pending', 'completed', 'refunded', 'cancelled')
            payment_status: Nouveau statut de paiement (optionnel)

        Returns:
            dict ou None: La vente mise à jour
        """
        try:
            update_data = {"status": status}
            if payment_status:
                update_data["payment_status"] = payment_status
                if payment_status == "paid":
                    update_data["payment_processed_at"] = datetime.utcnow().isoformat()

            result = (
                self.supabase.table("sales").update(update_data).eq("id", str(sale_id)).execute()
            )

            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut de la vente: {str(e)}")
            return None
