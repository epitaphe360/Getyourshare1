# ============================================
# Root Dockerfile for Railway - Monorepo setup - Force rebuild
# ============================================

FROM python:3.11-slim

# Définir le répertoire de travail pour le backend
WORKDIR /backend

# Copier uniquement le fichier des dépendances pour profiter de la mise en cache de Docker
# Le fichier est copié de ./backend/requirements.txt (dans le contexte de build)
# vers ./requirements.txt (dans le WORKDIR /backend)
COPY backend/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
# Le reste du contenu de ./backend/ est copié dans /backend/
COPY backend/ .

# Expose port
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]
