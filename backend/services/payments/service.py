"""
Service de gestion des paiements et commissions.
Contient la logique métier pour l'approbation et le paiement des commissions.
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class PaymentsService:
    """Service pour gérer les commissions et appeler approve_payout_transaction."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def approve_commission(
        self,
        commission_id: UUID,
        new_status: str = "approved"
    ) -> bool:
        """
        Approuve ou change le statut d'une commission via approve_payout_transaction.
        
        Args:
            commission_id: ID de la commission
            new_status: Nouveau statut ('approved', 'paid', 'rejected', 'pending')
        
        Returns:
            bool: True si succès
        
        Raises:
            ValueError: Si les paramètres sont invalides
            RuntimeError: Si l'appel à la fonction PL/pgSQL échoue
        """
        try:
            logger.info(f"Changement statut commission {commission_id} → {new_status}")
            
            # Appel de la fonction PL/pgSQL approve_payout_transaction via RPC
            result = self.supabase.rpc(
                "approve_payout_transaction",
                {
                    "p_commission_id": str(commission_id),
                    "p_status": new_status
                }
            ).execute()
            
            if result.data is None:
                raise RuntimeError("La fonction approve_payout_transaction n'a retourné aucune donnée")
            
            success = result.data
            logger.info(f"Statut commission {commission_id} mis à jour: {success}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la commission: {str(e)}")
            error_msg = str(e)
            
            # Parser les erreurs PostgreSQL
            if "introuvable" in error_msg:
                raise ValueError(f"Commission ou ressource introuvable: {error_msg}")
            elif "Solde insuffisant" in error_msg:
                raise ValueError("Solde insuffisant pour approuver cette commission")
            elif "déjà été réglée" in error_msg:
                raise ValueError("Cette commission a déjà été payée et ne peut plus être modifiée")
            elif "doit être approuvée avant" in error_msg:
                raise ValueError("La commission doit être approuvée avant d'être marquée comme payée")
            elif "non supporté" in error_msg:
                raise ValueError(f"Statut invalide: {error_msg}")
            else:
                raise RuntimeError(f"Erreur lors de la mise à jour de la commission: {error_msg}")
    
    async def get_commission_by_id(self, commission_id: UUID) -> Optional[dict]:
        """
        Récupère une commission par son ID.
        
        Args:
            commission_id: ID de la commission
        
        Returns:
            dict ou None: La commission si trouvée
        """
        try:
            result = (
                self.supabase.table("commissions")
                .select("*, sales(*), influencers(id, username, balance)")
                .eq("id", str(commission_id))
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la commission: {str(e)}")
            return None
    
    async def get_commissions_by_status(
        self,
        status: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Récupère les commissions par statut.
        
        Args:
            status: Statut recherché ('pending', 'approved', 'paid', 'cancelled')
            limit: Nombre max de résultats
            offset: Offset pour la pagination
        
        Returns:
            List[dict]: Liste des commissions
        """
        try:
            result = (
                self.supabase.table("commissions")
                .select("*, sales(amount, product_id), influencers(id, username)")
                .eq("status", status)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des commissions: {str(e)}")
            return []
    
    async def get_commissions_by_influencer(
        self,
        influencer_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Récupère les commissions d'un influenceur.
        
        Args:
            influencer_id: ID de l'influenceur
            status: Filtre par statut (optionnel)
            limit: Nombre max de résultats
            offset: Offset pour la pagination
        
        Returns:
            List[dict]: Liste des commissions
        """
        try:
            query = (
                self.supabase.table("commissions")
                .select("*, sales(amount, product_id, created_at)")
                .eq("influencer_id", str(influencer_id))
            )
            
            if status:
                query = query.eq("status", status)
            
            result = (
                query
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des commissions: {str(e)}")
            return []
    
    async def get_pending_commissions_total(self, influencer_id: UUID) -> float:
        """
        Calcule le total des commissions en attente pour un influenceur.
        
        Args:
            influencer_id: ID de l'influenceur
        
        Returns:
            float: Total des commissions pending
        """
        try:
            result = (
                self.supabase.table("commissions")
                .select("amount")
                .eq("influencer_id", str(influencer_id))
                .eq("status", "pending")
                .execute()
            )
            
            total = sum(float(c.get("amount", 0)) for c in result.data)
            return total
        except Exception as e:
            logger.error(f"Erreur lors du calcul du total: {str(e)}")
            return 0.0
    
    async def get_approved_commissions_total(self, influencer_id: UUID) -> float:
        """
        Calcule le total des commissions approuvées pour un influenceur.
        
        Args:
            influencer_id: ID de l'influenceur
        
        Returns:
            float: Total des commissions approved
        """
        try:
            result = (
                self.supabase.table("commissions")
                .select("amount")
                .eq("influencer_id", str(influencer_id))
                .eq("status", "approved")
                .execute()
            )
            
            total = sum(float(c.get("amount", 0)) for c in result.data)
            return total
        except Exception as e:
            logger.error(f"Erreur lors du calcul du total: {str(e)}")
            return 0.0
    
    async def batch_approve_commissions(
        self,
        commission_ids: List[UUID],
        new_status: str = "approved"
    ) -> dict:
        """
        Approuve plusieurs commissions en lot.
        
        Args:
            commission_ids: Liste des IDs de commissions
            new_status: Nouveau statut à appliquer
        
        Returns:
            dict: Résumé des opérations (success, failed)
        """
        success = []
        failed = []
        
        for commission_id in commission_ids:
            try:
                await self.approve_commission(commission_id, new_status)
                success.append(str(commission_id))
            except Exception as e:
                logger.error(f"Échec pour commission {commission_id}: {str(e)}")
                failed.append({"id": str(commission_id), "error": str(e)})
        
        return {
            "success_count": len(success),
            "failed_count": len(failed),
            "success": success,
            "failed": failed
        }
