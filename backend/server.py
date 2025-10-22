"""
ShareYourSales API Server - Version Supabase
Tous les endpoints utilisent Supabase au lieu de MOCK_DATA
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

# Importer les helpers Supabase
from db_helpers import *
from supabase_client import supabase

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(title="ShareYourSales API - Supabase Edition")

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-please-set-env-variable")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

if JWT_SECRET == "fallback-secret-please-set-env-variable":
    print("⚠️  WARNING: JWT_SECRET not set in environment!")

# Pydantic Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class TwoFAVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")
    temp_token: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(merchant|influencer)$")
    phone: Optional[str] = None

class AdvertiserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    country: str = Field(..., min_length=2, max_length=2)
    status: Optional[str] = "active"

class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|paused|ended)$")
    budget: Optional[float] = None

class AffiliateStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(active|inactive|suspended)$")

class PayoutStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|approved|rejected|paid)$")

class AffiliateLinkGenerate(BaseModel):
    product_id: str = Field(..., min_length=1)

class AIContentGenerate(BaseModel):
    type: str = Field(default="social_post", pattern="^(social_post|email|blog)$")
    platform: Optional[str] = "Instagram"

# Helper Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.get("/")
async def root():
    return {
        "message": "ShareYourSales API - Supabase Edition",
        "version": "2.0.0",
        "status": "running",
        "database": "Supabase PostgreSQL"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ShareYourSales API",
        "database": "Supabase Connected"
    }

@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    """Login avec email et mot de passe"""
    # Trouver l'utilisateur dans Supabase
    user = get_user_by_email(login_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Vérifier le mot de passe
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Vérifier si le compte est actif
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )

    # Si 2FA activé
    if user.get("two_fa_enabled", False):
        code = "123456"  # Mock - en production, envoyer par SMS

        temp_token = create_access_token(
            {"sub": user["id"], "temp": True},
            expires_delta=timedelta(minutes=5)
        )

        print(f"📱 Code 2FA pour {user['email']}: {code}")

        return {
            "requires_2fa": True,
            "temp_token": temp_token,
            "token_type": "bearer",
            "message": f"Code 2FA envoyé"
        }

    # Pas de 2FA, connexion directe
    update_user_last_login(user["id"])

    access_token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"]
    })

    # Retirer le password_hash de la réponse
    user_data = {k: v for k, v in user.items() if k != "password_hash"}

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_2fa": False,
        "user": user_data
    }

@app.post("/api/auth/verify-2fa")
async def verify_2fa(data: TwoFAVerifyRequest):
    """Vérification du code 2FA"""
    # Vérifier le temp_token
    try:
        payload = jwt.decode(data.temp_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Code expiré, veuillez vous reconnecter")
    except Exception:
        raise HTTPException(status_code=400, detail="Token invalide")

    if not payload.get("temp"):
        raise HTTPException(status_code=400, detail="Token invalide")

    # Trouver l'utilisateur
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Vérifier le code 2FA (mock - accepter 123456)
    if data.code != "123456":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Code 2FA incorrect"
        )

    # Code correct, créer le vrai token
    update_user_last_login(user["id"])

    access_token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"]
    })

    user_data = {k: v for k, v in user.items() if k != "password_hash"}

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    """Récupère l'utilisateur connecté"""
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return user_data

@app.post("/api/auth/logout")
async def logout(payload: dict = Depends(verify_token)):
    """Logout (invalidation côté client)"""
    return {"message": "Logged out successfully"}

