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


# ============================================
# CAMPAIGNS
# ============================================

async def get_user_campaigns(user_id: str) -> List[Dict[str, Any]]:
    """
    Liste des campagnes d'un merchant
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
        
        # Récupérer les campagnes
        campaigns_response = supabase.table("campaigns") \
            .select("*") \
            .eq("merchant_id", merchant_id) \
            .order("created_at", desc=True) \
            .execute()
        
        campaigns = []
        for campaign in campaigns_response.data:
            campaigns.append({
                "id": campaign["id"],
                "name": campaign["name"],
                "description": campaign.get("description", ""),
                "budget": float(campaign.get("budget", 0)),
                "spent": float(campaign.get("spent", 0)),
                "start_date": campaign.get("start_date"),
                "end_date": campaign.get("end_date"),
                "status": campaign.get("status", "draft"),
                "total_clicks": campaign.get("total_clicks", 0),
                "total_conversions": campaign.get("total_conversions", 0),
                "total_revenue": float(campaign.get("total_revenue", 0)),
                "roi": float(campaign.get("roi", 0)),
                "created_at": campaign.get("created_at")
            })
        
        return campaigns
    
    except Exception as e:
        print(f"❌ Erreur get_user_campaigns: {str(e)}")
        return []


# ============================================
# AFFILIATE LINKS - CREATE
# ============================================

async def create_affiliate_link(
    product_id: str, 
    influencer_id: str, 
    custom_code: str = None,
    commission_rate: float = None
) -> Dict[str, Any]:
    """
    Créer un lien d'affiliation pour un produit et un influenceur
    """
    try:
        supabase = get_supabase_client()
        
        # Générer un code unique si non fourni
        if not custom_code:
            import secrets
            custom_code = f"LINK-{secrets.token_urlsafe(8).upper()}"
        
        # Récupérer les infos du produit pour le commission_rate par défaut
        product_response = supabase.table("products") \
            .select("commission_rate, name") \
            .eq("id", product_id) \
            .single() \
            .execute()
        
        if not product_response.data:
            return {"success": False, "error": "Product not found"}
        
        product = product_response.data
        final_commission_rate = commission_rate if commission_rate else product.get("commission_rate", 15.00)
        
        # Construire les URLs
        full_url = f"https://tracknow.io/track?code={custom_code}&product={product_id}&influencer={influencer_id}"
        short_url = f"https://trck.now/{custom_code}"
        
        # Insérer le lien dans la table
        link_data = {
            "product_id": product_id,
            "influencer_id": influencer_id,
            "unique_code": custom_code,
            "full_url": full_url,
            "short_url": short_url,
            "is_active": True
        }
        
        link_response = supabase.table("trackable_links") \
            .insert(link_data) \
            .execute()
        
        if not link_response.data:
            return {"success": False, "error": "Failed to create link"}
        
        created_link = link_response.data[0]
        
        return {
            "success": True,
            "link": {
                "id": created_link["id"],
                "product_id": product_id,
                "product_name": product.get("name"),
                "unique_code": custom_code,
                "short_url": short_url,
                "full_url": full_url,
                "commission_rate": final_commission_rate,
                "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?data={short_url}",
                "status": "active",
                "created_at": created_link.get("created_at")
            }
        }
    
    except Exception as e:
        print(f"❌ Erreur create_affiliate_link: {str(e)}")
        return {"success": False, "error": str(e)}


# ============================================
# PRODUCTS - GET ALL WITH FILTERS
# ============================================

async def get_all_products(
    category: str = None,
    search: str = None,
    min_price: float = None,
    max_price: float = None,
    sort_by: str = "created_at",
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Récupérer la liste de tous les produits avec filtres
    """
    try:
        supabase = get_supabase_client()
        
        # Base query
        query = supabase.table("products").select("*")
        
        # Filtrer par catégorie
        if category:
            query = query.eq("category", category)
        
        # Filtrer par prix
        if min_price is not None:
            query = query.gte("price", min_price)
        if max_price is not None:
            query = query.lte("price", max_price)
        
        # Recherche textuelle (simple)
        if search:
            query = query.ilike("name", f"%{search}%")
        
        # Tri
        if sort_by == "price_asc":
            query = query.order("price", desc=False)
        elif sort_by == "price_desc":
            query = query.order("price", desc=True)
        elif sort_by == "popularity":
            query = query.order("total_sales", desc=True)
        else:
            query = query.order("created_at", desc=True)
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        products_response = query.execute()
        
        # Compter le total (sans pagination)
        count_query = supabase.table("products").select("id", count="exact")
        if category:
            count_query = count_query.eq("category", category)
        if min_price is not None:
            count_query = count_query.gte("price", min_price)
        if max_price is not None:
            count_query = count_query.lte("price", max_price)
        
        count_response = count_query.execute()
        total = count_response.count if count_response.count else 0
        
        # Formater les produits
        products = []
        for product in products_response.data:
            products.append({
                "id": product["id"],
                "name": product["name"],
                "description": product.get("description", ""),
                "price": float(product["price"]),
                "category": product.get("category", ""),
                "commission_rate": float(product.get("commission_rate", 0)),
                "commission_type": product.get("commission_type", "percentage"),
                "images": product.get("images", []),
                "stock": product.get("stock", 0),
                "total_views": product.get("total_views", 0),
                "total_clicks": product.get("total_clicks", 0),
                "total_sales": product.get("total_sales", 0),
                "rating": product.get("rating", 0),
                "created_at": product.get("created_at")
            })
        
        return {
            "products": products,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }
    
    except Exception as e:
        print(f"❌ Erreur get_all_products: {str(e)}")
        return {
            "products": [],
            "pagination": {"total": 0, "limit": limit, "offset": offset, "has_more": False}
        }


