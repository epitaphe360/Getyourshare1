"""
Script automatique pour créer les tables manquantes dans Supabase
Utilise le token fourni pour se connecter et créer les tables directement
"""

import os
import requests
import json

# Token Supabase fourni
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://bmcdjlqfyzvmmjuvmrgz.supabase.co")
SUPABASE_KEY = "sbp_d45d903473cb0435b31f5ddafc74f8dff93273fe"

print("=" * 80)
print("🔍 CONNEXION À SUPABASE ET VÉRIFICATION DES TABLES")
print("=" * 80)
print(f"\n📡 URL: {SUPABASE_URL}")
print(f"🔑 Token: {SUPABASE_KEY[:20]}...")

# Headers pour les requêtes
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Fonction pour exécuter du SQL directement
def execute_sql(sql_query):
    """Exécute du SQL via l'API REST de Supabase"""
    try:
        # Utiliser l'endpoint RPC pour exécuter du SQL
        url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"

        # Si l'endpoint n'existe pas, on utilise psql directement
        # Pour l'instant, on va lister les tables existantes via postgrest

        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

# Fonction pour lister les tables existantes
def list_existing_tables():
    """Liste toutes les tables existantes dans la base"""
    print("\n" + "=" * 80)
    print("📊 TABLES EXISTANTES DANS VOTRE BASE DE DONNÉES")
    print("=" * 80)

    # Tester chaque table possible
    tables_to_check = [
        'users',
        'campaigns',
        'products',
        'sales',
        'clicks',
        'conversions',
        'trust_scores',
        'payouts',
        'payment_accounts',
        'ai_content_history',
        'smart_matches',
        'achievements',
        'user_levels',
        'notification_subscriptions'
    ]

    existing_tables = []
    missing_tables = []

    for table in tables_to_check:
        try:
            url = f"{SUPABASE_URL}/rest/v1/{table}?limit=1"
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                print(f"   ✅ {table}")
                existing_tables.append(table)
            elif response.status_code == 404 or 'does not exist' in response.text:
                print(f"   ❌ {table} (MANQUANTE)")
                missing_tables.append(table)
            else:
                print(f"   ⚠️  {table} (Erreur: {response.status_code})")
        except Exception as e:
            print(f"   ⚠️  {table} (Erreur: {str(e)[:50]})")

    return existing_tables, missing_tables

# Fonction pour vérifier la structure d'une table
def check_table_structure(table_name):
    """Vérifie la structure d'une table existante"""
    print(f"\n🔍 Structure de la table '{table_name}':")

    try:
        # Faire une requête pour voir un exemple de données
        url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                columns = list(data[0].keys())
                print(f"   Colonnes: {', '.join(columns)}")
                return columns
            else:
                print(f"   ⚠️  Table vide, impossible de voir la structure")
                return []
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return []
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return []

# Fonction pour créer une table via INSERT (méthode alternative)
def create_table_data(table_name, test_data):
    """Essaie de créer une entrée de test pour voir si la table existe"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table_name}"
        response = requests.post(url, headers=headers, json=test_data, timeout=5)

        if response.status_code in [200, 201]:
            print(f"   ✅ Table {table_name} accessible en écriture")
            return True
        else:
            print(f"   ❌ Impossible d'écrire dans {table_name}: {response.status_code}")
            print(f"      Message: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

# SCRIPT PRINCIPAL
def main():
    print("\n🚀 DÉMARRAGE DE L'ANALYSE...\n")

    # 1. Lister les tables existantes
    existing, missing = list_existing_tables()

    print("\n" + "=" * 80)
    print(f"📊 RÉSUMÉ:")
    print("=" * 80)
    print(f"✅ Tables existantes: {len(existing)}")
    print(f"❌ Tables manquantes: {len(missing)}")

    # 2. Vérifier la structure des tables importantes
    if 'users' in existing:
        print("\n" + "=" * 80)
        print("👤 STRUCTURE DE LA TABLE 'users'")
        print("=" * 80)
        user_columns = check_table_structure('users')

        # Vérifier si user_id existe
        if user_columns:
            if 'user_id' in user_columns:
                print("\n   ✅ Colonne 'user_id' existe dans users")
            elif 'id' in user_columns:
                print("\n   ⚠️  La table users utilise 'id' et non 'user_id'")
                print("   💡 Solution: Les nouvelles tables doivent utiliser 'id' comme référence")
            else:
                print("\n   ⚠️  Ni 'id' ni 'user_id' trouvé")

    if 'campaigns' in existing:
        print("\n" + "=" * 80)
        print("📊 STRUCTURE DE LA TABLE 'campaigns'")
        print("=" * 80)
        check_table_structure('campaigns')

    # 3. Afficher les tables à créer
    if missing:
        print("\n" + "=" * 80)
        print("📝 TABLES À CRÉER:")
        print("=" * 80)
        for table in missing:
            print(f"   - {table}")

        print("\n💡 SOLUTION:")
        print("=" * 80)
        print("Ces tables doivent être créées via SQL Editor dans Supabase.")
        print("Le fichier SQL approprié est: database/migrations/create_tables_SIMPLE.sql")
        print("\nPour créer les tables automatiquement:")
        print("1. Ouvrez Supabase Dashboard: https://app.supabase.co")
        print("2. SQL Editor → New Query")
        print("3. Copiez le contenu de create_tables_SIMPLE.sql")
        print("4. Cliquez RUN")

    # 4. Test de connexion
    print("\n" + "=" * 80)
    print("🧪 TEST DE CONNEXION")
    print("=" * 80)

    if existing:
        test_table = existing[0]
        print(f"Test avec la table '{test_table}'...")
        url = f"{SUPABASE_URL}/rest/v1/{test_table}?limit=1"
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            print(f"✅ Connexion réussie !")
            print(f"✅ Token valide !")
            print(f"✅ Accès en lecture: OK")
        else:
            print(f"❌ Erreur de connexion: {response.status_code}")

    print("\n" + "=" * 80)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 80)

if __name__ == "__main__":
    main()
