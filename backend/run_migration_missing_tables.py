"""
Script pour exécuter la migration des tables manquantes
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ ERREUR: Variables d'environnement Supabase manquantes")
    print("   Vérifiez SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY dans .env")
    exit(1)

# Client Supabase avec droits admin
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("=" * 70)
print("🚀 MIGRATION - Tables manquantes ShareYourSales")
print("=" * 70)
print(f"📍 URL: {SUPABASE_URL}\n")

# Lire le fichier SQL
migration_path = os.path.join(
    os.path.dirname(__file__), "..", "database", "migrations", "add_only_missing_tables.sql"
)

print(f"📄 Lecture du fichier: {migration_path}")

try:
    with open(migration_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print(f"✅ Fichier lu: {len(sql_content)} caractères\n")

    print("⚠️  IMPORTANT: Ce script ne peut pas exécuter directement le SQL.")
    print("   Supabase Python SDK ne supporte pas l'exécution de DDL (CREATE TABLE).\n")

    print("📋 INSTRUCTIONS POUR EXÉCUTER LA MIGRATION:")
    print("-" * 70)
    print("1. Ouvrez votre navigateur:")
    print(f"   https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits/sql/new")
    print("")
    print("2. Copiez le contenu du fichier:")
    print(f"   {migration_path}")
    print("")
    print("3. Collez dans l'éditeur SQL de Supabase")
    print("")
    print("4. Cliquez sur 'RUN' (bouton vert en haut à droite)")
    print("")
    print("5. Vérifiez les résultats:")
    print("   - 8 nouvelles tables créées")
    print("   - 28 permissions insérées")
    print("   - 5 templates d'emails insérés")
    print("")
    print("=" * 70)
    print("📋 TABLES QUI SERONT CRÉÉES:")
    print("=" * 70)
    tables = [
        "1. company_settings       - Paramètres entreprise",
        "2. payment_gateways       - Gateways paiement (CMI, PayZen, SG Maroc)",
        "3. invoices               - Facturation automatique",
        "4. activity_log           - Journal d'activité",
        "5. mlm_commissions        - Commissions MLM multi-niveaux",
        "6. permissions            - Permissions granulaires par rôle",
        "7. traffic_sources        - Sources de trafic UTM",
        "8. email_templates        - Templates emails transactionnels",
    ]
    for table in tables:
        print(f"   {table}")

    print("")
    print("=" * 70)
    print("💡 ALTERNATIVE: Copier-coller manuel")
    print("=" * 70)
    print("Si vous préférez copier le SQL directement, tapez:")
    print(f"   cat {migration_path}")
    print("")
    print("Puis copiez tout le contenu et collez dans Supabase SQL Editor.")
    print("")

except FileNotFoundError:
    print(f"❌ ERREUR: Fichier non trouvé: {migration_path}")
    print("   Vérifiez que le fichier existe dans database/migrations/")
    exit(1)
except Exception as e:
    print(f"❌ ERREUR: {e}")
    exit(1)

print("✅ Script terminé")
print("   Suivez les instructions ci-dessus pour exécuter la migration.")
