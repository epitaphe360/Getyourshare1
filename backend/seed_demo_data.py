"""
========================================
SEED DEMO DATA - Populate Supabase avec données mockées
========================================
Ce script copie TOUTES les valeurs mockées des endpoints dans Supabase.
Utilise les mêmes données que celles hardcodées dans server_complete.py.

Exécution: python seed_demo_data.py
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import uuid
import bcrypt
from dotenv import load_dotenv

# Import Supabase client
from supabase_client import get_supabase_client

load_dotenv()

class DemoDataSeeder:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.created_ids = {
            'users': [],
            'merchants': [],
            'influencers': [],
            'products': [],
            'trackable_links': [],
            'sales': [],
            'commissions': [],
            'campaigns': []
        }
    
    def hash_password(self, password: str) -> str:
        """Hash un mot de passe avec bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # ==========================================
    # ÉTAPE 1: Créer les utilisateurs
    # ==========================================
    
    def create_users(self):
        """Créer 3 utilisateurs: admin, merchant, influencer"""
        print("\n📝 Création des utilisateurs...")
        
        users_data = [
            {
                "email": "admin@tracknow.io",
                "password_hash": self.hash_password("Admin123!"),
                "role": "admin",
                "is_active": True,
                "phone_verified": True,
                "two_fa_enabled": False,
                "created_at": (datetime.utcnow() - timedelta(days=365)).isoformat()
            },
            {
                "email": "merchant@beautymaroc.com",
                "password_hash": self.hash_password("Merchant123!"),
                "role": "merchant",
                "is_active": True,
                "phone_verified": True,
                "two_fa_enabled": False,
                "created_at": (datetime.utcnow() - timedelta(days=180)).isoformat()
            },
            {
                "email": "sarah@influencer.com",
                "password_hash": self.hash_password("Influencer123!"),
                "role": "influencer",
                "is_active": True,
                "phone_verified": True,
                "two_fa_enabled": False,
                "created_at": (datetime.utcnow() - timedelta(days=90)).isoformat()
            }
        ]
        
        for user_data in users_data:
            try:
                # Vérifier si l'user existe déjà
                existing = self.supabase.table("users").select("id").eq("email", user_data['email']).execute()
                if existing.data and len(existing.data) > 0:
                    user_id = existing.data[0]['id']
                    self.created_ids['users'].append(user_id)
                    print(f"  ⚠️  User existe déjà: {user_data['email']} (ID: {user_id})")
                else:
                    result = self.supabase.table("users").insert(user_data).execute()
                    user_id = result.data[0]['id']
                    self.created_ids['users'].append(user_id)
                    print(f"  ✅ User créé: {user_data['email']} (ID: {user_id}, Role: {user_data['role']})")
            except Exception as e:
                print(f"  ❌ Erreur création user {user_data['email']}: {e}")
        
        return self.created_ids['users']
    
    # ==========================================
    # ÉTAPE 2: Créer les merchants
    # ==========================================
    
    def create_merchants(self, user_ids: List[str]):
        """Créer 2 merchants avec profils complets"""
        print("\n🏢 Création des merchants...")
        
        # user_ids[1] est le merchant
        merchant_user_id = user_ids[1]
        
        merchants_data = [
            {
                "user_id": merchant_user_id,
                "company_name": "BeautyMaroc Premium",
                "industry": "Beauté et bien-être",
                "category": "Beauté et bien-être",
                "description": "Leader marocain des produits de beauté naturels et cosmétiques bio",
                "website": "https://beautymaroc.ma",
                "address": "123 Avenue Mohammed V, Casablanca",
                "tax_id": "MA123456789",
                "subscription_plan": "pro",
                "subscription_status": "active",
                "commission_rate": 5.00,
                "monthly_fee": 199.00,
                "created_at": (datetime.utcnow() - timedelta(days=180)).isoformat()
            }
        ]
        
        for merchant_data in merchants_data:
            try:
                result = self.supabase.table("merchants").insert(merchant_data).execute()
                merchant_id = result.data[0]['id']
                self.created_ids['merchants'].append(merchant_id)
                print(f"  ✅ Merchant créé: {merchant_data['company_name']} (ID: {merchant_id})")
            except Exception as e:
                print(f"  ❌ Erreur création merchant: {e}")
        
        return self.created_ids['merchants']
    
    # ==========================================
    # ÉTAPE 3: Créer les influencers
    # ==========================================
    
    def create_influencers(self, user_ids: List[str]):
        """Créer 1 influencer avec profil complet"""
        print("\n🌟 Création des influencers...")
        
        # user_ids[2] est l'influencer
        influencer_user_id = user_ids[2]
        
        influencers_data = [
            {
                "user_id": influencer_user_id,
                "username": "@sarah_beauty",
                "full_name": "Sarah Alami",
                "bio": "Passionnée de beauté naturelle 🌿 | Beauty & Lifestyle Influencer | Partenariats: dm",
                "profile_picture_url": "https://i.pravatar.cc/300?img=47",
                "category": "Beauty & Cosmetics",
                "influencer_type": "macro",
                "audience_size": 125000,
                "engagement_rate": 4.8,
                "subscription_plan": "pro",
                "subscription_status": "active",
                "platform_fee_rate": 5.00,
                "monthly_fee": 29.90,
                "social_links": '{"instagram": "@sarah_beauty", "tiktok": "@sarah.beauty", "youtube": "SarahBeautyVlog"}',
                "total_clicks": 12470,
                "total_sales": 245,
                "total_earnings": 18920.50,
                "balance": 2450.75,
                "payment_method": "bank_transfer",
                "payment_details": '{"bank_account": "MA00987654321098765432109876"}',
                "created_at": (datetime.utcnow() - timedelta(days=90)).isoformat()
            }
        ]
        
        for influencer_data in influencers_data:
            try:
                result = self.supabase.table("influencers").insert(influencer_data).execute()
                influencer_id = result.data[0]['id']
                self.created_ids['influencers'].append(influencer_id)
                print(f"  ✅ Influencer créé: {influencer_data['username']} (ID: {influencer_id}, {influencer_data['followers_count']} followers)")
            except Exception as e:
                print(f"  ❌ Erreur création influencer: {e}")
        
        return self.created_ids['influencers']
    
    # ==========================================
    # ÉTAPE 4: Créer les produits
    # ==========================================
    
    def create_products(self, merchant_ids: List[str]):
        """Créer 5 produits pour les merchants"""
        print("\n📦 Création des produits...")
        
        merchant_id = merchant_ids[0]
        
        # Produits mockés - colonnes adaptées au schema.sql
        products_data = [
            {
                "merchant_id": merchant_id,
                "name": "Huile d'Argan Bio Certifiée",
                "description": "Huile d'argan 100% pure et bio, pressée à froid. Idéale pour les cheveux et la peau.",
                "price": 180.00,
                "currency": "MAD",
                "category": "Beauté",
                "images": '["https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400"]',
                "stock_quantity": 150,
                "commission_rate": 15.00,
                "commission_type": "percentage",
                "is_available": True,
                "total_views": 3456,
                "total_clicks": 1247,
                "total_sales": 89,
                "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat()
            },
            {
                "merchant_id": merchant_id,
                "name": "Caftan Moderne Premium",
                "description": "Caftan marocain moderne en satin brodé. Parfait pour les grandes occasions.",
                "price": 890.00,
                "currency": "MAD",
                "category": "Mode",
                "images": '["https://images.unsplash.com/photo-1583391733981-5ade4c896b77?w=400"]',
                "stock_quantity": 25,
                "commission_rate": 12.00,
                "commission_type": "percentage",
                "is_available": True,
                "total_views": 1234,
                "total_clicks": 456,
                "total_sales": 12,
                "created_at": (datetime.utcnow() - timedelta(days=50)).isoformat()
            },
            {
                "merchant_id": merchant_id,
                "name": "Tajine en Céramique Artisanal",
                "description": "Tajine traditionnel fait main par des artisans de Fès. Diamètre 30cm.",
                "price": 320.00,
                "currency": "MAD",
                "category": "Artisanat",
                "images": '["https://images.unsplash.com/photo-1579027989536-b7b1f875659b?w=400"]',
                "stock_quantity": 50,
                "commission_rate": 18.00,
                "commission_type": "percentage",
                "is_available": True,
                "total_views": 2100,
                "total_clicks": 789,
                "total_sales": 34,
                "created_at": (datetime.utcnow() - timedelta(days=45)).isoformat()
            },
            {
                "merchant_id": merchant_id,
                "name": "Savon Noir Naturel",
                "description": "Savon noir beldi 100% naturel, idéal pour le hammam.",
                "price": 45.00,
                "currency": "MAD",
                "category": "Beauté",
                "images": '["https://images.unsplash.com/photo-1584305574647-0cc949a2bb9f?w=400"]',
                "stock_quantity": 200,
                "commission_rate": 20.00,
                "commission_type": "percentage",
                "is_available": True,
                "total_views": 5678,
                "total_clicks": 2340,
                "total_sales": 156,
                "created_at": (datetime.utcnow() - timedelta(days=40)).isoformat()
            },
            {
                "merchant_id": merchant_id,
                "name": "Babouches Marocaines Cuir",
                "description": "Babouches en cuir véritable, cousues main. Plusieurs couleurs disponibles.",
                "price": 250.00,
                "currency": "MAD",
                "category": "Mode",
                "images": '["https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400"]',
                "stock_quantity": 80,
                "commission_rate": 15.00,
                "commission_type": "percentage",
                "is_available": True,
                "total_views": 2890,
                "total_clicks": 1123,
                "total_sales": 67,
                "created_at": (datetime.utcnow() - timedelta(days=35)).isoformat()
            }
        ]
        
        for product_data in products_data:
            try:
                result = self.supabase.table("products").insert(product_data).execute()
                product_id = result.data[0]['id']
                self.created_ids['products'].append(product_id)
                print(f"  ✅ Produit créé: {product_data['name']} (ID: {product_id}, Prix: {product_data['price']} {product_data['currency']})")
            except Exception as e:
                print(f"  ❌ Erreur création produit {product_data['name']}: {e}")
        
        return self.created_ids['products']
    
    # ==========================================
    # ÉTAPE 5: Créer les liens d'affiliation
    # ==========================================
    
    def create_trackable_links(self, product_ids: List[str], influencer_ids: List[str]):
        """Créer des liens d'affiliation entre influencers et produits"""
        print("\n🔗 Création des liens d'affiliation...")
        
        influencer_id = influencer_ids[0]
        
        # Liens mockés du endpoint /api/affiliate-links - colonnes adaptées
        links_data = [
            {
                "product_id": product_ids[0],  # Huile d'Argan
                "influencer_id": influencer_id,
                "unique_code": "SARAH-ARGAN-2024",
                "short_url": "https://trck.now/argan-sarah",
                "full_url": f"https://tracknow.io/track?code=SARAH-ARGAN-2024&product={product_ids[0]}&influencer={influencer_id}",
                "clicks": 145,
                "unique_clicks": 98,
                "sales": 12,
                "conversion_rate": 8.28,
                "total_revenue": 2160.00,
                "total_commission": 324.00,
                "is_active": True,
                "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat()
            },
            {
                "product_id": product_ids[1],  # Caftan
                "influencer_id": influencer_id,
                "unique_code": "SARAH-CAFTAN-2024",
                "short_url": "https://trck.now/caftan-sarah",
                "full_url": f"https://tracknow.io/track?code=SARAH-CAFTAN-2024&product={product_ids[1]}&influencer={influencer_id}",
                "clicks": 89,
                "unique_clicks": 67,
                "sales": 5,
                "conversion_rate": 5.62,
                "total_revenue": 4450.00,
                "total_commission": 534.00,
                "is_active": True,
                "created_at": (datetime.utcnow() - timedelta(days=50)).isoformat()
            },
            {
                "product_id": product_ids[2],  # Tajine
                "influencer_id": influencer_id,
                "unique_code": "SARAH-TAJINE-2024",
                "short_url": "https://trck.now/tajine-sarah",
                "full_url": f"https://tracknow.io/track?code=SARAH-TAJINE-2024&product={product_ids[2]}&influencer={influencer_id}",
                "clicks": 67,
                "unique_clicks": 54,
                "sales": 8,
                "conversion_rate": 11.94,
                "total_revenue": 2560.00,
                "total_commission": 460.80,
                "is_active": True,
                "created_at": (datetime.utcnow() - timedelta(days=45)).isoformat()
            }
        ]
        
        for link_data in links_data:
            try:
                result = self.supabase.table("trackable_links").insert(link_data).execute()
                link_id = result.data[0]['id']
                self.created_ids['trackable_links'].append(link_id)
                print(f"  ✅ Lien créé: {link_data['unique_code']} (ID: {link_id}, {link_data['clicks']} clicks, {link_data['sales']} ventes)")
            except Exception as e:
                print(f"  ❌ Erreur création lien {link_data['unique_code']}: {e}")
        
        return self.created_ids['trackable_links']
    
    # ==========================================
    # ÉTAPE 6: Créer les ventes
    # ==========================================
    
    def create_sales(self, link_ids: List[str], product_ids: List[str], influencer_ids: List[str], merchant_ids: List[str]):
        """Créer des ventes réalistes sur les 60 derniers jours"""
        print("\n💰 Création des ventes...")
        
        influencer_id = influencer_ids[0]
        merchant_id = merchant_ids[0]
        
        # Générer 50 ventes sur 60 jours
        sales_count = 0
        for i in range(50):
            link_id = link_ids[i % len(link_ids)]
            product_id = product_ids[i % len(product_ids)]
            
            # Prix variés (simuler différents produits)
            prices = [180.00, 890.00, 320.00, 45.00, 250.00]
            amount = prices[i % len(prices)]
            
            commission_rates = [15.00, 12.00, 18.00, 20.00, 15.00]
            commission_rate = commission_rates[i % 5]
            influencer_commission = round(amount * commission_rate / 100, 2)
            platform_commission = round(amount * 5 / 100, 2)  # 5% pour la plateforme
            merchant_revenue = round(amount - influencer_commission - platform_commission, 2)
            
            sale_data = {
                "link_id": link_id,
                "product_id": product_id,
                "influencer_id": influencer_id,
                "merchant_id": merchant_id,
                "amount": amount,
                "currency": "MAD",
                "quantity": 1,
                "influencer_commission": influencer_commission,
                "platform_commission": platform_commission,
                "merchant_revenue": merchant_revenue,
                "status": "completed",
                "payment_status": "paid" if i % 3 == 0 else "pending",
                "customer_email": f"customer{i}@example.com",
                "sale_timestamp": (datetime.utcnow() - timedelta(days=60-i)).isoformat(),
                "created_at": (datetime.utcnow() - timedelta(days=60-i)).isoformat()
            }
            
            try:
                result = self.supabase.table("sales").insert(sale_data).execute()
                sale_id = result.data[0]['id']
                self.created_ids['sales'].append(sale_id)
                sales_count += 1
                
                # Créer la commission associée
                self.create_commission_for_sale(sale_id, sale_data, influencer_commission, commission_rate)
                
            except Exception as e:
                print(f"  ❌ Erreur création vente {i}: {e}")
        
        print(f"  ✅ {sales_count} ventes créées avec succès")
        return self.created_ids['sales']
    
    # ==========================================
    # ÉTAPE 7: Créer les commissions
    # ==========================================
    
    def create_commission_for_sale(self, sale_id: str, sale_data: Dict, commission_amount: float, commission_rate: float):
        """Créer une commission pour une vente"""
        # Statuts variés: 30% paid, 50% approved, 20% pending
        import random
        statuses = ['paid', 'paid', 'paid', 'approved', 'approved', 'approved', 'approved', 'approved', 'pending', 'pending']
        status = random.choice(statuses)
        
        commission_data = {
            "sale_id": sale_id,
            "influencer_id": sale_data['influencer_id'],
            "amount": commission_amount,
            "currency": sale_data['currency'],
            "status": status,
            "payment_method": "bank_transfer" if status == 'paid' else None,
            "paid_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat() if status == 'paid' else None,
            "created_at": sale_data['created_at']
        }
        
        try:
            result = self.supabase.table("commissions").insert(commission_data).execute()
            commission_id = result.data[0]['id']
            self.created_ids['commissions'].append(commission_id)
        except Exception as e:
            print(f"  ⚠️ Erreur création commission pour vente {sale_id}: {e}")
    
    # ==========================================
    # ÉTAPE 8: Créer les campagnes
    # ==========================================
    
    def create_campaigns(self, merchant_ids: List[str]):
        """Créer 3 campagnes marketing"""
        print("\n📢 Création des campagnes...")
        
        merchant_id = merchant_ids[0]
        
        campaigns_data = [
            {
                "merchant_id": merchant_id,
                "name": "Promo Ramadan 2024",
                "description": "Offres spéciales pour le mois sacré - jusqu'à -30%",
                "start_date": (datetime.utcnow() - timedelta(days=30)).date().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=30)).date().isoformat(),
                "budget": 5000.00,
                "spent": 1250.00,
                "target_audience": '{"age_range": "25-45", "gender": "all", "location": "Morocco"}',
                "status": "active",
                "total_clicks": 2340,
                "total_conversions": 78,
                "total_revenue": 12450.00,
                "roi": 149.00,
                "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat()
            },
            {
                "merchant_id": merchant_id,
                "name": "Black Friday Beauté",
                "description": "Réductions exceptionnelles sur tous les produits beauté",
                "start_date": (datetime.utcnow() + timedelta(days=5)).date().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=10)).date().isoformat(),
                "budget": 8000.00,
                "spent": 0.00,
                "target_audience": '{"age_range": "18-55", "gender": "all", "location": "Morocco"}',
                "status": "draft",
                "total_clicks": 0,
                "total_conversions": 0,
                "total_revenue": 0.00,
                "roi": 0.00,
                "created_at": (datetime.utcnow() - timedelta(days=15)).isoformat()
            },
            {
                "merchant_id": merchant_id,
                "name": "Été 2024 - Artisanat",
                "description": "Collection été des meilleurs artisans marocains",
                "start_date": (datetime.utcnow() - timedelta(days=90)).date().isoformat(),
                "end_date": (datetime.utcnow() - timedelta(days=10)).date().isoformat(),
                "budget": 3000.00,
                "spent": 2890.00,
                "target_audience": '{"age_range": "30-60", "interests": ["culture", "artisanat"], "location": "International"}',
                "status": "completed",
                "total_clicks": 4560,
                "total_conversions": 156,
                "total_revenue": 28900.00,
                "roi": 281.00,
                "created_at": (datetime.utcnow() - timedelta(days=90)).isoformat()
            }
        ]
        
        for campaign_data in campaigns_data:
            try:
                result = self.supabase.table("campaigns").insert(campaign_data).execute()
                campaign_id = result.data[0]['id']
                self.created_ids['campaigns'].append(campaign_id)
                print(f"  ✅ Campagne créée: {campaign_data['name']} (ID: {campaign_id}, Budget: {campaign_data['budget']} {campaign_data['currency']})")
            except Exception as e:
                print(f"  ❌ Erreur création campagne {campaign_data['name']}: {e}")
        
        return self.created_ids['campaigns']
    
    # ==========================================
    # MAIN: Exécuter tout le seeding
    # ==========================================
    
    def seed_all(self):
        """Exécuter tout le processus de seeding"""
        print("\n" + "="*60)
        print("🌱 DÉMARRAGE DU SEEDING - Données de démonstration")
        print("="*60)
        
        try:
            # Étape 1: Users
            user_ids = self.create_users()
            if len(user_ids) < 3:
                print("❌ Échec: Impossible de créer les users")
                return False
            
            # Étape 2: Merchants
            merchant_ids = self.create_merchants(user_ids)
            if len(merchant_ids) == 0:
                print("❌ Échec: Impossible de créer les merchants")
                return False
            
            # Étape 3: Influencers
            influencer_ids = self.create_influencers(user_ids)
            if len(influencer_ids) == 0:
                print("❌ Échec: Impossible de créer les influencers")
                return False
            
            # Étape 4: Products
            product_ids = self.create_products(merchant_ids)
            if len(product_ids) == 0:
                print("❌ Échec: Impossible de créer les produits")
                return False
            
            # Étape 5: Trackable Links
            link_ids = self.create_trackable_links(product_ids, influencer_ids)
            if len(link_ids) == 0:
                print("❌ Échec: Impossible de créer les liens")
                return False
            
            # Étape 6: Sales + Commissions
            sale_ids = self.create_sales(link_ids, product_ids, influencer_ids, merchant_ids)
            if len(sale_ids) == 0:
                print("❌ Échec: Impossible de créer les ventes")
                return False
            
            # Étape 7: Campaigns
            campaign_ids = self.create_campaigns(merchant_ids)
            
            # Résumé
            print("\n" + "="*60)
            print("✅ SEEDING TERMINÉ AVEC SUCCÈS!")
            print("="*60)
            print(f"\n📊 RÉSUMÉ:")
            print(f"  - {len(self.created_ids['users'])} utilisateurs créés")
            print(f"  - {len(self.created_ids['merchants'])} merchants créés")
            print(f"  - {len(self.created_ids['influencers'])} influencers créés")
            print(f"  - {len(self.created_ids['products'])} produits créés")
            print(f"  - {len(self.created_ids['trackable_links'])} liens d'affiliation créés")
            print(f"  - {len(self.created_ids['sales'])} ventes créées")
            print(f"  - {len(self.created_ids['commissions'])} commissions créées")
            print(f"  - {len(self.created_ids['campaigns'])} campagnes créées")
            
            print("\n🔐 COMPTES DE TEST:")
            print("  Admin:")
            print("    Email: admin@tracknow.io")
            print("    Password: Admin123!")
            print("\n  Merchant:")
            print("    Email: merchant@beautymaroc.com")
            print("    Password: Merchant123!")
            print("\n  Influencer:")
            print("    Email: sarah@influencer.com")
            print("    Password: Influencer123!")
            
            print("\n✅ Vous pouvez maintenant tester les endpoints avec ces comptes!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERREUR CRITIQUE: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("\n⚠️  ATTENTION: Ce script va insérer des données de démonstration dans Supabase")
    print("⚠️  Assurez-vous que votre .env contient les bonnes credentials Supabase\n")
    
    response = input("Voulez-vous continuer? (oui/non): ")
    if response.lower() in ['oui', 'yes', 'y', 'o']:
        seeder = DemoDataSeeder()
        success = seeder.seed_all()
        
        if success:
            print("\n🎉 Seeding terminé! Les endpoints sont maintenant connectés à de vraies données.")
            sys.exit(0)
        else:
            print("\n❌ Seeding échoué. Vérifiez les logs ci-dessus.")
            sys.exit(1)
    else:
        print("\n❌ Seeding annulé.")
        sys.exit(0)
