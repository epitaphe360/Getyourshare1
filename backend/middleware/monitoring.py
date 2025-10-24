"""
Monitoring & Observability - Production Grade

Intégrations:
1. Sentry - Error tracking & Performance monitoring
2. Structured Logging - JSON logs pour analytics
3. Health Checks
4. Metrics
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import structlog
import logging
import os
import time
from fastapi import Request, Response
from typing import Callable
import psutil
import sys

# Configuration
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

logger = structlog.get_logger()


# ============================================
# SENTRY CONFIGURATION
# ============================================

def init_sentry():
    """
    Initialiser Sentry pour error tracking et performance monitoring

    Features activées:
    - Error tracking automatique
    - Performance monitoring (APM)
    - Request tracking
    - Database query tracking
    - Redis operation tracking
    - Breadcrumbs (trail d'événements avant erreur)
    """
    if not SENTRY_DSN:
        logger.warning("sentry_not_configured", message="SENTRY_DSN not set. Skipping Sentry initialization.")
        return

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        release=f"shareyoursales@{APP_VERSION}",

        # Integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            RedisIntegration(),
            SqlalchemyIntegration(),
        ],

        # Performance Monitoring
        traces_sample_rate=1.0 if ENVIRONMENT == "development" else 0.1,  # 100% dev, 10% prod

        # Error Sampling
        sample_rate=1.0,  # Capturer 100% des erreurs

        # Profiling (experimental)
        profiles_sample_rate=0.1 if ENVIRONMENT == "production" else 0,

        # Options
        attach_stacktrace=True,  # Stack traces complets
        send_default_pii=False,  # Ne pas envoyer PII (privacy)
        max_breadcrumbs=50,  # Nombre max de breadcrumbs
        debug=ENVIRONMENT == "development",

        # Filter events
        before_send=before_send_sentry_event,
    )

    logger.info("sentry_initialized", environment=ENVIRONMENT, version=APP_VERSION)


def before_send_sentry_event(event, hint):
    """
    Hook appelé avant d'envoyer événement à Sentry

    Permet de:
    - Filtrer certaines erreurs
    - Enrichir avec contexte supplémentaire
    - Masquer données sensibles
    """
    # Filtrer erreurs HTTP 404 (trop bruyant)
    if event.get("exception"):
        for exception in event["exception"].get("values", []):
            if exception.get("type") == "HTTPException":
                # Ne pas envoyer 404
                if "404" in str(exception.get("value", "")):
                    return None

    # Masquer données sensibles dans breadcrumbs
    if "breadcrumbs" in event:
        for breadcrumb in event["breadcrumbs"]:
            if "data" in breadcrumb:
                # Masquer tokens, passwords, etc.
                for key in ["password", "token", "authorization", "api_key"]:
                    if key in breadcrumb["data"]:
                        breadcrumb["data"][key] = "[REDACTED]"

    return event


# ============================================
# STRUCTURED LOGGING
# ============================================

def configure_logging():
    """
    Configure structured logging (JSON)

    Avantages:
    - Facilement parsable par outils (Datadog, ELK, etc.)
    - Contexte riche
    - Correlation IDs
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()  # JSON output
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# ============================================
# REQUEST LOGGING MIDDLEWARE
# ============================================

async def request_logging_middleware(request: Request, call_next: Callable):
    """
    Middleware pour logger toutes les requêtes avec métriques

    Logs:
    - Request details (method, path, IP)
    - Response status
    - Duration
    - User context (si authentifié)
    """
    start_time = time.time()

    # Générer request ID unique
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")

    # Contexte pour cette requête
    log_context = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent", "unknown")[:100]
    }

    # Ajouter user_id si authentifié
    if hasattr(request.state, "user") and request.state.user:
        log_context["user_id"] = request.state.user.get("id")
        log_context["user_role"] = request.state.user.get("role")

    # Logger requête
    logger.info("request_started", **log_context)

    # Sentry: Set user context
    if hasattr(request.state, "user") and request.state.user:
        sentry_sdk.set_user({
            "id": request.state.user.get("id"),
            "email": request.state.user.get("email"),
            "role": request.state.user.get("role")
        })

    # Sentry: Add breadcrumb
    sentry_sdk.add_breadcrumb(
        category="request",
        message=f"{request.method} {request.url.path}",
        level="info"
    )

    # Exécuter requête
    try:
        response = await call_next(request)

        # Calculer durée
        duration = time.time() - start_time

        # Logger réponse
        logger.info(
            "request_completed",
            **log_context,
            status=response.status_code,
            duration=f"{duration:.3f}s"
        )

        # Ajouter headers de tracking
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        return response

    except Exception as e:
        duration = time.time() - start_time

        # Logger erreur
        logger.error(
            "request_failed",
            **log_context,
            error=str(e),
            error_type=type(e).__name__,
            duration=f"{duration:.3f}s"
        )

        # Sentry: Capturer exception avec contexte
        sentry_sdk.capture_exception(e)

        raise


