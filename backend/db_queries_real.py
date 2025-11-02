"""
Helpers pour requêtes de base de données - Endpoints réels (non-mockés)
Remplace toutes les données statiques par des requêtes Supabase réelles
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from supabase_client import get_supabase_client

# ============================================
# ANALYTICS - INFLUENCER
# ============================================

async def get_influencer_overview_stats(user_id: str) -> Dict[str, Any]:
    """
    Récupère les statistiques globales pour un influenceur
    Balance, clics totaux, conversions, gains totaux, etc.
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer le profil influenceur
        influencer_response = supabase.table("influencers") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not influencer_response.data:
            return {
                "balance": 0.00,
                "total_clicks": 0,
                "total_sales": 0,
                "total_earnings": 0.00,
                "conversion_rate": 0.00,
                "active_links": 0
            }
        
        influencer = influencer_response.data
        influencer_id = influencer["id"]
        
        # Compter les liens actifs
        links_response = supabase.table("trackable_links") \
            .select("id", count="exact") \
            .eq("influencer_id", influencer_id) \
            .eq("is_active", True) \
            .execute()
        
        active_links = links_response.count if links_response.count else 0
        
        # Calculer le taux de conversion
        total_clicks = influencer.get("total_clicks", 0)
        total_sales = influencer.get("total_sales", 0)
        conversion_rate = (total_sales / total_clicks * 100) if total_clicks > 0 else 0.00
        
        return {
            "balance": float(influencer.get("balance", 0.00)),
            "total_clicks": total_clicks,
            "total_sales": total_sales,
            "total_earnings": float(influencer.get("total_earnings", 0.00)),
            "conversion_rate": round(conversion_rate, 2),
            "active_links": active_links
        }
    
    except Exception as e:
        print(f"❌ Erreur get_influencer_overview_stats: {str(e)}")
        return {
            "balance": 0.00,
            "total_clicks": 0,
            "total_sales": 0,
            "total_earnings": 0.00,
            "conversion_rate": 0.00,
            "active_links": 0
        }


async def get_influencer_earnings_chart(user_id: str, weeks: int = 4) -> List[Dict[str, Any]]:
    """
    Graphique des gains d'un influenceur sur les dernières semaines
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer l'influencer_id
        influencer_response = supabase.table("influencers") \
            .select("id") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not influencer_response.data:
            return []
        
        influencer_id = influencer_response.data["id"]
        
        # Date de début (X semaines en arrière)
        start_date = datetime.now() - timedelta(weeks=weeks)
        
        # Récupérer les commissions des dernières semaines
        commissions_response = supabase.table("commissions") \
            .select("amount, created_at") \
            .eq("influencer_id", influencer_id) \
            .gte("created_at", start_date.isoformat()) \
            .order("created_at") \
            .execute()
        
        # Agréger par semaine
        weekly_data = {}
        for commission in commissions_response.data:
            created_at = datetime.fromisoformat(commission["created_at"].replace("Z", "+00:00"))
            week_num = created_at.isocalendar()[1]  # Numéro de semaine
            week_label = f"Sem {week_num}"
            
            if week_label not in weekly_data:
                weekly_data[week_label] = 0.0
            
            weekly_data[week_label] += float(commission["amount"])
        
        # Formater pour le graphique
        chart_data = [
            {"week": week, "earnings": round(amount, 2)}
            for week, amount in sorted(weekly_data.items())
        ]
        
        return chart_data if chart_data else [{"week": "Sem 1", "earnings": 0}]
    
    except Exception as e:
        print(f"❌ Erreur get_influencer_earnings_chart: {str(e)}")
        return [{"week": f"Sem {i+1}", "earnings": 0} for i in range(weeks)]


# ============================================
# ANALYTICS - MERCHANT
# ============================================

async def get_merchant_sales_chart(user_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Graphique des ventes d'un marchand sur les derniers jours
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer merchant_id
        merchant_response = supabase.table("merchants") \
            .select("id") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not merchant_response.data:
            return []
        
        merchant_id = merchant_response.data["id"]
        
        # Date de début
        start_date = datetime.now() - timedelta(days=days-1)
        
        # Récupérer les ventes
        sales_response = supabase.table("sales") \
            .select("amount, sale_timestamp") \
            .eq("merchant_id", merchant_id) \
            .gte("sale_timestamp", start_date.isoformat()) \
            .execute()
        
        # Agréger par jour
        daily_data = {}
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%d/%m")
            daily_data[date_str] = {"ventes": 0, "revenus": 0.00}
        
        for sale in sales_response.data:
            sale_date = datetime.fromisoformat(sale["sale_timestamp"].replace("Z", "+00:00"))
            date_str = sale_date.strftime("%d/%m")
            
            if date_str in daily_data:
                daily_data[date_str]["ventes"] += 1
                daily_data[date_str]["revenus"] += float(sale["amount"])
        
        # Formater pour le graphique
        chart_data = [
            {
                "date": date,
                "ventes": data["ventes"],
                "revenus": round(data["revenus"], 2)
            }
            for date, data in daily_data.items()
        ]
        
        return chart_data
    
    except Exception as e:
        print(f"❌ Erreur get_merchant_sales_chart: {str(e)}")
        return [
            {"date": (datetime.now() - timedelta(days=i)).strftime("%d/%m"), "ventes": 0, "revenus": 0}
            for i in range(days)
        ]


# ============================================
# LIENS D'AFFILIATION
# ============================================

async def get_user_affiliate_links(user_id: str) -> List[Dict[str, Any]]:
    """
    Récupère tous les liens d'affiliation d'un influenceur
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer influencer_id
        influencer_response = supabase.table("influencers") \
            .select("id") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not influencer_response.data:
            return []
        
        influencer_id = influencer_response.data["id"]
        
        # Récupérer les liens avec les infos produits
        links_response = supabase.table("trackable_links") \
            .select("""
                *,
                products:product_id (
                    name,
                    price,
                    category,
                    images
                )
            """) \
            .eq("influencer_id", influencer_id) \
            .order("created_at", desc=True) \
            .execute()
        
        # Formater les données
        links = []
        for link in links_response.data:
            product = link.get("products", {})
            links.append({
                "id": link["id"],
                "product_name": product.get("name", "Produit inconnu"),
                "product_price": float(product.get("price", 0)),
                "category": product.get("category", "Autre"),
                "unique_code": link["unique_code"],
                "full_url": link["full_url"],
                "short_url": link.get("short_url"),
                "clicks": link.get("clicks", 0),
                "sales": link.get("sales", 0),
                "conversion_rate": float(link.get("conversion_rate", 0.00)),
                "total_commission": float(link.get("total_commission", 0.00)),
                "is_active": link.get("is_active", True),
                "created_at": link.get("created_at")
            })
        
        return links
    
    except Exception as e:
        print(f"❌ Erreur get_user_affiliate_links: {str(e)}")
        return []


