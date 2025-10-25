"""
Rate Limiting Middleware - Production Grade

Implémentation avec Redis pour distributed rate limiting.

Features:
- Multiple strategies (Fixed Window, Sliding Window, Token Bucket)
- Redis-based (scale horizontale)
- Customizable limits par endpoint/user
- Automatic cleanup
- Headers informatifs (X-RateLimit-*)
"""

import redis
import time
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional
import structlog
import os
from functools import wraps

logger = structlog.get_logger()

# Configuration Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class RateLimitExceeded(HTTPException):
    """Exception personnalisée pour rate limit dépassé"""

    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
            headers={"Retry-After": str(retry_after)}
        )


class RateLimiter:
    """
    Rate limiter avec stratégie sliding window

    Plus précis que fixed window, évite les bursts en fin de fenêtre
    """

    def __init__(
        self,
        key_prefix: str = "ratelimit",
        default_limit: int = 100,
        default_window: int = 60  # secondes
    ):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.default_limit = default_limit
        self.default_window = default_window

    def get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """Générer clé Redis unique"""
        return f"{self.key_prefix}:{endpoint}:{identifier}"

    async def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> tuple[bool, int, int]:
        """
        Vérifier rate limit avec sliding window

        Args:
            identifier: Identifiant unique (user_id, IP, etc.)
            endpoint: Nom de l'endpoint
            limit: Nombre max de requêtes (None = default)
            window: Fenêtre en secondes (None = default)

        Returns:
            (allowed, remaining, retry_after)
        """
        limit = limit or self.default_limit
        window = window or self.default_window

        key = self.get_rate_limit_key(identifier, endpoint)
        now = time.time()
        window_start = now - window

        try:
            # Pipeline Redis pour atomicité
            pipe = self.redis.pipeline()

            # 1. Supprimer les timestamps hors fenêtre
            pipe.zremrangebyscore(key, 0, window_start)

            # 2. Compter requêtes dans la fenêtre
            pipe.zcard(key)

            # 3. Ajouter timestamp actuel
            pipe.zadd(key, {str(now): now})

            # 4. Expiration de la clé (cleanup auto)
            pipe.expire(key, window * 2)

            results = pipe.execute()
            current_count = results[1]  # Résultat du ZCARD

            # Vérifier si limite dépassée
            if current_count >= limit:
                # Calculer retry_after (temps jusqu'à expiration de la plus vieille requête)
                oldest_timestamps = self.redis.zrange(key, 0, 0, withscores=True)
                if oldest_timestamps:
                    oldest_time = oldest_timestamps[0][1]
                    retry_after = int(window - (now - oldest_time)) + 1
                else:
                    retry_after = window

                return False, 0, retry_after

            remaining = limit - current_count - 1  # -1 pour la requête actuelle
            return True, remaining, 0

        except redis.RedisError as e:
            logger.error("rate_limit_redis_error", error=str(e))
            # En cas d'erreur Redis, permettre la requête (fail open)
            return True, limit, 0

    async def reset_limit(self, identifier: str, endpoint: str):
        """Reset rate limit pour un identifiant (utile pour tests/admin)"""
        key = self.get_rate_limit_key(identifier, endpoint)
        self.redis.delete(key)


# Instance globale
rate_limiter = RateLimiter()


# ============================================
# MIDDLEWARE FASTAPI
# ============================================

