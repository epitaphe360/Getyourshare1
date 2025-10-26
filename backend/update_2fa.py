from supabase_client import supabase

print("🔧 Activation de la 2FA pour tous les utilisateurs...")
print("=" * 60)

# Activer la 2FA pour tous les utilisateurs
try:
    # Mettre à jour tous les utilisateurs
    result = supabase.table('users').update({
        'two_fa_enabled': True
    }).neq('id', '00000000-0000-0000-0000-000000000000').execute()  # Update tous sauf un ID fictif
    
    if result.data:
        print(f"✅ 2FA activée pour {len(result.data)} utilisateurs")
        
        # Afficher les utilisateurs mis à jour
        users = supabase.table('users').select('email, role, two_fa_enabled').execute()
        
        print("\n📋 État actuel des utilisateurs:")
        print("-" * 60)
        
        for user in users.data:
            two_fa_icon = "✅" if user.get('two_fa_enabled') else "❌"
            print(f"{two_fa_icon} {user['email']:<35} | Rôle: {user['role']:<12} | 2FA: {user.get('two_fa_enabled')}")
        
        print("\n" + "=" * 60)
        print("✅ Configuration terminée!")
        print("\n💡 Vous pouvez maintenant vous connecter avec:")
        print("   - Code 2FA: 123456 (pour tous les comptes)")
        
    else:
        print("⚠️ Aucune mise à jour effectuée")
        print("\n💡 Essayons une approche différente...")
        
        # Récupérer tous les utilisateurs
        all_users = supabase.table('users').select('id, email, role').execute()
        
        if all_users.data:
            print(f"\nMise à jour individuelle de {len(all_users.data)} utilisateurs...")
            updated_count = 0
            
            for user in all_users.data:
                try:
                    update_result = supabase.table('users').update({
                        'two_fa_enabled': True
                    }).eq('id', user['id']).execute()
                    
                    if update_result.data:
                        print(f"  ✅ {user['email']}")
                        updated_count += 1
                    else:
                        print(f"  ⚠️ {user['email']} (pas de changement)")
                        
                except Exception as e:
                    print(f"  ❌ {user['email']}: {e}")
            
            print(f"\n✅ {updated_count} utilisateurs mis à jour avec succès!")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\n💡 Vérifiez que:")
    print("   1. La colonne 'two_fa_enabled' existe dans la table 'users'")
    print("   2. Vous avez les permissions nécessaires")
    print("   3. La connexion Supabase est fonctionnelle")
