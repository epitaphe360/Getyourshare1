#!/bin/bash

# ============================================
# Script de Déploiement Railway - GetYourShare
# ============================================

set -e

echo "🚀 Déploiement GetYourShare sur Railway"
echo "========================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les erreurs
error() {
    echo -e "${RED}❌ Erreur: $1${NC}"
    exit 1
}

# Fonction pour afficher les succès
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Fonction pour afficher les infos
info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Vérifier si Railway CLI est installé
if ! command -v railway &> /dev/null; then
    info "Railway CLI n'est pas installé"
    echo "Installation de Railway CLI..."

    # Détection du système d'exploitation
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://railway.app/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install railway
    else
        error "Système d'exploitation non supporté. Installez Railway CLI manuellement: https://docs.railway.app/develop/cli"
    fi

    success "Railway CLI installé"
fi

# Vérifier l'authentification Railway
info "Vérification de l'authentification Railway..."
if ! railway whoami &> /dev/null; then
    info "Vous n'êtes pas connecté à Railway"
    echo "Connexion à Railway..."
    railway login
    success "Connecté à Railway"
else
    success "Déjà connecté à Railway"
fi

# Vérifier si .env existe
if [ ! -f ".env.example" ]; then
    error "Le fichier .env.example n'existe pas. Exécutez d'abord la configuration."
fi

# Créer .env si n'existe pas
if [ ! -f "backend/.env" ]; then
    info "Création du fichier .env..."
    cp .env.example backend/.env
    echo ""
    echo "⚠️  IMPORTANT: Éditez backend/.env avec vos vraies valeurs avant de continuer"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_KEY"
    echo "   - STRIPE_SECRET_KEY"
    echo "   - JWT_SECRET_KEY"
    echo ""
    read -p "Appuyez sur Entrée une fois que vous avez édité le fichier .env..."
fi

# Menu de sélection
echo ""
echo "Que voulez-vous déployer?"
echo "1) Backend uniquement"
echo "2) Frontend uniquement"
echo "3) Backend + Frontend (Complet)"
echo "4) Configurer les variables d'environnement"
echo "5) Voir les logs"
read -p "Votre choix (1-5): " choice

case $choice in
    1)
        info "Déploiement du Backend..."
        cd backend

        # Vérifier si un projet Railway existe
        if [ ! -f ".railway" ]; then
            info "Initialisation du projet Railway pour le backend..."
            railway init
        fi

        # Déployer
        railway up
        success "Backend déployé!"

        # Obtenir l'URL
        BACKEND_URL=$(railway domain)
        success "Backend accessible sur: $BACKEND_URL"
        ;;

    2)
        info "Déploiement du Frontend..."
        cd frontend

        if [ ! -f ".railway" ]; then
            info "Initialisation du projet Railway pour le frontend..."
            railway init
        fi

        railway up
        success "Frontend déployé!"

        FRONTEND_URL=$(railway domain)
        success "Frontend accessible sur: $FRONTEND_URL"
        ;;

    3)
        info "Déploiement complet (Backend + Frontend)..."

        # Backend
        info "Étape 1/2: Déploiement du backend..."
        cd backend
        if [ ! -f ".railway" ]; then
            railway init
        fi
        railway up
        BACKEND_URL=$(railway domain)
        success "Backend déployé sur: $BACKEND_URL"
        cd ..

        # Frontend
        info "Étape 2/2: Déploiement du frontend..."
        cd frontend
        if [ ! -f ".railway" ]; then
            railway init
        fi

        # Mettre à jour la variable d'environnement du frontend
        railway variables set REACT_APP_API_URL="$BACKEND_URL"

        railway up
        FRONTEND_URL=$(railway domain)
        success "Frontend déployé sur: $FRONTEND_URL"
        cd ..

        # Mettre à jour le CORS du backend
        cd backend
        railway variables set ALLOWED_ORIGINS="$FRONTEND_URL"
        cd ..

        echo ""
        success "🎉 Déploiement complet réussi!"
        echo ""
        echo "📌 URLs de votre application:"
        echo "   Frontend: $FRONTEND_URL"
        echo "   Backend:  $BACKEND_URL"
        echo "   API Docs: $BACKEND_URL/docs"
        ;;

    4)
        info "Configuration des variables d'environnement..."
        echo "Pour quel service?"
        echo "1) Backend"
        echo "2) Frontend"
        read -p "Votre choix: " service_choice

        if [ "$service_choice" == "1" ]; then
            cd backend
            railway variables
        else
            cd frontend
            railway variables
        fi
        ;;

    5)
        info "Affichage des logs..."
        echo "Pour quel service?"
        echo "1) Backend"
        echo "2) Frontend"
        read -p "Votre choix: " log_choice

        if [ "$log_choice" == "1" ]; then
            cd backend
            railway logs
        else
            cd frontend
            railway logs
        fi
        ;;

    *)
        error "Choix invalide"
        ;;
esac

echo ""
success "Terminé! 🎊"
