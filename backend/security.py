from fastapi import Depends, HTTPException
from server import get_current_user
from typing import List

def require_role(roles: List[str]):
    """
    Dépendance FastAPI pour vérifier si l'utilisateur connecté a l'un des rôles requis.
    
    Args:
        roles: Liste des rôles autorisés (ex: ["merchant", "admin"])
    """
    def role_checker(user: dict = Depends(get_current_user)):
        user_role = user.get("role")
        if user_role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Accès refusé. Rôle requis: {', '.join(roles)}. Rôle actuel: {user_role}",
            )
        return user
    return role_checker

# Dépendances de rôle courantes
# Uniquement les marchands et les admins peuvent gérer les paramètres de l'entreprise
MERCHANT_OR_ADMIN = require_role(["merchant", "admin"])

# Seuls les admins peuvent gérer les utilisateurs et les factures
ADMIN_ONLY = require_role(["admin"])

# Tous les utilisateurs authentifiés
AUTHENTICATED_USER = require_role(["influencer", "merchant", "admin"])
