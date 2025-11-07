"""
ProductRepository - Gestion des produits
CRUD et requêtes spécifiques pour la table products
"""

from typing import Dict, List, Optional
from .base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class ProductRepository(BaseRepository):
    """Repository pour la table products"""

    def get_table_name(self) -> str:
        return "products"

    # ============================================================================
    # REQUÊTES SPÉCIFIQUES PRODUCTS
    # ============================================================================

    def find_by_merchant(self, merchant_id: str) -> List[Dict]:
        """
        Trouve tous les produits d'un merchant
        
        Args:
            merchant_id: ID du merchant
            
        Returns:
            Liste de produits
        """
        return self.find_all({"merchant_id": merchant_id})

    def count_by_merchant(self, merchant_id: str) -> int:
        """
        Compte les produits d'un merchant
        
        Args:
            merchant_id: ID du merchant
            
        Returns:
            Nombre de produits
        """
        return self.count({"merchant_id": merchant_id})

    def find_active_products(self, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Trouve les produits actifs
        
        Args:
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de produits actifs
        """
        filters = {"is_active": True}
        if merchant_id:
            filters["merchant_id"] = merchant_id
        return self.find_all(filters)

    def find_by_category(self, category: str) -> List[Dict]:
        """
        Trouve les produits d'une catégorie
        
        Args:
            category: Nom de la catégorie
            
        Returns:
            Liste de produits
        """
        return self.find_all({"category": category})

    def find_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """
        Trouve les produits dans une fourchette de prix
        
        Args:
            min_price: Prix minimum
            max_price: Prix maximum
            
        Returns:
            Liste de produits
        """
        try:
            result = self.table.select("*") \
                .gte("price", min_price) \
                .lte("price", max_price) \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error finding products by price range: {e}")
            return []

    def search_products(self, query: str, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Recherche de produits par nom ou description
        
        Args:
            query: Texte de recherche
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de produits correspondants
        """
        try:
            search_query = self.table.select("*").or_(
                f"name.ilike.%{query}%,"
                f"description.ilike.%{query}%"
            )
            
            if merchant_id:
                search_query = search_query.eq("merchant_id", merchant_id)
            
            result = search_query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []

    def activate_product(self, product_id: str) -> Optional[Dict]:
        """
        Active un produit
        
        Args:
            product_id: ID du produit
            
        Returns:
            Produit mis à jour ou None
        """
        return self.update(product_id, {"is_active": True})

    def deactivate_product(self, product_id: str) -> Optional[Dict]:
        """
        Désactive un produit
        
        Args:
            product_id: ID du produit
            
        Returns:
            Produit mis à jour ou None
        """
        return self.update(product_id, {"is_active": False})

    def update_stock(self, product_id: str, quantity: int) -> Optional[Dict]:
        """
        Met à jour le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Nouvelle quantité
            
        Returns:
            Produit mis à jour ou None
        """
        return self.update(product_id, {"stock_quantity": quantity})

    def decrement_stock(self, product_id: str, quantity: int) -> Optional[Dict]:
        """
        Décrémente le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Quantité à décrémenter
            
        Returns:
            Produit mis à jour ou None
        """
        product = self.find_by_id(product_id)
        if not product:
            return None
        
        new_quantity = max(0, product.get("stock_quantity", 0) - quantity)
        return self.update_stock(product_id, new_quantity)

    def increment_stock(self, product_id: str, quantity: int) -> Optional[Dict]:
        """
        Incrémente le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Quantité à incrémenter
            
        Returns:
            Produit mis à jour ou None
        """
        product = self.find_by_id(product_id)
        if not product:
            return None
        
        new_quantity = product.get("stock_quantity", 0) + quantity
        return self.update_stock(product_id, new_quantity)

    def get_low_stock_products(self, threshold: int = 10, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Trouve les produits avec stock faible
        
        Args:
            threshold: Seuil de stock faible
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de produits en stock faible
        """
        try:
            query = self.table.select("*").lte("stock_quantity", threshold)
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting low stock products: {e}")
            return []

    def get_out_of_stock_products(self, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Trouve les produits en rupture de stock
        
        Args:
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de produits en rupture
        """
        filters = {"stock_quantity": 0}
        if merchant_id:
            filters["merchant_id"] = merchant_id
        return self.find_all(filters)

    def get_best_sellers(self, limit: int = 10, merchant_id: Optional[str] = None) -> List[Dict]:
        """
        Récupère les produits les plus vendus
        
        Args:
            limit: Nombre de produits à retourner
            merchant_id: Filtre optionnel par merchant
            
        Returns:
            Liste de produits les plus vendus
        """
        try:
            query = self.table.select("*").order("total_sales", desc=True).limit(limit)
            
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting best sellers: {e}")
            return []

    def update_commission_rate(self, product_id: str, commission_rate: float) -> Optional[Dict]:
        """
        Met à jour le taux de commission d'un produit
        
        Args:
            product_id: ID du produit
            commission_rate: Nouveau taux (0-100)
            
        Returns:
            Produit mis à jour ou None
        """
        if not 0 <= commission_rate <= 100:
            logger.error(f"Invalid commission rate: {commission_rate}")
            return None
        
        return self.update(product_id, {"commission_rate": commission_rate})

    def get_products_with_tracking_links(self, merchant_id: str) -> List[Dict]:
        """
        Récupère les produits avec le nombre de liens de tracking
        
        Args:
            merchant_id: ID du merchant
            
        Returns:
            Liste de produits avec nombre de liens
        """
        try:
            result = self.supabase.rpc(
                "get_products_with_tracking_count",
                {"p_merchant_id": merchant_id}
            ).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting products with tracking links: {e}")
            return self.find_by_merchant(merchant_id)
