"""
TrackingRepository - Gestion des liens de tracking
CRUD et requêtes spécifiques pour la table tracking_links
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class TrackingRepository(BaseRepository):
    """Repository pour la table trackable_links"""

    def get_table_name(self) -> str:
        return "trackable_links"

    # ============================================================================
    # REQUÊTES SPÉCIFIQUES TRACKING LINKS
    # ============================================================================

    def find_by_merchant(self, merchant_id: str) -> List[Dict]:
        """
        Trouve tous les liens d'un merchant
        
        Args:
            merchant_id: ID du merchant
            
        Returns:
            Liste de liens de tracking
        """
        return self.find_all({"merchant_id": merchant_id})

    def find_by_influencer(self, influencer_id: str) -> List[Dict]:
        """
        Trouve tous les liens d'un influencer
        
        Args:
            influencer_id: ID de l'influencer
            
        Returns:
            Liste de liens de tracking
        """
        return self.find_all({"influencer_id": influencer_id})

    def find_by_product(self, product_id: str) -> List[Dict]:
        """
        Trouve les liens d'un produit
        
        Args:
            product_id: ID du produit
            
        Returns:
            Liste de liens de tracking
        """
        return self.find_all({"product_id": product_id})

    def find_by_short_code(self, short_code: str) -> Optional[Dict]:
        """
        Trouve un lien par son code court
        
        Args:
            short_code: Code court (ex: ABC123)
            
        Returns:
            Lien de tracking ou None
        """
        return self.find_one({"unique_code": short_code})

    def find_active_links(self, merchant_id: Optional[str] = None, influencer_id: Optional[str] = None) -> List[Dict]:
        """
        Trouve les liens actifs
        
        Args:
            merchant_id: Filtre optionnel par merchant
            influencer_id: Filtre optionnel par influencer
            
        Returns:
            Liste de liens actifs
        """
        filters = {"is_active": True}
        if merchant_id:
            filters["merchant_id"] = merchant_id
        if influencer_id:
            filters["influencer_id"] = influencer_id
        return self.find_all(filters)

    def short_code_exists(self, short_code: str) -> bool:
        """
        Vérifie si un code court existe déjà
        
        Args:
            short_code: Code court à vérifier
            
        Returns:
            True si existe, False sinon
        """
        return self.find_by_short_code(short_code) is not None

    def increment_clicks(self, link_id: str) -> Optional[Dict]:
        """
        Incrémente le compteur de clics d'un lien
        
        Args:
            link_id: ID du lien
            
        Returns:
            Lien mis à jour ou None
        """
        link = self.find_by_id(link_id)
        if not link:
            return None
        
        new_clicks = link.get("total_clicks", 0) + 1
        return self.update(link_id, {"total_clicks": new_clicks})

    def increment_conversions(self, link_id: str) -> Optional[Dict]:
        """
        Incrémente le compteur de conversions d'un lien
        
        Args:
            link_id: ID du lien
            
        Returns:
            Lien mis à jour ou None
        """
        link = self.find_by_id(link_id)
        if not link:
            return None
        
        new_conversions = link.get("total_conversions", 0) + 1
        return self.update(link_id, {"total_conversions": new_conversions})

    def update_revenue(self, link_id: str, additional_revenue: float) -> Optional[Dict]:
        """
        Met à jour le revenu généré par un lien
        
        Args:
            link_id: ID du lien
            additional_revenue: Revenu additionnel
            
        Returns:
            Lien mis à jour ou None
        """
        link = self.find_by_id(link_id)
        if not link:
            return None
        
        new_revenue = link.get("total_revenue", 0) + additional_revenue
        return self.update(link_id, {"total_revenue": new_revenue})

    def activate_link(self, link_id: str) -> Optional[Dict]:
        """
        Active un lien de tracking
        
        Args:
            link_id: ID du lien
            
        Returns:
            Lien mis à jour ou None
        """
        return self.update(link_id, {"is_active": True})

    def deactivate_link(self, link_id: str) -> Optional[Dict]:
        """
        Désactive un lien de tracking
        
        Args:
            link_id: ID du lien
            
        Returns:
            Lien mis à jour ou None
        """
        return self.update(link_id, {"is_active": False})

    def get_conversion_rate(self, link_id: str) -> float:
        """
        Calcule le taux de conversion d'un lien
        
        Args:
            link_id: ID du lien
            
        Returns:
            Taux de conversion (%)
        """
        link = self.find_by_id(link_id)
        if not link:
            return 0.0
        
        clicks = link.get("total_clicks", 0)
        if clicks == 0:
            return 0.0
        
        conversions = link.get("total_conversions", 0)
        return (conversions / clicks) * 100

    def get_performance_metrics(self, link_id: str) -> Dict:
        """
        Récupère les métriques de performance d'un lien
        
        Args:
            link_id: ID du lien
            
        Returns:
            Dict avec clicks, conversions, revenue, conversion_rate
        """
        link = self.find_by_id(link_id)
        if not link:
            return {
                "clicks": 0,
                "conversions": 0,
                "revenue": 0.0,
                "conversion_rate": 0.0
            }
        
        clicks = link.get("total_clicks", 0)
        conversions = link.get("total_conversions", 0)
        revenue = link.get("total_revenue", 0.0)
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        
        return {
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "conversion_rate": conversion_rate
        }

    def get_top_performing_links(self, limit: int = 10, merchant_id: Optional[str] = None, influencer_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les liens les plus performants
        
        Args:
            limit: Nombre de liens
            merchant_id: Filtre par merchant
            influencer_id: Filtre par influencer
            
        Returns:
            Liste de liens triés par conversions
        """
        try:
            query = self.table.select("*").order("total_conversions", desc=True).limit(limit)
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            if influencer_id:
                query = query.eq("influencer_id", influencer_id)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting top performing links: {e}")
            return []

    def get_links_created_today(self, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les liens créés aujourd'hui
        
        Args:
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de liens
        """
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        
        try:
            query = self.table.select("*") \
                .gte("created_at", today) \
                .lt("created_at", tomorrow)
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting links created today: {e}")
            return []

    def count_active_links(self, merchant_id: Optional[str] = None, influencer_id: Optional[str] = None) -> int:
        """
        Compte le nombre de liens actifs
        
        Args:
            merchant_id: Filtre par merchant
            influencer_id: Filtre par influencer
            
        Returns:
            Nombre de liens actifs
        """
        filters = {"is_active": True}
        if merchant_id:
            filters["merchant_id"] = merchant_id
        if influencer_id:
            filters["influencer_id"] = influencer_id
        
        return self.count(filters)

    def get_total_clicks(self, merchant_id: Optional[str] = None, influencer_id: Optional[str] = None) -> int:
        """
        Calcule le total de clics
        
        Args:
            merchant_id: Filtre par merchant
            influencer_id: Filtre par influencer
            
        Returns:
            Nombre total de clics
        """
        try:
            query = self.table.select("total_clicks")
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            if influencer_id:
                query = query.eq("influencer_id", influencer_id)
            
            result = query.execute()
            
            if result.data:
                return sum(link.get("total_clicks", 0) for link in result.data)
            return 0
        except Exception as e:
            logger.error(f"Error calculating total clicks: {e}")
            return 0

    def get_total_conversions(self, merchant_id: Optional[str] = None, influencer_id: Optional[str] = None) -> int:
        """
        Calcule le total de conversions
        
        Args:
            merchant_id: Filtre par merchant
            influencer_id: Filtre par influencer
            
        Returns:
            Nombre total de conversions
        """
        try:
            query = self.table.select("total_conversions")
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            if influencer_id:
                query = query.eq("influencer_id", influencer_id)
            
            result = query.execute()
            
            if result.data:
                return sum(link.get("total_conversions", 0) for link in result.data)
            return 0
        except Exception as e:
            logger.error(f"Error calculating total conversions: {e}")
            return 0

    def get_overall_conversion_rate(self, merchant_id: Optional[str] = None, influencer_id: Optional[str] = None) -> float:
        """
        Calcule le taux de conversion global
        
        Args:
            merchant_id: Filtre par merchant
            influencer_id: Filtre par influencer
            
        Returns:
            Taux de conversion global (%)
        """
        clicks = self.get_total_clicks(merchant_id, influencer_id)
        if clicks == 0:
            return 0.0
        
        conversions = self.get_total_conversions(merchant_id, influencer_id)
        return (conversions / clicks) * 100
