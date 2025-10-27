import requests
import json

# Test script pour vérifier le système d'affiliation unifié
BASE_URL = "http://localhost:8001"

def test_affiliation_stats():
    """Tester l'endpoint des statistiques d'affiliation"""
    try:
        # Note: En production, il faudrait un vrai token JWT
        headers = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }

        response = requests.get(f"{BASE_URL}/api/affiliation-requests/stats", headers=headers)
        print(f"Stats endpoint status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Stats endpoint fonctionne:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Erreur stats: {response.text}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_merchant_requests():
    """Tester l'endpoint des demandes de marchand"""
    try:
        headers = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }

        response = requests.get(f"{BASE_URL}/api/affiliation-requests/merchant", headers=headers)
        print(f"Merchant requests endpoint status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Merchant requests endpoint fonctionne:")
            print(f"Nombre de demandes: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"❌ Erreur merchant requests: {response.text}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    print("🧪 Test du système d'affiliation unifié")
    print("=" * 50)

    test_affiliation_stats()
    print()
    test_merchant_requests()

    print("\n✅ Tests terminés")
