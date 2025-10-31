#!/bin/sh
set -e

# Injection des variables d'environnement dans le fichier env-config.js
cat <<EOF > /usr/share/nginx/html/env-config.js
window._env_ = {
  REACT_APP_API_URL: "${REACT_APP_API_URL:-http://localhost:8001}",
  REACT_APP_SUPABASE_URL: "${REACT_APP_SUPABASE_URL}",
  REACT_APP_SUPABASE_ANON_KEY: "${REACT_APP_SUPABASE_ANON_KEY}",
  REACT_APP_STRIPE_PUBLISHABLE_KEY: "${REACT_APP_STRIPE_PUBLISHABLE_KEY}",
  REACT_APP_ENVIRONMENT: "${REACT_APP_ENVIRONMENT:-production}"
};
EOF

echo "Environment variables injected successfully"

# Exécuter la commande passée au script
exec "$@"
