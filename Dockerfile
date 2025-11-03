# ============================================
# Dockerfile de la dernière chance - Simple et Direct
# ============================================
FROM python:3.11-slim

# Répertoire de travail
WORKDIR /app

# Copier tout le contenu du projet
COPY . .

# --- DÉBOGAGE ---
# Lister récursivement tous les fichiers dans /app pour voir ce qui a été copié.
# Si 'backend/requirements.txt' n'apparaît pas ici, le problème vient de .dockerignore.
RUN ls -R

# Se déplacer dans le dossier backend
WORKDIR /app/backend

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Lancer l'application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]

