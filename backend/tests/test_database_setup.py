"""
Configuration base de donnes de test avec Supabase RELLE
Remplace TOUS les mocks par des donnes relles
"""

import os
import asyncio
from uuid import uuid4
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


class TestDatabase:
    """Gestion de la base de donnes de test"""
    
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.test_data = {}
        
    async def setup(self):
        """Crer toutes les donnes de test dans la vraie DB"""
        print(" Configuration base de donnes de test...")
        
        # Nettoyer les anciennes donnes de test
        await self.cleanup()
        
        # Crer les donnes de test
        await self.create_test_users()
        await self.create_test_products()
        await self.create_test_trackable_links()
        await self.create_test_sales()
        await self.create_test_commissions()
        
        print(" Base de donnes de test prte!")
        return self.test_data
    
    async def cleanup(self):
        """Nettoyer les donnes de test"""
        print(" Nettoyage donnes de test...")
        
        try:
            # Supprimer dans l'ordre inverse des dpendances
            tables = ['commissions', 'sales', 'trackable_links', 'products', 'users']
            
            for table in tables:
                # Supprimer seulement les donnes de test (email contient 'test')
                if table == 'users':
                    self.client.table(table).delete().ilike('email', '%test%').execute()
                elif table in ['products', 'trackable_links', 'sales', 'commissions']:
                    # Supprimer par crateur test ou description test
                    try:
                        self.client.table(table).delete().ilike('name', '%TEST%').execute()
                    except:
                        pass
                        
        except Exception as e:
            print(f"  Erreur nettoyage: {e}")
    
    async def create_test_users(self):
        """Crer utilisateurs de test"""
        print(" Cration utilisateurs de test...")
        
        # Crer les users basiques d'abord
        users_basic = [
            {
                "id": str(uuid4()),
                "email": "influencer_test@example.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpWQhCRgD1GC",  # "password123"
                "role": "influencer",
            },
            {
                "id": str(uuid4()),
                "email": "merchant_test@example.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpWQhCRgD1GC",
                "role": "merchant",
            },
            {
                "id": str(uuid4()),
                "email": "admin_test@example.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpWQhCRgD1GC",
                "role": "admin",
            },
        ]
        
        for user in users_basic:
            try:
                result = self.client.table("users").insert(user).execute()
                if result.data:
                    self.test_data[f"user_{user['role']}"] = result.data[0]
                    user_id = result.data[0]['id']
                    print(f"   User {user['role']}: {user_id}")
                    
                    # Crer influencer profile si influencer
                    if user['role'] == 'influencer':
                        influencer_data = {
                            "user_id": user_id,
                            "username": "test_influencer",
                            "balance": 500.0,
                            "total_earnings": 1000.0,
                        }
                        inf_result = self.client.table("influencers").insert(influencer_data).execute()
                        if inf_result.data:
                            print(f"     Influencer profile cr")
                    
                    # Crer merchant profile si merchant
                    elif user['role'] == 'merchant':
                        merchant_data = {
                            "user_id": user_id,
                            "company_name": "TEST Company",
                        }
                        merch_result = self.client.table("merchants").insert(merchant_data).execute()
                        if merch_result.data:
                            print(f"     Merchant profile cr")
                            
            except Exception as e:
                print(f"    User {user['role']}: {e}")
    
    async def create_test_products(self):
        """Crer produits de test"""
        print(" Cration produits de test...")
        
        # Rcuprer le merchant profile (pas user!)
        merchant_user = self.test_data.get("user_merchant", {})
        if not merchant_user:
            print("    Pas de merchant user, skip produits")
            return
        
        # Trouver le merchant profile
        try:
            merchant_result = self.client.table("merchants").select("*").eq("user_id", merchant_user['id']).execute()
            if not merchant_result.data:
                print("    Pas de merchant profile, skip produits")
                return
            merchant_id = merchant_result.data[0]['id']
        except Exception as e:
            print(f"    Erreur rcupration merchant: {e}")
            return
        
        products = [
            {
                "id": str(uuid4()),
                "name": "TEST Product Premium",
                "description": "Produit de test premium",
                "price": 99.99,
                "merchant_id": merchant_id,
                "commission_rate": 15.0,
                "stock": 100,
                "is_active": True,
            },
            {
                "id": str(uuid4()),
                "name": "TEST Product Standard",
                "description": "Produit de test standard",
                "price": 49.99,
                "merchant_id": merchant_id,
                "commission_rate": 10.0,
                "stock": 50,
                "is_active": True,
            },
        ]
        
        for product in products:
            try:
                result = self.client.table("products").insert(product).execute()
                if result.data:
                    key = f"product_{product['name'].split()[-1].lower()}"
                    self.test_data[key] = result.data[0]
                    print(f"   Product: {result.data[0]['id']}")
            except Exception as e:
                print(f"    Product: {e}")
    
    async def create_test_trackable_links(self):
        """Crer liens de tracking de test"""
        print(" Cration tracking links de test...")
        
        # Rcuprer influencer profile
        influencer_user = self.test_data.get("user_influencer", {})
        if not influencer_user:
            print("    Pas d'influencer user, skip tracking")
            return
        
        try:
            inf_result = self.client.table("influencers").select("*").eq("user_id", influencer_user['id']).execute()
            if not inf_result.data:
                print("    Pas d'influencer profile, skip tracking")
                return
            influencer_id = inf_result.data[0]['id']
        except Exception as e:
            print(f"    Erreur rcupration influencer: {e}")
            return
        
        product_premium = self.test_data.get("product_premium")
        
        if not product_premium:
            print("    Donnes produit manquantes, skip tracking links")
            return
        
        links = [
            {
                "id": str(uuid4()),
                "unique_code": "TEST001",
                "full_url": f"https://example.com/product/{product_premium['id']}",
                "influencer_id": influencer_id,
                "product_id": product_premium['id'],
                "clicks": 150,
                "sales": 10,
                "is_active": True,
            },
        ]
        
        for link in links:
            try:
                result = self.client.table("trackable_links").insert(link).execute()
                if result.data:
                    self.test_data["tracking_link"] = result.data[0]
                    print(f"   Tracking link: {result.data[0]['id']}")
            except Exception as e:
                print(f"    Tracking link: {e}")
    
    async def create_test_sales(self):
        """Crer ventes de test"""
        print(" Cration ventes de test...")
        
        # Rcuprer les profiles
        influencer_user = self.test_data.get("user_influencer", {})
        merchant_user = self.test_data.get("user_merchant", {})
        
        if not influencer_user or not merchant_user:
            print("    Users manquants, skip sales")
            return
        
        try:
            # Influencer profile
            inf_result = self.client.table("influencers").select("*").eq("user_id", influencer_user['id']).execute()
            influencer_id = inf_result.data[0]['id'] if inf_result.data else None
            
            # Merchant profile
            merch_result = self.client.table("merchants").select("*").eq("user_id", merchant_user['id']).execute()
            merchant_id = merch_result.data[0]['id'] if merch_result.data else None
            
            if not influencer_id or not merchant_id:
                print("    Profiles manquants, skip sales")
                return
                
        except Exception as e:
            print(f"    Erreur rcupration profiles: {e}")
            return
        
        product_premium = self.test_data.get("product_premium")
        tracking_link = self.test_data.get("tracking_link")
        
        if not product_premium or not tracking_link:
            print("    Produit/link manquants, skip sales")
            return
        
        sales = [
            {
                "id": str(uuid4()),
                "amount": 99.99,
                "quantity": 1,
                "influencer_id": influencer_id,
                "merchant_id": merchant_id,
                "product_id": product_premium['id'],
                "link_id": tracking_link['id'],
                "influencer_commission": 14.99,  # 15% de 99.99
                "platform_commission": 0.75,  # 5% de 14.99
                "merchant_revenue": 84.25,  # 99.99 - 14.99 - 0.75
                "status": "completed",
                "payment_status": "paid",
            },
            {
                "id": str(uuid4()),
                "amount": 199.98,
                "quantity": 2,
                "influencer_id": influencer_id,
                "merchant_id": merchant_id,
                "product_id": product_premium['id'],
                "link_id": tracking_link['id'],
                "influencer_commission": 29.99,  # 15% de 199.98
                "platform_commission": 1.50,  # 5% de 29.99
                "merchant_revenue": 168.49,  # 199.98 - 29.99 - 1.50
                "status": "pending",
                "payment_status": "pending",
            },
        ]
        
        for sale in sales:
            try:
                result = self.client.table("sales").insert(sale).execute()
                if result.data:
                    key = f"sale_{sale['status']}"
                    self.test_data[key] = result.data[0]
                    print(f"   Sale {sale['status']}: {result.data[0]['id']}")
            except Exception as e:
                print(f"    Sale: {e}")
    
    async def create_test_commissions(self):
        """Crer commissions de test"""
        print(" Cration commissions de test...")
        
        # Rcuprer influencer profile
        influencer_user = self.test_data.get("user_influencer", {})
        if not influencer_user:
            print("    Pas d'influencer, skip commissions")
            return
        
        try:
            inf_result = self.client.table("influencers").select("*").eq("user_id", influencer_user['id']).execute()
            influencer_id = inf_result.data[0]['id'] if inf_result.data else None
            if not influencer_id:
                print("    Pas d'influencer profile, skip commissions")
                return
        except Exception as e:
            print(f"    Erreur rcupration influencer: {e}")
            return
        
        sale_completed = self.test_data.get("sale_completed")
        sale_pending = self.test_data.get("sale_pending")
        
        if not sale_completed or not sale_pending:
            print("    Sales manquantes, skip commissions")
            return
        
        commissions = [
            {
                "id": str(uuid4()),
                "amount": 14.99,  # 15% de 99.99
                "influencer_id": influencer_id,
                "sale_id": sale_completed['id'],
                "status": "paid",
            },
            {
                "id": str(uuid4()),
                "amount": 29.99,  # 15% de 199.98
                "influencer_id": influencer_id,
                "sale_id": sale_pending['id'],
                "status": "pending",
            },
        ]
        
        for commission in commissions:
            try:
                result = self.client.table("commissions").insert(commission).execute()
                if result.data:
                    key = f"commission_{commission['status']}"
                    self.test_data[key] = result.data[0]
                    print(f"   Commission {commission['status']}: {result.data[0]['id']}")
            except Exception as e:
                print(f"    Commission: {e}")
    
    def get_real_supabase_client(self):
        """Retourne le vrai client Supabase (pas de mock!)"""
        return self.client


# Instance globale
test_db = TestDatabase()


async def setup_test_database():
    """Setup  appeler au dbut des tests"""
    return await test_db.setup()


def get_test_data():
    """Rcuprer les donnes de test"""
    return test_db.test_data


def get_supabase_for_tests():
    """Rcuprer le client Supabase REL pour les tests"""
    return test_db.get_real_supabase_client()


if __name__ == "__main__":
    # Test du setup
    asyncio.run(setup_test_database())
    print("\n Donnes de test cres:")
    for key, value in test_db.test_data.items():
        print(f"  - {key}: {value.get('id', value)}")
