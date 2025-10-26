from supabase_client import supabase
import json

print("🔍 Vérification du système d'affiliation unifié...")
print("=" * 60)

# 1. Vérifier si les fonctions SQL existent
print("\n1️⃣ Vérification des fonctions SQL...")
try:
    # Test d'appel de fonction (va échouer mais confirme l'existence)
    result = supabase.rpc('approve_affiliation_request', {
        'p_request_id': '00000000-0000-0000-0000-000000000000',
        'p_merchant_response': 'test',
        'p_reviewed_by': '00000000-0000-0000-0000-000000000000'
    }).execute()
    print("   ❌ Fonction appelée (erreur attendue car ID fictif)")
except Exception as e:
    error_msg = str(e)
    if "function" in error_msg.lower() and "does not exist" in error_msg.lower():
        print(f"   ❌ ERREUR: La fonction approve_affiliation_request n'existe pas!")
        print(f"      Message: {error_msg}")
    elif "non trouvée" in error_msg or "not found" in error_msg.lower():
        print("   ✅ Fonction approve_affiliation_request existe (erreur normale avec ID fictif)")
    else:
        print(f"   ⚠️  Erreur inattendue: {error_msg}")

# 2. Vérifier les colonnes de trackable_links
print("\n2️⃣ Vérification de la structure trackable_links...")
try:
    links = supabase.table('trackable_links').select('*').limit(1).execute()
    
    if links.data:
        columns = list(links.data[0].keys())
        required_columns = ['influencer_message', 'merchant_response', 'reviewed_at', 'reviewed_by', 'status']
        
        print(f"   Colonnes trouvées: {len(columns)}")
        
        for col in required_columns:
            if col in columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} - MANQUANTE!")
    else:
        print("   ⚠️  Aucun lien de tracking trouvé (table vide)")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 3. Vérifier les vues
print("\n3️⃣ Vérification des vues...")
try:
    # Vue merchant_affiliation_requests
    result = supabase.table('merchant_affiliation_requests').select('*').limit(1).execute()
    print(f"   ✅ merchant_affiliation_requests existe ({len(result.data) if result.data else 0} lignes)")
except Exception as e:
    print(f"   ❌ merchant_affiliation_requests: {e}")

try:
    # Vue affiliation_requests_stats
    result = supabase.table('affiliation_requests_stats').select('*').limit(1).execute()
    print(f"   ✅ affiliation_requests_stats existe ({len(result.data) if result.data else 0} lignes)")
except Exception as e:
    print(f"   ❌ affiliation_requests_stats: {e}")

# 4. Vérifier les demandes en attente
print("\n4️⃣ Demandes d'affiliation en attente...")
try:
    requests = supabase.table('trackable_links').select('*').eq('status', 'pending_approval').execute()
    
    if requests.data:
        print(f"   ✅ {len(requests.data)} demande(s) en attente trouvée(s)")
        
        for req in requests.data[:3]:  # Afficher les 3 premières
            print(f"\n   📄 Demande ID: {req['id'][:8]}...")
            print(f"      Influenceur: {req.get('influencer_id', 'N/A')[:8]}...")
            print(f"      Produit: {req.get('product_id', 'N/A')[:8]}...")
            print(f"      Message: {req.get('influencer_message', 'N/A')[:50]}...")
            print(f"      Créée le: {req.get('created_at', 'N/A')}")
    else:
        print("   ℹ️  Aucune demande en attente")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 60)
print("💡 Résultat:")
print("   Si des éléments sont marqués ❌, exécutez la migration:")
print("   database/migrations/modify_trackable_links_unified.sql")
print("\n   Via Supabase Dashboard > SQL Editor")