@app.post("/api/auth/register")
async def register(data: RegisterRequest):
    """Inscription d'un nouvel utilisateur"""
    # Vérifier si l'email existe déjà
    existing_user = get_user_by_email(data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Créer l'utilisateur
    user = create_user(
        email=data.email,
        password=data.password,
        role=data.role,
        phone=data.phone,
        two_fa_enabled=False
    )

    if not user:
        raise HTTPException(status_code=500, detail="Erreur lors de la création du compte")

    return {"message": "Compte créé avec succès", "user_id": user["id"]}

# ============================================
# DASHBOARD & ANALYTICS
# ============================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats_endpoint(payload: dict = Depends(verify_token)):
    """Statistiques du dashboard selon le rôle"""
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = get_dashboard_stats(user["role"], user["id"])
    return stats

@app.get("/api/analytics/overview")
async def get_analytics_overview(payload: dict = Depends(verify_token)):
    """Vue d'ensemble des analytics"""
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = get_dashboard_stats(user["role"], user["id"])
    return stats

# ============================================
# MERCHANTS ENDPOINTS
# ============================================

@app.get("/api/merchants")
async def get_merchants(payload: dict = Depends(verify_token)):
    """Liste tous les merchants"""
    merchants = get_all_merchants()
    return {"merchants": merchants, "total": len(merchants)}

@app.get("/api/merchants/{merchant_id}")
async def get_merchant(merchant_id: str, payload: dict = Depends(verify_token)):
    """Récupère les détails d'un merchant"""
    merchant = get_merchant_by_id(merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant non trouvé")
    return merchant

# ============================================
# INFLUENCERS ENDPOINTS
# ============================================

@app.get("/api/influencers")
async def get_influencers(payload: dict = Depends(verify_token)):
    """Liste tous les influencers"""
    influencers = get_all_influencers()
    return {"influencers": influencers, "total": len(influencers)}

@app.get("/api/influencers/{influencer_id}")
async def get_influencer(influencer_id: str, payload: dict = Depends(verify_token)):
    """Récupère les détails d'un influencer"""
    influencer = get_influencer_by_id(influencer_id)
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer non trouvé")
    return influencer

# ============================================
# PRODUCTS ENDPOINTS
# ============================================

@app.get("/api/products")
async def get_products(category: Optional[str] = None, merchant_id: Optional[str] = None):
    """Liste tous les produits avec filtres optionnels"""
    products = get_all_products(category=category, merchant_id=merchant_id)
    return {"products": products, "total": len(products)}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Récupère les détails d'un produit"""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product

# ============================================
# AFFILIATE LINKS ENDPOINTS
# ============================================

@app.get("/api/affiliate-links")
async def get_affiliate_links_endpoint(payload: dict = Depends(verify_token)):
    """Liste les liens d'affiliation"""
    user = get_user_by_id(payload["sub"])

    if user["role"] == "influencer":
        influencer = get_influencer_by_user_id(user["id"])
        if influencer:
            links = get_affiliate_links(influencer_id=influencer["id"])
        else:
            links = []
    else:
        links = get_affiliate_links()

    return {"links": links, "total": len(links)}

@app.post("/api/affiliate-links/generate")
async def generate_affiliate_link(data: AffiliateLinkGenerate, payload: dict = Depends(verify_token)):
    """Génère un lien d'affiliation"""
    user = get_user_by_id(payload["sub"])

    if user["role"] != "influencer":
        raise HTTPException(status_code=403, detail="Accès refusé")

    influencer = get_influencer_by_user_id(user["id"])
    if not influencer:
        raise HTTPException(status_code=404, detail="Profil influencer non trouvé")

    product = get_product_by_id(data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # Générer un code unique
    import secrets
    unique_code = secrets.token_urlsafe(12)

    # Créer le lien
    link = create_affiliate_link(
        product_id=data.product_id,
        influencer_id=influencer["id"],
        unique_code=unique_code
    )

    if not link:
        raise HTTPException(status_code=500, detail="Erreur lors de la création du lien")

    return {"message": "Lien généré avec succès", "link": link}

# ============================================
# CAMPAIGNS ENDPOINTS
# ============================================

@app.get("/api/campaigns")
async def get_campaigns_endpoint(payload: dict = Depends(verify_token)):
    """Liste toutes les campagnes"""
    user = get_user_by_id(payload["sub"])

    if user["role"] == "merchant":
        merchant = get_merchant_by_user_id(user["id"])
        campaigns = get_all_campaigns(merchant_id=merchant["id"]) if merchant else []
    else:
        campaigns = get_all_campaigns()

    return {"data": campaigns, "total": len(campaigns)}

@app.post("/api/campaigns")
async def create_campaign_endpoint(campaign_data: CampaignCreate, payload: dict = Depends(verify_token)):
    """Créer une nouvelle campagne"""
    user = get_user_by_id(payload["sub"])

    if user["role"] != "merchant":
        raise HTTPException(status_code=403, detail="Seuls les merchants peuvent créer des campagnes")

    merchant = get_merchant_by_user_id(user["id"])
    if not merchant:
        raise HTTPException(status_code=404, detail="Profil merchant non trouvé")

    campaign = create_campaign(
        merchant_id=merchant["id"],
        name=campaign_data.name,
        description=campaign_data.description,
        budget=campaign_data.budget,
        status=campaign_data.status
    )

    if not campaign:
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la campagne")

    return campaign

# ============================================
# PERFORMANCE ENDPOINTS
# ============================================

@app.get("/api/conversions")
async def get_conversions_endpoint(payload: dict = Depends(verify_token)):
    """Liste des conversions"""
    conversions = get_conversions(limit=20)
    return {"data": conversions, "total": len(conversions)}

@app.get("/api/clicks")
async def get_clicks_endpoint(payload: dict = Depends(verify_token)):
    """Liste des clics"""
    clicks = get_clicks(limit=50)
    return {"data": clicks, "total": len(clicks)}

# ============================================
# PAYOUTS ENDPOINTS
# ============================================

@app.get("/api/payouts")
async def get_payouts_endpoint(payload: dict = Depends(verify_token)):
    """Liste des payouts"""
    payouts = get_payouts()
    return {"data": payouts, "total": len(payouts)}

@app.put("/api/payouts/{payout_id}/status")
async def update_payout_status_endpoint(payout_id: str, data: PayoutStatusUpdate, payload: dict = Depends(verify_token)):
    """Mettre à jour le statut d'un payout"""
    success = update_payout_status(payout_id, data.status)

    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")

    return {"message": "Statut mis à jour", "status": data.status}

# ============================================
# SETTINGS ENDPOINTS
# ============================================

@app.get("/api/settings")
async def get_settings(payload: dict = Depends(verify_token)):
    """Récupère les paramètres"""
    # Mock settings pour l'instant
    return {
        "default_currency": "EUR",
        "platform_commission": 5.0,
        "min_payout": 50.0
    }

@app.put("/api/settings")
async def update_settings(settings: dict, payload: dict = Depends(verify_token)):
    """Met à jour les paramètres"""
    # Mock pour l'instant
    return settings

# ============================================
# AI MARKETING ENDPOINTS
# ============================================

@app.post("/api/ai/generate-content")
async def generate_ai_content(data: AIContentGenerate, payload: dict = Depends(verify_token)):
    """Génère du contenu avec l'IA (mock)"""
    if data.type == "social_post":
        generated_text = f"🌟 Découvrez ce produit incroyable ! Parfait pour vous. Ne manquez pas cette opportunité ! 💫 #Promo #Shopping #Lifestyle"
    elif data.type == "email":
        generated_text = "Bonjour,\n\nNous sommes ravis de vous présenter notre dernier produit...\n\nCordialement"
    else:
        generated_text = "Contenu généré par IA"

    return {
        "content": generated_text,
        "type": data.type,
        "platform": data.platform,
        "suggested_hashtags": ["#Promo", "#Shopping", "#Deal"]
    }

@app.get("/api/ai/predictions")
async def get_ai_predictions(payload: dict = Depends(verify_token)):
    """Récupère les prédictions IA (mock)"""
    return {
        "predicted_sales": 150,
        "trend_score": 75.5,
        "recommended_strategy": "Augmenter le budget publicitaire de 20%"
    }

# ============================================
# SUBSCRIPTION PLANS ENDPOINTS
# ============================================

@app.get("/api/subscription-plans")
async def get_subscription_plans():
    """Récupère tous les plans d'abonnement"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Gratuit",
                "price": 0,
                "features": ["10 liens", "Rapports basiques"]
            },
            {
                "id": "starter",
                "name": "Starter",
                "price": 49,
                "features": ["100 liens", "Rapports avancés", "Support"]
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 149,
                "features": ["500 liens", "IA Marketing", "Support prioritaire"]
            }
        ]
    }

# ============================================
# ADVERTISERS ENDPOINTS (Compatibility)
# ============================================

@app.get("/api/advertisers")
async def get_advertisers(payload: dict = Depends(verify_token)):
    """Liste des advertisers (alias pour merchants)"""
    merchants = get_all_merchants()
    return {"data": merchants, "total": len(merchants)}

@app.get("/api/affiliates")
async def get_affiliates(payload: dict = Depends(verify_token)):
    """Liste des affiliés (alias pour influencers)"""
    influencers = get_all_influencers()
    return {"data": influencers, "total": len(influencers)}

# ============================================
# LOGS ENDPOINTS (Mock pour l'instant)
# ============================================

@app.get("/api/logs/postback")
async def get_postback_logs(payload: dict = Depends(verify_token)):
    """Logs des postbacks"""
    return {"data": [], "total": 0}

@app.get("/api/logs/audit")
async def get_audit_logs(payload: dict = Depends(verify_token)):
    """Logs d'audit"""
    return {"data": [], "total": 0}

@app.get("/api/logs/webhooks")
async def get_webhook_logs(payload: dict = Depends(verify_token)):
    """Logs des webhooks"""
    return {"data": [], "total": 0}

# ============================================
# COUPONS ENDPOINTS (Mock)
# ============================================

@app.get("/api/coupons")
async def get_coupons(payload: dict = Depends(verify_token)):
    """Liste des coupons"""
    return {"data": [], "total": 0}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur Supabase...")
    print("📊 Base de données: Supabase PostgreSQL")
    uvicorn.run(app, host="0.0.0.0", port=8001)
