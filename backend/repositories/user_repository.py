"""
UserRepository - Gestion des utilisateurs
CRUD et requêtes spécifiques pour la table users
"""

from typing import Dict, List, Optional
from .base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository pour la table users"""

    def get_table_name(self) -> str:
        return "users"

    # ============================================================================
    # REQUÊTES SPÉCIFIQUES USERS
    # ============================================================================

    def find_by_email(self, email: str) -> Optional[Dict]:
        """
        Trouve un utilisateur par email
        
        Args:
            email: Adresse email
            
        Returns:
            User dict ou None
        """
        return self.find_one({"email": email})

    def find_by_role(self, role: str) -> List[Dict]:
        """
        Trouve tous les utilisateurs d'un rôle
        
        Args:
            role: Role (admin, merchant, influencer)
            
        Returns:
            Liste d'utilisateurs
        """
        return self.find_all({"role": role})

    def count_by_role(self, role: str) -> int:
        """
        Compte les utilisateurs d'un rôle
        
        Args:
            role: Role à compter
            
        Returns:
            Nombre d'utilisateurs
        """
        return self.count({"role": role})

    def find_active_users(self) -> List[Dict]:
        """
        Trouve tous les utilisateurs actifs (non désactivés)
        
        Returns:
            Liste d'utilisateurs actifs
        """
        return self.find_where("is_active", "eq", True)

    def find_by_subscription(self, subscription_plan: str) -> List[Dict]:
        """
        Trouve les utilisateurs avec un plan d'abonnement spécifique
        
        Args:
            subscription_plan: Nom du plan (free, pro, enterprise)
            
        Returns:
            Liste d'utilisateurs
        """
        return self.find_all({"subscription_plan": subscription_plan})

    def activate_user(self, user_id: str) -> Optional[Dict]:
        """
        Active un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            User mis à jour ou None
        """
        return self.update(user_id, {"is_active": True})

    def deactivate_user(self, user_id: str) -> Optional[Dict]:
        """
        Désactive un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            User mis à jour ou None
        """
        return self.update(user_id, {"is_active": False})

    def update_last_login(self, user_id: str) -> Optional[Dict]:
        """
        Met à jour la date de dernière connexion
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            User mis à jour ou None
        """
        from datetime import datetime
        return self.update(user_id, {"last_login": datetime.now().isoformat()})

    def update_profile(self, user_id: str, profile_data: Dict) -> Optional[Dict]:
        """
        Met à jour le profil utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            profile_data: Données du profil (first_name, last_name, phone, etc.)
            
        Returns:
            User mis à jour ou None
        """
        # Filtrer les champs autorisés
        allowed_fields = {
            "first_name", "last_name", "phone", "avatar_url",
            "bio", "website", "location", "company_name"
        }
        filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        
        return self.update(user_id, filtered_data)

    def update_subscription(self, user_id: str, plan: str, expires_at: Optional[str] = None) -> Optional[Dict]:
        """
        Met à jour l'abonnement d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            plan: Nouveau plan (free, pro, enterprise)
            expires_at: Date d'expiration (ISO format)
            
        Returns:
            User mis à jour ou None
        """
        data = {"subscription_plan": plan}
        if expires_at:
            data["subscription_expires_at"] = expires_at
        
        return self.update(user_id, data)

    def get_merchants_with_stats(self) -> List[Dict]:
        """
        Récupère les merchants avec leurs statistiques
        (nombre de produits, ventes, etc.)
        
        Returns:
            Liste de merchants avec stats
        """
        try:
            # Requête avec jointure sur products et sales
            result = self.supabase.rpc(
                "get_merchants_with_stats"
            ).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting merchants with stats: {e}")
            # Fallback: retourner juste les merchants
            return self.find_by_role("merchant")

    def get_influencers_with_stats(self) -> List[Dict]:
        """
        Récupère les influencers avec leurs statistiques
        (nombre de liens, conversions, etc.)
        
        Returns:
            Liste d'influencers avec stats
        """
        try:
            result = self.supabase.rpc(
                "get_influencers_with_stats"
            ).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting influencers with stats: {e}")
            return self.find_by_role("influencer")

    def search_users(self, query: str, role: Optional[str] = None) -> List[Dict]:
        """
        Recherche d'utilisateurs par nom, email ou username
        
        Args:
            query: Texte de recherche
            role: Filtre optionnel par rôle
            
        Returns:
            Liste d'utilisateurs correspondants
        """
        try:
            # Recherche avec ilike (case-insensitive)
            search_query = self.table.select("*").or_(
                f"first_name.ilike.%{query}%,"
                f"last_name.ilike.%{query}%,"
                f"email.ilike.%{query}%,"
                f"username.ilike.%{query}%"
            )
            
            if role:
                search_query = search_query.eq("role", role)
            
            result = search_query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Trouve un utilisateur par username
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            User ou None
        """
        return self.find_one({"username": username})

    def email_exists(self, email: str) -> bool:
        """
        Vérifie si un email existe déjà
        
        Args:
            email: Email à vérifier
            
        Returns:
            True si existe, False sinon
        """
        return self.find_by_email(email) is not None

    def username_exists(self, username: str) -> bool:
        """
        Vérifie si un username existe déjà
        
        Args:
            username: Username à vérifier
            
        Returns:
            True si existe, False sinon
        """
        return self.get_user_by_username(username) is not None
