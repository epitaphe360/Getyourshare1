"""
Script de test pour les nouveaux endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8001"


def test_login():
    """Test de connexion"""
    print("\n🔐 Test de connexion...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@shareyoursales.com", "password": "Admin123!"},
    )
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"✅ Connexion réussie - Token obtenu")
        return token
    else:
        print(f"❌ Erreur de connexion: {response.status_code}")
        print(response.text)
        return None


def test_products(token):
    """Test des endpoints produits"""
    headers = {"Authorization": f"Bearer {token}"}

    print("\n📦 Test GET /api/products...")
    response = requests.get(f"{BASE_URL}/api/products", headers=headers)
    if response.status_code == 200:
        products = response.json()
        print(f"✅ {len(products)} produits trouvés")
        if products:
            print(f"   Premier produit: {products[0].get('name', 'N/A')}")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")


def test_campaigns(token):
    """Test des endpoints campagnes"""
    headers = {"Authorization": f"Bearer {token}"}

    print("\n🎯 Test GET /api/campaigns...")
    response = requests.get(f"{BASE_URL}/api/campaigns", headers=headers)
    if response.status_code == 200:
        campaigns = response.json()
        print(f"✅ {len(campaigns)} campagnes trouvées")
        if campaigns:
            print(f"   Première campagne: {campaigns[0].get('name', 'N/A')}")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")


def test_sales(token):
    """Test des endpoints ventes"""
    headers = {"Authorization": f"Bearer {token}"}

    print("\n💰 Test GET /api/sales/1...")
    response = requests.get(f"{BASE_URL}/api/sales/1", headers=headers)
    if response.status_code == 200:
        sales = response.json()
        print(f"✅ {len(sales)} ventes trouvées pour l'influenceur 1")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")


def test_commissions(token):
    """Test des endpoints commissions"""
    headers = {"Authorization": f"Bearer {token}"}

    print("\n💵 Test GET /api/commissions/1...")
    response = requests.get(f"{BASE_URL}/api/commissions/1", headers=headers)
    if response.status_code == 200:
        commissions = response.json()
        print(f"✅ {len(commissions)} commissions trouvées pour l'influenceur 1")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")


def test_reports(token):
    """Test des endpoints rapports"""
    headers = {"Authorization": f"Bearer {token}"}

    print("\n📊 Test GET /api/reports/performance...")
    response = requests.get(
        f"{BASE_URL}/api/reports/performance",
        headers=headers,
        params={"user_id": 1, "start_date": "2024-01-01", "end_date": "2025-12-31"},
    )
    if response.status_code == 200:
        report = response.json()
        print(f"✅ Rapport généré:")
        print(f"   Total ventes: {report.get('total_sales', 0)}")
        print(f"   Revenus: {report.get('total_revenue', 0)}€")
        print(f"   Commissions: {report.get('total_commission', 0)}€")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")


def test_settings(token):
    """Test des endpoints paramètres"""
    headers = {"Authorization": f"Bearer {token}"}

    print("\n⚙️  Test GET /api/settings...")
    response = requests.get(f"{BASE_URL}/api/settings", headers=headers)
    if response.status_code == 200:
        settings = response.json()
        print(f"✅ {len(settings)} paramètres trouvés")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")


def main():
    print("=" * 60)
    print("🧪 TEST DES NOUVEAUX ENDPOINTS")
    print("=" * 60)

    # Test de connexion
    token = test_login()
    if not token:
        print("\n❌ Impossible de continuer sans token")
        return

    # Tests des différents endpoints
    test_products(token)
    test_campaigns(token)
    test_sales(token)
    test_commissions(token)
    test_reports(token)
    test_settings(token)

    print("\n" + "=" * 60)
    print("✅ Tests terminés")
    print("=" * 60)


if __name__ == "__main__":
    main()
