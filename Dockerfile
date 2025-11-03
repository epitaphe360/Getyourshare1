# =================================================
# Dockerfile Final - Stratégie Robuste
# =================================================
FROM python:3.11-slim

# 1. Définir le répertoire de travail pour le backend
WORKDIR /app

# 2. Copier UNIQUEMENT le fichier des dépendances
# Si cette étape échoue, le problème vient du contexte de build (ex: .dockerignore)
COPY backend/requirements.txt .

# 3. Installer les dépendances. Cette couche sera mise en cache.
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copier tout le reste du code du backend
COPY backend/ .

# 5. Lancer l'application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]

