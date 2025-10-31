# ============================================
# Multi-stage Dockerfile pour Backend FastAPI
# Production-Grade avec optimisations
# ============================================

# Stage 1: Builder - Installation dépendances
FROM python:3.11-slim as builder

# Métadonnées
LABEL maintainer="ShareYourSales <contact@shareyoursales.ma>"
LABEL description="Backend FastAPI - ShareYourSales Platform"
LABEL version="1.0.0"

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier requirements et installer
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# Stage 2: Runtime - Image finale
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production

# Installer uniquement dépendances runtime nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer utilisateur non-root pour sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copier virtual environment du builder
COPY --from=builder /opt/venv /opt/venv

# Créer répertoire app
WORKDIR /app

# Copier code application
COPY --chown=appuser:appuser . .

# Créer répertoires nécessaires (incluant ceux de la branche en conflit)
RUN mkdir -p /app/logs /app/uploads /app/invoices && \
    chown -R appuser:appuser /app

# Passer à utilisateur non-root
USER appuser

# Exposer port (Utilisation du port 8001 pour l'environnement Railway)
EXPOSE 8001

# Health check (Ajusté pour le port 8001)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Commande de démarrage (Ajusté pour le port 8001)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]

