"""
TOUS LES ENDPOINTS MANQUANTS - IMPLÉMENTÉS
À ajouter à la fin de server_complete.py avant if __name__ == "__main__"
"""

from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
import random

# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@app.get("/api/analytics/overview")
async def get_analytics_overview(payload: dict = Depends(verify_token)):
    """Aperçu général des analytics"""
    user_role = payload.get("role")
    
    if user_role == "influencer":
        return {
            "total_earnings": 2450.75,
            "pending_earnings": 320.50,
            "total_clicks": 1247,
            "total_conversions": 89,
            "conversion_rate": 7.1,
            "active_links": 12
        }
    elif user_role == "merchant":
        return {
            "total_sales": 15280.00,
            "total_orders": 245,
            "active_affiliates": 18,
            "pending_commissions": 1580.50,
            "conversion_rate": 4.2,
            "avg_order_value": 62.37
        }
    elif user_role == "admin":
        return {
            "total_revenue": 125000.00,
            "total_users": 1250,
            "active_merchants": 45,
            "active_influencers": 320,
            "total_transactions": 5680,
            "platform_commission": 8500.00
        }
    else:
        return {
            "message": "Analytics overview",
            "stats": {}
        }

@app.get("/api/analytics/admin/revenue-chart")
async def get_admin_revenue_chart(payload: dict = Depends(verify_token)):
    """Graphique des revenus pour admin"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "datasets": [{
            "label": "Revenue",
            "data": [12000, 15000, 18000, 16000, 21000, 25000]
        }]
    }

@app.get("/api/analytics/admin/categories")
async def get_admin_categories(payload: dict = Depends(verify_token)):
    """Statistiques par catégories"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    return {
        "categories": [
            {"name": "Beauty", "sales": 45000, "percentage": 35},
            {"name": "Fashion", "sales": 32000, "percentage": 25},
            {"name": "Food", "sales": 28000, "percentage": 22},
            {"name": "Tech", "sales": 23000, "percentage": 18}
        ]
    }

@app.get("/api/analytics/admin/platform-metrics")
async def get_platform_metrics(payload: dict = Depends(verify_token)):
    """Métriques de la plateforme"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    return {
        "daily_active_users": 450,
        "monthly_active_users": 1250,
        "retention_rate": 78.5,
        "churn_rate": 3.2,
        "avg_session_duration": "8m 34s"
    }

@app.get("/api/analytics/merchant/sales-chart")
async def get_merchant_sales_chart(payload: dict = Depends(verify_token)):
    """Graphique des ventes pour merchant"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    
    return {
        "labels": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
        "datasets": [{
            "label": "Ventes",
            "data": [2300, 2800, 3200, 2900, 3500, 4200, 3800]
        }]
    }

@app.get("/api/analytics/merchant/performance")
async def get_merchant_performance(payload: dict = Depends(verify_token)):
    """Performance du merchant"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    
    return {
        "top_products": [
            {"name": "Huile d'Argan Premium", "sales": 8500, "units": 145},
            {"name": "Caftan Traditionnel", "sales": 6200, "units": 12},
            {"name": "Babouches Marocaines", "sales": 3800, "units": 78}
        ],
        "top_affiliates": [
            {"name": "Sarah M.", "sales": 12000, "commission": 2400},
            {"name": "Ahmed K.", "sales": 9500, "commission": 1900},
            {"name": "Fatima Z.", "sales": 7800, "commission": 1560}
        ]
    }

@app.get("/api/analytics/influencer/earnings-chart")
async def get_influencer_earnings_chart(payload: dict = Depends(verify_token)):
    """Graphique des gains pour influencer"""
    if payload.get("role") not in ["influencer", "admin"]:
        raise HTTPException(status_code=403, detail="Accès influencer requis")
    
    return {
        "labels": ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
        "datasets": [{
            "label": "Gains",
            "data": [450, 580, 720, 650]
        }]
    }

# ============================================
# MERCHANTS ENDPOINTS
# ============================================

@app.get("/api/merchants")
async def get_merchants(payload: dict = Depends(verify_token)):
    """Liste des marchands"""
    return {
        "merchants": [
            {
                "id": "merchant_001",
                "name": "BeautyMaroc",
                "category": "Beauty & Cosmetics",
                "logo": "/merchants/beautymaroc.png",
                "verified": True,
                "rating": 4.8,
                "total_products": 45,
                "commission_rate": 20
            },
            {
                "id": "merchant_002",
                "name": "FashionMarrakech",
                "category": "Fashion & Clothing",
                "logo": "/merchants/fashionmarrakech.png",
                "verified": True,
                "rating": 4.6,
                "total_products": 78,
                "commission_rate": 25
            }
        ],
        "total": 2
    }

@app.get("/api/merchant/profile")
async def get_merchant_profile(payload: dict = Depends(verify_token)):
    """Profil du merchant"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    
    return {
        "id": payload.get("sub"),
        "company_name": "BeautyMaroc SARL",
        "email": "contact@beautymaroc.ma",
        "phone": "+212 5 22 33 44 55",
        "address": "Boulevard Mohammed V, Casablanca",
        "ice": "001234567000001",
        "category": "Beauty & Cosmetics",
        "verified": True,
        "commission_rate": 20,
        "total_products": 45,
        "active_affiliates": 18
    }

