"""
Cache Manager - Gestion centralisée du cache Redis
Permet de réduire la charge DB pour les données fréquemment consultées
"""

import redis
import json
import os
from typing import Optional, Any, Callable
from functools import wraps
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Configuration Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Durées de cache par défaut
CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes  
CACHE_TTL_LONG = 3600  # 1 heure


class CacheManager:
    """Gestionnaire de cache Redis avec fallback gracieux"""
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connexion à Redis avec gestion d'erreurs"""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connexion
            self.redis_client.ping()
            logger.info(f"✅ Redis connecté: {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logger.warning(f"⚠️ Redis non disponible: {e}. Cache désactivé (fallback gracieux).")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"🎯 Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"❌ Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Erreur lecture cache {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = CACHE_TTL_MEDIUM):
        """Enregistre une valeur dans le cache"""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Erreur écriture cache {key}: {e}")
            return False
    
    def delete(self, key: str):
        """Supprime une clé du cache"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            logger.debug(f"🗑️ Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Erreur suppression cache {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str):
        """Invalide toutes les clés correspondant au pattern"""
        if not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"🗑️ Invalidation cache pattern: {pattern} ({len(keys)} clés)")
            return True
        except Exception as e:
            logger.error(f"Erreur invalidation pattern {pattern}: {e}")
            return False
    
    def flush_all(self):
        """Vide tout le cache (à utiliser avec précaution!)"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            logger.warning("⚠️ Cache FLUSH: Toutes les données supprimées")
            return True
        except Exception as e:
            logger.error(f"Erreur flush cache: {e}")
            return False


# Instance globale
cache = CacheManager()


def cached(ttl: int = CACHE_TTL_MEDIUM, key_prefix: str = ""):
    """
    Décorateur pour mettre en cache le résultat d'une fonction
    
    Usage:
        @cached(ttl=300, key_prefix="dashboard_stats")
        def get_dashboard_stats(user_id: str, role: str):
            # Calculs lourds
            return stats
    
    Args:
        ttl: Durée de vie du cache en secondes
        key_prefix: Préfixe pour la clé de cache
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer clé de cache unique basée sur fonction + arguments
            func_name = func.__name__
            args_key = "_".join(str(arg) for arg in args)
            kwargs_key = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"{key_prefix}:{func_name}:{args_key}:{kwargs_key}"
            
            # Essayer de récupérer du cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Si pas en cache, exécuter fonction
            result = func(*args, **kwargs)
            
            # Mettre en cache le résultat
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Invalide le cache pour un pattern donné
    
    Usage:
        # Après modification user
        invalidate_cache("dashboard_stats:*")
    """
    return cache.invalidate_pattern(pattern)


# Fonctions helper pour patterns courants
def cache_dashboard_stats(user_id: str, role: str, stats: dict):
    """Cache les stats dashboard pour un user"""
    key = f"dashboard_stats:{role}:{user_id}"
    cache.set(key, stats, CACHE_TTL_MEDIUM)


def get_cached_dashboard_stats(user_id: str, role: str) -> Optional[dict]:
    """Récupère les stats dashboard depuis le cache"""
    key = f"dashboard_stats:{role}:{user_id}"
    return cache.get(key)


def invalidate_user_cache(user_id: str):
    """Invalide tout le cache d'un user"""
    cache.invalidate_pattern(f"*:{user_id}:*")
    cache.invalidate_pattern(f"*:{user_id}")


if __name__ == "__main__":
    # Test du cache
    print("🧪 Test Cache Manager")
    
    # Test set/get
    cache.set("test_key", {"message": "Hello Redis"}, 60)
    result = cache.get("test_key")
    print(f"✅ Test set/get: {result}")
    
    # Test décorateur
    @cached(ttl=10, key_prefix="test")
    def expensive_function(x: int) -> int:
        print(f"  🔄 Calcul coûteux pour x={x}")
        return x * 2
    
    print(f"Appel 1: {expensive_function(5)}")  # Calcul
    print(f"Appel 2: {expensive_function(5)}")  # Cache
    print(f"Appel 3: {expensive_function(10)}")  # Nouveau calcul
    
    print("✅ Tests terminés")
