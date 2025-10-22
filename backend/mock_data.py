# Mock data for ShareYourSales Platform
from datetime import datetime, timedelta
import random

# ============================================
# USERS - Tous les utilisateurs de la plateforme
# ============================================
MOCK_USERS = [
    # Admin
    {
        "id": "user_admin_1",
        "email": "admin@shareyoursales.com",
        "password": "$2b$12$f19klH3itoqd..dxoRL0zuMA57VzhlzkB3TdEsns8NPySv6VDIX7W",  # admin123 (hashed)
        "role": "admin",
        "first_name": "Sophie",
        "last_name": "Admin",
        "phone": "+33612345678",
        "phone_verified": True,
        "two_fa_enabled": True,
        "two_fa_code": None,
        "two_fa_expires_at": None,
        "country": "FR",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sophie",
        "is_active": True,
        "last_login": datetime.now().isoformat(),
        "created_at": "2024-01-01T00:00:00Z"
    },
    # Merchants (Entreprises)
    {
        "id": "user_merchant_1",
        "email": "contact@techstyle.fr",
        "password": "$2b$12$XDH/0kAWJdNCRcm3yFXsXeBtobKN1mkZKEcRxj5taoYPZARTGpDpW",  # merchant123 (hashed)
        "role": "merchant",
        "first_name": "Jean",
        "last_name": "Dupont",
        "phone": "+33698765432",
        "phone_verified": True,
        "two_fa_enabled": True,
        "two_fa_code": None,
        "two_fa_expires_at": None,
        "country": "FR",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jean",
        "is_active": True,
        "last_login": datetime.now().isoformat(),
        "created_at": "2024-01-15T00:00:00Z"
    },
    {
        "id": "user_merchant_2",
        "email": "hello@beautypro.com",
        "password": "$2b$12$XDH/0kAWJdNCRcm3yFXsXeBtobKN1mkZKEcRxj5taoYPZARTGpDpW",  # merchant123 (hashed)
        "role": "merchant",
        "first_name": "Marie",
        "last_name": "Laurent",
        "phone": "+33687654321",
        "phone_verified": True,
        "two_fa_enabled": True,
        "country": "FR",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Marie",
        "is_active": True,
        "last_login": datetime.now().isoformat(),
        "created_at": "2024-02-01T00:00:00Z"
    },
    # Influencers
    {
        "id": "user_influencer_1",
        "email": "emma.style@instagram.com",
        "password": "$2b$12$2SolTi1T4Kr.yPE7hQkvD.mMd1uidM8DsVjo1ZmiU7gSKYgruXnC6",  # influencer123 (hashed)
        "role": "influencer",
        "first_name": "Emma",
        "last_name": "Style",
        "phone": "+33676543210",
        "phone_verified": True,
        "two_fa_enabled": True,
        "country": "FR",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Emma",
        "is_active": True,
        "last_login": datetime.now().isoformat(),
        "created_at": "2024-02-10T00:00:00Z"
    },
    {
        "id": "user_influencer_2",
        "email": "lucas.tech@youtube.com",
        "password": "$2b$12$2SolTi1T4Kr.yPE7hQkvD.mMd1uidM8DsVjo1ZmiU7gSKYgruXnC6",  # influencer123 (hashed)
        "role": "influencer",
        "first_name": "Lucas",
        "last_name": "Tech",
        "phone": "+33665432109",
        "phone_verified": True,
        "two_fa_enabled": True,
        "country": "FR",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lucas",
        "is_active": True,
        "last_login": datetime.now().isoformat(),
        "created_at": "2024-02-15T00:00:00Z"
    },
    {
        "id": "user_influencer_3",
        "email": "julie.beauty@tiktok.com",
        "password": "$2b$12$2SolTi1T4Kr.yPE7hQkvD.mMd1uidM8DsVjo1ZmiU7gSKYgruXnC6",  # influencer123 (hashed)
        "role": "influencer",
        "first_name": "Julie",
        "last_name": "Beauty",
        "phone": "+33654321098",
        "phone_verified": True,
        "two_fa_enabled": True,
        "country": "FR",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Julie",
        "is_active": True,
        "last_login": datetime.now().isoformat(),
        "created_at": "2024-03-01T00:00:00Z"
    },
    # Test user without 2FA
    {
        "id": "user_test_no2fa",
        "email": "test@example.com",
        "password": "test123",
        "role": "influencer",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+33600000000",
        "phone_verified": True,
        "two_fa_enabled": False,
        "country": "FR",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Test",
        "is_active": True,
        "last_login": datetime.now().isoformat(),
        "created_at": "2024-03-01T00:00:00Z"
    }
]