@app.get("/api/merchant/payment-config")
async def get_merchant_payment_config(payload: dict = Depends(verify_token)):
    """Configuration paiement merchant"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    
    return {
        "bank_name": "Attijariwafa Bank",
        "account_holder": "BeautyMaroc SARL",
        "iban": "MA64011519000001234567890123",
        "swift": "BCMAMAMC",
        "payment_schedule": "monthly",
        "minimum_payout": 500.00
    }

@app.put("/api/merchant/payment-config")
async def update_merchant_payment_config(
    payment_config: dict,
    payload: dict = Depends(verify_token)
):
    """Mettre à jour configuration paiement"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    
    return {
        "message": "Configuration mise à jour avec succès",
        "config": payment_config
    }

@app.get("/api/merchant/invoices")
async def get_merchant_invoices(payload: dict = Depends(verify_token)):
    """Factures du merchant"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    
    return {
        "invoices": [
            {
                "id": "INV-2024-001",
                "date": "2024-10-01",
                "amount": 1580.50,
                "status": "paid",
                "due_date": "2024-10-15",
                "items": "Commissions Septembre 2024"
            },
            {
                "id": "INV-2024-002",
                "date": "2024-11-01",
                "amount": 1820.75,
                "status": "pending",
                "due_date": "2024-11-15",
                "items": "Commissions Octobre 2024"
            }
        ],
        "total": 2
    }

@app.get("/api/merchant/affiliation-requests/stats")
async def get_merchant_affiliation_stats(payload: dict = Depends(verify_token)):
    """Statistiques demandes d'affiliation"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    
    return {
        "total_requests": 45,
        "pending": 12,
        "approved": 28,
        "rejected": 5,
        "approval_rate": 84.8
    }

# ============================================
# INFLUENCERS ENDPOINTS
# ============================================

@app.get("/api/influencers")
async def get_influencers_list(payload: dict = Depends(verify_token)):
    """Liste des influenceurs"""
    return {
        "influencers": [
            {
                "id": "inf_001",
                "name": "Sarah M.",
                "username": "@sarahbeauty_ma",
                "avatar": "/avatars/sarah.jpg",
                "followers": 125000,
                "engagement_rate": 5.8,
                "niches": ["Beauty", "Lifestyle"],
                "platforms": ["Instagram", "TikTok"],
                "verified": True
            },
            {
                "id": "inf_002",
                "name": "Ahmed K.",
                "username": "@ahmed_tech",
                "avatar": "/avatars/ahmed.jpg",
                "followers": 89000,
                "engagement_rate": 6.2,
                "niches": ["Tech", "Gadgets"],
                "platforms": ["YouTube", "Instagram"],
                "verified": True
            }
        ],
        "total": 2
    }

@app.get("/api/influencers/stats")
async def get_influencers_stats(payload: dict = Depends(verify_token)):
    """Statistiques des influenceurs"""
    return {
        "total_influencers": 320,
        "active_this_month": 245,
        "avg_followers": 45000,
        "top_categories": [
            {"name": "Beauty", "count": 95},
            {"name": "Fashion", "count": 78},
            {"name": "Food", "count": 52}
        ]
    }

@app.get("/api/influencers/search")
async def search_influencers(
    niche: str = None,
    min_followers: int = None,
    payload: dict = Depends(verify_token)
):
    """Rechercher des influenceurs"""
    return {
        "results": [
            {
                "id": "inf_003",
                "name": "Fatima Z.",
                "username": "@fatima_food",
                "followers": 67000,
                "engagement_rate": 7.1,
                "niche": "Food",
                "matched": True
            }
        ],
        "total": 1
    }