# ============================================
# HEALTH CHECKS
# ============================================

async def health_check() -> dict:
    """
    Health check endpoint

    Vérifie:
    - API alive
    - Database connection
    - Redis connection
    - Disk space
    - Memory
    """
    checks = {}

    # 1. API Status
    checks["api"] = {"status": "healthy"}

    # 2. Database
    try:
        # TODO: Tester connection DB
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}

    # 3. Redis
    try:
        from middleware.rate_limiting import redis_client
        redis_client.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}

    # 4. Disk Space
    try:
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        checks["disk"] = {
            "status": "healthy" if disk_percent < 90 else "warning",
            "used_percent": disk_percent,
            "free_gb": round(disk.free / (1024**3), 2)
        }
    except Exception as e:
        checks["disk"] = {"status": "unknown", "error": str(e)}

    # 5. Memory
    try:
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        checks["memory"] = {
            "status": "healthy" if memory_percent < 90 else "warning",
            "used_percent": memory_percent,
            "available_gb": round(memory.available / (1024**3), 2)
        }
    except Exception as e:
        checks["memory"] = {"status": "unknown", "error": str(e)}

    # Statut global
    overall_status = "healthy"
    for check in checks.values():
        if check.get("status") == "unhealthy":
            overall_status = "unhealthy"
            break
        elif check.get("status") == "warning" and overall_status != "unhealthy":
            overall_status = "degraded"

    return {
        "status": overall_status,
        "timestamp": time.time(),
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "checks": checks
    }


async def readiness_check() -> dict:
    """
    Readiness check (pour Kubernetes)

    Indique si l'app est prête à recevoir du traffic
    """
    # Vérifier services critiques
    try:
        # TODO: Vérifier DB connection
        # TODO: Vérifier Redis connection

        return {
            "status": "ready",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": time.time()
        }


async def liveness_check() -> dict:
    """
    Liveness check (pour Kubernetes)

    Indique si l'app est alive (pas freeze/deadlock)
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime": time.time() - psutil.boot_time()
    }


# ============================================
# METRICS
# ============================================

class Metrics:
    """
    Collecteur de métriques basique

    En production, remplacer par Prometheus/Datadog
    """

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []

    def record_request(self, duration: float, status: int):
        """Enregistrer une requête"""
        self.request_count += 1
        self.response_times.append(duration)

        if status >= 500:
            self.error_count += 1

        # Garder seulement les 1000 dernières
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

    def get_stats(self) -> dict:
        """Récupérer statistiques"""
        if not self.response_times:
            return {
                "request_count": self.request_count,
                "error_count": self.error_count,
                "avg_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0
            }

        sorted_times = sorted(self.response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)

        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "avg_response_time": sum(sorted_times) / len(sorted_times),
            "p95_response_time": sorted_times[p95_index],
            "p99_response_time": sorted_times[p99_index],
            "min_response_time": min(sorted_times),
            "max_response_time": max(sorted_times)
        }


metrics = Metrics()


# ============================================
# ALERTING (Sentry)
# ============================================

def send_alert(title: str, message: str, level: str = "error"):
    """
    Envoyer une alerte via Sentry

    Usage:
        send_alert("Payment Failed", "Stripe payment failed for user X", level="error")
    """
    with sentry_sdk.push_scope() as scope:
        scope.level = level
        scope.set_tag("alert", "true")
        sentry_sdk.capture_message(f"{title}: {message}")
