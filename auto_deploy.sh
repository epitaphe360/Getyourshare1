#!/bin/bash

# ============================================
# 🚀 INSTALLATION AUTOMATIQUE RAILWAY
# GetYourShare - Déploiement Production
# ============================================

set -e  # Arrêt en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonctions d'affichage
error() {
    echo -e "${RED}❌ $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

step() {
    echo -e "\n${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔹 $1${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

banner() {
    echo -e "\n${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║        🚀 GETYOURSHARE - DÉPLOIEMENT AUTOMATIQUE 🚀       ║"
    echo "║                                                            ║"
    echo "║           Railway + Supabase + Production Ready            ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

# Variables globales
BACKEND_URL=""
FRONTEND_URL=""
PROJECT_DIR=$(pwd)

# ============================================
# ÉTAPE 0: Vérifications Préalables
# ============================================
check_prerequisites() {
    step "Vérification des prérequis"

    # Vérifier Git
    if ! command -v git &> /dev/null; then
        error "Git n'est pas installé"
        exit 1
    fi
    success "Git installé"

    # Vérifier si on est dans le bon dossier
    if [ ! -f "DEPLOY_RAILWAY.md" ]; then
        error "Ce script doit être exécuté depuis le dossier racine du projet"
        exit 1
    fi
    success "Dossier projet détecté"

    # Vérifier si .env.production existe
    if [ ! -f ".env.production" ]; then
        error "Fichier .env.production non trouvé"
        exit 1
    fi
    success "Fichier .env.production trouvé"
}

# ============================================
# ÉTAPE 1: Installation Railway CLI
# ============================================
install_railway_cli() {
    step "Installation de Railway CLI"

    if command -v railway &> /dev/null; then
        success "Railway CLI déjà installé"
        railway --version
        return
    fi

    info "Installation de Railway CLI..."

    # Détection du système d'exploitation
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        info "Système: Linux"
        bash <(curl -fsSL https://railway.app/install.sh)
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        info "Système: macOS"
        if command -v brew &> /dev/null; then
            brew install railway
        else
            bash <(curl -fsSL https://railway.app/install.sh)
        fi
    else
        error "Système non supporté. Installez manuellement: https://docs.railway.app/develop/cli"
        exit 1
    fi

    success "Railway CLI installé"
}

# ============================================
# ÉTAPE 2: Connexion à Railway
# ============================================
login_railway() {
    step "Connexion à Railway"

    if railway whoami &> /dev/null; then
        RAILWAY_USER=$(railway whoami)
        success "Déjà connecté en tant que: $RAILWAY_USER"
        return
    fi

    info "Ouverture du navigateur pour connexion..."
    railway login

    if railway whoami &> /dev/null; then
        success "Connecté à Railway avec succès"
    else
        error "Échec de la connexion à Railway"
        exit 1
    fi
}

# ============================================
# ÉTAPE 3: Configuration Supabase
# ============================================
setup_supabase() {
    step "Configuration de Supabase"

    info "Vérification de la connexion Supabase..."

    # Extraire les credentials depuis .env.production
    source .env.production

    if [ -z "$SUPABASE_URL" ]; then
        error "SUPABASE_URL non trouvé dans .env.production"
        exit 1
    fi

    success "Supabase URL: $SUPABASE_URL"

    warning "ÉTAPE MANUELLE REQUISE:"
    echo ""
    echo "   1. Ouvrez: https://app.supabase.com/project/iamezkmapbhlhhvvsits/editor"
    echo "   2. Cliquez sur 'New Query'"
    echo "   3. Copiez le contenu de: backend/create_subscription_tables.sql"
    echo "   4. Cliquez sur 'Run'"
    echo ""
    read -p "   Appuyez sur Entrée une fois les tables créées..."

    success "Configuration Supabase terminée"
}

# ============================================
# ÉTAPE 4: Création du Projet Railway
# ============================================
create_railway_project() {
    step "Création du projet Railway"

    info "Initialisation du projet Railway..."

    # Vérifier si déjà initialisé
    if [ -d ".railway" ]; then
        warning "Projet Railway déjà initialisé"
        read -p "   Voulez-vous créer un nouveau projet? (o/N): " response
        if [[ ! "$response" =~ ^[Oo]$ ]]; then
            info "Utilisation du projet existant"
            return
        fi
        rm -rf .railway
    fi

    # Créer un nouveau projet
    railway init

    success "Projet Railway créé"
}

# ============================================
# ÉTAPE 5: Déploiement du Backend
# ============================================
deploy_backend() {
    step "Déploiement du Backend"

    cd "$PROJECT_DIR/backend"

    info "Configuration du service backend..."

    # Créer railway.toml s'il n'existe pas
    if [ ! -f "railway.toml" ]; then
        cat > railway.toml <<EOF
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn server:app --host 0.0.0.0 --port \$PORT --workers 4"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
healthcheckPath = "/health"
healthcheckTimeout = 100
EOF
    fi

    # Charger les variables depuis .env.production
    source "$PROJECT_DIR/.env.production"

    info "Configuration des variables d'environnement backend..."

    # Configurer les variables essentielles
    railway variables set SUPABASE_URL="$SUPABASE_URL" \
        SUPABASE_KEY="$SUPABASE_KEY" \
        SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
        JWT_SECRET_KEY="$JWT_SECRET_KEY" \
        JWT_ALGORITHM="HS256" \
        APP_ENV="production" \
        PORT="8001" \
        AUTO_PAYMENTS_ENABLED="true" \
        ALLOWED_ORIGINS="*"

    success "Variables backend configurées"

    info "Déploiement du backend en cours..."
    railway up --detach

    success "Backend déployé"

    info "Génération du domaine backend..."
    railway domain

    # Récupérer l'URL du backend
    sleep 5
    BACKEND_URL=$(railway domain 2>/dev/null | grep -oP 'https://[^ ]+' || echo "")

    if [ -n "$BACKEND_URL" ]; then
        success "Backend accessible sur: $BACKEND_URL"
    else
        warning "URL backend non récupérée automatiquement"
        echo "Consultez: railway domain"
    fi

    cd "$PROJECT_DIR"
}

# ============================================
# ÉTAPE 6: Déploiement du Frontend
# ============================================
deploy_frontend() {
    step "Déploiement du Frontend"

    cd "$PROJECT_DIR/frontend"

    info "Configuration du service frontend..."

    # Créer railway.toml s'il n'existe pas
    if [ ! -f "railway.toml" ]; then
        cat > railway.toml <<EOF
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
healthcheckPath = "/health"
healthcheckTimeout = 100
EOF
    fi

    # Charger les variables
    source "$PROJECT_DIR/.env.production"

    info "Configuration des variables d'environnement frontend..."

    # Configurer les variables frontend
    railway variables set REACT_APP_SUPABASE_URL="$REACT_APP_SUPABASE_URL" \
        REACT_APP_SUPABASE_ANON_KEY="$REACT_APP_SUPABASE_ANON_KEY" \
        REACT_APP_ENVIRONMENT="production" \
        PORT="80"

    # Ajouter l'URL du backend si disponible
    if [ -n "$BACKEND_URL" ]; then
        railway variables set REACT_APP_API_URL="$BACKEND_URL"
    fi

    success "Variables frontend configurées"

    info "Déploiement du frontend en cours..."
    railway up --detach

    success "Frontend déployé"

    info "Génération du domaine frontend..."
    railway domain

    # Récupérer l'URL du frontend
    sleep 5
    FRONTEND_URL=$(railway domain 2>/dev/null | grep -oP 'https://[^ ]+' || echo "")

    if [ -n "$FRONTEND_URL" ]; then
        success "Frontend accessible sur: $FRONTEND_URL"
    else
        warning "URL frontend non récupérée automatiquement"
        echo "Consultez: railway domain"
    fi

    cd "$PROJECT_DIR"
}

# ============================================
# ÉTAPE 7: Configuration CORS
# ============================================
configure_cors() {
    step "Configuration CORS"

    if [ -z "$FRONTEND_URL" ]; then
        warning "URL frontend non disponible, CORS non configuré"
        return
    fi

    cd "$PROJECT_DIR/backend"

    info "Mise à jour de ALLOWED_ORIGINS..."
    railway variables set ALLOWED_ORIGINS="$FRONTEND_URL"

    success "CORS configuré"

    cd "$PROJECT_DIR"
}

# ============================================
# ÉTAPE 8: Vérification du Déploiement
# ============================================
verify_deployment() {
    step "Vérification du déploiement"

    if [ -n "$BACKEND_URL" ]; then
        info "Test du backend..."
        sleep 10  # Attendre que le service démarre

        if curl -f "$BACKEND_URL/health" &> /dev/null; then
            success "Backend opérationnel ✓"
        else
            warning "Backend en cours de démarrage (peut prendre 2-3 minutes)..."
        fi
    fi

    if [ -n "$FRONTEND_URL" ]; then
        info "Test du frontend..."
        if curl -f "$FRONTEND_URL/health" &> /dev/null; then
            success "Frontend opérationnel ✓"
        else
            warning "Frontend en cours de démarrage (peut prendre 2-3 minutes)..."
        fi
    fi
}

# ============================================
# ÉTAPE 9: Résumé Final
# ============================================
show_summary() {
    step "🎉 Déploiement Terminé!"

    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║              ✅ DÉPLOIEMENT RÉUSSI! ✅                    ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"

    info "📌 URLs de votre application:"
    echo ""

    if [ -n "$BACKEND_URL" ]; then
        echo -e "   ${CYAN}Backend API:${NC}     $BACKEND_URL"
        echo -e "   ${CYAN}API Docs:${NC}        $BACKEND_URL/docs"
    else
        echo -e "   ${YELLOW}Backend:${NC}         Consultez 'railway domain' dans backend/"
    fi

    if [ -n "$FRONTEND_URL" ]; then
        echo -e "   ${CYAN}Frontend App:${NC}    $FRONTEND_URL"
    else
        echo -e "   ${YELLOW}Frontend:${NC}        Consultez 'railway domain' dans frontend/"
    fi

    echo ""
    info "📊 Dashboards:"
    echo "   - Supabase:  https://app.supabase.com/project/iamezkmapbhlhhvvsits"
    echo "   - Railway:   https://railway.app/dashboard"
    echo ""

    info "🔧 Prochaines étapes:"
    echo "   1. Configurer Stripe (STRIPE_SECRET_KEY dans Railway)"
    echo "   2. Configurer Email SMTP (Gmail App Password)"
    echo "   3. Tester les dashboards"
    echo "   4. Configurer un domaine personnalisé (optionnel)"
    echo ""

    success "Installation terminée! 🎊"
    echo ""
}

# ============================================
# FONCTION PRINCIPALE
# ============================================
main() {
    banner

    # Menu de démarrage
    echo "Que voulez-vous faire?"
    echo ""
    echo "  1) Installation complète automatique (Recommandé)"
    echo "  2) Déployer backend uniquement"
    echo "  3) Déployer frontend uniquement"
    echo "  4) Configuration Supabase uniquement"
    echo "  5) Annuler"
    echo ""
    read -p "Votre choix (1-5): " choice

    case $choice in
        1)
            check_prerequisites
            install_railway_cli
            login_railway
            setup_supabase
            create_railway_project
            deploy_backend
            deploy_frontend
            configure_cors
            verify_deployment
            show_summary
            ;;
        2)
            check_prerequisites
            install_railway_cli
            login_railway
            create_railway_project
            deploy_backend
            verify_deployment
            echo ""
            success "Backend déployé: $BACKEND_URL"
            ;;
        3)
            check_prerequisites
            install_railway_cli
            login_railway
            create_railway_project
            deploy_frontend
            verify_deployment
            echo ""
            success "Frontend déployé: $FRONTEND_URL"
            ;;
        4)
            setup_supabase
            ;;
        5)
            info "Installation annulée"
            exit 0
            ;;
        *)
            error "Choix invalide"
            exit 1
            ;;
    esac
}

# Exécution
main
