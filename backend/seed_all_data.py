"""
Script COMPLET pour peupler TOUTES les tables Supabase avec des données de test
Migre les données MOCK + ajoute des données de test supplémentaires
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta
import json
import random

# Charger les variables d'environnement
load_dotenv()

# Importer les données MOCK
sys.path.insert(0, os.path.dirname(__file__))
from mock_data import *

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Client Supabase avec droits admin
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("=" * 80)
print("🌱 SEED COMPLET - Toutes les Tables Supabase")
print("=" * 80)
print(f"📍 URL: {SUPABASE_URL}\n")

# Mappings pour stocker les IDs créés
user_ids = {}
merchant_ids = {}
influencer_ids = {}
product_ids = {}
link_ids = {}
campaign_ids = {}

# ============================================
# ÉTAPE 1: Migrer les USERS
# ============================================

print("📋 ÉTAPE 1: Migration des utilisateurs")
print("-" * 80)

for user in MOCK_USERS:
    try:
        user_data = {
            "email": user["email"],
            "password_hash": user["password"],
            "role": user["role"],
            "phone": user.get("phone"),
            "phone_verified": user.get("phone_verified", False),
            "two_fa_enabled": user.get("two_fa_enabled", False),
            "last_login": user.get("last_login"),
            "is_active": user.get("is_active", True)
        }

        result = supabase.table("users").insert(user_data).execute()

        if result.data:
            user_ids[user["email"]] = result.data[0]["id"]
            print(f"  ✅ {user['email']} ({user['role']})")

    except Exception as e:
        print(f"  ⚠️  {user['email']}: {str(e)}")

# ============================================
# ÉTAPE 2: Migrer les MERCHANTS
# ============================================

print("\n📋 ÉTAPE 2: Migration des merchants")
print("-" * 80)

merchant_emails = {
    "merchant_1": "contact@techstyle.fr",
    "merchant_2": "hello@beautypro.com"
}

for merchant in MOCK_MERCHANTS:
    try:
        email = merchant_emails.get(merchant["id"], "contact@techstyle.fr")
        user_id = user_ids.get(email)

        if not user_id:
            print(f"  ⚠️  User introuvable pour {merchant['company_name']}")
            continue

        merchant_data = {
            "user_id": user_id,
            "company_name": merchant["company_name"],
            "industry": merchant.get("industry"),
            "category": merchant.get("category"),
            "website": merchant.get("website"),
            "description": merchant.get("description"),
            "subscription_plan": merchant.get("subscription_plan", "free"),
            "commission_rate": merchant.get("commission_rate", 5.0),
            "total_sales": merchant.get("total_sales", 0),
            "total_commission_paid": merchant.get("total_commission_paid", 0)
        }

        result = supabase.table("merchants").insert(merchant_data).execute()

        if result.data:
            merchant_ids[merchant["id"]] = result.data[0]["id"]
            print(f"  ✅ {merchant['company_name']}")

    except Exception as e:
        print(f"  ❌ {merchant['company_name']}: {str(e)}")

# ============================================
# ÉTAPE 3: Migrer les INFLUENCERS
# ============================================

print("\n📋 ÉTAPE 3: Migration des influencers")
print("-" * 80)

influencer_emails = {
    "influencer_1": "emma.style@instagram.com",
    "influencer_2": "lucas.tech@youtube.com",
    "influencer_3": "julie.beauty@tiktok.com"
}

for influencer in MOCK_INFLUENCERS:
    try:
        email = influencer_emails.get(influencer["id"])
        user_id = user_ids.get(email)

        if not user_id:
            print(f"  ⚠️  User introuvable pour {influencer['full_name']}")
            continue

        influencer_data = {
            "user_id": user_id,
            "username": influencer["username"],
            "full_name": influencer["full_name"],
            "bio": influencer.get("bio"),
            "category": influencer.get("category"),
            "influencer_type": influencer.get("influencer_type"),
            "audience_size": influencer.get("audience_size", 0),
            "engagement_rate": influencer.get("engagement_rate", 0.0),
            "subscription_plan": influencer.get("subscription_plan", "starter"),
            "total_clicks": influencer.get("total_clicks", 0),
            "total_sales": influencer.get("total_sales", 0),
            "total_earnings": influencer.get("total_earnings", 0.0),
            "balance": influencer.get("balance", 0.0),
            "social_links": json.dumps(influencer.get("social_links", {}))
        }

        result = supabase.table("influencers").insert(influencer_data).execute()

        if result.data:
            influencer_ids[influencer["id"]] = result.data[0]["id"]
            print(f"  ✅ {influencer['full_name']} (@{influencer['username']})")

    except Exception as e:
        print(f"  ❌ {influencer['full_name']}: {str(e)}")

# ============================================
# ÉTAPE 4: Migrer les PRODUCTS
# ============================================

print("\n📋 ÉTAPE 4: Migration des produits")
print("-" * 80)

# Récupérer le premier merchant_id pour les produits
default_merchant_id = list(merchant_ids.values())[0] if merchant_ids else None

if not default_merchant_id:
    print("  ❌ Aucun merchant trouvé, impossible d'ajouter des produits")
else:
    for product in MOCK_PRODUCTS:
        try:
            product_data = {
                "merchant_id": default_merchant_id,
                "name": product["name"],
                "description": product.get("description"),
                "category": product["category"],
                "price": product["price"],
                "commission_rate": product["commission_rate"],
                "commission_type": "percentage",
                "images": json.dumps(product.get("images", [])),
                "slug": product.get("slug"),
                "stock_quantity": product.get("stock", 100),
                "is_available": product.get("is_available", True)
            }

            result = supabase.table("products").insert(product_data).execute()

            if result.data:
                product_ids[product["id"]] = result.data[0]["id"]
                print(f"  ✅ {product['name']} ({product['category']})")

        except Exception as e:
            print(f"  ⚠️  {product['name']}: {str(e)}")

# ============================================
# ÉTAPE 5: Créer des TRACKABLE LINKS
# ============================================

print("\n📋 ÉTAPE 5: Création de liens d'affiliation")
print("-" * 80)

if influencer_ids and product_ids:
    # Créer 10 liens d'affiliation
    import secrets

    influencer_list = list(influencer_ids.values())
    product_list = list(product_ids.values())

    for i in range(min(10, len(product_list))):
        try:
            unique_code = secrets.token_urlsafe(12)

            link_data = {
                "product_id": product_list[i % len(product_list)],
                "influencer_id": influencer_list[i % len(influencer_list)],
                "unique_code": unique_code,
                "full_url": f"https://shareyoursales.com/track/{unique_code}",
                "short_url": f"shs.io/{unique_code[:8]}",
                "clicks": random.randint(50, 500),
                "unique_clicks": random.randint(30, 400),
                "sales": random.randint(5, 50),
                "conversion_rate": round(random.uniform(2.0, 15.0), 2),
                "total_revenue": round(random.uniform(500, 5000), 2),
                "total_commission": round(random.uniform(50, 500), 2),
                "is_active": True
            }

            result = supabase.table("trackable_links").insert(link_data).execute()

            if result.data:
                link_ids[i] = result.data[0]["id"]
                print(f"  ✅ Lien {i+1}: {unique_code[:12]}... ({link_data['clicks']} clics)")

        except Exception as e:
            print(f"  ⚠️  Lien {i+1}: {str(e)}")

# ============================================
# ÉTAPE 6: Créer des CAMPAIGNS
# ============================================

print("\n📋 ÉTAPE 6: Création de campagnes")
print("-" * 80)

if merchant_ids:
    campaigns_data = [
        {"name": "Campagne Été 2024", "status": "active", "budget": 5000},
        {"name": "Black Friday 2024", "status": "active", "budget": 10000},
        {"name": "Rentrée Scolaire", "status": "paused", "budget": 3000},
        {"name": "Noël 2024", "status": "draft", "budget": 15000}
    ]

    default_merchant = list(merchant_ids.values())[0]

    for camp in campaigns_data:
        try:
            campaign_data = {
                "merchant_id": default_merchant,
                "name": camp["name"],
                "description": f"Description de {camp['name']}",
                "budget": camp["budget"],
                "spent": round(camp["budget"] * random.uniform(0.1, 0.8), 2),
                "status": camp["status"],
                "start_date": (datetime.now() - timedelta(days=30)).date().isoformat(),
                "end_date": (datetime.now() + timedelta(days=60)).date().isoformat(),
                "total_clicks": random.randint(1000, 5000),
                "total_conversions": random.randint(50, 500),
                "total_revenue": round(random.uniform(5000, 50000), 2),
                "roi": round(random.uniform(150, 400), 2)
            }

            result = supabase.table("campaigns").insert(campaign_data).execute()

            if result.data:
                campaign_ids[camp["name"]] = result.data[0]["id"]
                print(f"  ✅ {camp['name']} ({camp['status']})")

        except Exception as e:
            print(f"  ⚠️  {camp['name']}: {str(e)}")

# ============================================
# ÉTAPE 7: Créer des SALES
# ============================================

print("\n📋 ÉTAPE 7: Création de ventes")
print("-" * 80)

if link_ids and product_ids and influencer_ids and merchant_ids:
    link_list = list(link_ids.values())
    product_list = list(product_ids.values())
    influencer_list = list(influencer_ids.values())
    merchant_list = list(merchant_ids.values())

    for i in range(20):  # 20 ventes
        try:
            amount = round(random.uniform(50, 500), 2)
            commission_rate = random.uniform(10, 25)
            influencer_commission = round(amount * (commission_rate / 100), 2)
            platform_commission = round(amount * 0.05, 2)
            merchant_revenue = round(amount - influencer_commission - platform_commission, 2)

            sale_data = {
                "link_id": link_list[i % len(link_list)],
                "product_id": product_list[i % len(product_list)],
                "influencer_id": influencer_list[i % len(influencer_list)],
                "merchant_id": merchant_list[i % len(merchant_list)],
                "customer_email": f"customer{i}@example.com",
                "customer_name": f"Client Test {i}",
                "quantity": random.randint(1, 3),
                "amount": amount,
                "currency": "EUR",
                "influencer_commission": influencer_commission,
                "platform_commission": platform_commission,
                "merchant_revenue": merchant_revenue,
                "status": random.choice(["completed", "completed", "completed", "pending"]),
                "payment_status": "paid",
                "sale_timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            }

            result = supabase.table("sales").insert(sale_data).execute()

            if result.data:
                print(f"  ✅ Vente {i+1}: {amount}€ ({sale_data['status']})")

        except Exception as e:
            print(f"  ⚠️  Vente {i+1}: {str(e)}")

# ============================================
# ÉTAPE 8: Créer des COMMISSIONS
# ============================================

print("\n📋 ÉTAPE 8: Création de commissions")
print("-" * 80)

if influencer_ids:
    # Récupérer les sales
    sales_result = supabase.table("sales").select("*").limit(10).execute()

    for sale in sales_result.data:
        try:
            commission_data = {
                "sale_id": sale["id"],
                "influencer_id": sale["influencer_id"],
                "amount": sale["influencer_commission"],
                "currency": "EUR",
                "status": random.choice(["pending", "approved", "paid", "paid"]),
                "payment_method": random.choice(["PayPal", "Bank Transfer"]),
                "paid_at": datetime.now().isoformat() if random.choice([True, False]) else None
            }

            result = supabase.table("commissions").insert(commission_data).execute()

            if result.data:
                print(f"  ✅ Commission: {commission_data['amount']}€ ({commission_data['status']})")

        except Exception as e:
            print(f"  ⚠️  Commission: {str(e)}")

# ============================================
# ÉTAPE 9: Créer des CLICKS
# ============================================

print("\n📋 ÉTAPE 9: Création de clics")
print("-" * 80)

if link_ids:
    link_list = list(link_ids.values())

    for i in range(50):  # 50 clics
        try:
            click_data = {
                "link_id": link_list[i % len(link_list)],
                "ip_address": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                "user_agent": random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                ]),
                "referrer": random.choice([
                    "https://instagram.com",
                    "https://facebook.com",
                    "https://twitter.com",
                    "https://tiktok.com"
                ]),
                "country": random.choice(["FR", "BE", "CH", "CA"]),
                "city": random.choice(["Paris", "Lyon", "Marseille", "Bruxelles"]),
                "device_type": random.choice(["Mobile", "Desktop", "Tablet"]),
                "os": random.choice(["Windows", "iOS", "Android", "macOS"]),
                "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"]),
                "is_unique_visitor": random.choice([True, False]),
                "clicked_at": (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat()
            }

            result = supabase.table("click_tracking").insert(click_data).execute()

            if result.data and i % 10 == 0:
                print(f"  ✅ {i+1} clics créés...")

        except Exception as e:
            if i == 0:
                print(f"  ⚠️  Clic: {str(e)}")

    print(f"  ✅ Total: 50 clics créés")

# ============================================
# ÉTAPE 10: Créer des REVIEWS
# ============================================

print("\n📋 ÉTAPE 10: Création d'avis")
print("-" * 80)

if product_ids and user_ids:
    product_list = list(product_ids.values())
    user_list = list(user_ids.values())

    reviews_texts = [
        ("Excellent produit!", "Très satisfait de mon achat, je recommande vivement."),
        ("Bon rapport qualité/prix", "Produit conforme à la description, livraison rapide."),
        ("Parfait", "Exactement ce que je cherchais, merci!"),
        ("Déçu", "La qualité n'est pas au rendez-vous..."),
        ("Super!", "Je suis ravi, produit de qualité.")
    ]

    for i in range(min(15, len(product_list))):
        try:
            title, comment = random.choice(reviews_texts)

            review_data = {
                "product_id": product_list[i % len(product_list)],
                "user_id": user_list[i % len(user_list)] if user_list else None,
                "rating": random.randint(3, 5),
                "title": title,
                "comment": comment,
                "is_verified_purchase": random.choice([True, True, False]),
                "is_approved": True,
                "helpful_count": random.randint(0, 20)
            }

            result = supabase.table("reviews").insert(review_data).execute()

            if result.data:
                print(f"  ✅ Avis {i+1}: {review_data['rating']}⭐ - {title}")

        except Exception as e:
            print(f"  ⚠️  Avis {i+1}: {str(e)}")

# ============================================
# FINALISATION
# ============================================

print("\n" + "=" * 80)
print("✅ SEED COMPLET TERMINÉ !")
print("=" * 80)

# Compter les données créées
try:
    stats = {
        "users": supabase.table("users").select("id", count="exact").execute().count,
        "merchants": supabase.table("merchants").select("id", count="exact").execute().count,
        "influencers": supabase.table("influencers").select("id", count="exact").execute().count,
        "products": supabase.table("products").select("id", count="exact").execute().count,
        "trackable_links": supabase.table("trackable_links").select("id", count="exact").execute().count,
        "campaigns": supabase.table("campaigns").select("id", count="exact").execute().count,
        "sales": supabase.table("sales").select("id", count="exact").execute().count,
        "commissions": supabase.table("commissions").select("id", count="exact").execute().count,
        "click_tracking": supabase.table("click_tracking").select("id", count="exact").execute().count,
        "reviews": supabase.table("reviews").select("id", count="exact").execute().count,
    }

    print("\n📊 Données créées:")
    print(f"  ✅ {stats['users']} utilisateurs")
    print(f"  ✅ {stats['merchants']} merchants")
    print(f"  ✅ {stats['influencers']} influencers")
    print(f"  ✅ {stats['products']} produits")
    print(f"  ✅ {stats['trackable_links']} liens d'affiliation")
    print(f"  ✅ {stats['campaigns']} campagnes")
    print(f"  ✅ {stats['sales']} ventes")
    print(f"  ✅ {stats['commissions']} commissions")
    print(f"  ✅ {stats['click_tracking']} clics")
    print(f"  ✅ {stats['reviews']} avis")

except Exception as e:
    print(f"\n⚠️  Erreur lors du comptage: {e}")

print("""
🎉 Toutes les tables sont maintenant peuplées avec des données de test !

Prochaines étapes:
1. Démarrer le backend: python3 -m uvicorn server:app --reload
2. Démarrer le frontend: npm start
3. Se connecter avec: admin@shareyoursales.com / admin123

📊 Dashboard Supabase: https://iamezkmapbhlhhvvsits.supabase.co
""")
