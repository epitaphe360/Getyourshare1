# ============================================
# Root Dockerfile for Railway - Monorepo setup - Force rebuild
# ============================================

FROM python:3.11-slim

# Définir le répertoire de travail temporaire
WORKDIR /tmp/app

# Copier TOUT le contexte de build dans le répertoire temporaire
COPY . .

# Déplacer le contenu du backend vers le répertoire de travail final
# Nous supposons que le Dockerfile est à la racine et que le dossier backend existe
RUN mv backend/* . && rm -rf backend

# Installer les dépendances (le fichier est maintenant à /tmp/app/requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Définir le répertoire de travail final
WORKDIR /tmp/app

# Expose port
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]