# ============================================
# MERCHANTS - GET ALL
# ============================================

async def get_all_merchants() -> List[Dict[str, Any]]:
    """
    Récupérer la liste de tous les marchands
    """
    try:
        supabase = get_supabase_client()
        
        # Query merchants avec JOIN sur users pour avoir les infos de base
        merchants_response = supabase.table("merchants") \
            .select("*, users(id, email, created_at)") \
            .order("created_at", desc=True) \
            .execute()
        
        merchants = []
        for merchant in merchants_response.data:
            user_data = merchant.get("users", {})
            
            merchants.append({
                "id": merchant["id"],
                "user_id": merchant["user_id"],
                "email": user_data.get("email", ""),
                "company_name": merchant.get("company_name", ""),
                "industry": merchant.get("industry", ""),
                "category": merchant.get("category", ""),
                "subscription_plan": merchant.get("subscription_plan", "free"),
                "commission_rate": float(merchant.get("commission_rate", 0)),
                "balance": float(merchant.get("balance", 0)),
                "total_revenue": float(merchant.get("total_revenue", 0)),
                "total_sales": merchant.get("total_sales", 0),
                "created_at": user_data.get("created_at") or merchant.get("created_at")
            })
        
        return merchants
    
    except Exception as e:
        print(f"❌ Erreur get_all_merchants: {str(e)}")
        return []


# ============================================
# INFLUENCERS - GET ALL
# ============================================

async def get_all_influencers(
    min_followers: int = None,
    category: str = None
) -> List[Dict[str, Any]]:
    """
    Récupérer la liste de tous les influenceurs avec filtres
    """
    try:
        supabase = get_supabase_client()
        
        # Query influencers avec JOIN sur users
        query = supabase.table("influencers") \
            .select("*, users(id, email, created_at)")
        
        # Filtrer par catégorie
        if category:
            query = query.eq("category", category)
        
        # Filtrer par nombre de followers
        if min_followers:
            query = query.gte("audience_size", min_followers)
        
        query = query.order("total_earnings", desc=True)
        
        influencers_response = query.execute()
        
        influencers = []
        for influencer in influencers_response.data:
            user_data = influencer.get("users", {})
            
            influencers.append({
                "id": influencer["id"],
                "user_id": influencer["user_id"],
                "email": user_data.get("email", ""),
                "username": influencer.get("username", ""),
                "full_name": influencer.get("full_name", ""),
                "bio": influencer.get("bio", ""),
                "category": influencer.get("category", ""),
                "influencer_type": influencer.get("influencer_type", ""),
                "audience_size": influencer.get("audience_size", 0),
                "engagement_rate": float(influencer.get("engagement_rate", 0)),
                "social_links": influencer.get("social_links", {}),
                "balance": float(influencer.get("balance", 0)),
                "total_earnings": float(influencer.get("total_earnings", 0)),
                "total_clicks": influencer.get("total_clicks", 0),
                "total_conversions": influencer.get("total_conversions", 0),
                "created_at": user_data.get("created_at") or influencer.get("created_at")
            })
        
        return influencers
    
    except Exception as e:
        print(f"❌ Erreur get_all_influencers: {str(e)}")
        return []