# ============================================
# MERCHANTS - Profils des entreprises
# ============================================
MOCK_MERCHANTS = [
    {
        "id": "merchant_1",
        "user_id": "user_merchant_1",
        "company_name": "TechStyle Paris",
        "industry": "Technology",
        "category": "Mode et lifestyle",
        "address": "123 Avenue des Champs-Élysées, 75008 Paris",
        "tax_id": "FR12345678901",
        "website": "https://techstyle.fr",
        "logo_url": "https://via.placeholder.com/200x200/4F46E5/FFFFFF?text=TS",
        "subscription_plan": "pro",
        "commission_rate": 3.0,
        "monthly_fee": 199.00,
        "total_sales": 145000.00,
        "total_commission_paid": 28500.00,
        "products_count": 45,
        "active_campaigns": 8,
        "affiliates_count": 23,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": "merchant_2",
        "user_id": "user_merchant_2",
        "company_name": "BeautyPro Cosmétiques",
        "industry": "Beauty & Wellness",
        "category": "Beauté et bien-être",
        "address": "456 Rue de Rivoli, 75001 Paris",
        "tax_id": "FR98765432109",
        "website": "https://beautypro.com",
        "logo_url": "https://via.placeholder.com/200x200/EC4899/FFFFFF?text=BP",
        "subscription_plan": "starter",
        "commission_rate": 5.0,
        "monthly_fee": 49.00,
        "total_sales": 68000.00,
        "total_commission_paid": 12800.00,
        "products_count": 28,
        "active_campaigns": 3,
        "affiliates_count": 12,
        "created_at": "2024-02-01T14:30:00Z",
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": "merchant_3",
        "user_id": "user_admin_1",  # For demo
        "company_name": "FitGear Sports",
        "industry": "Sports & Fitness",
        "category": "Sport et fitness",
        "address": "789 Boulevard Saint-Germain, 75006 Paris",
        "tax_id": "FR11223344556",
        "website": "https://fitgear-sports.com",
        "logo_url": "https://via.placeholder.com/200x200/10B981/FFFFFF?text=FG",
        "subscription_plan": "enterprise",
        "commission_rate": 1.5,
        "monthly_fee": 499.00,
        "total_sales": 289000.00,
        "total_commission_paid": 45600.00,
        "products_count": 67,
        "active_campaigns": 12,
        "affiliates_count": 45,
        "created_at": "2023-11-20T09:00:00Z",
        "updated_at": datetime.now().isoformat()
    }
]

# ============================================
# INFLUENCERS - Profils des influenceurs
# ============================================
MOCK_INFLUENCERS = [
    {
        "id": "influencer_1",
        "user_id": "user_influencer_1",
        "username": "emma_style_paris",
        "full_name": "Emma Style",
        "bio": "Passionnée de mode et lifestyle 🌟 Partage mes coups de coeur mode & beauté • Paris 🇫🇷",
        "profile_picture_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Emma",
        "category": "Mode et lifestyle",
        "influencer_type": "macro",
        "audience_size": 245000,
        "engagement_rate": 4.8,
        "subscription_plan": "pro",
        "platform_fee_rate": 3.0,
        "monthly_fee": 29.90,
        "social_links": {
            "instagram": "https://instagram.com/emma_style_paris",
            "tiktok": "https://tiktok.com/@emmastyle",
            "youtube": "https://youtube.com/@emmastyleParis"
        },
        "total_clicks": 12450,
        "total_sales": 186,
        "total_earnings": 18650.00,
        "balance": 4250.00,
        "payment_method": "PayPal",
        "payment_details": {"email": "emma.payments@gmail.com"},
        "created_at": "2024-02-10T11:00:00Z",
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": "influencer_2",
        "user_id": "user_influencer_2",
        "username": "lucas_tech_reviews",
        "full_name": "Lucas Tech",
        "bio": "Tech Reviewer 📱💻 Tests et avis tech • Unboxing • Comparatifs • 200K+ subs sur YouTube",
        "profile_picture_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lucas",
        "category": "Technologie",
        "influencer_type": "macro",
        "audience_size": 198000,
        "engagement_rate": 6.2,
        "subscription_plan": "pro",
        "platform_fee_rate": 3.0,
        "monthly_fee": 29.90,
        "social_links": {
            "youtube": "https://youtube.com/@lucastechreviews",
            "instagram": "https://instagram.com/lucas.tech",
            "twitter": "https://twitter.com/lucastech"
        },
        "total_clicks": 18950,
        "total_sales": 312,
        "total_earnings": 28400.00,
        "balance": 6800.00,
        "payment_method": "Bank Transfer",
        "payment_details": {"iban": "FR76****1234"},
        "created_at": "2024-02-15T15:30:00Z",
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": "influencer_3",
        "user_id": "user_influencer_3",
        "username": "julie_beauty_tips",
        "full_name": "Julie Beauty",
        "bio": "Makeup Artist 💄 Beauty & Skincare • Tutos maquillage • Conseils beauté • Collaboration 📧",
        "profile_picture_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Julie",
        "category": "Beauté",
        "influencer_type": "micro",
        "audience_size": 45000,
        "engagement_rate": 8.5,
        "subscription_plan": "starter",
        "platform_fee_rate": 5.0,
        "monthly_fee": 9.90,
        "social_links": {
            "tiktok": "https://tiktok.com/@juliebeautytips",
            "instagram": "https://instagram.com/julie.beauty",
            "youtube": "https://youtube.com/@juliebeauty"
        },
        "total_clicks": 5680,
        "total_sales": 94,
        "total_earnings": 8920.00,
        "balance": 1850.00,
        "payment_method": "PayPal",
        "payment_details": {"email": "julie.beauty@gmail.com"},
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": datetime.now().isoformat()
    }
]

