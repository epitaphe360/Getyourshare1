"""
Script pour activer la 2FA pour tous les utilisateurs
"""

from supabase_client import supabase

print("\n" + "=" * 60)
print("ACTIVATION DE LA 2FA POUR TOUS LES UTILISATEURS")
print("=" * 60 + "\n")

try:
    # 1. Récupérer tous les utilisateurs
    print("1. Récupération des utilisateurs...")
    users_response = supabase.table("users").select("id, email, role, two_fa_enabled").execute()

    if not users_response.data:
        print("   ERREUR: Aucun utilisateur trouvé dans la base de données")
        exit(1)

    print(f"   OK: {len(users_response.data)} utilisateurs trouvés\n")

    # 2. Afficher l'état actuel
    print("2. État actuel de la 2FA:")
    print("-" * 60)
    for user in users_response.data:
        status = "ACTIVEE" if user.get("two_fa_enabled") else "DESACTIVEE"
        print(f"   {user['email']:<35} | {status}")
    print()

    # 3. Activer la 2FA pour tous
    print("3. Activation de la 2FA pour tous les utilisateurs...")
    updated_count = 0

    for user in users_response.data:
        if not user.get("two_fa_enabled"):
            try:
                update_response = (
                    supabase.table("users")
                    .update({"two_fa_enabled": True})
                    .eq("id", user["id"])
                    .execute()
                )

                if update_response.data:
                    print(f"   OK: {user['email']}")
                    updated_count += 1
                else:
                    print(f"   ERREUR: {user['email']} - Aucune mise à jour")
            except Exception as e:
                print(f"   ERREUR: {user['email']} - {str(e)}")
        else:
            print(f"   SKIP: {user['email']} (déjà activée)")

    print()
    print("=" * 60)
    print(f"SUCCÈS: 2FA activée pour {updated_count} utilisateur(s)")
    print("=" * 60)
    print("\nVous pouvez maintenant vous connecter avec:")
    print("   Email: admin@shareyoursales.com")
    print("   Password: admin123")
    print("   Code 2FA: 123456")
    print()

except Exception as e:
    print(f"\nERREUR CRITIQUE: {str(e)}")
    import traceback

    traceback.print_exc()
    exit(1)
