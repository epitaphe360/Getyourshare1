"""
Fonctions avancées pour la gestion complète de la plateforme
Ajout des fonctionnalités CRUD complètes
"""

from supabase_client import supabase
from typing import Optional, List, Dict, Any
from datetime import datetime
import secrets

# ============================================
# PRODUCTS - CRUD COMPLET
# ============================================

def create_product(merchant_id: str, name: str, price: float, commission_rate: float, **kwargs) -> Optional[Dict]:
    """Crée un nouveau produit"""
    try:
        product_data = {
            "merchant_id": merchant_id,
            "name": name,
            "description": kwargs.get("description"),
            "category": kwargs.get("category", "Autre"),
            "price": price,
            "commission_rate": commission_rate,
            "commission_type": kwargs.get("commission_type", "percentage"),
            "images": kwargs.get("images", []),
            "slug": kwargs.get("slug", name.lower().replace(" ", "-")),
            "stock_quantity": kwargs.get("stock_quantity", 0),
            "is_available": kwargs.get("is_available", True),
            "sku": kwargs.get("sku"),
            "weight": kwargs.get("weight"),
            "dimensions": kwargs.get("dimensions")
        }

        result = supabase.table("products").insert(product_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating product: {e}")
        return None

def update_product(product_id: str, updates: Dict) -> bool:
    """Met à jour un produit"""
    try:
        updates["updated_at"] = datetime.now().isoformat()
        supabase.table("products").update(updates).eq("id", product_id).execute()
        return True
    except Exception as e:
        print(f"Error updating product: {e}")
        return False

def delete_product(product_id: str) -> bool:
    """Supprime un produit (soft delete)"""
    try:
        supabase.table("products").update({
            "is_available": False,
            "deleted_at": datetime.now().isoformat()
        }).eq("id", product_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting product: {e}")
        return False

# ============================================
# CAMPAIGNS - CRUD COMPLET
# ============================================

def update_campaign(campaign_id: str, updates: Dict) -> bool:
    """Met à jour une campagne"""
    try:
        updates["updated_at"] = datetime.now().isoformat()
        supabase.table("campaigns").update(updates).eq("id", campaign_id).execute()
        return True
    except Exception as e:
        print(f"Error updating campaign: {e}")
        return False

def delete_campaign(campaign_id: str) -> bool:
    """Supprime une campagne"""
    try:
        supabase.table("campaigns").update({
            "status": "archived",
            "deleted_at": datetime.now().isoformat()
        }).eq("id", campaign_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting campaign: {e}")
        return False

def assign_products_to_campaign(campaign_id: str, product_ids: List[str]) -> bool:
    """Assigne des produits à une campagne"""
    try:
        # Créer une table de liaison si elle n'existe pas déjà
        assignments = [
            {"campaign_id": campaign_id, "product_id": pid}
            for pid in product_ids
        ]
        
        # Note: nécessite une table campaign_products
        # supabase.table("campaign_products").insert(assignments).execute()
        return True
    except Exception as e:
        print(f"Error assigning products: {e}")
        return False

# ============================================
# AFFILIATE INVITATIONS
# ============================================

def create_invitation(merchant_id: str, email: str, **kwargs) -> Optional[Dict]:
    """Crée une invitation pour un affilié"""
    try:
        invitation_code = secrets.token_urlsafe(32)
        
        invitation_data = {
            "merchant_id": merchant_id,
            "email": email,
            "invitation_code": invitation_code,
            "status": "pending",
            "message": kwargs.get("message"),
            "commission_rate": kwargs.get("commission_rate"),
            "expires_at": kwargs.get("expires_at"),
        }

        result = supabase.table("invitations").insert(invitation_data).execute()
        
        # TODO: Envoyer l'email d'invitation
        # send_invitation_email(email, invitation_code)
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating invitation: {e}")
        return None

def accept_invitation(invitation_code: str, user_id: str) -> bool:
    """Accepte une invitation"""
    try:
        # Vérifier l'invitation
        result = supabase.table("invitations").select("*").eq("invitation_code", invitation_code).execute()
        
        if not result.data:
            return False
        
        invitation = result.data[0]
        
        # Créer le profil influencer
        influencer_data = {
            "user_id": user_id,
            "merchant_id": invitation["merchant_id"],
            "status": "active"
        }
        
        supabase.table("influencers").insert(influencer_data).execute()
        
        # Marquer l'invitation comme acceptée
        supabase.table("invitations").update({
            "status": "accepted",
            "accepted_at": datetime.now().isoformat()
        }).eq("invitation_code", invitation_code).execute()
        
        return True
    except Exception as e:
        print(f"Error accepting invitation: {e}")
        return False

# ============================================
# COMMISSION MANAGEMENT
# ============================================

def calculate_commission(sale_amount: float, commission_rate: float, commission_type: str = "percentage") -> float:
    """Calcule le montant de la commission"""
    if commission_type == "percentage":
        return round(sale_amount * (commission_rate / 100), 2)
    elif commission_type == "fixed":
        return commission_rate
    return 0.0

def create_sale(link_id: str, product_id: str, influencer_id: str, merchant_id: str, amount: float, **kwargs) -> Optional[Dict]:
    """Crée une nouvelle vente et calcule les commissions"""
    try:
        # Récupérer le taux de commission du produit
        payload = {
            "p_link_id": link_id,
            "p_product_id": product_id,
            "p_influencer_id": influencer_id,
            "p_merchant_id": merchant_id,
            "p_amount": amount,
            "p_currency": kwargs.get("currency", "EUR"),
            "p_quantity": kwargs.get("quantity", 1),
            "p_customer_email": kwargs.get("customer_email"),
            "p_customer_name": kwargs.get("customer_name"),
            "p_payment_status": kwargs.get("payment_status", "pending"),
            "p_status": kwargs.get("status", "completed"),
            "p_metadata": kwargs.get("metadata")
        }

        result = supabase.rpc("create_sale_transaction", payload).execute()

        if not result.data:
            return None

        sale_data = result.data if isinstance(result.data, dict) else result.data[0]
        return sale_data
    except Exception as e:
        print(f"Error creating sale: {e}")
        return None

def update_link_stats(link_id: str, revenue: float, commission: float):
    """Met à jour les statistiques d'un lien d'affiliation"""
    try:
        link = supabase.table("trackable_links").select("sales, total_revenue, total_commission").eq("id", link_id).execute()
        
        if link.data:
            current_sales = link.data[0].get("sales", 0)
            current_revenue = link.data[0].get("total_revenue", 0)
            current_commission = link.data[0].get("total_commission", 0)
            
            supabase.table("trackable_links").update({
                "sales": current_sales + 1,
                "total_revenue": round(current_revenue + revenue, 2),
                "total_commission": round(current_commission + commission, 2)
            }).eq("id", link_id).execute()
    except Exception as e:
        print(f"Error updating link stats: {e}")

# ============================================
# PAYOUT REQUESTS
# ============================================

def create_payout_request(influencer_id: str, amount: float, payment_method: str) -> Optional[Dict]:
    """Crée une demande de paiement"""
    try:
        # Vérifier le solde disponible
        influencer = supabase.table("influencers").select("balance").eq("id", influencer_id).execute()
        
        if not influencer.data or influencer.data[0]["balance"] < amount:
            return None
        
        payout_data = {
            "influencer_id": influencer_id,
            "amount": amount,
            "currency": "EUR",
            "payment_method": payment_method,
            "status": "pending"
        }

        result = supabase.table("commissions").insert(payout_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating payout request: {e}")
        return None

def approve_payout(payout_id: str) -> bool:
    """Approuve une demande de paiement"""
    try:
        result = supabase.rpc("approve_payout_transaction", {
            "p_commission_id": payout_id,
            "p_status": "approved"
        }).execute()
        data = result.data
        if isinstance(data, list):
            return bool(data and data[0])
        return bool(data)
    except Exception as e:
        print(f"Error approving payout: {e}")
        return False

# ============================================
# TRACKING ADVANCED
# ============================================

def record_click(link_id: str, ip_address: str, user_agent: str, **kwargs) -> Optional[Dict]:
    """Enregistre un clic sur un lien d'affiliation"""
    try:
        click_data = {
            "link_id": link_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "referrer": kwargs.get("referrer"),
            "country": kwargs.get("country"),
            "city": kwargs.get("city"),
            "device_type": kwargs.get("device_type"),
            "os": kwargs.get("os"),
            "browser": kwargs.get("browser"),
            "is_unique_visitor": kwargs.get("is_unique_visitor", False),
            "clicked_at": datetime.now().isoformat()
        }

        result = supabase.table("click_tracking").insert(click_data).execute()
        
        # Incrémenter le compteur de clics du lien
        link = supabase.table("trackable_links").select("clicks, unique_clicks").eq("id", link_id).execute()
        
        if link.data:
            new_clicks = link.data[0]["clicks"] + 1
            new_unique = link.data[0]["unique_clicks"] + (1 if kwargs.get("is_unique_visitor") else 0)
            
            supabase.table("trackable_links").update({
                "clicks": new_clicks,
                "unique_clicks": new_unique
            }).eq("id", link_id).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error recording click: {e}")
        return None

# ============================================
# REPORTS & ANALYTICS
# ============================================

def get_performance_report(influencer_id: str, start_date: str, end_date: str) -> Dict:
    """Génère un rapport de performance pour un influencer"""
    try:
        # Récupérer les ventes dans la période
        sales = supabase.table("sales").select("*").eq("influencer_id", influencer_id).gte("sale_timestamp", start_date).lte("sale_timestamp", end_date).execute()
        
        # Récupérer les clics
        links = supabase.table("trackable_links").select("id").eq("influencer_id", influencer_id).execute()
        link_ids = [link["id"] for link in links.data] if links.data else []
        
        total_clicks = 0
        if link_ids:
            clicks = supabase.table("click_tracking").select("id", count="exact").in_("link_id", link_ids).gte("clicked_at", start_date).lte("clicked_at", end_date).execute()
            total_clicks = clicks.count or 0
        
        # Calculer les métriques
        total_sales = len(sales.data) if sales.data else 0
        total_revenue = sum([sale["amount"] for sale in sales.data]) if sales.data else 0
        total_commission = sum([sale["influencer_commission"] for sale in sales.data]) if sales.data else 0
        
        conversion_rate = round((total_sales / total_clicks * 100), 2) if total_clicks > 0 else 0
        
        return {
            "period": {"start": start_date, "end": end_date},
            "clicks": total_clicks,
            "sales": total_sales,
            "revenue": total_revenue,
            "commission": total_commission,
            "conversion_rate": conversion_rate,
            "average_order_value": round(total_revenue / total_sales, 2) if total_sales > 0 else 0
        }
    except Exception as e:
        print(f"Error generating report: {e}")
        return {}

# ============================================
# SETTINGS & CONFIGURATION
# ============================================

def get_platform_settings() -> Dict:
    """Récupère les paramètres de la plateforme"""
    try:
        result = supabase.table("settings").select("*").execute()
        
        if result.data:
            return {item["key"]: item["value"] for item in result.data}
        
        # Valeurs par défaut
        return {
            "default_currency": "EUR",
            "platform_commission": 5.0,
            "min_payout": 50.0,
            "default_commission_rate": 10.0
        }
    except Exception as e:
        print(f"Error getting settings: {e}")
        return {}

def update_platform_setting(key: str, value: Any) -> bool:
    """Met à jour un paramètre de la plateforme"""
    try:
        # Vérifier si le paramètre existe
        existing = supabase.table("settings").select("id").eq("key", key).execute()
        
        if existing.data:
            supabase.table("settings").update({"value": value}).eq("key", key).execute()
        else:
            supabase.table("settings").insert({"key": key, "value": value}).execute()
        
        return True
    except Exception as e:
        print(f"Error updating setting: {e}")
        return False

# ============================================
# USER MANAGEMENT ADVANCED
# ============================================

def update_user_profile(user_id: str, updates: Dict) -> bool:
    """Met à jour le profil d'un utilisateur"""
    try:
        updates["updated_at"] = datetime.now().isoformat()
        supabase.table("users").update(updates).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False

def deactivate_user(user_id: str) -> bool:
    """Désactive un utilisateur"""
    try:
        supabase.table("users").update({
            "is_active": False,
            "deactivated_at": datetime.now().isoformat()
        }).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error deactivating user: {e}")
        return False
