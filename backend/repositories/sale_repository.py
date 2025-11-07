"""
SaleRepository - Gestion des ventes
CRUD et requêtes spécifiques pour la table sales
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class SaleRepository(BaseRepository):
    """Repository pour la table sales"""

    def get_table_name(self) -> str:
        return "sales"

    # ============================================================================
    # REQUÊTES SPÉCIFIQUES SALES
    # ============================================================================

    def find_by_merchant(self, merchant_id: str) -> List[Dict]:
        """
        Trouve toutes les ventes d'un merchant
        
        Args:
            merchant_id: ID du merchant
            
        Returns:
            Liste de ventes
        """
        return self.find_all({"merchant_id": merchant_id})

    def find_by_influencer(self, influencer_id: str) -> List[Dict]:
        """
        Trouve toutes les ventes d'un influencer
        
        Args:
            influencer_id: ID de l'influencer
            
        Returns:
            Liste de ventes
        """
        return self.find_all({"influencer_id": influencer_id})

    def find_by_product(self, product_id: str) -> List[Dict]:
        """
        Trouve toutes les ventes d'un produit
        
        Args:
            product_id: ID du produit
            
        Returns:
            Liste de ventes
        """
        return self.find_all({"product_id": product_id})

    def find_by_tracking_link(self, tracking_link_id: str) -> List[Dict]:
        """
        Trouve les ventes d'un lien de tracking
        
        Args:
            tracking_link_id: ID du lien de tracking
            
        Returns:
            Liste de ventes
        """
        return self.find_all({"tracking_link_id": tracking_link_id})

    def find_by_status(self, status: str, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Trouve les ventes par statut
        
        Args:
            status: Statut (pending, completed, cancelled, refunded)
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de ventes
        """
        filters = {"status": status}
        if merchant_id:
            filters["merchant_id"] = merchant_id
        return self.find_all(filters)

    def get_total_revenue(self, merchant_id: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> float:
        """
        Calcule le revenu total
        
        Args:
            merchant_id: Filtre optionnel par merchant
            start_date: Date de début (ISO)
            end_date: Date de fin (ISO)
            
        Returns:
            Revenu total
        """
        try:
            query = self.table.select("amount").eq("status", "completed")
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            if start_date:
                query = query.gte("created_at", start_date)
            
            if end_date:
                query = query.lte("created_at", end_date)
            
            result = query.execute()
            
            if result.data:
                return sum(sale.get("amount", 0) for sale in result.data)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating total revenue: {e}")
            return 0.0

    def get_total_commission(self, influencer_id: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> float:
        """
        Calcule le total des commissions
        
        Args:
            influencer_id: Filtre optionnel par influencer
            start_date: Date de début (ISO)
            end_date: Date de fin (ISO)
            
        Returns:
            Total des commissions
        """
        try:
            query = self.table.select("commission_amount").eq("status", "completed")
            
            if influencer_id:
                query = query.eq("influencer_id", influencer_id)
            
            if start_date:
                query = query.gte("created_at", start_date)
            
            if end_date:
                query = query.lte("created_at", end_date)
            
            result = query.execute()
            
            if result.data:
                return sum(sale.get("commission_amount", 0) for sale in result.data)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating total commission: {e}")
            return 0.0

    def count_sales(self, merchant_id: Optional[str] = None, influencer_id: Optional[str] = None, status: Optional[str] = None) -> int:
        """
        Compte le nombre de ventes
        
        Args:
            merchant_id: Filtre optionnel par merchant
            influencer_id: Filtre optionnel par influencer
            status: Filtre optionnel par statut
            
        Returns:
            Nombre de ventes
        """
        filters = {}
        if merchant_id:
            filters["merchant_id"] = merchant_id
        if influencer_id:
            filters["influencer_id"] = influencer_id
        if status:
            filters["status"] = status
        
        return self.count(filters)

    def get_sales_by_date_range(self, start_date: str, end_date: str, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les ventes dans une plage de dates
        
        Args:
            start_date: Date de début (ISO)
            end_date: Date de fin (ISO)
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de ventes
        """
        try:
            query = self.table.select("*") \
                .gte("created_at", start_date) \
                .lte("created_at", end_date)
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting sales by date range: {e}")
            return []

    def get_recent_sales(self, limit: int = 10, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les ventes récentes
        
        Args:
            limit: Nombre de ventes à retourner
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de ventes récentes
        """
        try:
            query = self.table.select("*").order("created_at", desc=True).limit(limit)
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting recent sales: {e}")
            return []

    def get_sales_today(self, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les ventes du jour
        
        Args:
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de ventes du jour
        """
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        return self.get_sales_by_date_range(today, tomorrow, merchant_id)

    def get_sales_this_month(self, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les ventes du mois
        
        Args:
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de ventes du mois
        """
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1).isoformat()
        return self.get_sales_by_date_range(start_of_month, end_of_month, merchant_id)

    def update_sale_status(self, sale_id: str, status: str) -> Optional[Dict]:
        """
        Met à jour le statut d'une vente
        
        Args:
            sale_id: ID de la vente
            status: Nouveau statut (pending, completed, cancelled, refunded)
            
        Returns:
            Vente mise à jour ou None
        """
        valid_statuses = ["pending", "completed", "cancelled", "refunded"]
        if status not in valid_statuses:
            logger.error(f"Invalid status: {status}")
            return None
        
        return self.update(sale_id, {"status": status})

    def confirm_sale(self, sale_id: str) -> Optional[Dict]:
        """
        Confirme une vente (passe à completed)
        
        Args:
            sale_id: ID de la vente
            
        Returns:
            Vente mise à jour ou None
        """
        return self.update_sale_status(sale_id, "completed")

    def cancel_sale(self, sale_id: str) -> Optional[Dict]:
        """
        Annule une vente
        
        Args:
            sale_id: ID de la vente
            
        Returns:
            Vente mise à jour ou None
        """
        return self.update_sale_status(sale_id, "cancelled")

    def refund_sale(self, sale_id: str) -> Optional[Dict]:
        """
        Rembourse une vente
        
        Args:
            sale_id: ID de la vente
            
        Returns:
            Vente mise à jour ou None
        """
        return self.update_sale_status(sale_id, "refunded")

    def get_conversion_rate(self, merchant_id: Optional[str] = None, influencer_id: Optional[str] = None) -> float:
        """
        Calcule le taux de conversion
        
        Args:
            merchant_id: Filtre par merchant
            influencer_id: Filtre par influencer
            
        Returns:
            Taux de conversion (%)
        """
        try:
            # Total des clics (devrait venir de tracking_links)
            # Pour simplifier, on calcule ratio completed/pending+completed
            
            filters = {}
            if merchant_id:
                filters["merchant_id"] = merchant_id
            if influencer_id:
                filters["influencer_id"] = influencer_id
            
            total_sales = self.count(filters)
            if total_sales == 0:
                return 0.0
            
            filters["status"] = "completed"
            completed_sales = self.count(filters)
            
            return (completed_sales / total_sales) * 100
        except Exception as e:
            logger.error(f"Error calculating conversion rate: {e}")
            return 0.0

    def get_top_products(self, limit: int = 10, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les produits les plus vendus
        
        Args:
            limit: Nombre de produits
            merchant_id: Filtre par merchant
            
        Returns:
            Liste de {product_id, product_name, total_sales, total_revenue}
        """
        try:
            params = {"p_limit": limit}
            if merchant_id:
                params["p_merchant_id"] = merchant_id
            
            result = self.supabase.rpc("get_top_selling_products", params).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []

    def get_top_influencers(self, limit: int = 10, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les influencers les plus performants
        
        Args:
            limit: Nombre d'influencers
            merchant_id: Filtre par merchant
            
        Returns:
            Liste de {influencer_id, influencer_name, total_sales, total_revenue}
        """
        try:
            params = {"p_limit": limit}
            if merchant_id:
                params["p_merchant_id"] = merchant_id
            
            result = self.supabase.rpc("get_top_influencers", params).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting top influencers: {e}")
            return []