# ============================================
# PRODUCTS - CREATE NEW
# ============================================

async def create_product(merchant_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Créer un nouveau produit pour un merchant
    """
    try:
        supabase = get_supabase_client()
        
        # Préparer les données du produit
        product_insert = {
            "merchant_id": merchant_id,
            "name": product_data.get("name"),
            "description": product_data.get("description", ""),
            "price": float(product_data.get("price", 0)),
            "category": product_data.get("category", ""),
            "commission_rate": float(product_data.get("commission_rate", 10)),
            "commission_type": product_data.get("commission_type", "percentage"),
            "images": product_data.get("images", []),
            "stock": product_data.get("stock", 0),
            "is_active": product_data.get("is_active", True)
        }
        
        # Insérer le produit
        product_response = supabase.table("products") \
            .insert(product_insert) \
            .execute()
        
        created_product = product_response.data[0]
        
        return {
            "success": True,
            "product": {
                "id": created_product["id"],
                "name": created_product["name"],
                "description": created_product.get("description", ""),
                "price": float(created_product["price"]),
                "category": created_product.get("category", ""),
                "commission_rate": float(created_product.get("commission_rate", 0)),
                "images": created_product.get("images", []),
                "stock": created_product.get("stock", 0),
                "is_active": created_product.get("is_active", True),
                "created_at": created_product.get("created_at")
            }
        }
    
    except Exception as e:
        print(f"❌ Erreur create_product: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# MERCHANT PERFORMANCE
# ============================================

async def get_merchant_performance(user_id: str) -> Dict[str, Any]:
    """
    Récupérer les métriques de performance d'un merchant
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer le merchant_id
        merchant_response = supabase.table("merchants") \
            .select("id, total_revenue, total_sales") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        merchant_id = merchant_response.data["id"]
        total_revenue = float(merchant_response.data.get("total_revenue", 0))
        total_sales = merchant_response.data.get("total_sales", 0)
        
        # Récupérer les stats des produits
        products_response = supabase.table("products") \
            .select("total_views, total_clicks, total_sales") \
            .eq("merchant_id", merchant_id) \
            .execute()
        
        total_views = sum(p.get("total_views", 0) for p in products_response.data)
        total_clicks = sum(p.get("total_clicks", 0) for p in products_response.data)
        product_sales = sum(p.get("total_sales", 0) for p in products_response.data)
        
        # Calculer le taux de conversion
        conversion_rate = (product_sales / total_clicks * 100) if total_clicks > 0 else 0
        
        # Calculer le taux d'engagement (clicks / views)
        engagement_rate = (total_clicks / total_views * 100) if total_views > 0 else 0
        
        # Récupérer les ventes récentes pour calculer la satisfaction
        sales_response = supabase.table("sales") \
            .select("status") \
            .eq("merchant_id", merchant_id) \
            .execute()
        
        completed_sales = len([s for s in sales_response.data if s.get("status") == "completed"])
        total_sales_count = len(sales_response.data)
        satisfaction_rate = (completed_sales / total_sales_count * 100) if total_sales_count > 0 else 0
        
        # Calculer la progression vers l'objectif mensuel (objectif fictif de 50000 MAD)
        monthly_goal = 50000
        monthly_goal_progress = (total_revenue / monthly_goal * 100) if monthly_goal > 0 else 0
        
        return {
            "conversion_rate": round(conversion_rate, 2),
            "engagement_rate": round(engagement_rate, 2),
            "satisfaction_rate": round(satisfaction_rate, 1),
            "monthly_goal_progress": round(monthly_goal_progress, 1),
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "total_views": total_views,
            "total_clicks": total_clicks
        }
    
    except Exception as e:
        print(f"❌ Erreur get_merchant_performance: {str(e)}")
        return {
            "conversion_rate": 0,
            "engagement_rate": 0,
            "satisfaction_rate": 0,
            "monthly_goal_progress": 0
        }


# ============================================
# SALES - GET ALL
# ============================================

async def get_all_sales(
    user_id: str,
    user_role: str,
    status: str = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Récupérer les ventes d'un utilisateur (merchant ou influencer)
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("sales").select("*, products(name), trackable_links(unique_code)")
        
        # Filtrer selon le rôle
        if user_role == "merchant":
            # Récupérer le merchant_id
            merchant_response = supabase.table("merchants") \
                .select("id") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            merchant_id = merchant_response.data["id"]
            query = query.eq("merchant_id", merchant_id)
        
        elif user_role == "influencer":
            # Récupérer l'influencer_id
            influencer_response = supabase.table("influencers") \
                .select("id") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            influencer_id = influencer_response.data["id"]
            query = query.eq("influencer_id", influencer_id)
        
        # Filtrer par statut
        if status:
            query = query.eq("status", status)
        
        # Pagination et tri
        query = query.order("sale_timestamp", desc=True).range(offset, offset + limit - 1)
        
        sales_response = query.execute()
        
        # Formater les ventes
        sales = []
        for sale in sales_response.data:
            product_data = sale.get("products", {})
            link_data = sale.get("trackable_links", {})
            
            sales.append({
                "id": sale["id"],
                "product_name": product_data.get("name", ""),
                "tracking_code": link_data.get("unique_code", ""),
                "amount": float(sale.get("amount", 0)),
                "influencer_commission": float(sale.get("influencer_commission", 0)),
                "platform_commission": float(sale.get("platform_commission", 0)),
                "merchant_revenue": float(sale.get("merchant_revenue", 0)),
                "status": sale.get("status", "pending"),
                "payment_status": sale.get("payment_status", "pending"),
                "sale_timestamp": sale.get("sale_timestamp"),
                "created_at": sale.get("created_at")
            })
        
        # Compter le total
        count_query = supabase.table("sales").select("id", count="exact")
        if user_role == "merchant":
            count_query = count_query.eq("merchant_id", merchant_id)
        elif user_role == "influencer":
            count_query = count_query.eq("influencer_id", influencer_id)
        if status:
            count_query = count_query.eq("status", status)
        
        count_response = count_query.execute()
        total = count_response.count if count_response.count else 0
        
        return {
            "sales": sales,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        print(f"❌ Erreur get_all_sales: {str(e)}")
        return {
            "sales": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }


# ============================================
# NOTIFICATIONS - GET ALL
# ============================================

async def get_user_notifications(
    user_id: str,
    unread_only: bool = False
) -> Dict[str, Any]:
    """
    Récupérer les notifications d'un utilisateur
    Note: Table notifications peut ne pas exister, retourne données basiques
    """
    try:
        supabase = get_supabase_client()
        
        # Vérifier si la table notifications existe
        query = supabase.table("notifications").select("*").eq("user_id", user_id)
        
        if unread_only:
            query = query.eq("read", False)
        
        query = query.order("created_at", desc=True).limit(50)
        
        notifications_response = query.execute()
        
        notifications = []
        for notif in notifications_response.data:
            notifications.append({
                "id": notif["id"],
                "type": notif.get("type", "info"),
                "title": notif.get("title", ""),
                "message": notif.get("message", ""),
                "read": notif.get("read", False),
                "timestamp": notif.get("created_at"),
                "action_url": notif.get("action_url", "")
            })
        
        unread_count = len([n for n in notifications if not n["read"]])
        
        return {
            "notifications": notifications,
            "unread_count": unread_count
        }
    
    except Exception as e:
        print(f"❌ Erreur get_user_notifications (table peut ne pas exister): {str(e)}")
        # Retourner notifications système par défaut
        return {
            "notifications": [
                {
                    "id": "sys_1",
                    "type": "system",
                    "title": "Bienvenue sur TrackNow",
                    "message": "Votre compte a été créé avec succès!",
                    "read": False,
                    "timestamp": datetime.now().isoformat(),
                    "action_url": "/dashboard"
                }
            ],
            "unread_count": 1
        }


# ============================================
# TOP PRODUCTS ANALYTICS
# ============================================

async def get_top_products(
    merchant_id: str = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Récupérer les produits les plus performants
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("products").select("*")
        
        if merchant_id:
            query = query.eq("merchant_id", merchant_id)
        
        # Trier par total_sales décroissant
        query = query.order("total_sales", desc=True).limit(limit)
        
        products_response = query.execute()
        
        products = []
        for product in products_response.data:
            products.append({
                "id": product["id"],
                "name": product["name"],
                "category": product.get("category", ""),
                "price": float(product.get("price", 0)),
                "total_sales": product.get("total_sales", 0),
                "total_revenue": float(product.get("price", 0)) * product.get("total_sales", 0),
                "total_clicks": product.get("total_clicks", 0),
                "conversion_rate": (product.get("total_sales", 0) / product.get("total_clicks", 1) * 100) if product.get("total_clicks", 0) > 0 else 0
            })
        
        return products
    
    except Exception as e:
        print(f"❌ Erreur get_top_products: {str(e)}")
        return []


# ============================================
# CONVERSION FUNNEL ANALYTICS
# ============================================

async def get_conversion_funnel(user_id: str, user_role: str) -> Dict[str, Any]:
    """
    Récupérer les données du tunnel de conversion
    """
    try:
        supabase = get_supabase_client()
        
        if user_role == "merchant":
            # Récupérer le merchant_id
            merchant_response = supabase.table("merchants") \
                .select("id") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            merchant_id = merchant_response.data["id"]
            
            # Stats des produits
            products_response = supabase.table("products") \
                .select("total_views, total_clicks, total_sales") \
                .eq("merchant_id", merchant_id) \
                .execute()
            
            total_views = sum(p.get("total_views", 0) for p in products_response.data)
            total_clicks = sum(p.get("total_clicks", 0) for p in products_response.data)
            total_sales = sum(p.get("total_sales", 0) for p in products_response.data)
            
        elif user_role == "influencer":
            # Récupérer l'influencer_id
            influencer_response = supabase.table("influencers") \
                .select("id, total_clicks, total_conversions") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            
            total_clicks = influencer_response.data.get("total_clicks", 0)
            total_sales = influencer_response.data.get("total_conversions", 0)
            
            # Estimer les views (3x les clicks)
            total_views = total_clicks * 3
        
        else:
            total_views = 0
            total_clicks = 0
            total_sales = 0
        
        # Calculer les taux de conversion
        click_rate = (total_clicks / total_views * 100) if total_views > 0 else 0
        conversion_rate = (total_sales / total_clicks * 100) if total_clicks > 0 else 0
        
        return {
            "funnel": [
                {"stage": "Impressions", "count": total_views, "percentage": 100},
                {"stage": "Clics", "count": total_clicks, "percentage": round(click_rate, 1)},
                {"stage": "Conversions", "count": total_sales, "percentage": round(conversion_rate, 1)}
            ],
            "totals": {
                "views": total_views,
                "clicks": total_clicks,
                "sales": total_sales
            }
        }
    
    except Exception as e:
        print(f"❌ Erreur get_conversion_funnel: {str(e)}")
        return {
            "funnel": [
                {"stage": "Impressions", "count": 0, "percentage": 100},
                {"stage": "Clics", "count": 0, "percentage": 0},
                {"stage": "Conversions", "count": 0, "percentage": 0}
            ],
            "totals": {"views": 0, "clicks": 0, "sales": 0}
        }