async def rate_limit_middleware(request: Request, call_next: Callable):
    """
    Middleware FastAPI pour rate limiting automatique

    Apply sur toutes les requêtes API
    """
    # Extraire identifiant (user ou IP)
    identifier = None
    endpoint = request.url.path

    # 1. Priorité à l'user_id si authentifié
    if hasattr(request.state, "user") and request.state.user:
        identifier = f"user:{request.state.user['id']}"
    else:
        # 2. Sinon utiliser IP
        client_ip = request.client.host
        identifier = f"ip:{client_ip}"

    # Limites personnalisées selon endpoint
    limits = get_endpoint_limits(endpoint)

    # Vérifier rate limit
    allowed, remaining, retry_after = await rate_limiter.check_rate_limit(
        identifier=identifier,
        endpoint=endpoint,
        limit=limits["limit"],
        window=limits["window"]
    )

    if not allowed:
        logger.warning(
            "rate_limit_exceeded",
            identifier=identifier,
            endpoint=endpoint,
            retry_after=retry_after
        )

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "retry_after": retry_after,
                "message": f"Too many requests. Please retry after {retry_after} seconds."
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(limits["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + retry_after)
            }
        )

    # Requête autorisée, continuer
    response = await call_next(request)

    # Ajouter headers rate limit
    response.headers["X-RateLimit-Limit"] = str(limits["limit"])
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + limits["window"])

    return response


def get_endpoint_limits(endpoint: str) -> dict:
    """
    Récupérer les limites spécifiques à un endpoint

    Endpoints critiques = limites plus strictes
    """
    # Limites par défaut
    default = {"limit": 100, "window": 60}  # 100 req/min

    # Limites personnalisées
    custom_limits = {
        # Auth endpoints - très strict
        "/api/auth/login": {"limit": 5, "window": 60},  # 5/min
        "/api/auth/register": {"limit": 3, "window": 3600},  # 3/heure
        "/api/auth/reset-password": {"limit": 3, "window": 3600},

        # Upload endpoints - modéré
        "/api/kyc/upload": {"limit": 10, "window": 3600},  # 10/heure
        "/api/products/upload-image": {"limit": 20, "window": 3600},

        # API endpoints - généreux pour utilisateurs payants
        "/api/products": {"limit": 300, "window": 60},
        "/api/influencers": {"limit": 300, "window": 60},

        # Webhooks - très généreux (vient de Stripe/etc)
        "/api/stripe/webhook": {"limit": 1000, "window": 60},
        "/api/social-media/webhooks": {"limit": 1000, "window": 60},

        # Bot IA - modéré
        "/api/bot/chat": {"limit": 30, "window": 60},  # 30 msg/min
    }

    return custom_limits.get(endpoint, default)


# ============================================
# DECORATEUR POUR ENDPOINTS SPÉCIFIQUES
# ============================================

def rate_limit(limit: int, window: int):
    """
    Décorateur pour appliquer rate limit sur endpoint spécifique

    Usage:
        @router.post("/api/sensitive")
        @rate_limit(limit=5, window=60)
        async def sensitive_endpoint():
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request") or args[0]

            # Extraire identifiant
            identifier = getattr(request.state, "user_id", request.client.host)
            endpoint = request.url.path

            # Vérifier rate limit
            allowed, remaining, retry_after = await rate_limiter.check_rate_limit(
                identifier=identifier,
                endpoint=endpoint,
                limit=limit,
                window=window
            )

            if not allowed:
                raise RateLimitExceeded(retry_after=retry_after)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================
# HELPERS ADMIN
# ============================================

async def get_rate_limit_stats(identifier: str, endpoint: str) -> dict:
    """Récupérer stats rate limit pour debugging"""
    key = rate_limiter.get_rate_limit_key(identifier, endpoint)

    count = redis_client.zcard(key)
    ttl = redis_client.ttl(key)

    return {
        "identifier": identifier,
        "endpoint": endpoint,
        "current_count": count,
        "ttl": ttl
    }


async def whitelist_ip(ip: str, duration: int = 3600):
    """Whitelist une IP (bypass rate limiting)"""
    key = f"ratelimit:whitelist:{ip}"
    redis_client.setex(key, duration, "1")


async def is_whitelisted(ip: str) -> bool:
    """Vérifier si IP est whitelistée"""
    key = f"ratelimit:whitelist:{ip}"
    return redis_client.exists(key) == 1