# ============================================
# PRODUCTS - Catalogue de produits
# ============================================
MOCK_PRODUCTS = [
    {
        "id": "prod_1",
        "merchant_id": "merchant_1",
        "merchant_name": "TechStyle Paris",
        "name": "Montre Connectée SmartWatch Pro",
        "description": "Montre connectée haut de gamme avec suivi santé, GPS intégré, et autonomie 7 jours",
        "category": "Technologie",
        "price": 299.99,
        "currency": "EUR",
        "commission_rate": 15.0,
        "commission_type": "percentage",
        "images": [
            "https://via.placeholder.com/600x400/4F46E5/FFFFFF?text=SmartWatch+Pro",
            "https://via.placeholder.com/600x400/4F46E5/FFFFFF?text=Side+View"
        ],
        "videos": [],
        "specifications": {
            "brand": "TechStyle",
            "model": "SW-Pro-2024",
            "color": "Noir",
            "features": ["GPS", "Cardio", "SpO2", "Étanche 50m"]
        },
        "stock_quantity": 150,
        "is_available": True,
        "slug": "montre-connectee-smartwatch-pro",
        "total_views": 3250,
        "total_clicks": 890,
        "total_sales": 124,
        "created_at": "2024-01-20T10:00:00Z"
    },
    {
        "id": "prod_2",
        "merchant_id": "merchant_2",
        "merchant_name": "BeautyPro Cosmétiques",
        "name": "Sérum Anti-Âge Vitamine C",
        "description": "Sérum facial concentré en vitamine C pour un teint éclatant et uniforme",
        "category": "Beauté",
        "price": 49.90,
        "currency": "EUR",
        "commission_rate": 20.0,
        "commission_type": "percentage",
        "images": [
            "https://via.placeholder.com/600x400/EC4899/FFFFFF?text=Serum+Vitamine+C",
            "https://via.placeholder.com/600x400/EC4899/FFFFFF?text=Product+Details"
        ],
        "videos": [],
        "specifications": {
            "brand": "BeautyPro",
            "volume": "30ml",
            "type": "Sérum facial",
            "ingredients": ["Vitamine C", "Acide hyaluronique", "Aloe vera"]
        },
        "stock_quantity": 320,
        "is_available": True,
        "slug": "serum-anti-age-vitamine-c",
        "total_views": 4580,
        "total_clicks": 1240,
        "total_sales": 186,
        "created_at": "2024-02-05T14:00:00Z"
    },
    {
        "id": "prod_3",
        "merchant_id": "merchant_3",
        "merchant_name": "FitGear Sports",
        "name": "Tapis de Yoga Premium",
        "description": "Tapis de yoga antidérapant, écologique, 6mm d'épaisseur avec sac de transport",
        "category": "Sport",
        "price": 39.99,
        "currency": "EUR",
        "commission_rate": 18.0,
        "commission_type": "percentage",
        "images": [
            "https://via.placeholder.com/600x400/10B981/FFFFFF?text=Yoga+Mat+Premium"
        ],
        "videos": [],
        "specifications": {
            "brand": "FitGear",
            "dimensions": "183cm x 61cm x 6mm",
            "material": "TPE écologique",
            "color": "Violet"
        },
        "stock_quantity": 200,
        "is_available": True,
        "slug": "tapis-yoga-premium",
        "total_views": 2890,
        "total_clicks": 680,
        "total_sales": 98,
        "created_at": "2024-01-10T09:00:00Z"
    }
]

