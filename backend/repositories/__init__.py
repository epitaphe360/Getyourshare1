"""
Repositories - Couche d'accès aux données
Implémente le Repository Pattern pour découpler la logique métier de l'accès DB
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .product_repository import ProductRepository
from .sale_repository import SaleRepository
from .tracking_repository import TrackingRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'ProductRepository',
    'SaleRepository',
    'TrackingRepository',
]
