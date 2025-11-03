# ============================================
# Root Dockerfile for Railway - Monorepo setup - Force rebuild
# ============================================

FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier tout le contexte de build dans /app
# Cela inclut le dossier 'backend'
COPY . .

# Installer les dépendances du backend
# Le fichier est maintenant à /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Définir le répertoire de travail final pour l'exécution
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]