# ============================================
# AFFILIATE LINKS - Liens de tracking
# ============================================
MOCK_AFFILIATE_LINKS = [
    {
        "id": "link_1",
        "influencer_id": "influencer_1",
        "influencer_name": "Emma Style",
        "product_id": "prod_1",
        "product_name": "Montre Connectée SmartWatch Pro",
        "short_link": "shs.io/emma-sw",
        "full_link": "https://shareyoursales.com/track/emma_style_paris_smartwatch_pro",
        "clicks": 890,
        "conversions": 124,
        "conversion_rate": 13.93,
        "revenue": 37198.76,
        "commission_earned": 5579.81,
        "status": "active",
        "created_at": "2024-02-12T10:00:00Z"
    },
    {
        "id": "link_2",
        "influencer_id": "influencer_3",
        "influencer_name": "Julie Beauty",
        "product_id": "prod_2",
        "product_name": "Sérum Anti-Âge Vitamine C",
        "short_link": "shs.io/julie-serum",
        "full_link": "https://shareyoursales.com/track/julie_beauty_tips_serum_vitaminec",
        "clicks": 1240,
        "conversions": 186,
        "conversion_rate": 15.0,
        "revenue": 9281.40,
        "commission_earned": 1856.28,
        "status": "active",
        "created_at": "2024-03-05T11:00:00Z"
    },
    {
        "id": "link_3",
        "influencer_id": "influencer_2",
        "influencer_name": "Lucas Tech",
        "product_id": "prod_1",
        "product_name": "Montre Connectée SmartWatch Pro",
        "short_link": "shs.io/lucas-watch",
        "full_link": "https://shareyoursales.com/track/lucas_tech_reviews_smartwatch",
        "clicks": 2150,
        "conversions": 312,
        "conversion_rate": 14.51,
        "revenue": 93596.88,
        "commission_earned": 14039.53,
        "status": "active",
        "created_at": "2024-02-18T15:00:00Z"
    }
]

# ============================================
# SUBSCRIPTION PLANS
# ============================================
SUBSCRIPTION_PLANS = {
    "merchants": [
        {
            "id": "plan_merchant_free",
            "name": "Gratuit (Découverte)",
            "price": 0,
            "commission_rate": 7.0,
            "features": {
                "user_accounts": 1,
                "trackable_links_per_month": 10,
                "reports": "Basique",
                "support": "Email"
            }
        },
        {
            "id": "plan_merchant_starter",
            "name": "Starter (PME)",
            "price": 49,
            "commission_rate": 5.0,
            "features": {
                "user_accounts": 5,
                "trackable_links_per_month": 100,
                "reports": "Avancé",
                "support": "Email + Chat"
            }
        },
        {
            "id": "plan_merchant_pro",
            "name": "Pro (Croissance)",
            "price": 199,
            "commission_rate": 3.0,
            "features": {
                "user_accounts": 20,
                "trackable_links_per_month": 500,
                "reports": "IA Marketing",
                "ai_tools": True,
                "support": "Prioritaire"
            }
        },
        {
            "id": "plan_merchant_enterprise",
            "name": "Enterprise (Sur mesure)",
            "price": None,  # Custom pricing
            "commission_rate": 1.5,
            "features": {
                "user_accounts": "Illimité",
                "trackable_links_per_month": "Illimité",
                "reports": "Personnalisé",
                "ai_tools": True,
                "dedicated_manager": True,
                "support": "24/7 Dédié"
            }
        }
    ],
    "influencers": [
        {
            "id": "plan_influencer_starter",
            "name": "Influencer Starter",
            "price": 9.90,
            "platform_fee_rate": 5.0,
            "features": {
                "ai_tools": "Recommandation",
                "campaigns_per_month": 3,
                "payments": "Mensuel",
                "analytics": "Basique"
            }
        },
        {
            "id": "plan_influencer_pro",
            "name": "Influencer Pro",
            "price": 29.90,
            "platform_fee_rate": 3.0,
            "features": {
                "ai_tools": "Avancé (analyse prédictive)",
                "campaigns_per_month": "Illimité",
                "payments": "Instantané (+ 1% frais)",
                "analytics": "Avancé",
                "priority_support": True
            }
        }
    ]
}

