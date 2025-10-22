from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import os
from mock_data_shareyoursales import *

# Initialize FastAPI app
app = FastAPI(
    title="ShareYourSales API",
    description="API complète pour la plateforme ShareYourSales",
    version="1.0.0"
)

# CORS configuration - IMPORTANT: Ne pas modifier
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8001")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "shareyoursales-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# ============================================
# PYDANTIC MODELS
# ============================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TwoFactorRequest(BaseModel):
    email: EmailStr
    code: str
    temp_token: str

class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    temp_token: Optional[str] = None
    token_type: str = "bearer"
    requires_2fa: bool = False
    user: Optional[dict] = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # 'merchant' or 'influencer'
    first_name: str
    last_name: str
    phone: str
    # Additional fields based on role
    company_name: Optional[str] = None
    username: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
    success: bool = True

class StatsResponse(BaseModel):
    stats: dict

# ============================================
# HELPER FUNCTIONS
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie et décode un token JWT"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

def get_current_user(payload: dict = Depends(verify_token)):
    """Récupère l'utilisateur actuel depuis le token"""
    user = next((u for u in MOCK_USERS if u["id"] == payload.get("sub")), None)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.get("/")
async def root():
    return {
        "message": "ShareYourSales API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Connexion utilisateur avec 2FA
    Étape 1: Vérification email/password
    Étape 2: Envoi code 2FA (mock)
    """
    # Find user
    user = next((u for u in MOCK_USERS if u["email"] == request.email), None)
    
    if not user or user["password"] != request.password:
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
        code = MOCK_2FA_CODES.get(user["email"], generate_2fa_code())
        
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
            "message": f"Code 2FA envoyé au {user['phone']}"
        }
    
    # Si pas de 2FA, connexion directe
    access_token = create_access_token({"sub": user["id"], "email": user["email"], "role": user["role"]})
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_2fa": False,
        "user": user_data
    }

@app.post("/api/auth/verify-2fa", response_model=LoginResponse)
async def verify_2fa(request: TwoFactorRequest):
    """
    Vérification du code 2FA
    """
    try:
        # Vérifier temp_token
        payload = jwt.decode(request.temp_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if not payload.get("temp"):
            raise HTTPException(status_code=400, detail="Token invalide")
        
        # Trouver l'utilisateur
        user = next((u for u in MOCK_USERS if u["id"] == payload["sub"]), None)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Vérifier le code 2FA
        expected_code = MOCK_2FA_CODES.get(user["email"], "123456")
        if request.code != expected_code:
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
            "requires_2fa": False,
            "user": user_data
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Code expiré, veuillez vous reconnecter")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Token invalide")

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """
    Inscription nouvel utilisateur (Merchant ou Influencer)
    """
    # Vérifier si email existe déjà
    if any(u["email"] == request.email for u in MOCK_USERS):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Créer nouvel utilisateur (mock)
    new_user_id = f"user_{request.role}_{len(MOCK_USERS) + 1}"
    
    new_user = {
        "id": new_user_id,
        "email": request.email,
        "password": request.password,
        "role": request.role,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "phone": request.phone,
        "phone_verified": False,
        "two_fa_enabled": True,
        "country": "FR",
        "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={request.first_name}",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_USERS.append(new_user)
    
    # Créer profil selon le rôle
    if request.role == "merchant" and request.company_name:
        new_merchant = {
            "id": f"merchant_{len(MOCK_MERCHANTS) + 1}",
            "user_id": new_user_id,
            "company_name": request.company_name,
            "subscription_plan": "free",
            "commission_rate": 7.0,
            "monthly_fee": 0.0,
            "total_sales": 0.0,
            "total_commission_paid": 0.0,
            "created_at": datetime.now().isoformat()
        }
        MOCK_MERCHANTS.append(new_merchant)
    
    elif request.role == "influencer" and request.username:
        new_influencer = {
            "id": f"influencer_{len(MOCK_INFLUENCERS) + 1}",
            "user_id": new_user_id,
            "username": request.username,
            "full_name": f"{request.first_name} {request.last_name}",
            "subscription_plan": "starter",
            "platform_fee_rate": 5.0,
            "monthly_fee": 9.90,
            "total_clicks": 0,
            "total_sales": 0,
            "total_earnings": 0.0,
            "balance": 0.0,
            "created_at": datetime.now().isoformat()
        }
        MOCK_INFLUENCERS.append(new_influencer)
    
    return {
        "message": "Inscription réussie ! Un code de vérification a été envoyé à votre téléphone.",
        "user_id": new_user_id,
        "success": True
    }

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur connecté"""
    user_data = {k: v for k, v in current_user.items() if k != "password"}
    
    # Ajouter les infos du profil selon le rôle
    if current_user["role"] == "merchant":
        merchant = next((m for m in MOCK_MERCHANTS if m["user_id"] == current_user["id"]), None)
        if merchant:
            user_data["merchant_profile"] = merchant
    
    elif current_user["role"] == "influencer":
        influencer = next((i for i in MOCK_INFLUENCERS if i["user_id"] == current_user["id"]), None)
        if influencer:
            user_data["influencer_profile"] = influencer
    
    return user_data

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Déconnexion"""
    return {"message": "Déconnexion réussie"}

# ============================================
# DASHBOARD ENDPOINTS
# ============================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats_endpoint(current_user: dict = Depends(get_current_user)):
    """Récupère les statistiques du dashboard selon le rôle"""
    stats = get_dashboard_stats(current_user["role"], current_user["id"])
    return {"stats": stats}

@app.get("/api/dashboard/charts")
async def get_dashboard_charts(current_user: dict = Depends(get_current_user)):
    """Récupère les données pour les graphiques du dashboard"""
    
    # Mock data pour les graphiques
    last_7_days = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    
    return {
        "revenue_chart": [
            {"date": date, "revenue": random.randint(3000, 8000)} 
            for date in last_7_days
        ],
        "conversions_chart": [
            {"date": date, "conversions": random.randint(20, 50)} 
            for date in last_7_days
        ],
        "clicks_chart": [
            {"date": date, "clicks": random.randint(200, 600)} 
            for date in last_7_days
        ]
    }

# ============================================
# MERCHANTS ENDPOINTS
# ============================================

@app.get("/api/merchants")
async def get_merchants(current_user: dict = Depends(get_current_user)):
    """Liste tous les merchants (Admin seulement)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return {"merchants": MOCK_MERCHANTS, "total": len(MOCK_MERCHANTS)}

@app.get("/api/merchants/{merchant_id}")
async def get_merchant(merchant_id: str, current_user: dict = Depends(get_current_user)):
    """Récupère les détails d'un merchant"""
    merchant = next((m for m in MOCK_MERCHANTS if m["id"] == merchant_id), None)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant non trouvé")
    
    return merchant

@app.put("/api/merchants/{merchant_id}")
async def update_merchant(
    merchant_id: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Met à jour un merchant"""
    merchant = next((m for m in MOCK_MERCHANTS if m["id"] == merchant_id), None)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant non trouvé")
    
    # Vérifier les permissions
    if current_user["role"] not in ["admin", "merchant"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Update mock data
    merchant.update(data)
    merchant["updated_at"] = datetime.now().isoformat()
    
    return {"message": "Merchant mis à jour", "merchant": merchant}

# ============================================
# INFLUENCERS ENDPOINTS
# ============================================

@app.get("/api/influencers")
async def get_influencers(current_user: dict = Depends(get_current_user)):
    """Liste tous les influencers"""
    return {"influencers": MOCK_INFLUENCERS, "total": len(MOCK_INFLUENCERS)}

@app.get("/api/influencers/{influencer_id}")
async def get_influencer(influencer_id: str, current_user: dict = Depends(get_current_user)):
    """Récupère les détails d'un influencer"""
    influencer = next((i for i in MOCK_INFLUENCERS if i["id"] == influencer_id), None)
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer non trouvé")
    
    return influencer

@app.put("/api/influencers/{influencer_id}")
async def update_influencer(
    influencer_id: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Met à jour un influencer"""
    influencer = next((i for i in MOCK_INFLUENCERS if i["id"] == influencer_id), None)
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer non trouvé")
    
    # Vérifier les permissions
    if current_user["role"] not in ["admin", "influencer"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Update mock data
    influencer.update(data)
    influencer["updated_at"] = datetime.now().isoformat()
    
    return {"message": "Influencer mis à jour", "influencer": influencer}

# ============================================
# PRODUCTS ENDPOINTS
# ============================================

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    merchant_id: Optional[str] = None
):
    """Liste tous les produits avec filtres optionnels"""
    products = MOCK_PRODUCTS
    
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    
    if merchant_id:
        products = [p for p in products if p["merchant_id"] == merchant_id]
    
    return {"products": products, "total": len(products)}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Récupère les détails d'un produit"""
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return product

@app.post("/api/products")
async def create_product(data: dict, current_user: dict = Depends(get_current_user)):
    """Crée un nouveau produit (Merchant seulement)"""
    if current_user["role"] != "merchant":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    new_product = {
        "id": f"prod_{len(MOCK_PRODUCTS) + 1}",
        "merchant_id": data.get("merchant_id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "category": data.get("category"),
        "price": data.get("price"),
        "currency": "EUR",
        "commission_rate": data.get("commission_rate", 15.0),
        "commission_type": "percentage",
        "is_available": True,
        "total_views": 0,
        "total_clicks": 0,
        "total_sales": 0,
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_PRODUCTS.append(new_product)
    
    return {"message": "Produit créé", "product": new_product}

# ============================================
# AFFILIATE LINKS ENDPOINTS
# ============================================

@app.get("/api/affiliate-links")
async def get_affiliate_links(current_user: dict = Depends(get_current_user)):
    """Liste les liens d'affiliation"""
    links = MOCK_AFFILIATE_LINKS
    
    # Filtrer selon le rôle
    if current_user["role"] == "influencer":
        influencer = next((i for i in MOCK_INFLUENCERS if i["user_id"] == current_user["id"]), None)
        if influencer:
            links = [l for l in links if l["influencer_id"] == influencer["id"]]
    
    return {"links": links, "total": len(links)}

@app.post("/api/affiliate-links/generate")
async def generate_affiliate_link(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Génère un lien d'affiliation (Influencer seulement)"""
    if current_user["role"] != "influencer":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    influencer = next((i for i in MOCK_INFLUENCERS if i["user_id"] == current_user["id"]), None)
    if not influencer:
        raise HTTPException(status_code=404, detail="Profil influencer non trouvé")
    
    product_id = data.get("product_id")
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Générer le lien
    short_code = f"{influencer['username'][:4]}-{product['slug'][:6]}"
    new_link = {
        "id": f"link_{len(MOCK_AFFILIATE_LINKS) + 1}",
        "influencer_id": influencer["id"],
        "influencer_name": influencer["full_name"],
        "product_id": product_id,
        "product_name": product["name"],
        "short_link": f"shs.io/{short_code}",
        "full_link": f"https://shareyoursales.com/track/{influencer['username']}_{product['slug']}",
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

# ============================================
# AI MARKETING ENDPOINTS
# ============================================

@app.post("/api/ai/generate-content")
async def generate_ai_content(data: dict, current_user: dict = Depends(get_current_user)):
    """Génère du contenu avec l'IA (mock)"""
    content_type = data.get("type", "social_post")
    platform = data.get("platform", "Instagram")
    tone = data.get("tone", "friendly")
    product_id = data.get("product_id")
    
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
        "tone": tone,
        "suggested_hashtags": ["#Promo", "#Shopping", "#Deal"]
    }

@app.get("/api/ai/predictions")
async def get_ai_predictions(current_user: dict = Depends(get_current_user)):
    """Récupère les prédictions IA (mock)"""
    return MOCK_AI_PREDICTIONS

@app.post("/api/ai/optimize-campaign")
async def optimize_campaign(data: dict, current_user: dict = Depends(get_current_user)):
    """Optimise une campagne avec l'IA (mock)"""
    campaign_id = data.get("campaign_id")
    
    return {
        "recommendations": [
            "Augmenter le budget de 15% sur Instagram",
            "Cibler les 25-34 ans pour de meilleurs résultats",
            "Publier entre 18h-20h pour plus d'engagement"
        ],
        "predicted_improvement": 23.5,
        "confidence": 87.3
    }

# ============================================
# SUBSCRIPTION PLANS ENDPOINTS
# ============================================

@app.get("/api/subscription-plans")
async def get_subscription_plans():
    """Récupère tous les plans d'abonnement"""
    return SUBSCRIPTION_PLANS

@app.post("/api/subscription/upgrade")
async def upgrade_subscription(data: dict, current_user: dict = Depends(get_current_user)):
    """Change le plan d'abonnement"""
    plan_id = data.get("plan_id")
    
    # Mock: Mise à jour du plan
    if current_user["role"] == "merchant":
        merchant = next((m for m in MOCK_MERCHANTS if m["user_id"] == current_user["id"]), None)
        if merchant:
            # Extraire le plan name depuis plan_id
            plan_name = plan_id.replace("plan_merchant_", "")
            merchant["subscription_plan"] = plan_name
            merchant["updated_at"] = datetime.now().isoformat()
    
    elif current_user["role"] == "influencer":
        influencer = next((i for i in MOCK_INFLUENCERS if i["user_id"] == current_user["id"]), None)
        if influencer:
            plan_name = plan_id.replace("plan_influencer_", "")
            influencer["subscription_plan"] = plan_name
            influencer["updated_at"] = datetime.now().isoformat()
    
    return {"message": "Abonnement mis à jour avec succès", "new_plan": plan_id}

# ============================================
# STATS & ANALYTICS ENDPOINTS
# ============================================

@app.get("/api/analytics/overview")
async def get_analytics_overview(current_user: dict = Depends(get_current_user)):
    """Vue d'ensemble des analytics"""
    
    if current_user["role"] == "admin":
        return {
            "total_revenue": 502000.00,
            "total_merchants": len(MOCK_MERCHANTS),
            "total_influencers": len(MOCK_INFLUENCERS),
            "total_products": len(MOCK_PRODUCTS),
            "active_links": len(MOCK_AFFILIATE_LINKS),
            "month_over_month_growth": 12.5
        }
    
    elif current_user["role"] == "merchant":
        merchant = next((m for m in MOCK_MERCHANTS if m["user_id"] == current_user["id"]), MOCK_MERCHANTS[0])
        return {
            "total_sales": merchant["total_sales"],
            "products_count": merchant.get("products_count", 0),
            "affiliates_count": merchant.get("affiliates_count", 0),
            "roi": 320.5
        }
    
    elif current_user["role"] == "influencer":
        influencer = next((i for i in MOCK_INFLUENCERS if i["user_id"] == current_user["id"]), MOCK_INFLUENCERS[0])
        return {
            "total_earnings": influencer["total_earnings"],
            "total_clicks": influencer["total_clicks"],
            "total_sales": influencer["total_sales"],
            "conversion_rate": (influencer["total_sales"] / influencer["total_clicks"] * 100) if influencer["total_clicks"] > 0 else 0
        }
    
    return {}

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ShareYourSales API"
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
