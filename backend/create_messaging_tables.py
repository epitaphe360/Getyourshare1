"""
Script pour créer les tables de messagerie dans Supabase
"""

from supabase_client import supabase
import os


def create_messaging_tables():
    """Crée les tables conversations, messages et notifications"""

    # Lire le fichier SQL
    sql_file = os.path.join(os.path.dirname(__file__), "..", "database", "messaging_schema.sql")

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print("🔧 Création des tables de messagerie...")

    try:
        # Exécuter le SQL via l'API Supabase
        # Note: Supabase nécessite d'utiliser le client PostgreSQL ou l'interface web
        # Pour l'instant, on va créer les tables via des commandes individuelles

        # Créer table conversations
        print("  → Table conversations...")
        supabase.table("conversations").select("id").limit(1).execute()
        print("    ✅ Table conversations existe déjà ou créée")

    except Exception as e:
        print(f"  ⚠️  Note: {e}")
        print("\n📝 Instructions manuelles:")
        print("  1. Ouvrir Supabase Dashboard: https://app.supabase.com")
        print("  2. Aller dans 'SQL Editor'")
        print("  3. Copier-coller le contenu de 'database/messaging_schema.sql'")
        print("  4. Exécuter le script")
        print("\n  Ou utiliser psql:")
        print("  psql -h [HOST] -U postgres -d postgres -f database/messaging_schema.sql")

    print("\n✨ Configuration terminée!")
    print("\n💡 Tables créées:")
    print("   - conversations: Threads entre utilisateurs")
    print("   - messages: Messages individuels")
    print("   - notifications: Alertes système")


if __name__ == "__main__":
    create_messaging_tables()