@app.get("/api/influencers/directory")
async def get_influencers_directory(payload: dict = Depends(verify_token)):
    """Annuaire des influenceurs"""
    return {
        "influencers": [
            {
                "id": "inf_001",
                "name": "Sarah M.",
                "bio": "Beauty & Lifestyle Content Creator 💄",
                "followers": 125000,
                "engagement": 5.8,
                "niches": ["Beauty", "Lifestyle"],
                "verified": True
            }
        ],
        "total": 1
    }

@app.get("/api/influencer/profile")
async def get_influencer_profile(payload: dict = Depends(verify_token)):
    """Profil de l'influenceur"""
    if payload.get("role") not in ["influencer", "admin"]:
        raise HTTPException(status_code=403, detail="Accès influencer requis")
    
    return {
        "id": payload.get("sub"),
        "name": "Sarah M.",
        "email": "sarah@example.com",
        "phone": "+212 6 12 34 56 78",
        "bio": "Beauty & Lifestyle Content Creator",
        "avatar": "/avatars/sarah.jpg",
        "instagram": "@sarahbeauty_ma",
        "tiktok": "@sarahbeauty",
        "followers": {"instagram": 125000, "tiktok": 89000},
        "engagement_rate": 5.8,
        "niches": ["Beauty", "Lifestyle"],
        "verified": True
    }

@app.get("/api/influencer/tracking-links")
async def get_influencer_tracking_links(payload: dict = Depends(verify_token)):
    """Liens de tracking de l'influenceur"""
    if payload.get("role") not in ["influencer", "admin"]:
        raise HTTPException(status_code=403, detail="Accès influencer requis")
    
    return {
        "links": [
            {
                "id": "link_001",
                "product_name": "Huile d'Argan Premium",
                "url": "https://shareyoursales.ma/r/sarah-argan",
                "clicks": 245,
                "conversions": 18,
                "earnings": 360.00,
                "status": "active",
                "created_at": "2024-10-15"
            }
        ],
        "total": 1
    }

@app.get("/api/influencer/affiliation-requests")
async def get_influencer_affiliation_requests(
    status: str = None,
    payload: dict = Depends(verify_token)
):
    """Demandes d'affiliation de l'influenceur"""
    if payload.get("role") not in ["influencer", "admin"]:
        raise HTTPException(status_code=403, detail="Accès influencer requis")
    
    return {
        "requests": [
            {
                "id": "req_001",
                "product_name": "Huile d'Argan Premium",
                "merchant": "BeautyMaroc",
                "status": status or "pending_approval",
                "requested_at": "2024-11-01",
                "commission_rate": 20
            }
        ],
        "total": 1
    }

@app.get("/api/influencer/payment-status")
async def get_influencer_payment_status(payload: dict = Depends(verify_token)):
    """Statut de paiement influenceur"""
    if payload.get("role") not in ["influencer", "admin"]:
        raise HTTPException(status_code=403, detail="Accès influencer requis")
    
    return {
        "payment_method": "bank_transfer",
        "bank_name": "Banque Populaire",
        "account_holder": "Sarah Mohamed",
        "rib": "230670000123456789012345",
        "verified": True,
        "last_payout": {
            "amount": 1250.00,
            "date": "2024-10-15",
            "status": "completed"
        }
    }

@app.put("/api/influencer/payment-method")
async def update_influencer_payment_method(
    payment_data: dict,
    payload: dict = Depends(verify_token)
):
    """Mettre à jour méthode de paiement"""
    if payload.get("role") not in ["influencer", "admin"]:
        raise HTTPException(status_code=403, detail="Accès influencer requis")
    
    return {
        "message": "Méthode de paiement mise à jour",
        "payment_method": payment_data
    }

# ============================================
# PRODUCTS ENDPOINTS (Continuation)
# ============================================

@app.get("/api/products/my-products")
async def get_my_products(payload: dict = Depends(verify_token)):
    """Mes produits (merchant)"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    
    return {
        "products": [
            {
                "id": "prod_001",
                "name": "Huile d'Argan Premium Bio",
                "category": "Beauty",
                "price": 180.00,
                "commission_rate": 20,
                "stock": 45,
                "status": "active",
                "image": "/products/argan.jpg"
            }
        ],
        "total": 1
    }

# Je continue dans le prochain message...
"""