# ============================================
# AI MARKETING MOCK DATA
# ============================================
MOCK_AI_CONTENT_TEMPLATES = [
    {
        "id": "ai_template_1",
        "type": "social_post",
        "platform": "Instagram",
        "tone": "friendly",
        "generated_text": "🌟 Découvrez notre nouvelle collection ! Des pièces uniques qui vont transformer votre garde-robe 💫 Cliquez sur le lien dans ma bio pour en savoir plus ! #Fashion #Style #NewCollection"
    },
    {
        "id": "ai_template_2",
        "type": "email",
        "subject": "Offre exclusive pour vous !",
        "tone": "professional",
        "generated_text": "Bonjour,\n\nNous avons le plaisir de vous présenter notre nouvelle collection exclusive. Profitez de -20% avec le code WELCOME20.\n\nCordialement,\nL'équipe"
    }
]

MOCK_AI_PREDICTIONS = {
    "sales_forecast": {
        "next_month": 45000,
        "next_quarter": 135000,
        "confidence": 85.5
    },
    "best_performing_products": ["prod_1", "prod_2"],
    "recommended_influencers": ["influencer_1", "influencer_2"],
    "optimal_posting_times": ["18:00-20:00", "12:00-14:00"]
}

# ============================================
# 2FA MOCK DATA
# ============================================
def generate_2fa_code():
    """Génère un code 2FA à 6 chiffres"""
    return str(random.randint(100000, 999999))

MOCK_2FA_CODES = {
    # For testing: email -> code
    "admin@shareyoursales.com": "123456",
    "contact@techstyle.fr": "234567",
    "emma.style@instagram.com": "345678"
}

# ============================================
# DASHBOARD STATS
# ============================================
def get_dashboard_stats(user_role, user_id=None):
    """Retourne les stats du dashboard selon le rôle"""
    
    if user_role == "admin":
        return {
            "total_merchants": len(MOCK_MERCHANTS),
            "total_influencers": len(MOCK_INFLUENCERS),
            "total_products": len(MOCK_PRODUCTS),
            "total_revenue": 502000.00,
            "total_commission_paid": 86900.00,
            "active_links": len(MOCK_AFFILIATE_LINKS),
            "total_clicks": sum(link["clicks"] for link in MOCK_AFFILIATE_LINKS),
            "total_conversions": sum(link["conversions"] for link in MOCK_AFFILIATE_LINKS),
            "average_conversion_rate": 14.48,
            "monthly_revenue": 145000.00,
            "monthly_growth": 12.5
        }
    
    elif user_role == "merchant":
        merchant = next((m for m in MOCK_MERCHANTS if m["user_id"] == user_id), MOCK_MERCHANTS[0])
        return {
            "total_sales": merchant["total_sales"],
            "total_commission_paid": merchant["total_commission_paid"],
            "products_count": merchant["products_count"],
            "active_campaigns": merchant["active_campaigns"],
            "affiliates_count": merchant["affiliates_count"],
            "monthly_revenue": merchant["total_sales"] * 0.3,  # 30% du total
            "monthly_growth": 8.5,
            "roi": 320.5
        }
    
    elif user_role == "influencer":
        influencer = next((i for i in MOCK_INFLUENCERS if i["user_id"] == user_id), MOCK_INFLUENCERS[0])
        return {
            "total_clicks": influencer["total_clicks"],
            "total_sales": influencer["total_sales"],
            "total_earnings": influencer["total_earnings"],
            "balance": influencer["balance"],
            "engagement_rate": influencer["engagement_rate"],
            "conversion_rate": (influencer["total_sales"] / influencer["total_clicks"] * 100) if influencer["total_clicks"] > 0 else 0,
            "monthly_earnings": influencer["total_earnings"] * 0.25,  # 25% du total
            "pending_payment": influencer["balance"]
        }
    
    return {}

# Export all mock data
__all__ = [
    'MOCK_USERS',
    'MOCK_MERCHANTS',
    'MOCK_INFLUENCERS',
    'MOCK_PRODUCTS',
    'MOCK_AFFILIATE_LINKS',
    'SUBSCRIPTION_PLANS',
    'MOCK_AI_CONTENT_TEMPLATES',
    'MOCK_AI_PREDICTIONS',
    'MOCK_2FA_CODES',
    'generate_2fa_code',
    'get_dashboard_stats'
]