# ============================================
# PAIEMENTS & HISTORIQUE
# ============================================

async def get_payment_history(user_id: str) -> Dict[str, Any]:
    """
    Historique des paiements pour un influenceur
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer influencer
        influencer_response = supabase.table("influencers") \
            .select("id, balance, total_earnings") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not influencer_response.data:
            return {"payments": [], "total_earned": 0.00, "pending_amount": 0.00}
        
        influencer = influencer_response.data
        influencer_id = influencer["id"]
        
        # Récupérer les commissions payées
        commissions_response = supabase.table("commissions") \
            .select("*") \
            .eq("influencer_id", influencer_id) \
            .eq("status", "paid") \
            .order("paid_at", desc=True) \
            .limit(20) \
            .execute()
        
        # Formater l'historique
        payments = []
        for comm in commissions_response.data:
            payments.append({
                "id": comm["id"],
                "amount": float(comm["amount"]),
                "currency": comm.get("currency", "EUR"),
                "status": "completed",
                "method": comm.get("payment_method", "bank_transfer"),
                "description": f"Commission {datetime.fromisoformat(comm['paid_at'].replace('Z', '+00:00')).strftime('%B %Y')}",
                "date": comm.get("paid_at"),
                "transaction_id": comm.get("transaction_id")
            })
        
        # Calculer pending (commissions approved mais non payées)
        pending_response = supabase.table("commissions") \
            .select("amount") \
            .eq("influencer_id", influencer_id) \
            .eq("status", "approved") \
            .execute()
        
        pending_amount = sum(float(c["amount"]) for c in pending_response.data)
        
        return {
            "payments": payments,
            "total_earned": float(influencer.get("total_earnings", 0.00)),
            "pending_amount": pending_amount,
            "balance": float(influencer.get("balance", 0.00))
        }
    
    except Exception as e:
        print(f"❌ Erreur get_payment_history: {str(e)}")
        return {"payments": [], "total_earned": 0.00, "pending_amount": 0.00, "balance": 0.00}


# ============================================
# PRODUITS
# ============================================

async def get_merchant_products(user_id: str) -> List[Dict[str, Any]]:
    """
    Récupère tous les produits d'un marchand
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer merchant_id
        merchant_response = supabase.table("merchants") \
            .select("id") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not merchant_response.data:
            return []
        
        merchant_id = merchant_response.data["id"]
        
        # Récupérer les produits
        products_response = supabase.table("products") \
            .select("*") \
            .eq("merchant_id", merchant_id) \
            .order("created_at", desc=True) \
            .execute()
        
        # Formater les produits
        products = []
        for prod in products_response.data:
            products.append({
                "id": prod["id"],
                "name": prod["name"],
                "description": prod.get("description"),
                "category": prod.get("category"),
                "price": float(prod["price"]),
                "currency": prod.get("currency", "EUR"),
                "commission_rate": float(prod["commission_rate"]),
                "stock": prod.get("stock_quantity", 0),
                "status": "active" if prod.get("is_available") else "inactive",
                "images": prod.get("images", []),
                "total_views": prod.get("total_views", 0),
                "total_clicks": prod.get("total_clicks", 0),
                "total_sales": prod.get("total_sales", 0),
                "created_at": prod.get("created_at")
            })
        
        return products
    
    except Exception as e:
        print(f"❌ Erreur get_merchant_products: {str(e)}")
        return []


# ============================================
# PAYOUTS
# ============================================

async def get_user_payouts(user_id: str) -> List[Dict[str, Any]]:
    """
    Liste des demandes de payout d'un influenceur
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer influencer_id
        influencer_response = supabase.table("influencers") \
            .select("id") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not influencer_response.data:
            return []
        
        influencer_id = influencer_response.data["id"]
        
        # Récupérer les payouts (table à créer si elle n'existe pas)
        # Pour l'instant, on utilise les commissions avec status = "paid"
        payouts_response = supabase.table("commissions") \
            .select("*") \
            .eq("influencer_id", influencer_id) \
            .in_("status", ["approved", "paid"]) \
            .order("created_at", desc=True) \
            .limit(10) \
            .execute()
        
        payouts = []
        for payout in payouts_response.data:
            payouts.append({
                "id": payout["id"],
                "amount": float(payout["amount"]),
                "status": payout["status"],
                "method": payout.get("payment_method", "bank_transfer"),
                "date": payout.get("paid_at") or payout.get("created_at")
            })
        
        return payouts
    
    except Exception as e:
        print(f"❌ Erreur get_user_payouts: {str(e)}")
        return []
