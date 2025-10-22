from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
from mock_data import *

app = FastAPI(title="ShareYourSales API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = "your-secret-key-change-this-in-production-12345"
JWT_ALGORITHM = "HS256"

# Pydantic Models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class MessageResponse(BaseModel):
    message: str

# Helper Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "ShareYourSales API - v1.0.0", "status": "running"}

# Authentication Endpoints
@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    # Find user
    user = next((u for u in MOCK_USERS if u["email"] == login_data.email), None)
    
    if not user or user["password"] != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Check if account is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    # Si 2FA activé, générer code et retourner temp_token
    if user.get("two_fa_enabled", False):
        # Générer code 2FA (mock)
        code = MOCK_2FA_CODES.get(user["email"], "123456")
        
        # Créer temp token pour la vérification 2FA
        temp_token = create_access_token(
            {"sub": user["id"], "temp": True},
            expires_delta=timedelta(minutes=5)
        )
        
        # En production, envoyer le code par SMS ici
        print(f"📱 Code 2FA pour {user['email']}: {code}")
        
        return {
            "requires_2fa": True,
            "temp_token": temp_token,
            "token_type": "bearer",
            "message": f"Code 2FA envoyé au {user.get('phone', 'téléphone')}"
        }
    
    # Si pas de 2FA, connexion directe
    access_token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"]
    })
    
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_2fa": False,
        "user": user_data
    }

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    user = next((u for u in MOCK_USERS if u["id"] == payload["sub"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = {k: v for k, v in user.items() if k != "password"}
    return user_data

@app.post("/api/auth/logout")
async def logout(payload: dict = Depends(verify_token)):
    return {"message": "Logged out successfully"}

# Dashboard Endpoint
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(payload: dict = Depends(verify_token)):
    return MOCK_DASHBOARD_STATS

# Advertisers Endpoints
@app.get("/api/advertisers")
async def get_advertisers(payload: dict = Depends(verify_token)):
    return {"data": MOCK_ADVERTISERS, "total": len(MOCK_ADVERTISERS)}

@app.get("/api/advertisers/{advertiser_id}")
async def get_advertiser(advertiser_id: str, payload: dict = Depends(verify_token)):
    advertiser = next((a for a in MOCK_ADVERTISERS if a["id"] == advertiser_id), None)
    if not advertiser:
        raise HTTPException(status_code=404, detail="Advertiser not found")
    return advertiser

@app.post("/api/advertisers")
async def create_advertiser(advertiser: dict, payload: dict = Depends(verify_token)):
    new_advertiser = {
        "id": f"adv_{len(MOCK_ADVERTISERS) + 1}",
        **advertiser,
        "created_at": datetime.now().isoformat()
    }
    MOCK_ADVERTISERS.append(new_advertiser)
    return new_advertiser

@app.put("/api/advertisers/{advertiser_id}")
async def update_advertiser(advertiser_id: str, advertiser: dict, payload: dict = Depends(verify_token)):
    idx = next((i for i, a in enumerate(MOCK_ADVERTISERS) if a["id"] == advertiser_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Advertiser not found")
    MOCK_ADVERTISERS[idx].update(advertiser)
    return MOCK_ADVERTISERS[idx]

# Campaigns Endpoints
@app.get("/api/campaigns")
async def get_campaigns(payload: dict = Depends(verify_token)):
    return {"data": MOCK_CAMPAIGNS, "total": len(MOCK_CAMPAIGNS)}

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, payload: dict = Depends(verify_token)):
    campaign = next((c for c in MOCK_CAMPAIGNS if c["id"] == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@app.post("/api/campaigns")
async def create_campaign(campaign: dict, payload: dict = Depends(verify_token)):
    new_campaign = {
        "id": f"camp_{len(MOCK_CAMPAIGNS) + 1}",
        **campaign,
        "clicks": 0,
        "conversions": 0,
        "revenue": 0,
        "created_at": datetime.now().isoformat()
    }
    MOCK_CAMPAIGNS.append(new_campaign)
    return new_campaign

# Affiliates Endpoints
@app.get("/api/affiliates")
async def get_affiliates(payload: dict = Depends(verify_token)):
    return {"data": MOCK_AFFILIATES, "total": len(MOCK_AFFILIATES)}

@app.get("/api/affiliates/{affiliate_id}")
async def get_affiliate(affiliate_id: str, payload: dict = Depends(verify_token)):
    affiliate = next((a for a in MOCK_AFFILIATES if a["id"] == affiliate_id), None)
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    return affiliate

@app.put("/api/affiliates/{affiliate_id}/status")
async def update_affiliate_status(affiliate_id: str, data: dict, payload: dict = Depends(verify_token)):
    idx = next((i for i, a in enumerate(MOCK_AFFILIATES) if a["id"] == affiliate_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    MOCK_AFFILIATES[idx]["status"] = data["status"]
    return MOCK_AFFILIATES[idx]

# Conversions Endpoints
@app.get("/api/conversions")
async def get_conversions(payload: dict = Depends(verify_token)):
    return {"data": MOCK_CONVERSIONS[:20], "total": len(MOCK_CONVERSIONS)}

# Clicks Endpoints
@app.get("/api/clicks")
async def get_clicks(payload: dict = Depends(verify_token)):
    return {"data": MOCK_CLICKS[:50], "total": len(MOCK_CLICKS)}

# Payouts Endpoints
@app.get("/api/payouts")
async def get_payouts(payload: dict = Depends(verify_token)):
    return {"data": MOCK_PAYOUTS, "total": len(MOCK_PAYOUTS)}

@app.put("/api/payouts/{payout_id}/status")
async def update_payout_status(payout_id: str, data: dict, payload: dict = Depends(verify_token)):
    idx = next((i for i, p in enumerate(MOCK_PAYOUTS) if p["id"] == payout_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Payout not found")
    MOCK_PAYOUTS[idx]["status"] = data["status"]
    if data["status"] == "approved":
        MOCK_PAYOUTS[idx]["processed_at"] = datetime.now().isoformat()
    return MOCK_PAYOUTS[idx]

# Coupons Endpoints
@app.get("/api/coupons")
async def get_coupons(payload: dict = Depends(verify_token)):
    return {"data": MOCK_COUPONS, "total": len(MOCK_COUPONS)}

# Settings Endpoints
@app.get("/api/settings")
async def get_settings(payload: dict = Depends(verify_token)):
    return MOCK_SETTINGS

@app.put("/api/settings")
async def update_settings(settings: dict, payload: dict = Depends(verify_token)):
    MOCK_SETTINGS.update(settings)
    return MOCK_SETTINGS

# ============================================
# SHAREYOURSALES - NOUVELLES ROUTES
# ============================================

# 2FA Routes
@app.post("/api/auth/verify-2fa")
async def verify_2fa(data: dict):
    """Vérification du code 2FA"""
    email = data.get("email")
    code = data.get("code")
    temp_token = data.get("temp_token")
    
    try:
        # Vérifier temp_token
        payload = jwt.decode(temp_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Trouver l'utilisateur
        user = next((u for u in MOCK_USERS if u["id"] == payload["sub"]), None)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Vérifier le code 2FA (mock - accepter 123456 pour tous)
        expected_code = MOCK_2FA_CODES.get(user["email"], "123456")
        if code != expected_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code 2FA incorrect"
            )
        
        # Code correct, créer le vrai token
        access_token = create_access_token({
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"]
        })
        
        user_data = {k: v for k, v in user.items() if k != "password"}
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Code expiré, veuillez vous reconnecter")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Token invalide")

# Merchants Routes (ShareYourSales)
@app.get("/api/merchants")
async def get_merchants(payload: dict = Depends(verify_token)):
    """Liste tous les merchants"""
    return {"merchants": MOCK_MERCHANTS, "total": len(MOCK_MERCHANTS)}

@app.get("/api/merchants/{merchant_id}")
async def get_merchant(merchant_id: str, payload: dict = Depends(verify_token)):
    """Récupère les détails d'un merchant"""
    merchant = next((m for m in MOCK_MERCHANTS if m["id"] == merchant_id), None)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant non trouvé")
    return merchant

# Influencers Routes
@app.get("/api/influencers")
async def get_influencers(payload: dict = Depends(verify_token)):
    """Liste tous les influencers"""
    return {"influencers": MOCK_INFLUENCERS, "total": len(MOCK_INFLUENCERS)}

@app.get("/api/influencers/{influencer_id}")
async def get_influencer(influencer_id: str, payload: dict = Depends(verify_token)):
    """Récupère les détails d'un influencer"""
    influencer = next((i for i in MOCK_INFLUENCERS if i["id"] == influencer_id), None)
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer non trouvé")
    return influencer

# Products Routes
@app.get("/api/products")
async def get_products(category: Optional[str] = None, merchant_id: Optional[str] = None):
    """Liste tous les produits avec filtres optionnels"""
    products = MOCK_PRODUCTS
    
    if category:
        products = [p for p in products if p.get("category", "").lower() == category.lower()]
    
    if merchant_id:
        products = [p for p in products if p.get("merchant_id") == merchant_id]
    
    return {"products": products, "total": len(products)}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Récupère les détails d'un produit"""
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product

# Affiliate Links Routes
@app.get("/api/affiliate-links")
async def get_affiliate_links(payload: dict = Depends(verify_token)):
    """Liste les liens d'affiliation"""
    user = next((u for u in MOCK_USERS if u["id"] == payload["sub"]), None)
    links = MOCK_AFFILIATE_LINKS
    
    # Filtrer selon le rôle
    if user and user["role"] == "influencer":
        influencer = next((i for i in MOCK_INFLUENCERS if i["user_id"] == user["id"]), None)
        if influencer:
            links = [l for l in links if l.get("influencer_id") == influencer["id"]]
    
    return {"links": links, "total": len(links)}

@app.post("/api/affiliate-links/generate")
async def generate_affiliate_link(data: dict, payload: dict = Depends(verify_token)):
    """Génère un lien d'affiliation"""
    user = next((u for u in MOCK_USERS if u["id"] == payload["sub"]), None)
    
    if user["role"] != "influencer":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    influencer = next((i for i in MOCK_INFLUENCERS if i["user_id"] == user["id"]), None)
    if not influencer:
        raise HTTPException(status_code=404, detail="Profil influencer non trouvé")
    
    product_id = data.get("product_id")
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Générer le lien
    short_code = f"{influencer['username'][:4]}-{product.get('slug', 'prod')[:6]}"
    new_link = {
        "id": f"link_{len(MOCK_AFFILIATE_LINKS) + 1}",
        "influencer_id": influencer["id"],
        "influencer_name": influencer["full_name"],
        "product_id": product_id,
        "product_name": product["name"],
        "short_link": f"shs.io/{short_code}",
        "full_link": f"https://shareyoursales.com/track/{influencer['username']}_{product.get('slug', 'prod')}",
        "clicks": 0,
        "conversions": 0,
        "conversion_rate": 0.0,
        "revenue": 0.0,
        "commission_earned": 0.0,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_AFFILIATE_LINKS.append(new_link)
    
    return {"message": "Lien généré avec succès", "link": new_link}

# AI Marketing Routes
@app.post("/api/ai/generate-content")
async def generate_ai_content(data: dict, payload: dict = Depends(verify_token)):
    """Génère du contenu avec l'IA (mock)"""
    content_type = data.get("type", "social_post")
    platform = data.get("platform", "Instagram")
    
    # Mock: Générer du contenu
    if content_type == "social_post":
        generated_text = f"🌟 Découvrez ce produit incroyable ! Parfait pour vous. Ne manquez pas cette opportunité ! 💫 #Promo #Shopping #Lifestyle"
    elif content_type == "email":
        generated_text = "Bonjour,\n\nNous sommes ravis de vous présenter notre dernier produit...\n\nCordialement"
    else:
        generated_text = "Contenu généré par IA"
    
    return {
        "content": generated_text,
        "type": content_type,
        "platform": platform,
        "suggested_hashtags": ["#Promo", "#Shopping", "#Deal"]
    }

@app.get("/api/ai/predictions")
async def get_ai_predictions(payload: dict = Depends(verify_token)):
    """Récupère les prédictions IA (mock)"""
    return MOCK_AI_PREDICTIONS

# Subscription Plans Routes
@app.get("/api/subscription-plans")
async def get_subscription_plans():
    """Récupère tous les plans d'abonnement"""
    return SUBSCRIPTION_PLANS

# Analytics Routes
@app.get("/api/analytics/overview")
async def get_analytics_overview(payload: dict = Depends(verify_token)):
    """Vue d'ensemble des analytics"""
    user = next((u for u in MOCK_USERS if u["id"] == payload["sub"]), None)
    
    if user["role"] == "admin":
        return {
            "total_revenue": 502000.00,
            "total_merchants": len(MOCK_MERCHANTS),
            "total_influencers": len(MOCK_INFLUENCERS),
            "total_products": len(MOCK_PRODUCTS),
            "active_links": len(MOCK_AFFILIATE_LINKS)
        }
    
    elif user["role"] == "merchant":
        merchant = next((m for m in MOCK_MERCHANTS if m.get("user_id") == user["id"]), MOCK_MERCHANTS[0] if MOCK_MERCHANTS else {})
        return {
            "total_sales": merchant.get("total_sales", 0),
            "products_count": merchant.get("products_count", 0),
            "affiliates_count": merchant.get("affiliates_count", 0),
            "roi": 320.5
        }
    
    elif user["role"] == "influencer":
        influencer = next((i for i in MOCK_INFLUENCERS if i.get("user_id") == user["id"]), MOCK_INFLUENCERS[0] if MOCK_INFLUENCERS else {})
        return {
            "total_earnings": influencer.get("total_earnings", 0),
            "total_clicks": influencer.get("total_clicks", 0),
            "total_sales": influencer.get("total_sales", 0)
        }
    
    return {}

# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ShareYourSales API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
