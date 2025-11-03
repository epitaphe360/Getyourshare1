# ============================================
# Dockerfile - Backend Only (Updated for Railway)
# ============================================
FROM python:3.11-slim

# Copier tout le contenu du backend (qui est le contexte de build)
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Lancer l'application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]

