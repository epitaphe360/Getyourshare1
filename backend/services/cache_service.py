"""
Redis Caching Service - Production Grade

Features:
1. Cache decorator pour méthodes async
2. Cache invalidation patterns
3. Cache warming (preload)
4. TTL automatique
5. Serialization JSON/Pickle
6. Cache tagging pour invalidation groupée
7. Stats & monitoring
"""

import redis
import json
import pickle
import hashlib
from typing import Optional, Any, Callable, List
from functools import wraps
from datetime import timedelta
import structlog
import os
from contextlib import asynccontextmanager

logger = structlog.get_logger()

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_PREFIX = "sysales:cache:"
CACHE_DEFAULT_TTL = 3600  # 1 heure


# ============================================
# REDIS CLIENT
# ============================================

class RedisCache:
    """
    Client Redis pour caching avec features avancées
    """

    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=False)
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

    def _make_key(self, key: str, prefix: str = CACHE_PREFIX) -> str:
        """Générer clé Redis avec préfixe"""
        return f"{prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """
        Récupérer valeur du cache

        Returns:
            Valeur désérialisée ou None si pas trouvé
        """
        cache_key = self._make_key(key)

        try:
            value = self.redis.get(cache_key)

            if value is None:
                self.stats["misses"] += 1
                logger.debug("cache_miss", key=key)
                return None

            self.stats["hits"] += 1
            logger.debug("cache_hit", key=key)

            # Tenter de désérialiser JSON, sinon pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)

        except Exception as e:
            logger.error("cache_get_error", key=key, error=str(e))
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = CACHE_DEFAULT_TTL,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Stocker valeur dans le cache

        Args:
            key: Clé du cache
            value: Valeur à stocker
            ttl: Time to live en secondes
            tags: Tags pour invalidation groupée

        Returns:
            True si succès
        """
        cache_key = self._make_key(key)

        try:
            # Sérialiser (JSON si possible, sinon pickle)
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                serialized = pickle.dumps(value)

            # Stocker avec TTL
            self.redis.setex(cache_key, ttl, serialized)
            self.stats["sets"] += 1

            # Ajouter aux tags si spécifiés
            if tags:
                for tag in tags:
                    tag_key = self._make_key(f"tag:{tag}")
                    self.redis.sadd(tag_key, cache_key)
                    self.redis.expire(tag_key, ttl + 3600)  # Tag expire 1h après cache

            logger.debug("cache_set", key=key, ttl=ttl, tags=tags)
            return True

        except Exception as e:
            logger.error("cache_set_error", key=key, error=str(e))
            return False

    def delete(self, key: str) -> bool:
        """Supprimer clé du cache"""
        cache_key = self._make_key(key)

        try:
            result = self.redis.delete(cache_key)
            self.stats["deletes"] += 1
            logger.debug("cache_delete", key=key, deleted=result > 0)
            return result > 0
        except Exception as e:
            logger.error("cache_delete_error", key=key, error=str(e))
            return False

    def delete_by_pattern(self, pattern: str) -> int:
        """
        Supprimer toutes les clés matchant un pattern

        Example:
            cache.delete_by_pattern("user:*")
        """
        cache_pattern = self._make_key(pattern)

        try:
            cursor = 0
            deleted_count = 0

            while True:
                cursor, keys = self.redis.scan(cursor, match=cache_pattern, count=100)
                if keys:
                    deleted_count += self.redis.delete(*keys)

                if cursor == 0:
                    break

            logger.info("cache_pattern_delete", pattern=pattern, deleted=deleted_count)
            return deleted_count

        except Exception as e:
            logger.error("cache_pattern_delete_error", pattern=pattern, error=str(e))
            return 0

    def delete_by_tag(self, tag: str) -> int:
        """
        Supprimer toutes les clés associées à un tag

        Example:
            cache.set("user:123", data, tags=["users", "user:123"])
            cache.delete_by_tag("users")  # Supprime tous les users
        """
        tag_key = self._make_key(f"tag:{tag}")

        try:
            # Récupérer toutes les clés avec ce tag
            cache_keys = self.redis.smembers(tag_key)

            if not cache_keys:
                return 0

            # Supprimer toutes les clés
            deleted_count = self.redis.delete(*cache_keys)

            # Supprimer le tag lui-même
            self.redis.delete(tag_key)

            logger.info("cache_tag_delete", tag=tag, deleted=deleted_count)
            return deleted_count

        except Exception as e:
            logger.error("cache_tag_delete_error", tag=tag, error=str(e))
            return 0

    def clear_all(self) -> bool:
        """Vider tout le cache (DANGER en production!)"""
        try:
            self.redis.flushdb()
            logger.warning("cache_cleared_all")
            return True
        except Exception as e:
            logger.error("cache_clear_error", error=str(e))
            return False

    def get_stats(self) -> dict:
        """Récupérer statistiques du cache"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2)
        }

    def get_memory_info(self) -> dict:
        """Info mémoire Redis"""
        try:
            info = self.redis.info("memory")
            return {
                "used_memory_human": info.get("used_memory_human"),
                "used_memory_peak_human": info.get("used_memory_peak_human"),
                "maxmemory_human": info.get("maxmemory_human", "unlimited"),
                "mem_fragmentation_ratio": info.get("mem_fragmentation_ratio")
            }
        except Exception as e:
            logger.error("cache_memory_info_error", error=str(e))
            return {}


# Instance globale
cache = RedisCache()


# ============================================
# CACHE DECORATOR
# ============================================

def cached(
    key_prefix: str,
    ttl: int = CACHE_DEFAULT_TTL,
    tags: Optional[List[str]] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator pour cacher résultats de fonctions async

    Usage:
        @cached(key_prefix="user", ttl=3600, tags=["users"])
        async def get_user(user_id: str):
            # Fetch from DB...
            return user_data

    Args:
        key_prefix: Préfixe pour la clé de cache
        ttl: Time to live en secondes
        tags: Tags pour invalidation groupée
        key_builder: Fonction custom pour générer la clé (optionnel)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Générer clé de cache
            if key_builder:
                cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                # Clé par défaut basée sur args/kwargs
                args_str = "_".join(str(arg) for arg in args)
                kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{args_str}:{kwargs_str}"

            # Chercher dans cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Exécuter fonction
            result = await func(*args, **kwargs)

            # Stocker dans cache
            cache.set(cache_key, result, ttl=ttl, tags=tags)

            return result

        return wrapper
    return decorator


# ============================================
# CACHE UTILITIES
# ============================================

class CacheKeys:
    """
    Générateurs de clés de cache standardisés
    """

    @staticmethod
    def user(user_id: str) -> str:
        return f"user:{user_id}"

    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"user:{user_id}:profile"

    @staticmethod
    def user_stats(user_id: str) -> str:
        return f"user:{user_id}:stats"

    @staticmethod
    def product(product_id: str) -> str:
        return f"product:{product_id}"

    @staticmethod
    def products_list(merchant_id: str, page: int = 1) -> str:
        return f"products:{merchant_id}:page:{page}"

    @staticmethod
    def social_stats(user_id: str, platform: str) -> str:
        return f"social:{user_id}:{platform}:stats"

    @staticmethod
    def affiliate_link(link_id: str) -> str:
        return f"link:{link_id}"

    @staticmethod
    def tracking_stats(link_id: str, period: str) -> str:
        return f"tracking:{link_id}:{period}"

    @staticmethod
    def subscription(user_id: str) -> str:
        return f"subscription:{user_id}"

    @staticmethod
    def quotas(user_id: str) -> str:
        return f"quotas:{user_id}"


class CacheTags:
    """
    Tags standardisés pour invalidation groupée
    """

    USERS = "users"
    PRODUCTS = "products"
    SOCIAL_STATS = "social_stats"
    TRACKING = "tracking"
    SUBSCRIPTIONS = "subscriptions"

    @staticmethod
    def user(user_id: str) -> str:
        return f"user:{user_id}"

    @staticmethod
    def merchant(merchant_id: str) -> str:
        return f"merchant:{merchant_id}"

    @staticmethod
    def product(product_id: str) -> str:
        return f"product:{product_id}"


# ============================================
# CACHE WARMING
# ============================================

async def warm_cache():
    """
    Préchauffer le cache avec données fréquemment utilisées

    À appeler au démarrage de l'application
    """
    logger.info("cache_warming_started")

    try:
        # TODO: Implémenter warming selon vos besoins
        # Exemple:
        # - Charger tous les plans d'abonnement
        # - Charger top 100 produits
        # - Charger stats globales

        logger.info("cache_warming_completed")

    except Exception as e:
        logger.error("cache_warming_error", error=str(e))


# ============================================
# CACHE INVALIDATION HELPERS
# ============================================

class CacheInvalidator:
    """
    Helpers pour invalidation de cache
    """

    @staticmethod
    def invalidate_user(user_id: str):
        """Invalider tout le cache d'un utilisateur"""
        cache.delete_by_tag(CacheTags.user(user_id))
        cache.delete_by_pattern(f"user:{user_id}:*")

    @staticmethod
    def invalidate_merchant(merchant_id: str):
        """Invalider tout le cache d'un marchand"""
        cache.delete_by_tag(CacheTags.merchant(merchant_id))
        cache.delete_by_pattern(f"products:{merchant_id}:*")

    @staticmethod
    def invalidate_product(product_id: str, merchant_id: str):
        """Invalider cache d'un produit"""
        cache.delete(CacheKeys.product(product_id))
        cache.delete_by_pattern(f"products:{merchant_id}:*")

    @staticmethod
    def invalidate_social_stats(user_id: str, platform: str):
        """Invalider stats sociales"""
        cache.delete(CacheKeys.social_stats(user_id, platform))
        cache.delete_by_pattern(f"social:{user_id}:*")

    @staticmethod
    def invalidate_subscription(user_id: str):
        """Invalider abonnement et quotas"""
        cache.delete(CacheKeys.subscription(user_id))
        cache.delete(CacheKeys.quotas(user_id))


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

# Example 1: Cache avec decorator
@cached(key_prefix="user_profile", ttl=3600, tags=["users"])
async def get_user_profile(user_id: str):
    """
    Cette fonction sera cachée automatiquement
    """
    # Fetch from DB...
    return {"id": user_id, "name": "John Doe"}


# Example 2: Cache manuel
async def get_product_details(product_id: str):
    """
    Cache manuel avec contrôle total
    """
    cache_key = CacheKeys.product(product_id)

    # Chercher dans cache
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Fetch from DB...
    product = {"id": product_id, "name": "Product"}

    # Stocker avec tags
    cache.set(
        cache_key,
        product,
        ttl=3600,
        tags=[CacheTags.PRODUCTS, CacheTags.product(product_id)]
    )

    return product


# Example 3: Invalidation après update
async def update_product(product_id: str, merchant_id: str, data: dict):
    """
    Update avec invalidation de cache
    """
    # Update DB...

    # Invalider cache
    CacheInvalidator.invalidate_product(product_id, merchant_id)

    return {"success": True}
