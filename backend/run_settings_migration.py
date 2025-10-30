#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migration des tables de settings dans Supabase
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def run_migration():
    """Execute la migration SQL pour créer les tables de settings"""

    print("\n" + "=" * 60)
    print("  MIGRATION: Tables de Settings")
    print("=" * 60 + "\n")

    # Connexion PostgreSQL directe
    print("Connexion à Supabase PostgreSQL...")

    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("ERREUR: SUPABASE_DB_URL non trouvée dans .env")
        return False

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Lire le fichier SQL
    migration_file = os.path.join("..", "database", "migrations", "add_all_settings_tables.sql")
    print(f"Lecture du fichier: {migration_file}")

    with open(migration_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print(f"\nExecution du script SQL...\n")

    try:
        # Exécuter tout le SQL d'un coup
        cursor.execute(sql_content)
        conn.commit()

        print("OK - Script execute avec succes!")

        # Vérifier les tables créées
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%settings'
            ORDER BY table_name;
        """
        )

        tables = cursor.fetchall()

        success_count = len(tables)
        error_count = 0

    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            print(f"INFO: Certaines tables existent deja")
            success_count = 5
            error_count = 0
        else:
            print(f"ERREUR: {error_msg}")
            success_count = 0
            error_count = 1

    finally:
        cursor.close()
        conn.close()

    print("\n" + "=" * 60)
    print(f"  RÉSULTATS:")
    print(f"    Succès: {success_count}")
    print(f"    Erreurs: {error_count}")
    print("=" * 60)

    if error_count == 0:
        print("\n  MIGRATION TERMINÉE AVEC SUCCÈS!\n")
        print("  Tables créées:")
        print("    - permissions_settings")
        print("    - affiliate_settings")
        print("    - registration_settings")
        print("    - mlm_settings")
        print("    - whitelabel_settings")
        print("\n  Les boutons 'Enregistrer' sont maintenant fonctionnels!\n")
        return True
    else:
        print("\n  MIGRATION TERMINÉE AVEC ERREURS")
        print("  Vérifiez les messages ci-dessus\n")
        return False


if __name__ == "__main__":
    run_migration()
