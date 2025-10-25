#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'Installation Automatique Supabase
Crée toutes les tables nécessaires pour GetYourShare
"""

import os
import sys
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = "https://iamezkmapbhlhhvvsits.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

def print_success(message):
    """Affiche un message de succès"""
    print(f"✅ {message}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"❌ {message}")

def print_info(message):
    """Affiche un message d'info"""
    print(f"ℹ️  {message}")

def read_sql_file(filepath):
    """Lit un fichier SQL"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print_error(f"Fichier non trouvé: {filepath}")
        return None

def execute_sql(supabase: Client, sql_content):
    """Exécute du SQL via l'API REST Supabase"""
    try:
        # Supabase Python client ne supporte pas l'exécution SQL directe
        # Nous devons utiliser des requêtes HTTP
        import requests

        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }

        # Utiliser l'API PostgREST pour exécuter du SQL brut
        # Note: Ceci nécessite d'avoir activé l'extension pg_net dans Supabase
        print_info("Exécution du SQL via requête HTTP...")

        # Alternative: Utiliser l'API RPC de Supabase
        response = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        return True

    except Exception as e:
        print_error(f"Erreur lors de l'exécution SQL: {e}")
        return False

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🚀 INSTALLATION AUTOMATIQUE SUPABASE - GETYOURSHARE")
    print("="*60 + "\n")

    # Étape 1: Connexion à Supabase
    print_info("Connexion à Supabase...")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print_success("Connecté à Supabase")
    except Exception as e:
        print_error(f"Impossible de se connecter à Supabase: {e}")
        print_info("Installez le client Supabase: pip install supabase")
        sys.exit(1)

    # Étape 2: Lire le fichier SQL
    print_info("Lecture du fichier SQL de création des tables...")
    sql_file = "backend/create_subscription_tables.sql"
    sql_content = read_sql_file(sql_file)

    if not sql_content:
        print_error("Impossible de lire le fichier SQL")
        print_info("SOLUTION: Copiez manuellement le contenu de backend/create_subscription_tables.sql")
        print_info("          dans l'éditeur SQL de Supabase: https://app.supabase.com/project/iamezkmapbhlhhvvsits/editor")
        sys.exit(1)

    print_success(f"Fichier SQL lu ({len(sql_content)} caractères)")

    # Étape 3: Afficher les instructions manuelles (car l'API Python ne supporte pas l'exec SQL direct)
    print("\n" + "="*60)
    print("⚠️  ÉTAPE MANUELLE REQUISE")
    print("="*60)
    print("\nLe client Python Supabase ne permet pas l'exécution SQL directe.")
    print("Vous devez exécuter le SQL via le dashboard Supabase:\n")
    print("1. Ouvrez: https://app.supabase.com/project/iamezkmapbhlhhvvsits/editor")
    print("2. Cliquez sur 'New Query'")
    print("3. Copiez-collez le contenu de: backend/create_subscription_tables.sql")
    print("4. Cliquez sur 'Run'\n")
    print_info("Le fichier SQL est prêt dans: backend/create_subscription_tables.sql")

    # Proposer d'ouvrir le fichier
    print("\n" + "="*60)
    print("📄 CONTENU DU FICHIER SQL À COPIER")
    print("="*60 + "\n")

    print("Voulez-vous afficher le contenu SQL à copier? (o/n): ", end="")
    response = input().lower()

    if response == 'o' or response == 'oui' or response == 'y' or response == 'yes':
        print("\n" + "-"*60)
        print(sql_content)
        print("-"*60 + "\n")
        print_success("Copiez le contenu ci-dessus dans l'éditeur SQL Supabase")

    print("\n" + "="*60)
    print("✅ PROCHAINES ÉTAPES")
    print("="*60)
    print("\n1. Exécutez le SQL dans Supabase Dashboard")
    print("2. Vérifiez que les tables sont créées")
    print("3. Lancez: ./auto_deploy.sh")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
