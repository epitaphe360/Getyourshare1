# ============================================
# Root Dockerfile for Railway - Monorepo setup - Force rebuild
# ============================================

# ÉTAPE 1 : Build (pour installer les dépendances)
FROM python:3.11-slim as builder

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement le fichier des dépendances
COPY backend/requirements.txt .

# Installer les dépendances dans un dossier temporaire
RUN pip install --no-cache-dir -r requirements.txt --target=/usr/local/lib/python3.11/site-packages/

# ============================================
# ÉTAPE 2 : Final (pour le runtime)
# ============================================
FROM python:3.11-slim

# Définir le répertoire de travail pour le backend
WORKDIR /backend

# Copier les dépendances installées depuis l'étape 'builder'
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copier le reste du code de l'application
COPY backend/ .

# Expose port
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]
