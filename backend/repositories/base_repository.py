"""
BaseRepository - Interface de base pour tous les repositories
Fournit les opérations CRUD standard
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """
    Classe de base abstraite pour tous les repositories
    Implémente le pattern Repository pour l'accès aux données
    """

    def __init__(self, supabase_client):
        """
        Initialise le repository avec le client Supabase
        
        Args:
            supabase_client: Client Supabase pour l'accès DB
        """
        self.supabase = supabase_client
        self._table_name = None

    @abstractmethod
    def get_table_name(self) -> str:
        """
        Retourne le nom de la table Supabase
        Doit être implémenté par chaque repository concret
        """
        pass

    @property
    def table(self):
        """Accès rapide à la table Supabase"""
        if not self._table_name:
            self._table_name = self.get_table_name()
        return self.supabase.table(self._table_name)

    # ============================================================================
    # CRUD DE BASE
    # ============================================================================

    def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Trouve une entité par son ID
        
        Args:
            id: Identifiant de l'entité
            
        Returns:
            Dict contenant les données ou None si non trouvé
        """
        try:
            result = self.table.select("*").eq("id", id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error finding {self.get_table_name()} by ID {id}: {e}")
            return None

    def find_all(self, filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Trouve toutes les entités avec filtres optionnels
        
        Args:
            filters: Dictionnaire de filtres (ex: {"role": "merchant"})
            limit: Nombre maximum de résultats
            
        Returns:
            Liste de dictionnaires contenant les données
        """
        try:
            query = self.table.select("*")
            
            # Appliquer les filtres
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Appliquer la limite
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error finding all {self.get_table_name()}: {e}")
            return []

    def find_one(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Trouve une seule entité avec les filtres donnés
        
        Args:
            filters: Dictionnaire de filtres
            
        Returns:
            Dict contenant les données ou None
        """
        results = self.find_all(filters=filters, limit=1)
        return results[0] if results else None

    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crée une nouvelle entité
        
        Args:
            data: Données de l'entité à créer
            
        Returns:
            Dict contenant les données créées ou None en cas d'erreur
        """
        try:
            # Ajouter created_at si non présent
            if "created_at" not in data:
                data["created_at"] = datetime.now().isoformat()
            
            result = self.table.insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating {self.get_table_name()}: {e}")
            return None

    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour une entité existante
        
        Args:
            id: Identifiant de l'entité
            data: Données à mettre à jour
            
        Returns:
            Dict contenant les données mises à jour ou None
        """
        try:
            # Ajouter updated_at
            data["updated_at"] = datetime.now().isoformat()
            
            result = self.table.update(data).eq("id", id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating {self.get_table_name()} {id}: {e}")
            return None

    def delete(self, id: str) -> bool:
        """
        Supprime une entité
        
        Args:
            id: Identifiant de l'entité
            
        Returns:
            True si suppression réussie, False sinon
        """
        try:
            self.table.delete().eq("id", id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.get_table_name()} {id}: {e}")
            return False

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Compte le nombre d'entités
        
        Args:
            filters: Filtres optionnels
            
        Returns:
            Nombre d'entités
        """
        try:
            query = self.table.select("*", count="exact")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.execute()
            return result.count if hasattr(result, 'count') else len(result.data)
        except Exception as e:
            logger.error(f"Error counting {self.get_table_name()}: {e}")
            return 0

    def exists(self, id: str) -> bool:
        """
        Vérifie si une entité existe
        
        Args:
            id: Identifiant de l'entité
            
        Returns:
            True si existe, False sinon
        """
        return self.find_by_id(id) is not None

    # ============================================================================
    # REQUÊTES AVANCÉES
    # ============================================================================

    def find_where(self, column: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """
        Trouve des entités avec un opérateur personnalisé
        
        Args:
            column: Nom de la colonne
            operator: Opérateur (eq, neq, gt, gte, lt, lte, like, ilike, in_)
            value: Valeur à comparer
            
        Returns:
            Liste d'entités
        """
        try:
            query = self.table.select("*")
            
            # Appliquer l'opérateur
            if operator == "eq":
                query = query.eq(column, value)
            elif operator == "neq":
                query = query.neq(column, value)
            elif operator == "gt":
                query = query.gt(column, value)
            elif operator == "gte":
                query = query.gte(column, value)
            elif operator == "lt":
                query = query.lt(column, value)
            elif operator == "lte":
                query = query.lte(column, value)
            elif operator == "like":
                query = query.like(column, value)
            elif operator == "ilike":
                query = query.ilike(column, value)
            elif operator == "in_":
                query = query.in_(column, value)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error finding where {column} {operator} {value}: {e}")
            return []

    def find_by_date_range(self, date_column: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Trouve des entités dans une plage de dates
        
        Args:
            date_column: Nom de la colonne date
            start_date: Date de début (ISO format)
            end_date: Date de fin (ISO format)
            
        Returns:
            Liste d'entités
        """
        try:
            result = self.table.select("*") \
                .gte(date_column, start_date) \
                .lte(date_column, end_date) \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error finding by date range: {e}")
            return []

    def paginate(self, page: int = 1, page_size: int = 10, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Pagination des résultats
        
        Args:
            page: Numéro de page (commence à 1)
            page_size: Nombre d'éléments par page
            filters: Filtres optionnels
            
        Returns:
            Dict avec {data, total, page, page_size, total_pages}
        """
        try:
            # Calculer offset
            offset = (page - 1) * page_size
            
            # Requête pour les données
            query = self.table.select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            query = query.range(offset, offset + page_size - 1)
            result = query.execute()
            
            # Compter le total
            total = self.count(filters)
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "data": result.data if result.data else [],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        except Exception as e:
            logger.error(f"Error paginating {self.get_table_name()}: {e}")
            return {
                "data": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }

    # ============================================================================
    # OPÉRATIONS EN MASSE
    # ============================================================================

    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Crée plusieurs entités en une fois
        
        Args:
            data_list: Liste de dictionnaires à insérer
            
        Returns:
            Liste des entités créées
        """
        try:
            # Ajouter created_at à tous
            now = datetime.now().isoformat()
            for data in data_list:
                if "created_at" not in data:
                    data["created_at"] = now
            
            result = self.table.insert(data_list).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error bulk creating {self.get_table_name()}: {e}")
            return []

    def bulk_update(self, updates: List[Dict[str, Any]]) -> bool:
        """
        Met à jour plusieurs entités (nécessite id dans chaque dict)
        
        Args:
            updates: Liste de dicts avec id et champs à mettre à jour
            
        Returns:
            True si succès, False sinon
        """
        try:
            now = datetime.now().isoformat()
            for update in updates:
                if "id" in update:
                    update_data = {k: v for k, v in update.items() if k != "id"}
                    update_data["updated_at"] = now
                    self.update(update["id"], update_data)
            return True
        except Exception as e:
            logger.error(f"Error bulk updating {self.get_table_name()}: {e}")
            return False

    def bulk_delete(self, ids: List[str]) -> bool:
        """
        Supprime plusieurs entités
        
        Args:
            ids: Liste d'identifiants
            
        Returns:
            True si succès, False sinon
        """
        try:
            self.table.delete().in_("id", ids).execute()
            return True
        except Exception as e:
            logger.error(f"Error bulk deleting {self.get_table_name()}: {e}")
            return False
