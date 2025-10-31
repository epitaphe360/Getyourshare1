"""
Security Middleware - Production Grade

Implémente:
1. CSRF Protection (Double Submit Cookie)
2. Security Headers (CSP, HSTS, X-Frame-Options, etc.)
3. Request Validation
4. IP Filtering
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from typing import Callable
import secrets
import structlog
import os
from datetime import datetime, timedelta

logger = structlog.get_logger()

# Configuration
CSRF_TOKEN_LENGTH = 32
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


# ============================================
# CSRF PROTECTION
# ============================================

class CSRFProtection:
    """
    CSRF Protection avec Double Submit Cookie pattern

    Plus sécurisé que synchronizer token (pas besoin de session server-side)
    """

    def __init__(self):
        self.cookie_name = CSRF_COOKIE_NAME
        self.header_name = CSRF_HEADER_NAME

    def generate_token(self) -> str:
        """Générer un token CSRF aléatoire"""
        return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)

    def set_csrf_cookie(self, response: Response, token: str):
        """Ajouter le cookie CSRF à la réponse"""
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=True,  # Pas accessible en JavaScript
            secure=ENVIRONMENT == "production",  # HTTPS only en prod
            samesite="strict",  # Protection supplémentaire
            max_age=3600 * 24  # 24 heures
        )

    def validate_csrf_token(self, request: Request) -> bool:
        """
        Valider le token CSRF

        Compare le cookie avec le header
        """
        # Récupérer token du cookie
        cookie_token = request.cookies.get(self.cookie_name)

        # Récupérer token du header
        header_token = request.headers.get(self.header_name)

        if not cookie_token or not header_token:
            return False

        # Comparer les tokens (timing-safe)
        return secrets.compare_digest(cookie_token, header_token)


csrf_protection = CSRFProtection()


async def csrf_middleware(request: Request, call_next: Callable):
    """
    Middleware CSRF

    Vérifie le token CSRF sur toutes les requêtes mutantes (POST, PUT, DELETE, PATCH)
    """
    # Méthodes sûres (GET, HEAD, OPTIONS) = pas de vérification CSRF
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        response = await call_next(request)

        # Générer et ajouter token CSRF pour les requêtes GET
        if request.method == "GET":
            token = csrf_protection.generate_token()
            csrf_protection.set_csrf_cookie(response, token)

        return response

    # Exclure certains endpoints (webhooks externes)
    excluded_paths = [
        "/api/stripe/webhook",
        "/api/social-media/webhooks",
        "/api/auth/login",  # Géré différemment
        "/docs",
        "/openapi.json"
    ]

    if any(request.url.path.startswith(path) for path in excluded_paths):
        return await call_next(request)

    # Valider CSRF token
    if not csrf_protection.validate_csrf_token(request):
        logger.warning(
            "csrf_validation_failed",
            path=request.url.path,
            method=request.method,
            ip=request.client.host
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token validation failed"
        )

    response = await call_next(request)
    return response


# ============================================
# SECURITY HEADERS
# ============================================

async def security_headers_middleware(request: Request, call_next: Callable):
    """
    Middleware pour ajouter security headers à toutes les réponses

    Headers implémentés:
    - Content-Security-Policy (CSP)
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """
    response = await call_next(request)

    # Content Security Policy (CSP)
    # Définit les sources autorisées pour scripts, styles, images, etc.
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://cdn.jsdelivr.net",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        "img-src 'self' data: https: blob:",
        "connect-src 'self' https://api.stripe.com https://api.anthropic.com https://api.openai.com",
        "frame-src 'self' https://js.stripe.com",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",  # Équivalent à X-Frame-Options: DENY
        "upgrade-insecure-requests"  # Force HTTPS
    ]
    response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

    # HSTS - Force HTTPS (seulement en production)
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    # Empêche MIME-type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Protection contre clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # XSS Protection (legacy, mais toujours utile pour vieux navigateurs)
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Referrer Policy - Contrôle les infos envoyées dans l'en-tête Referer
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions Policy (anciennement Feature-Policy)
    # Désactive features navigateur potentiellement dangereuses
    permissions = [
        "geolocation=()",
        "microphone=()",
        "camera=()",
        "payment=(self)",
        "usb=()",
        "magnetometer=()",
        "gyroscope=()",
        "speaker=(self)"
    ]
    response.headers["Permissions-Policy"] = ", ".join(permissions)

    # Cache Control pour données sensibles
    if "/api/auth" in request.url.path or "/api/stripe" in request.url.path:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"

    # Server header (masquer la version)
    response.headers["Server"] = "ShareYourSales"

    return response


# ============================================
# REQUEST VALIDATION
# ============================================

async def request_validation_middleware(request: Request, call_next: Callable):
    """
    Middleware de validation des requêtes

    Vérifie:
    - Taille de la requête
    - Content-Type valide
    - User-Agent présent (anti-bot basique)
    """
    # Limite taille body (protection DoS)
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB

    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        logger.warning(
            "request_too_large",
            size=content_length,
            max_size=MAX_REQUEST_SIZE,
            ip=request.client.host
        )

        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Request body too large. Max size: {MAX_REQUEST_SIZE} bytes"
        )

    # Vérifier User-Agent (anti-bot basique)
    user_agent = request.headers.get("user-agent", "")
    if not user_agent and ENVIRONMENT == "production":
        logger.warning("missing_user_agent", ip=request.client.host)

        # Ne pas bloquer, juste logger (certains clients légitimes n'ont pas UA)
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing User-Agent")

    # Vérifier Content-Type pour POST/PUT/PATCH
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")

        # Autoriser JSON et multipart (pour uploads)
        allowed_types = [
            "application/json",
            "multipart/form-data",
            "application/x-www-form-urlencoded"
        ]

        if not any(allowed in content_type for allowed in allowed_types):
            # Ne pas bloquer les webhooks
            if "/webhook" not in request.url.path:
                logger.warning(
                    "invalid_content_type",
                    content_type=content_type,
                    path=request.url.path
                )

    response = await call_next(request)
    return response


# ============================================
# IP FILTERING (Optionnel)
# ============================================

class IPFilter:
    """
    Filtrage IP (blacklist/whitelist)

    Utile pour bloquer des IPs malveillantes ou restreindre l'accès
    """

    def __init__(self):
        self.blacklist = set()
        self.whitelist = set()

    def add_to_blacklist(self, ip: str):
        """Ajouter IP à la blacklist"""
        self.blacklist.add(ip)
        logger.info("ip_blacklisted", ip=ip)

    def remove_from_blacklist(self, ip: str):
        """Retirer IP de la blacklist"""
        self.blacklist.discard(ip)

    def add_to_whitelist(self, ip: str):
        """Ajouter IP à la whitelist"""
        self.whitelist.add(ip)
        logger.info("ip_whitelisted", ip=ip)

    def is_allowed(self, ip: str) -> bool:
        """Vérifier si IP est autorisée"""
        # Whitelist prioritaire
        if self.whitelist and ip in self.whitelist:
            return True

        # Blacklist
        if ip in self.blacklist:
            return False

        return True


ip_filter = IPFilter()


async def ip_filtering_middleware(request: Request, call_next: Callable):
    """Middleware de filtrage IP"""
    client_ip = request.client.host

    if not ip_filter.is_allowed(client_ip):
        logger.warning("ip_blocked", ip=client_ip, path=request.url.path)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return await call_next(request)


# ============================================
# CORS SECURITY
# ============================================

def get_cors_config():
    """
    Configuration CORS sécurisée

    En développement: permissif
    En production: restrictif
    """
    if ENVIRONMENT == "development":
        return {
            "allow_origins": ["http://localhost:3000", "http://localhost:3001"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    else:
        return {
            "allow_origins": [
                "https://shareyoursales.ma",
                "https://www.shareyoursales.ma",
                "https://app.shareyoursales.ma"
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-CSRF-Token",
                "X-Requested-With"
            ],
            "expose_headers": [
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "X-RateLimit-Reset"
            ]
        }
