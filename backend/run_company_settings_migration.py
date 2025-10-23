"""
Script pour exécuter la migration company_settings
"""
from supabase_client import supabase
import os

def run_migration():
    """Exécute la migration pour ajouter la table company_settings"""
    
    migration_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'database',
        'migrations',
        'add_company_settings.sql'
    )
    
    print("📄 Lecture du fichier de migration...")
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("🚀 Exécution de la migration company_settings...")
    
    try:
        # Supabase ne permet pas d'exécuter du SQL directement via l'API Python
        # Il faut utiliser l'interface SQL Editor de Supabase
        print("⚠️  Pour exécuter cette migration:")
        print("1. Ouvrez votre dashboard Supabase: https://supabase.com/dashboard")
        print("2. Allez dans 'SQL Editor'")
        print("3. Collez le contenu du fichier add_company_settings.sql")
        print("4. Cliquez sur 'Run'")
        print("")
        print("📋 Contenu SQL à exécuter:")
        print("="*60)
        print(sql)
        print("="*60)
        print("")
        print("✅ Une fois exécuté dans Supabase, les paramètres d'entreprise seront disponibles!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_migration()
