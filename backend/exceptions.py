"""
Exceptions Personnalisées - Gestion unifiée des erreurs
Tous les endpoints doivent utiliser ces exceptions pour cohérence
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class BaseAPIException(HTTPException):
    """Exception de base pour toutes les erreurs API"""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        internal_message: Optional[str] = None
    ):
        self.message = message
        self.details = details or {}
        self.internal_message = internal_message or message
        
        super().__init__(
            status_code=status_code,
            detail={
                "error": message,
                "details": self.details
            }
        )


# ============================================
# ERREURS AUTHENTIFICATION (401)
# ============================================

class InvalidCredentialsError(BaseAPIException):
    """Email ou mot de passe incorrect"""
    def __init__(self, details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Email ou mot de passe incorrect. Veuillez réessayer.",
            details=details,
            internal_message="Invalid login credentials"
        )


class TokenExpiredError(BaseAPIException):
    """Token JWT expiré"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Votre session a expiré. Veuillez vous reconnecter.",
            internal_message="JWT token expired"
        )


class InvalidTokenError(BaseAPIException):
    """Token JWT invalide"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Session invalide. Veuillez vous reconnecter.",
            internal_message="Invalid JWT token"
        )


class TwoFARequiredError(BaseAPIException):
    """2FA requis pour continuer"""
    def __init__(self, temp_token: str):
        super().__init__(
            status_code=status.HTTP_200_OK,  # Pas vraiment une erreur
            message="Authentification à deux facteurs requise",
            details={"temp_token": temp_token, "requires_2fa": True}
        )


# ============================================
# ERREURS AUTORISATION (403)
# ============================================

class ForbiddenError(BaseAPIException):
    """Accès refusé - permissions insuffisantes"""
    def __init__(self, resource: Optional[str] = None):
        message = f"Vous n'avez pas les permissions pour accéder à {resource}" if resource else "Accès refusé"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            internal_message=f"Forbidden access to {resource}"
        )


class AccountDisabledError(BaseAPIException):
    """Compte désactivé"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Votre compte a été désactivé. Contactez le support.",
            internal_message="Account disabled"
        )


# ============================================
# ERREURS RESSOURCES (404)
# ============================================

class ResourceNotFoundError(BaseAPIException):
    """Ressource non trouvée"""
    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        message = f"{resource_type} non trouvé(e)"
        if resource_id:
            message += f" (ID: {resource_id})"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            details={"resource_type": resource_type, "resource_id": resource_id},
            internal_message=f"{resource_type} not found: {resource_id}"
        )


class UserNotFoundError(ResourceNotFoundError):
    """Utilisateur non trouvé"""
    def __init__(self, user_id: Optional[str] = None):
        super().__init__("Utilisateur", user_id)


class ProductNotFoundError(ResourceNotFoundError):
    """Produit non trouvé"""
    def __init__(self, product_id: Optional[str] = None):
        super().__init__("Produit", product_id)


class MerchantNotFoundError(ResourceNotFoundError):
    """Marchand non trouvé"""
    def __init__(self, merchant_id: Optional[str] = None):
        super().__init__("Marchand", merchant_id)


class InfluencerNotFoundError(ResourceNotFoundError):
    """Influenceur non trouvé"""
    def __init__(self, influencer_id: Optional[str] = None):
        super().__init__("Influenceur", influencer_id)


# ============================================
# ERREURS VALIDATION (400, 422)
# ============================================

class ValidationError(BaseAPIException):
    """Données invalides"""
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=f"Erreur de validation: {message}",
            details={"field": field, "error": message},
            internal_message=f"Validation error on {field}"
        )


class EmailAlreadyExistsError(BaseAPIException):
    """Email déjà utilisé"""
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Cet email est déjà utilisé. Veuillez en choisir un autre.",
            details={"email": email},
            internal_message=f"Email already exists: {email}"
        )


class InvalidInputError(BaseAPIException):
    """Input invalide"""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            details={"field": field} if field else {},
            internal_message=f"Invalid input: {message}"
        )


# ============================================
# ERREURS BUSINESS LOGIC (400)
# ============================================

class InsufficientBalanceError(BaseAPIException):
    """Solde insuffisant"""
    def __init__(self, balance: float, required: float):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Solde insuffisant. Solde actuel: {balance}€, montant requis: {required}€",
            details={"balance": balance, "required": required},
            internal_message="Insufficient balance"
        )


class QuotaExceededError(BaseAPIException):
    """Quota dépassé"""
    def __init__(self, quota_type: str, limit: int, current: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Limite {quota_type} dépassée ({current}/{limit}). Veuillez upgrader votre plan.",
            details={"quota_type": quota_type, "limit": limit, "current": current},
            internal_message=f"Quota exceeded: {quota_type}"
        )


class SubscriptionRequiredError(BaseAPIException):
    """Abonnement requis"""
    def __init__(self, feature: str):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            message=f"Abonnement requis pour accéder à: {feature}",
            details={"feature": feature},
            internal_message=f"Subscription required for {feature}"
        )


# ============================================
# ERREURS SERVEUR (500)
# ============================================

class DatabaseError(BaseAPIException):
    """Erreur base de données"""
    def __init__(self, operation: str, details: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Une erreur est survenue. Veuillez réessayer plus tard.",
            details={"operation": operation},
            internal_message=f"Database error during {operation}: {details}"
        )


class ExternalServiceError(BaseAPIException):
    """Erreur service externe (Stripe, etc.)"""
    def __init__(self, service: str, error_message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=f"Le service {service} est temporairement indisponible. Veuillez réessayer.",
            details={"service": service},
            internal_message=f"{service} error: {error_message}"
        )


# ============================================
# ERREURS RATE LIMITING (429)
# ============================================

class RateLimitError(BaseAPIException):
    """Trop de requêtes"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=f"Trop de tentatives. Veuillez réessayer dans {retry_after} secondes.",
            details={"retry_after": retry_after},
            internal_message="Rate limit exceeded"
        )


# ============================================
# HELPER FUNCTIONS
# ============================================

def handle_database_error(operation: str, error: Exception) -> None:
    """Helper pour gérer les erreurs DB de manière uniforme"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Database error during {operation}: {str(error)}")
    raise DatabaseError(operation, str(error))


def require_authentication(user: Optional[Dict]) -> Dict:
    """Helper pour vérifier qu'un user est authentifié"""
    if not user:
        raise InvalidTokenError()
    return user


def require_role(user: Dict, required_role: str) -> None:
    """Helper pour vérifier le rôle d'un user"""
    if user.get("role") != required_role:
        raise ForbiddenError(f"ressource réservée aux {required_role}s")


def validate_not_none(value: Any, field_name: str, error_message: Optional[str] = None) -> Any:
    """Valide qu'une valeur n'est pas None"""
    if value is None:
        message = error_message or f"{field_name} est requis"
        raise ValidationError(field_name, message)
    return value
