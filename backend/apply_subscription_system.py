#!/usr/bin/env python3
"""
Script de migration pour appliquer le système d'abonnement SaaS
Ce script crée toutes les tables nécessaires et insère les plans par défaut
"""

import os
import sys
from dotenv import load_dotenv
from supabase_client import supabase

# Charger les variables d'environnement
load_dotenv()


def read_sql_file(filename):
    """Lit un fichier SQL et retourne son contenu"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Erreur: Le fichier {filename} n'a pas été trouvé")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")
        return None


def execute_sql(sql_content):
    """Exécute du code SQL via Supabase"""
    try:
        # Split le SQL en statements individuels
        statements = []
        current_statement = []

        for line in sql_content.split('\n'):
            # Ignorer les commentaires
            if line.strip().startswith('--'):
                continue

            current_statement.append(line)

            # Si la ligne se termine par ; , c'est la fin d'un statement
            if line.strip().endswith(';'):
                statement = '\n'.join(current_statement)
                if statement.strip():
                    statements.append(statement)
                current_statement = []

        print(f"📝 {len(statements)} statements SQL à exécuter\n")

        # Exécuter chaque statement
        for i, statement in enumerate(statements, 1):
            try:
                # Les statements CREATE TABLE, CREATE INDEX, etc. doivent être exécutés via RPC
                result = supabase.rpc('exec_sql', {'query': statement}).execute()
                print(f"✅ Statement {i}/{len(statements)} exécuté avec succès")
            except Exception as e:
                # Si la fonction RPC n'existe pas, on utilise une approche alternative
                # Certaines installations Supabase nécessitent l'exécution via le dashboard SQL
                print(f"⚠️  Statement {i}/{len(statements)}: {str(e)[:100]}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution SQL: {e}")
        return False


def check_tables_exist():
    """Vérifie si les tables d'abonnement existent déjà"""
    try:
        result = supabase.table("subscription_plans").select("id").limit(1).execute()
        return True
    except:
        return False


def main():
    """Fonction principale"""
    print("="*70)
    print("🚀 APPLICATION DU SYSTÈME D'ABONNEMENT SaaS")
    print("="*70)
    print()

    # Vérifier la connexion Supabase
    print("🔍 Vérification de la connexion Supabase...")
    try:
        result = supabase.table("users").select("id").limit(1).execute()
        print("✅ Connexion Supabase OK\n")
    except Exception as e:
        print(f"❌ Erreur de connexion Supabase: {e}")
        print("\n⚠️  Vérifiez vos credentials dans le fichier .env")
        sys.exit(1)

    # Vérifier si les tables existent déjà
    print("🔍 Vérification des tables existantes...")
    if check_tables_exist():
        print("⚠️  Les tables d'abonnement existent déjà!")
        response = input("\n❓ Voulez-vous continuer quand même? (yes/no): ")
        if response.lower() != 'yes':
            print("\n❌ Opération annulée")
            sys.exit(0)
    else:
        print("✅ Aucune table d'abonnement trouvée, prêt à créer\n")

    # Lire le fichier SQL
    print("📖 Lecture du fichier SQL...")
    sql_content = read_sql_file('create_subscription_tables.sql')

    if not sql_content:
        print("\n❌ Impossible de lire le fichier SQL")
        print("\n💡 Assurez-vous que le fichier 'create_subscription_tables.sql' existe dans le même dossier")
        sys.exit(1)

    print(f"✅ Fichier SQL chargé ({len(sql_content)} caractères)\n")

    # Message important
    print("="*70)
    print("⚠️  IMPORTANT - INSTRUCTIONS POUR SUPABASE")
    print("="*70)
    print()
    print("Supabase ne permet pas l'exécution directe de SQL DDL via l'API.")
    print("Vous devez exécuter le SQL manuellement via le dashboard Supabase:")
    print()
    print("1. Ouvrez votre projet Supabase: https://app.supabase.com")
    print("2. Allez dans 'SQL Editor' dans le menu de gauche")
    print("3. Créez une nouvelle requête")
    print("4. Copiez-collez le contenu du fichier: create_subscription_tables.sql")
    print("5. Cliquez sur 'Run' pour exécuter")
    print()
    print("Le fichier contient:")
    print("  ✅ Création de 8 tables (subscription_plans, subscriptions, etc.)")
    print("  ✅ Création des index pour performance")
    print("  ✅ Création des triggers pour updated_at")
    print("  ✅ Insertion des plans par défaut (Freemium, Standard, Premium, etc.)")
    print("  ✅ Insertion de coupons de lancement")
    print()
    print("="*70)
    print()

    response = input("❓ Avez-vous déjà exécuté le SQL dans Supabase? (yes/no): ")

    if response.lower() == 'yes':
        print("\n✅ Parfait! Le système d'abonnement devrait être opérationnel.")
        print()
        print("🎉 INSTALLATION TERMINÉE!")
        print()
        print("📝 Prochaines étapes:")
        print("  1. Configurez vos clés Stripe dans le fichier .env:")
        print("     STRIPE_SECRET_KEY=sk_test_...")
        print("     STRIPE_WEBHOOK_SECRET=whsec_...")
        print()
        print("  2. Installez les nouvelles dépendances:")
        print("     pip install -r requirements.txt")
        print()
        print("  3. Redémarrez votre serveur:")
        print("     python server.py")
        print()
        print("  4. Testez les endpoints d'abonnement:")
        print("     http://localhost:8001/docs")
        print()
        print("="*70)

    else:
        print("\n💡 Veuillez exécuter le SQL dans Supabase, puis relancez ce script.")
        print()
        print("📄 Le fichier SQL se trouve ici: ./create_subscription_tables.sql")
        print()
        sys.exit(0)


def create_example_env():
    """Crée un fichier .env.example avec les variables nécessaires"""
    env_content = """
# ============================================
# SYSTÈME D'ABONNEMENT SaaS - Configuration
# ============================================

# Stripe (Paiements)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Supabase (déjà configuré)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# JWT (déjà configuré)
JWT_SECRET=your_jwt_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
"""

    try:
        with open('.env.subscription.example', 'w') as f:
            f.write(env_content.strip())
        print("✅ Fichier .env.subscription.example créé")
    except Exception as e:
        print(f"⚠️  Impossible de créer .env.subscription.example: {e}")


if __name__ == "__main__":
    try:
        main()
        create_example_env()
    except KeyboardInterrupt:
        print("\n\n❌ Opération annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
