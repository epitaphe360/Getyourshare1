from supabase_client import supabase
import json

# Vérifier les utilisateurs et leur statut 2FA
print("🔍 Vérification de la configuration 2FA...")
print("=" * 50)

result = supabase.table('users').select('email, two_fa_enabled, role').execute()

if result.data:
    print(f"\n✅ Trouvé {len(result.data)} utilisateurs:\n")
    for user in result.data:
        two_fa_status = "✅ Activée" if user.get('two_fa_enabled') else "❌ Désactivée"
        print(f"  Email: {user['email']}")
        print(f"  Rôle: {user['role']}")
        print(f"  2FA: {two_fa_status}")
        print()
else:
    print("❌ Aucun utilisateur trouvé")

print("\n💡 Solution pour activer la 2FA:")
print("   Exécutez update_2fa.py pour activer la 2FA pour tous les utilisateurs")
