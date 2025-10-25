#!/usr/bin/env python3
"""
Script pour ajouter la validation des variables d'environnement
dans tous les fichiers d'endpoints
"""

import re

files_to_fix = [
    "backend/domain_endpoints.py",
    "backend/stripe_webhook_handler.py",
    "backend/commercials_directory_endpoints.py",
    "backend/influencers_directory_endpoints.py",
    "backend/company_links_management.py"
]

# Pattern à chercher
old_pattern = r'''# ============================================
# SUPABASE CLIENT
# ============================================

supabase: Client = create_client\(
    os\.getenv\("SUPABASE_URL"\),
    os\.getenv\("SUPABASE_SERVICE_ROLE_KEY"\)
\)'''

# Remplacement
new_code = '''# ============================================
# ENVIRONMENT VARIABLES VALIDATION
# ============================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing required Supabase environment variables")

# ============================================
# SUPABASE CLIENT
# ============================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)'''

for filepath in files_to_fix:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remplacer le pattern
        new_content = re.sub(old_pattern, new_code, content, flags=re.MULTILINE)

        # Écrire le fichier modifié
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ {filepath}")
    except Exception as e:
        print(f"❌ {filepath}: {e}")

print("\n✅ Tous les fichiers ont été corrigés!")
