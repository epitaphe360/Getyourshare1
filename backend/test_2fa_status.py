import sys
sys.path.insert(0, 'C:\\Users\\Admin\\Desktop\\shareyoursales\\Getyourshare1\\backend')

try:
    from supabase_client import supabase
    
    print("🔍 Test du statut 2FA...")
    print("=" * 60)
    
    # Vérifier l'utilisateur admin
    result = supabase.table('users').select('email, two_fa_enabled').eq('email', 'admin@shareyoursales.com').execute()
    
    if result.data:
        user = result.data[0]
        print(f"✅ Utilisateur trouvé: {user['email']}")
        print(f"   2FA activée: {user.get('two_fa_enabled', False)}")
        
        if not user.get('two_fa_enabled'):
            print("\n⚠️ 2FA n'est PAS activée! Activation...")
            update_result = supabase.table('users').update({'two_fa_enabled': True}).eq('email', 'admin@shareyoursales.com').execute()
            print("✅ 2FA activée avec succès!")
    else:
        print("❌ Utilisateur non trouvé")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
