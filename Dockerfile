# ============================================
# Dockerfile - Simple et Robuste
# ============================================
FROM python:3.11-slim

# 1. Définir le répertoire de travail principal
WORKDIR /app

# 2. Copier TOUT le projet. C'est la méthode la plus fiable.
#    Le .dockerignore s'occupe de filtrer les fichiers inutiles.
COPY . .

# 3. Se déplacer dans le dossier du backend
WORKDIR /app/backend

# 4. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Lancer l'application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]

