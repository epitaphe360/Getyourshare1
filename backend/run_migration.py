"""
Script de migration pour ajouter les colonnes et tables nécessaires
au système de paiement automatique
"""

from supabase_client import supabase
import os


def run_migration():
    """Exécute la migration SQL"""

    print("\n" + "=" * 60)
    print("🔄 MIGRATION: Paiements Automatiques")
    print("=" * 60 + "\n")

    # Lire le fichier SQL
    migration_file = os.path.join(
        os.path.dirname(__file__), "..", "database", "migrations", "add_payment_columns.sql"
    )

    try:
        with open(migration_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        print("📄 Fichier de migration chargé")
        print(f"   Taille: {len(sql_content)} caractères\n")

        # Supabase ne supporte pas l'exécution directe de SQL via l'API Python
        # On doit utiliser l'éditeur SQL dans le dashboard Supabase
        # Ou créer les tables manuellement via l'API

        print("⚠️  IMPORTANT:")
        print("   Supabase nécessite d'exécuter le SQL via le Dashboard\n")
        print("📋 INSTRUCTIONS:")
        print("   1. Ouvrez: https://supabase.com/dashboard")
        print("   2. Sélectionnez votre projet: iamezkmapbhlhhvvsits")
        print("   3. Allez dans 'SQL Editor'")
        print("   4. Copiez-collez le contenu du fichier:")
        print(f"      {migration_file}")
        print("   5. Cliquez sur 'Run'\n")

        # Alternative: Créer les tables via l'API REST
        print("🔧 Création alternative via API...\n")

        # 1. Créer la table payouts
        try:
            # Vérifier si la table existe déjà
            result = supabase.table("payouts").select("id").limit(1).execute()
            print("✅ Table 'payouts' existe déjà")
        except Exception as e:
            if "PGRST205" in str(e):  # Table n'existe pas
                print("❌ Table 'payouts' manquante")
                print("   → Créez-la via le Dashboard SQL Editor")
            else:
                print(f"⚠️  Erreur vérification 'payouts': {e}")

        # 2. Créer la table notifications
        try:
            result = supabase.table("notifications").select("id").limit(1).execute()
            print("✅ Table 'notifications' existe déjà")
        except Exception as e:
            if "PGRST205" in str(e):
                print("❌ Table 'notifications' manquante")
                print("   → Créez-la via le Dashboard SQL Editor")
            else:
                print(f"⚠️  Erreur vérification 'notifications': {e}")

        # 3. Vérifier les colonnes
        try:
            result = supabase.table("sales").select("updated_at").limit(1).execute()
            print("✅ Colonne 'sales.updated_at' existe")
        except Exception as e:
            if "PGRST204" in str(e):
                print("❌ Colonne 'sales.updated_at' manquante")
                print("   → Ajoutez-la via le Dashboard SQL Editor")
            else:
                print(f"⚠️  Erreur vérification 'sales.updated_at': {e}")

        try:
            result = supabase.table("commissions").select("approved_at").limit(1).execute()
            print("✅ Colonne 'commissions.approved_at' existe")
        except Exception as e:
            if "PGRST204" in str(e):
                print("❌ Colonne 'commissions.approved_at' manquante")
                print("   → Ajoutez-la via le Dashboard SQL Editor")
            else:
                print(f"⚠️  Erreur vérification 'commissions.approved_at': {e}")

        print("\n" + "=" * 60)
        print("📝 RÉSUMÉ")
        print("=" * 60)
        print("\nPour finaliser la migration:")
        print("1. Copiez le contenu de:")
        print(f"   {migration_file}")
        print("\n2. Exécutez-le dans Supabase SQL Editor:")
        print("   https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits/sql")
        print("\n3. Relancez ce script pour vérifier")
        print("\n" + "=" * 60 + "\n")

    except FileNotFoundError:
        print(f"❌ Fichier de migration non trouvé: {migration_file}")
        print("   Créez-le d'abord avec create_migration_file()")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def create_tables_manually():
    """Crée les tables manuellement (alternative)"""

    print("\n🔧 Création manuelle des tables...\n")

    # Note: Supabase API ne permet pas de créer des tables directement
    # Il faut utiliser le SQL Editor du Dashboard

    print("⚠️  Impossible de créer les tables via l'API Python")
    print("   Utilisez le Dashboard Supabase SQL Editor\n")


if __name__ == "__main__":
    print(
        """
╔═══════════════════════════════════════════════════════════╗
║   MIGRATION - SYSTÈME DE PAIEMENT AUTOMATIQUE            ║
╚═══════════════════════════════════════════════════════════╝
    """
    )

    run_migration()

    print("\n✅ Vérification terminée")
    print("\nAprès avoir exécuté le SQL dans Supabase Dashboard,")
    print("relancez les tests avec: python test_payment_system.py\n")
